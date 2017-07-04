#!/usr/bin/python

import sys
import re

if len(sys.argv)!=3:
	print "python extract_mumps.py [file] [id]"
	print "metrics:"
	print "id,file,Matrix,Local Matrix Init(s),Matrix Scaling(s),Partitioning(s),PaToH(s),Partitioning done(s),Init Partitioning(s),Partitions Created(s),Preprocessing(s),Factorization(s),BCG #Iterations,BCG(s),Projections Sum(s),Error Computation(s),BCG Rho,Backward Error,Residual,Scaled Residual"
	exit(0)

metrics_names=[
	'Getting matrix in file: ([.a-zA-Z0-9\-_/]*)',
	#Initialisation
	'\[..:..:......\] > Local matrix initialized in ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] > Time to scale the matrix: ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] > Time to partition the matrix: ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] Done with PaToH, time : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] Finished Partitioning, time: ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] Initialization time : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'\[..:..:......\] Partitions created in: ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] > Total time to preprocess: ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)s.',
	'\[..:..:......\] Factorization time : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	#CG
	'\[..:..:......\] BCG Iterations : ([+-]?\d+)',
	'\[..:..:......\] BCG TIME : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'\[..:..:......\] SumProject time : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'\[..:..:......\] Rho Computation time : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	#Error Analysis
	'\[..:..:......\] BCG Rho: ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'\[..:..:......\] Backward error       : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'\[..:..:......\] \|\|r\|\|_inf            : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)',
	'\[..:..:......\] \|\|r\|\|_inf/\|\|b\|\|_inf  : ([+-]?\d*\.?\d+(?:[dDeE][-+]?\d+)?)'
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

res=sys.argv[2] + "," + sys.argv[1] + ","
res+=",".join(metrics)
print res

