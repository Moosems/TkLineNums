# set ::tk::Priv(textanchoruid) 0

# proc ::tk::TextAnchor {w} {
#     variable Priv
#     if {![info exists Priv(textanchor,$w)]} {
#         set Priv(textanchor,$w) tk::anchor[incr Priv(textanchoruid)]
#     }
#     return $Priv(textanchor,$w)
# }

# proc ::tk::TextSelectTo {w x y {extend 0}} {
#     variable ::tk::Priv

#     set anchorname [tk::TextAnchor $w]
#     set cur [TextClosestGap $w $x $y]
#     if {[catch {$w index $anchorname}]} {
# 	$w mark set $anchorname $cur
#     }
#     set anchor [$w index $anchorname]
#     if {[$w compare $cur != $anchor] || (abs($Priv(pressX) - $x) >= 3)} {
# 	set Priv(mouseMoved) 1
#     }
#     switch -- $Priv(selectMode) {
# 	char {
# 	    if {[$w compare $cur < $anchorname]} {
# 		set first $cur
# 		set last $anchorname
# 	    } else {
# 		set first $anchorname
# 		set last $cur
# 	    }
# 	}
# 	word {
# 	    # Set initial range based only on the anchor (1 char min width)
# 	    if {[$w mark gravity $anchorname] eq "right"} {
# 		set first $anchorname
# 		set last "$anchorname + 1c"
# 	    } else {
# 		set first "$anchorname - 1c"
# 		set last $anchorname
# 	    }
# 	    # Extend range (if necessary) based on the current point
# 	    if {[$w compare $cur < $first]} {
# 		set first $cur
# 	    } elseif {[$w compare $cur > $last]} {
# 		set last $cur
# 	    }

# 	    # Now find word boundaries
# 	    set first [TextPrevPos $w "$first + 1c" tk::wordBreakBefore]
# 	    set last [TextNextPos $w "$last - 1c" tk::wordBreakAfter]
# 	}
# 	line {
# 	    # Set initial range based only on the anchor
# 	    set first "$anchorname linestart"
# 	    set last "$anchorname lineend"

# 	    # Extend range (if necessary) based on the current point
# 	    if {[$w compare $cur < $first]} {
# 		set first "$cur linestart"
# 	    } elseif {[$w compare $cur > $last]} {
# 		set last "$cur lineend"
# 	    }
# 	    set first [$w index $first]
# 	    set last [$w index "$last + 1c"]
# 	}
#     }
#     if {$Priv(mouseMoved) || ($Priv(selectMode) ne "char")} {
# 	$w tag remove sel 0.0 end
# 	$w mark set insert $cur
# 	$w tag add sel $first $last
# 	$w tag remove sel $last end
# 	update idletasks
#     }
# }

