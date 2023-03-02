# bgexec.tcl from http://chiselapp.com/user/MHo/repository/tcl-modules/dir?ci=6fca3679027cf4fb6340680f4bdad1649aec88e8&name=bgexec
source ./bgexec.tcl

set webotspath FILLTHISIN

proc webotscbk {txt} {
	global h1
	if {[string match "*INFO: 'heatmap_supervisor' controller exited successfully.*" $txt]} {
		puts "Ending Webots process."
		exec [auto_execok taskkill] /F /PID [pid $h1]
	} else {
		puts $txt
	}
}

global pCount
set h1 [bgExec "$webotspath --batch --stdout --stderr --minimize --no-rendering --mode=fast ../worlds/romer_lab.wbt" {webotscbk} pCount]
vwait pCount
set h2 [bgExec "python heatmap_plotter.py" {puts} pCount]
vwait pCount
