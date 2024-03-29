#! /usr/bin/env python

import sys
import stats
import getopt
import csv_file
#import pdb; pdb.set_trace()

def usage():
	print "\nHelp on compd tool\n"
	print "NAME"
	print "\tcompd"
	print "\nDESCRIPTION"
	print "\tThe compd is a tool which analyzes a determined feature of an application"
	print "\nARGUMENTS"
	print "\t--ds1 file1name --ds2 file2name: The rdt files to be compared. The complete path is needed if the files are not in the same directory as the script"
	print "\t--ds filename: The rdt file to be analyzed. The complete path is needed if the file are not in the same directory as the script"
	print "\t--cf column: The column to be anlyzed or/and compared. It corresponds to one of the columns of the rdt file(s). You must enter this argument."
	print "\t--cl number: The confidence level for the confidence interval. The values supported are 20%, 50%, 80%, 90%, 95%, 98%, 99%, 99.9%. In case no confidence level is set, the confidence interval will be calculated with a confidence value of 95%"
	print "\t--of1: Primary output format. There will be one line for each data set plus one line per each comparison result if there are two data sets. If no format is selected, the results will be displayed in this format."  
	print "\t--of2: Seconday output format. there will be a new line for each statistical result and comparison result if there are two data sets."
	print "\t--of string: User-defined output format. This format can be definded by a string containing one or more of the following tokens:" 
	print "\t\t(ds1-av), (ds1-gm), (ds1-ci), (ds1-std), (ds1-var), (ds1-med), (ds2-av), (ds2-gm), (ds2-ci), (ds2-std), (ds2-var), (ds2-med), (av-ratio), (gm-ratio),(av-ratio-low), (av-ratio-up), (av-diff), (gm-diff),  for a pair of data sets"
	print "\t\tor (ds-av), (ds-gm), (ds-ci), (ds-std), (ds-var) (ds-med) for a single data set.\n"

def error(message, status):
	sys.stderr.write(message+'\n')
	if status:
		sys.exit(status)
	return
		
def search(file, field):

	temp = file.readline().strip()
	list = temp.split(',')
	pos=0

	for word in list:
#       	print "Comparing (%s) with (%s)" %(word,field)
        	if word == field:
#               	print "File ds1: Found %s at column %i" %(field,pos1) 
                	break
        	pos+=1

	lineno=1
	column=[]

	while 1 :
        	temp=file.readline()
        	if not(temp) : break
        	list = temp.strip().split(",")
        	if pos<len(list) :
                	column.append(float(list[pos]))
        	else:
                	print "WARNING: could not read field %i from line %i (ds1), it has only %i fields" %(pos,lineno,len(list))
        	lineno+=1

	return column 

def calc(x, conf):
	
	size = len(x)
	sum = stats.sum(x)
	av = stats.average(sum, size)
	gm = stats.gmean(x)
	v = stats.var(sum, stats.sqsum(x), size)
	med = stats.median(x)

	if v != 'error':
		sd = stats.stdv1(v)
		c = stats.conf(float(conf), sd, size)
	else:
		sd = 'error'
		c = 'none'

	return av, gm, v, sd, c, med



# Main

flags = ['ds1=', 'ds2=', 'ds=', 'cf=', 'cl=', 'of1', 'of2', 'of=', 'help', 'dump=']

opts, args = getopt.getopt(sys.argv[1:], 'h', flags)

dataset1=dataset2=dataset=field=dump=0
confidence = 95 # Default confidence level
output = 1 # Default output format

for p,v in opts:
        if p == '--ds1':
                dataset1 = v
        elif p == '--ds2':
                dataset2 = v
        elif p == '--ds':
                dataset = v
        elif p == '--cf':
                field = v
        elif p == '--cl':
                confidence = v
        elif p == '--of1':
                output = 1
	elif p == '--of2':
		output = 2
	elif p == '--of':
		output = v
	elif p == '-h' or p == "--help":
		usage()
		sys.exit(0)
	elif p == "--dump":
		dump = v	

if not field:
        print "Field to be analyzed missing."
	usage()
        sys.exit(1)

