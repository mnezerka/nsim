#!/bin/tclsh

package require Tcl 8.4
package require json

# data is plain old tcl values
# spec is defined as follows:
# {string} - data is simply a string, "quote" it if it's not a number
# {list} - data is a tcl list of strings, convert to JSON arrays
# {list list} - data is a tcl list of lists
# {list dict} - data is a tcl list of dicts
# {dict} - data is a tcl dict of strings
# {dict xx list} - data is a tcl dict where the value of key xx is a tcl list
# {dict * list} - data is a tcl dict of lists
# etc..
proc compile_json {spec data} {
	while [llength $spec] {
		set type [lindex $spec 0]
		set spec [lrange $spec 1 end]

		switch -- $type {
			dict {
				lappend spec * string
				set json {}
				foreach {key val} $data {
					foreach {keymatch valtype} $spec {
						if {[string match $keymatch $key]} {
							lappend json [subst {"$key":[compile_json $valtype $val]}]
							break
						}
					}
				}
				return "{[join $json ,]}"
			}
			list {
				if {![llength $spec]} {
					set spec string
				} else {
					set spec [lindex $spec 0]
				}
				set json {}
				foreach {val} $data {
					lappend json [compile_json $spec $val]
				}
				return "\[[join $json ,]\]"
			}
			string {
				if {[string is double -strict $data]} {
					return $data
				} else {
					return "\"$data\""
				}
			}
			default {error "Invalid type"}
		}
	}
}

#set data [compile_json {dict * list} {a {1 2 3} b {4 5}}]
#set data [compile_json {list} {1 2 3 4 5}]
#puts $data

#puts [json::json2dict $data]

set sock [socket "www.seznam.cz" 80]
puts $sock "GET /\n"
flush $sock

set page "" 
while { [gets $sock line] >= 0 } {
	append page $line
}

puts $page
