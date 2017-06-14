#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "sh extract_mumps.sh [path/to/output_folder] [mumps_outputs_folder]"
	exit 1
fi

folder=$(dirname $0)
output_folder=$1
outputs=$2
mkdir -p $outputs

first=1
rm $outputs"/benchmarks.csv"
touch $outputs"/benchmarks.csv"
for fold in $output_folder/*
do
	csv=$fold/result/table_output_csv.dat
	base_fold=$(basename $fold)
	echo "Extracting "$fold"..."
	for f in $fold/*execute*/work/job.out
	do
		omp=$(grep "#MPI" $f | uniq | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | cut -d " " -f 9)
		mpi=$(grep "#MPI" $f | uniq | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | sed "s/  / /g" | cut -d " " -f 5)
		matrix=$(grep "/scratch" $f | head -n 1 | cut -f 5 -d " ")
#		matrix=$(dirname $matrix | sed "s#/scratch/algo/leleux/data/##g" | sed "s#/#_#g")
		matrix=$(sed "s#/scratch/algo/leleux/data/##g" <<< $matrix | sed "s#/#_#g")
		mkdir -p $outputs/$matrix
		cp $f $outputs"/"$matrix"/"$mpi"_"$omp".out"
		cp $csv $outputs"/"$matrix"/data_"$base_fold".csv"
	done
	first_line=1
	if [ $first -eq 1 ]; then
		first=0
		echo "matrix,"$(head -n 1 $csv) >> $outputs"/benchmarks.csv"
	fi
	while read line; do
		if [ $first_line -eq 1 ]; then
			first_line=0
		else
			echo $matrix","$line >> $outputs"/benchmarks.csv"
		fi
	done < $csv
done

python $folder/unroll_mumps_outputs.py $outputs"/benchmarks.csv" > $outputs"/benchmarks_unrolled.csv"
