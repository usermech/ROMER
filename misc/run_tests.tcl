# bgexec.tcl from http://chiselapp.com/user/MHo/repository/tcl-modules/dir?ci=6fca3679027cf4fb6340680f4bdad1649aec88e8&name=bgexec
source ./bgexec.tcl

set webotspath FILLTHISIN
set tagcountlist {15 25}
set gridlist {
	{5 3}
	{5 5}
}
	

proc webotscbk {txt} {
	global h2
	if {[string match "*INFO: 'heatmap_supervisor' controller exited successfully.*" $txt]} {
		puts -nonewline "\033\[0m"
		puts "Ending Webots process."
		exec [auto_execok taskkill] /F /PID [pid $h2]
	} else {
		puts $txt
	}
}


foreach tagcount $tagcountlist grid $gridlist {
	puts "NEW TEST: $tagcount with grid: $grid"
	global pCount
	# setup ceiling markers
	set h1 [bgExec "python ceiling_gen.py -d $tagcount \"$grid\"" {puts} pCount]
	vwait pCount
	# run sim
	puts -nonewline "\033\[1;33m"
	set h2 [bgExec "$webotspath --batch --stdout --stderr --minimize --no-rendering --mode=fast ../worlds/romer_lab.wbt" {webotscbk} pCount]
	vwait pCount
	# plot heatmaps
	set h3 [bgExec "python heatmap_plotter.py" {puts} pCount]
	vwait pCount
}
