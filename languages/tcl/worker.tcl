set KEY 151
proc transform {h key} {set out ""; for {set i 0} {$i < [string length $h]} {incr i 2} {scan [string range $h $i [expr {$i+1}]] %x v; append out [format %02x [expr {$v ^ $key}]]}; return $out}
fconfigure stdout -buffering line
while {[gets stdin line] >= 0} {set line [string trimright $line "\r"]; if {$line eq "PING"} {puts "PONG"; continue}; if {$line eq "QUIT"} break; if {[regexp {^[ED] ([0-9A-Fa-f]*)$} $line -> h]} {puts [transform $h $KEY]} else {puts "ERR"}}
