#!/usr/bin/env python
#-*- coding:utf-8 -*-

#general python modules:
import sys
import os
import logging

#import CLAM-specific modules:
import clam.common.data
import clam.common.status


#this script takes three arguments: $DATAFILE $STATUSFILE $OUTPUTDIRECTORY
datafile = sys.argv[1]
statusfile = sys.argv[2]
outputdir = sys.argv[3]

# compute paths in working directory
logfile = outputdir + "log"
logging.basicConfig(
    filename=logfile,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')

#Obtain all data from the CLAM system (stored in $DATAFILE (clam.xml))
clamdata = clam.common.data.getclamdata(datafile)

clam.common.status.write(statusfile, "Iterating over all input files...")
#Iterate over all inputfiles:
for inputfile in clamdata.input:
    outputfilename = outputdir + os.path.splitext(os.path.basename(str(inputfile)))[0] + ".xml"
    logging.info("renamed citizen to " + outputfilename)
    if isinstance(inputfile.metadata, clam.common.formats.PlainTextFormat):
        clam.common.status.write(statusfile, "Querying " + str(inputfile) + " ...")
        os.system('mql -b s3 -d /data/emdros/wivu/s3/bhs3 '  + str(inputfile) + ' --xml >> ' + outputfilename)
        clam.common.status.write(statusfile, "Got result: " + os.path.basename(outputfilename) + " ...")
    else:
        clam.common.status.write(statusfile, "Skipping " + str(inputfile) + ", invalid format")

clam.common.status.write(statusfile, "Done", 100)

sys.exit(0) #non-zero exit codes indicate an error!