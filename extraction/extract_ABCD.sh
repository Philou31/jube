#!/bin/bash

i=0

echo "date,"$(python extract_ABCD_submit.py)","$(python extract_ABCD.py)
for d in $(find $1 -maxdepth 15 -type d)
do
#	for f in $d/*
	for f in $d/job.out
	do
		if [[ -d $f ]]; then
		    continue
		fi
		test=$(grep "Getting matrix in file" $f)
		if [ -z "$test" ]; then
			a=0
		else
			i=$((i+1))
## benchmarks.csv
			date=$(ls -la $f | sed "s/  / /g" | sed "s/  / /g" |  sed "s/  / /g" | cut -f 6-7 -d " ")
			submit_script=$(dirname $f)/submit.job
			echo $date,$(python extract_ABCD_submit.py $submit_script),$(python extract_ABCD.py $f $i)
		fi
	done
done
