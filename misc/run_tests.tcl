# bgexec.tcl from http://chiselapp.com/user/MHo/repository/tcl-modules/dir?ci=6fca3679027cf4fb6340680f4bdad1649aec88e8&name=bgexec
source ./bgexec.tcl

set webotspath C:/Users/Anil/AppData/Local/Programs/Webots/msys64/mingw64/bin/webots.exe
set tagcountlist {49}
set gridlist {
	{7 7}
}
# tag edge length in cm
set tagsizelist {18}

# distance between heatmap grid points in cm
set gridsizelist {100}

# camera rotation in radians
set rotationlist {0.3}

proc webotscbk {txt} {
	global h3
	puts $txt
	if {[string match "*INFO: '*' controller exited successfully.*" $txt]} {
		puts -nonewline "\033\[0m"
		puts "Ending Webots process."
		after 1000 {exec [auto_execok taskkill] /F /PID [pid $h3]}
	}
}

foreach gridsize $gridsizelist {
	foreach rotation $rotationlist {
		foreach tagsize $tagsizelist {
			foreach tagcount $tagcountlist grid $gridlist {
				set tstart [clock seconds]
				puts "\033\[1;32mNEW TEST: $tagcount tags with grid: $grid, tag size: $tagsize cm, heatmap grid: $gridsize cm, rotation: $rotation rad\033\[0m"
				global pCount
				# setup ceiling markers
				set h1 [bgExec "python ceiling_gen.py --type DICT_4X4_100 --size $tagsize -d $tagcount \"$grid\"" {puts} pCount]
				vwait pCount
				# setup heatmap grid + cam rotation
				set h2 [bgExec "python creat_yaml.py --grid_size $gridsize --rotation $rotation" {puts} pCount]
				vwait pCount
				# run sim
				puts -nonewline "\033\[1;33m"
				set h3 [bgExec "$webotspath --batch --stdout --stderr --minimize --no-rendering --mode=fast ../worlds/romer_lab.wbt" {webotscbk} pCount]
				vwait pCount
				# plot heatmaps
				set h4 [bgExec "python heatmap_plotter_v2.py $tagcount $grid $tagsize" {puts} pCount]
				vwait pCount
				set tstop [clock seconds]
				lappend times [expr {$tstop - $tstart}]
			}
		}
	}
}
# sum all times to get total duration
set tsum [::tcl::mathop::+ {*}$times]
puts "\033\[1;32mTests completed.\n Total Duration: $tsum\n Test Durations: $times \033\[0m"
