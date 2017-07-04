#!/usr/bin/python

import sys
import re

if len(sys.argv)!=2:
#	print "python extract_ABCD_submit.py [file]"
#	print "metrics:"
	print "threshold,Partitions Imbalance(PaToH),#Partitions,Block Size,Augmentation Blocking,Partitioning Type,Scaling,Augmentation Type,Verbose,#Iterations Max.,#MPI,#OpenMP"
	exit(0)

metrics_names=[
        '--threshold[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
        '--part_imbalance[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
        '--nbparts[" "]*([+-]?\d+)',
        '--block_size[" "]*([+-]?\d+)',
        '--aug_blocking[" "]*([+-]?\d+)',
        '--part_type[" "]*([+-]?\d+)',
        '--scaling[" "]*([+-]?\d+)',
        '--aug_type[" "]*([+-]?\d+)',
        '--verbose[" "]*([+-]?\d+)',
        '--itmax[" "]*([+-]?\d+)',
	'#SBATCH[" "]*--ntasks=([+-]?\d+)',
	'#SBATCH[" "]*--cpus-per-task=([+-]?\d+)'
]

metrics=[]
for i in range(0, len(metrics_names)):
	metrics.append("0")

f=open(sys.argv[1],"r")
while 1:
	line=f.readline()
	if line=="":
		break
	for i in range(0, len(metrics)):
		if metrics[i]!="0":
			continue
		title_search = re.search(metrics_names[i], line[:-1], re.IGNORECASE)
		if title_search:
			metrics[i] = title_search.group(1)
f.close()


res=",".join(metrics)
print res
