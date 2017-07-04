import sys

f=open(sys.argv[1],"r")

first=1
while 1:
	line=f.readline()
	if line=="":
		break
	if first==1:
		print line[:-1]
		first=0
		continue
	array=line[:-1].split(",")
	res=array[0] + "," + ",".join(array[3:6])
	print res + ",analysis," + array[6]
	print res + ",facto," + array[7]
	print res + ",solve," + array[8]
f.close()
