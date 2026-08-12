if {$argc < 2 || [lindex $argv 0] eq "--help"} {puts "Usage: regex-filter PATTERN FILE ?--invert?"; exit [expr {$argc<2 ? 2 : 0}]}
set pattern [lindex $argv 0]; set file [lindex $argv 1]; set invert [expr {[lsearch -exact $argv "--invert"] >= 0}]
if {[catch {open $file r} f]} {puts stderr $f; exit 2}
set n 0; while {[gets $f line] >= 0} {set m [regexp -- $pattern $line]; if {$invert ? !$m : $m} {puts $line; incr n}}; close $f; puts stderr "matched=$n"
