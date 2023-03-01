 ################################################################################
 # Modul    : bgexec.tcl 1.16                                                   #
 # Changed  : 16.10.2015                                                        #
 # Purpose  : running processes in the background, catching their output via    #
 #            event handlers                                                    #
 # Author   : M.Hoffmann                                                        #
 # Hinweise : >&@ and 2>@stdout don't work on Windows. A work around probably   #
 #            could be using a temporay file. Beginning with Tcl 8.4.7 / 8.5    #
 #            there is another (yet undocumented) way of redirection: 2>@1.     #
 # History  :                                                                   #
 # 19.11.03 v1.0 1st version                                                    #
 # 20.07.04 v1.1 callback via UPLEVEL                                           #
 # 08.09.04 v1.2 using 2>@1 instead of 2>@stdout if Tcl >= 8.4.7;               #
 #               timeout-feature                                                #
 # 13.10.04 v1.3 bugfix in bgExecTimeout, readHandler is interruptable          #
 # 18.10.04 v1.4 bugfix: bgExecTimeout needs to be canceled when work is done;  #
 #               some optimizations                                             #
 # 14.03.05 v1.4 comments translated to english                                 #
 # 17.11.05 v1.5 If specidied, a user defined timeout handler `toExit` runs in  #
 #               case of a timeout to give chance to kill the PIDs given as     #
 #               arg. Call should be compatible (optional parameter).           #
 # 23.11.05 v1.6 User can give additional argument to his readhandler.          #
 # 03.07.07 v1.7 Some Simplifications (almost compatible, unless returned       #
 #               string where parsed):                                          #
 #               - don't catch error first then returning error to main...      #
 # 08.10.07 v1.8 fixed buggy version check!                                     #
 # 20.02.12 v1.9 Optionally signal EOF to eofHandler.                           #
 # 13.09.14 v1.10 bugfix: incr myCount later (in case of an (open)error it was  #
 #               erranously incremented yet)                                    #
 # 22.02.15 v1.11 llength instead of string length for some tests. Calling EOF- #
 #               handler when processing terminates via readhandler-break.      #
 # 28.02.15 v1.12 bugfix: preventing invalid processcounter w/timeout (I hope). #
 # 02.03.15 v1.13 eof handler not fired if user readhandler breaks.             #
 #               Logic of user timeout handler now equals user read handler.    #
 # 21.03.15 v1.14 Testing EOF right after read (man page); -buffering line.     #
 # 21.03.15 v1.15 CATCHing gets. New optional errHandler. Logic changed.        #
 # 16.10.15 v1.16 Bugfix: missing return after user-readhandler CATCHed.        #
 # ATTENTION: closing a pipe leads to error broken pipe if the opened process   #
 #             itself is a tclsh interpreter. Currently I don't know how to     #
 #             avoid this without killing the process via toExit before closing #
 #             the pipeline.                                                    #
 # - This Code uses one global var, the counter of currently started pipelines. #
 # TODO: Namespace or OO to clean up overall design.                            #
 ################################################################################

 # ATTENTION: This is the last version which maintains upward compatibility (I hope)
 package provide bgexec 1.16

 #-------------------------------------------------------------------------------
 # If the <prog>ram successfully starts, its STDOUT and STDERR is dispatched
 # line by line to the <readHandler> (via bgExecGenericHandler) as last arg. The
 # global var <pCount> holds the number of processes called this way. If a <timeout>
 # is specified (as msecs), the process pipeline will be automatically closed after
 # that duration. If specified, and a timeout occurs, <toExit> is called with the
 # PIDs of the processes right before closing the process pipeline.
 # Returns the handle of the process-pipeline.
 #
 proc bgExec {prog readHandler pCount {timeout 0} {toExit ""} {eofHandler ""} {errHandler ""}} {
      upvar #0 $pCount myCount
      set p [expr {[lindex [lsort -dict [list 8.4.7 [info patchlevel]]] 0] == "8.4.7"?"| $prog 2>@1":"| $prog 2>@stdout"}]
      set pH [open $p r]
      # Possible Problem if both after event and fileevents are delayed (no event loop) until timeout fires;
      # ProcessCount is then decremented before ever incremented. So increment ProcessCount early!
      set myCount [expr {[info exists myCount]?[incr myCount]:1}]; # precaution < 8.6
      fconfigure $pH -blocking 0 -buffering line
      set tID [expr {$timeout?[after $timeout [list bgExecTimeout $pH $pCount $toExit]]:{}}]
      fileevent $pH readable [list bgExecGenericHandler $pH $pCount $readHandler $tID $eofHandler $errHandler]
      return $pH
 }
 #-------------------------------------------------------------------------------
 proc bgExecGenericHandler {chan pCount readHandler tID eofHandler errHandler} {
      upvar #0 $pCount myCount
      if {[catch {gets $chan line} result]} {
         # read error -> abort processing. NOTE eof-handler NOT fired!
         after cancel $tID
         catch {close $chan}
         incr myCount -1
         if {[llength $errHandler]} {
            catch {uplevel $errHandler $chan $result}
         }
         return
      } elseif {$result >= 0} {
         # we got a whole line
         lappend readHandler $line; # readhandler doesn't get the chan...
         if {[catch {uplevel $readHandler}]} {
            # user-readHandler ended with errorcode which means here
            # "terminate the processing". NOTE eof-handler NOT fired!
            after cancel $tID
            catch {close $chan}
            incr myCount -1
            return
         }
      }; # not enough data (yet)
      if {[eof $chan]} {
         after cancel $tID; # terminate Timeout, no longer needed! 
         catch {close $chan}; # automatically deregisters the fileevent handler
         incr myCount -1
         if {[llength $eofHandler]} {
            catch {uplevel $eofHandler $chan}; # not called on timeout or user-break
         }
      }
 }
 #-------------------------------------------------------------------------------
 proc bgExecTimeout {chan pCount toExit} {
      upvar #0 $pCount myCount
      if {[llength $toExit]} {
         # The PIDs are one arg (list)
         if {[catch {uplevel [list {*}$toExit [pid $chan]]}]} {
            # user-timeoutHandler ended with error which means here
            # "we didn't kill the processes" (such a kill would have
            # normally triggered an EOF, so no other cleanup would be
            # required then), so end the processing explicitely and do
            # the cleanup. NOTE eof-handler NOT fired!
            catch {close $chan}
            incr myCount -1
         }
      } else {
         # No user-timeoutHandler exists, we must cleanup anyway
         #  NOTE eof-handler NOT fired!
         catch {close $chan}
         incr myCount -1
      }
 }
 #===============================================================================
