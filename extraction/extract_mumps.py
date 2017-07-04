#!/usr/bin/python

import sys
import re

if len(sys.argv)!=3:
	print "python extract_mumps.py [file] [id]"
	print "metrics:"
	print "date,id,file,#MPI,#OpenMP,matrix,error1,error2,Analysis(s),Facto(s),Solve(s),Facto Elimination(s),Forward Elim(s),Backward Elim(s),Facto Flops(Est.),Facto Flops,Real Space(Est.),Real Space,Integer Space(Est.),Integer Space,Max Front Size,Max Front Size,Max Space Used in S,Avg Space Used in S,Max Space Facto(Mb),Avg Space Facto(Mb),Max Space Solve(Mb),Avg Space Solve(Mb),Analysis Type,Ordering,Max. Transversal,Pivot Ordering,Pivoting Rel. Threshold,Memory Relax.(%),#Level2 Nodes,#Split Nodes,#Nodes in Tree,#Off Diagonal Pivots,#Negative Pivots,#Delayed Pivots,#2x2 Pivots(type 1 node),#2x2 Pivots(type 2 node),#Null Pivots,Deficiency(Est.),BLR epsilon,Min. BLR Block Size,Max. BLR Block Size,#BLR Fronts,Facto Full-Rank Flops,Facto Full-Rank Flops(%),Facto BLR Flops,Facto BLR Flops(%),A(Max-Norm),condition1,condition2,Residual(Max-Norm),Residual(2-Norm),Sol(Max Norm),Scaled Residual(Max-Norm),W1,W2,Error Upper Bound"
	exit(0)

