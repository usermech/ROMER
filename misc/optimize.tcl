# bgexec.tcl from http://chiselapp.com/user/MHo/repository/tcl-modules/dir?ci=6fca3679027cf4fb6340680f4bdad1649aec88e8&name=bgexec
source ./bgexec.tcl

set webotspath REPLACE_WITH_WEBOTS_PATH
# initial parameters. tagcount is gridx*gridy.
array set config {
	gridx 4
	gridy 4
	tagsize 10
}
# format: min incr max
set gridxlim {4 1 6}
set gridylim {4 1 6}
set tagsizelim {10 5 20}

set maxtags 100

proc webotscbk {txt} {
	global h2
	puts $txt
	if {[string match "*INFO: 'heatmap_supervisor' controller exited successfully.*" $txt]} {
		puts -nonewline "\033\[0m"
		puts "Ending Webots process."
		after 1000 {exec [auto_execok taskkill] /F /PID [pid $h2]}
	}
}

proc plottercbk {txt} {
	global scorelist config
	puts $txt
	if {[string match "*SCORE*" $txt]} {
		set score [lindex [split $txt] 1]
		set scorelist($score) [array get config]
	}
}

proc simulate {tagsize tagcount grid} {
	global webotspath h2 times
	
	set tstart [clock seconds]
	puts "\033\[1;32mNEW SIM: $tagcount tags with grid: $grid size: $tagsize\033\[0m"
	global pCount
	# setup ceiling markers
	set h1 [bgExec "python ceiling_gen.py --type DICT_4X4_100 --size $tagsize -d $tagcount \"$grid\"" {puts} pCount]
	vwait pCount
	# run sim
	puts -nonewline "\033\[1;33m"
	set h2 [bgExec "$webotspath --batch --stdout --stderr --minimize --no-rendering --mode=fast ../worlds/romer_lab.wbt" {webotscbk} pCount]
	vwait pCount
	# plot heatmaps
	set h3 [bgExec "python heatmap_plotter.py $tagcount $grid $tagsize" {plottercbk} pCount]
	vwait pCount
	set tstop [clock seconds]
	lappend times [expr {$tstop - $tstart}]
}

# which axes to optimize over, and in which order
set params {gridx gridy tagsize}

foreach param $params {
	# get relevant limits
	lassign [set ${param}lim] minval increment maxval
	
	# run simulation varying a single parameter. Also be careful not to go over the maximum tag count.
	for {set val $minval} {($val <= $maxval) && ($config(gridx)*$config(gridy)<=$maxtags)} {incr val $increment} {
		# update parameters
		set config($param) $val
		# run simulation
		simulate $config(tagsize) [expr {$config(gridx)*$config(gridy)}] [list $config(gridx) $config(gridy)]
	}
	
	puts "SCORES: [array get scorelist]"
	# find the configuration with the lowest score
	set lowestscore [lindex [lsort [array names scorelist]] 0]
	puts $lowestscore
	array set config $scorelist($lowestscore)
	
	# erase scores for next loop
	unset scorelist
}

# sum all times to get total duration
set tsum [::tcl::mathop::+ {*}$times]
puts "\033\[1;32mOptimization completed.\n Total Duration: $tsum\n Test Durations: $times\n Final Configuration: [array get config]\n Final Score: $lowestscore\033\[0m"
