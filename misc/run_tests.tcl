source ./bgexec.tcl

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
#set h1 [bgExec "C:/Users/Anil/AppData/Local/Programs/Webots/msys64/mingw64/bin/webots.exe --batch --stdout --stderr --minimize --no-rendering --mode=fast ../worlds/romer_lab.wbt" {webotscbk} pCount]
#vwait pCount
set h2 [bgExec "ipython heatmap_plotter.py" {puts} pCount]
vwait pCount