if not dataset:
        if not dataset1 or not dataset2:
                print "One or more data sets missing."
		usage()
		sys.exit(1)

	try:
        	file1 = open(dataset1, 'r')
	except IOError:
        	print "WARNING: could not read file ", dataset1
        	sys.exit(2)
	try:
        	file2 = open(dataset2, 'r')
	except IOError:
        	print "WARNING: could not read file ", dataset2
        	sys.exit(2)

	list1 = search(file1, field)
	list2 = search(file2, field)

	file1.close()
	file2.close()

	av1, gm1, v1, sd1, c1, med1 = calc(list1, confidence)
	av2, gm2, v2, sd2, c2, med2 = calc(list2, confidence)
	avr = stats.ratio(av1, av2)
	avr_up = stats.ratio(av1, av2, c1, c2, 'u')
	avr_low = stats.ratio(av1, av2, c1, c2, 'l')
	gmr = stats.ratio(gm1, gm2)
	avd = stats.diff(av1, av2)
	gmd = stats.diff(gm1, gm2)

	if output == 1:
		print field
		print '--'
        	print "Data set 1: av:%f geomean:%f var:%f stdev:%f conf:%f"  % (av1, gm1, v1, sd1, c1)
	        print "Data set 2: av:%f geomean:%f var:%f stdev:%f conf:%f"  % (av2, gm2, v2, sd2, c2)
        	print "Ratio: average:%f geometric mean:%f" % (avr, gmr)
	      	print "Diff: average:%f geometric mean:%f" % (avd, gmd)

	elif output == 2:
		print field
	        print "\nDATA SET 1"
	        print "average: ", av1
		if c1 != 'none':
			print "confidence interval: [%f,%f]" % (av1-c1, av1+c1)
	        print "geometric mean: ", gm1
		if c1 != 'none':
			print "confidence interval: [%f,%f]" % (gm1-c1, gm1+c1)
	        print "variance: ", v1
        	print "standard deviation: ", sd1
	        print "confidence interval: ", c1
	        print "\nDATA SET 2"
	        print "average: ", av2
		if c2 != 'none':
			print "confidence interval: [%f,%f]" % (av2-c2, av2+c2)
	        print "geometric mean: ", gm2
		if c2 != 'none':
			print "confidence interval: [%f,%f]" % (gm2-c2, gm2+c2)
	        print "variance: ", v2
	        print "standard deviation: ", sd2
	        print "confidence interval: ", c2
	        print "\nAverage ratio: ", avr
	        print "Geometric mean ratio: ", gmr
	        print "Average diff: ", avd
	        print "Geometric mean diff: ", gmd
	
	else:
		format = {'ds1-av':av1, 'ds1-gm':gm1, 'ds1-ci':c1, 'ds1-std':sd1, 
			  'ds1-var':v1, 'ds1-med':med1, 'ds2-av':av2, 'ds2-gm':gm2, 'ds2-ci':c2, 
			  'ds2-std':sd2, 'ds2-var':v2, 'ds2-med':med2, 'av-ratio':avr, 
			  'av-ratio-up':avr_up, 'av-ratio-low':avr_low, 
			  'gm-ratio':gmr, 'av-diff':avd, 'gm-diff':gmd}
                output = output.replace('(', '%(')
                output = output.replace(')', ')s')
		try:
                	sret = output % format
		except KeyError as e:
			print "WARNING: (%s) is not a valid token." % e
			usage();
		if not dump: print sret
		else: csv_file.write(dump, sret)
else:
        if dataset1 or dataset2:
                print "Use either --ds or --ds1 and --ds2."
                usage();
                sys.exit(1)

	try:
		file = open(dataset, 'r')
	except IOError:
		print "WARNING: could not read file", dataset
		sys.exit(2)

	list = search(file, field)
	file.close()
	av, gm, v, sd, c, med = calc(list, confidence)

	if output == 1:
		print field 
		print '--'
		print "average:%f geometric mean:%f variance:%f standard deviation:%f confidence:%f"  % (av, gm, v, sd, c)

	elif output == 2:
		print field
		print "\naverage: ", av
		if c != 'none':
			print "confidence interval: [%f,%f]" % (av-c, av+c)
		print "\ngeometric mean: ", gm
		if c != 'none':
			print "confidence interval: [%f,%f]" % (gm-c, gm+c)
		print "\nvariance: ", v
		print "standard deviation: ", sd
	else:
		format = {'ds-av':av, 'ds-gm':gm, 'ds-ci':c, 'ds-std':sd, 'ds-var':v, 'ds-med':med}
		output = output.replace('(', '%(')
		#TODO: add an option to set the real number print precision
		output = output.replace(')', ').2f')
		#output = output.replace(')', ').s')
		try:
                	sret = output % format
		except KeyError as e:
			print "WARNING: (%s) is not a valid token." % e
			usage();
		if not dump: print sret
		else: csv_file.write(dump, sret)