metrics_names=[
	'Getting matrix in file: ([.a-zA-Z0-9\-_/]*)',
	'On return from DMUMPS, INFOG\(1\)=[" "]*([+-]?\d+)',
	'On return from DMUMPS, INFOG\(2\)=[" "]*([+-]?\d+)',
	#Runtimes
	'[" "]*ELAPSED TIME IN ANALYSIS DRIVER=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*ELAPSED TIME IN FACTORIZATION DRIVER=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*ELAPSED TIME IN SOLVE DRIVER=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*ELAPSED TIME FOR FACTORIZATION[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*\.\. TIME in forward \(fwd\) step[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*\.\. TIME in backward \(bwd\) step[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	#Facto Flops
	'[" "]*RINFOG\(1\) Operations during elimination \(estim\)=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*------\(3\)  OPERATIONS IN NODE ELIMINATION=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	#Memory
	'[" "]*REAL SPACE FOR FACTORS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INFOG \(9\)  REAL SPACE FOR FACTORS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INTEGER SPACE FOR FACTORS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INFOG\(10\)  INTEGER SPACE FOR FACTORS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*MAXIMUM FRONTAL SIZE \(ESTIMATED\)[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INFOG\(11\)  MAXIMUM FRONT SIZE[" "]*=[" "]*([+-]?\d+)',
	'[" "]*Maximum effective space used in S[" "]*\(KEEP8\(67\)\)[" "]*[" "]*([+-]?\d+)',
	'[" "]*Average effective space used in S[" "]*\(KEEP8\(67\)\)[" "]*[" "]*([+-]?\d+)',
	'[" "]*\*\* Space in MBYTES used by this processor for facto[" "]*:[" "]*([+-]?\d+)',
	'[" "]*\*\* Avg. Space in MBYTES per working proc during facto[" "]*:[" "]*([+-]?\d+)',
	'[" "]*\*\* Space in MBYTES used by this processor for solve[" "]*:[" "]*([+-]?\d+)',
	'[" "]*\*\* Avg. Space in MBYTES per working proc during solve[" "]*:[" "]*([+-]?\d+)',
	#Parameters
	'[" "]*-- \(32\) Type of analysis effectively used[" "]*=[" "]*([+-]?\d+)',
	'[" "]*--  \(7\) Ordering option effectively used[" "]*=[" "]*([+-]?\d+)',
	'[" "]*ICNTL\(6\) Maximum transversal option[" "]*=[" "]*([+-]?\d+)',
	'[" "]*ICNTL\(7\) Pivot order option[" "]*=[" "]*([+-]?\d+)',
	'[" "]*RELATIVE THRESHOLD FOR PIVOTING, CNTL\(1\)[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*Percentage of memory relaxation \(effective\)[" "]*=[" "]*([+-]?\d+)',
	#Nodes
	'[" "]*Number of level 2 nodes[" "]*=[" "]*([+-]?\d+)',
	'[" "]*Number of split nodes[" "]*=[" "]*([+-]?\d+)',
	'[" "]*NUMBER OF NODES IN THE TREE[" "]*=[" "]*([+-]?\d+)',
	#Pivots
	'[" "]*INFOG\(12\)  NUMBER OF OFF DIAGONAL PIVOTS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INFOG\(12\)  NUMBER OF NEGATIVE PIVOTS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INFOG\(13\)  NUMBER OF DELAYED PIVOTS[" "]*=[" "]*([+-]?\d+)',
	'[" "]*NUMBER OF 2x2 PIVOTS in type 1 nodes[" "]*=[" "]*([+-]?\d+)',
	'[" "]*NUMBER OF 2x2 PIVOTS in type 2 nodes[" "]*=[" "]*([+-]?\d+)',
	'[" "]*NB OF NULL PIVOTS DETECTED BY ICNTL\(24\)[" "]*=[" "]*([+-]?\d+)',
	'[" "]*INFOG\(28\)  ESTIMATED DEFICIENCY[" "]*=[" "]*([+-]?\d+)',
	#BLR
	'[" "]*RRQR precision \(epsilon\)[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*Target BLR block size \(variable\)[" "]*=[" "]*([+-]?\d+)[" "]*-[" "]*[+-]?\d+',
	'[" "]*Target BLR block size \(variable\)[" "]*=[" "]*[+-]?\d+[" "]*-[" "]*([+-]?\d+)',
	'[" "]*Number of BLR fronts[" "]*=[" "]*([+-]?\d+)',
	'[" "]*Total theoretical full-rank OPC \(i.e. FR OPC\)[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?) \([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?%\)',
	'[" "]*Total theoretical full-rank OPC \(i.e. FR OPC\)[" "]*=[" "]*[+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)? \(([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)%\)',
	'[" "]*Total effective OPC[" "]*\(% FR OPC\)[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?) \([" "]*[+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?%\)',
	'[" "]*Total effective OPC[" "]*\(% FR OPC\)[" "]*=[" "]*[+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)? \([" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)%\)',
	#Pb Conditioning
	'[" "]*RINFOG\(4\):NORM OF input  Matrix  \(MAX-NORM\)=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*-----\(10\):CONDITION NUMBER \(1\) ............=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*-----\(11\):CONDITION NUMBER \(2\) ............=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	#Error Analysis
	'[" "]*RESIDUAL IS ............ \(MAX-NORM\)[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*.. \(2-NORM\)[" "]*=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*RINFOG\(5\):NORM OF Computed SOLUT \(MAX-NORM\)=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*RINFOG\(6\):SCALED RESIDUAL ...... \(MAX-NORM\)=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*RINFOG\(7\):COMPONENTWISE SCALED RESIDUAL\(W1\)=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*------\(8\):---------------------------- \(W2\)=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'[" "]*------\(9\):Upper bound ERROR ...............=[" "]*([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
]
metrics=[]
for i in range(0, len(metrics_names)):
	metrics.append("0")
PAR=[
      ['[" "]*executing #MPI =[" "]*([+-]?\d+) and #OMP =[" "]*[+-]?\d+', "0"],
      ['[" "]*executing #MPI =[" "]*[+-]?\d+ and #OMP =[" "]*([+-]?\d+)', "0"]
]

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
	for i in range(0, len(PAR)):
		title_search = re.search(PAR[i][0], line[:-1], re.IGNORECASE)
		if title_search:
			PAR[i][1] = title_search.group(1)
f.close()

res=sys.argv[2] + "," + sys.argv[1] + ","
if PAR[0][1]=="0":
	array=sys.argv[1].split("_")
	PAR[0][1]=array[-2]
	PAR[1][1]=array[-1]
#print sys.argv[2]
#print "#MPI: " + str(PAR[0][1])
#print "#OpenMP: " + str(PAR[1][1])
#for i in range(0, len(metrics)):
#	print str(metrics_names[i]) + ": " + str(metrics[i])
res+=",".join([str(PAR[0][1]), str(PAR[1][1])])
res+=","
res+=",".join(metrics)
print res
