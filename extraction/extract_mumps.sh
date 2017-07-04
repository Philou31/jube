#!/bin/bash

i=0

python extract_mumps.py
for d in $(find $1 -maxdepth 15 -type d)
do
#	for f in $d/*
	for f in $d/job.out
	do
#		grep "Entering DMUMPS" $f | cut -f 3 -d " " | sort -u
#		continue
		if [[ -d $f ]]; then
#		    echo $f "is a directory"
		    continue
		fi
		test=$(grep "Entering DMUMPS" $f)
		if [ -z "$test" ]; then
			a=0
		else
			i=$((i+1))
## benchmarks.csv
			date=$(ls -la $f | sed "s/  / /g" | sed "s/  / /g" |  sed "s/  / /g" | cut -f 6-7 -d " ")
			echo $date,$(python extract_mumps.py $f $i)
## benchmarks_CE.txt
#			echo $f
#			grep "cache\|pin\|binding\|kmp\|cpu\|--by\|bind-to\|distribution\|run\|domain\|map\|order" -i ${f%.*}.err | grep Info -v | cut -d ":" -f 2 | sed 's/^[" "]*[+-]*[" "]*//g' | sort -u
#			echo ""
## benchmarks_errors.txt
#			error=$(grep "On return from DMUMPS, INFOG(1)=" $f | grep -v "\-3" | cut -d "-" -f 2)
#			if [ -z "$error" ]; then
#				a=0
#			else
#				echo $f,$i,$error
#			fi
		fi
	done
done
