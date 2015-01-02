import fileinput
import sys

for line in fileinput.input(['./list.csv'], inplace=True):
	print('%srdf.xml' % line[:-2])
    #sys.stdout.write('{l}rdf.xml'.format(l=line))