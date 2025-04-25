package require Tk

# Main window setup
toplevel .main
wm title .main "Logic Minimization Tool"
wm geometry .main 600x600

set inputs {A B C}
set num_inputs 3
set num_rows [expr {pow(2, $num_inputs)}]

# Frame: Truth Table Input
frame .input -borderwidth 2 -relief sunken
pack .input -side top -fill both -expand 1 -padx 10 -pady 10

label .input.lbl_title -text "Enter Output Y (0, 1, or x for don't care)" -font {Arial 12 bold}
pack .input.lbl_title -side top -pady 5

# Generate Truth Table Rows
for {set i 0} {$i < $num_rows} {incr i} {
    frame .input.row$i
    pack .input.row$i -side top -fill x -padx 5 -pady 2

    foreach input $inputs {
        set bit [expr {($i >> [lsearch -exact $inputs $input]) & 1}]
        label .input.row$i.lbl_$input -text "$input=$bit" -width 5
        pack .input.row$i.lbl_$input -side left -padx 2
    }

    entry .input.row$i.ent_Y -width 3 -justify center
    .input.row$i.ent_Y insert 0 0
    pack .input.row$i.ent_Y -side left -padx 10
}

# Frame: Buttons
frame .buttons
pack .buttons -side top -fill x -padx 10 -pady 5

button .buttons.btn_submit -text "Submit" -command process_logic
pack .buttons.btn_submit -side top -pady 5

# Frame: Output Display
frame .output -borderwidth 2 -relief sunken
pack .output -side top -fill both -expand 1 -padx 10 -pady 10

label .output.lbl_title -text "Results" -font {Arial 12 bold}
pack .output.lbl_title -side top -pady 5

text .output.txt_results -width 70 -height 20 -wrap word
pack .output.txt_results -side top -fill both -expand 1 -padx 5 -pady 5

# --- Logic Processing Procedure ---
proc process_logic {} {
    global inputs num_inputs

    set truth_table {}
    set num_rows [expr {pow(2, $num_inputs)}]

    for {set i 0} {$i < $num_rows} {incr i} {
        array set row {}
        foreach input $inputs {
            set bit [expr {($i >> [lsearch -exact $inputs $input]) & 1}]
            set row($input) $bit
        }

        set y_val [.input.row$i.ent_Y get]
        if {![regexp {^[01xX]$} $y_val]} {
            tk_messageBox -message "Invalid output at row $i: must be 0, 1, or x" -icon error
            return
        }
        set row(Y) $y_val
        lappend truth_table [array get row]
    }

    # Write input.json
    set file [open "input.json" "w"]
    puts $file "\["
    set count 0
    foreach r $truth_table {
        array set row $r
        set line "  {"
        foreach i $inputs {
            append line "\"$i\": \"$row($i)\", "
        }
        append line "\"Y\": \"$row(Y)\"}"
        if {$count < [expr {[llength $truth_table] - 1}]} {
            append line ","
        }
        puts $file $line
        incr count
    }
    puts $file "\]"
    close $file

    # Call Python script
    if {[catch {exec py logic_minimizer.py} err]} {
        tk_messageBox -message "Python error:\n$err" -icon error
        return
    }

    # Display output.txt
    if {[file exists "output.txt"]} {
        set f [open "output.txt" "r"]
        set content [read $f]
        close $f

        .output.txt_results delete 1.0 end
        .output.txt_results insert end $content
    } else {
        .output.txt_results delete 1.0 end
        .output.txt_results insert end "Error: output.txt not generated.\n"
    }
}
