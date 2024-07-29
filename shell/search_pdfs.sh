#!/usr/bin/env bash

#------------------------------------------------
# Run Search
#------------------------------------------------

directory="$1"
pattern="$2"

(cd "${directory}" &&
     find -f ./*pdf |
	 sed 's/\ /\\ /g' |
	 xargs pdfgrep "$pattern" -n -i |
	 # Trim the leading ./
	 cut -c 3- 
)
