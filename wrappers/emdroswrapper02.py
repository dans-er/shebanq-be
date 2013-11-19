#!/usr/bin/env python
#-*- coding:utf-8 -*-

#general python modules:
import sys
import os
import logging
import subprocess

#import CLAM-specific modules:
import clam.common.data
import clam.common.status

def query(queryFilename, resultFilename):
    res_out = open(resultFilename, "w")
    error_out = open("error.txt", "w")
    p = subprocess.Popen(["mql", "-b", "s3", "-d", "/data/emdros/wivu/s3/bhs3", queryFilename, "--xml"],
                         stdout=res_out,
                         stderr=error_out)
    p.wait()
    rc = p.returncode
    if (rc != 0):
        logging.error("Exception while executing " + os.path.basename(queryFilename) + " returncode=" + str(rc))
    else:
        logging.info("Got result: " + os.path.basename(resultFilename))
    res_out.close()
    error_out.close()

#this script takes three arguments: $DATAFILE $STATUSFILE $OUTPUTDIRECTORY
datafile = sys.argv[1]
statusfile = sys.argv[2]
outputdir = sys.argv[3]

# set up logging
logfile = outputdir + "log"
logging.basicConfig(
    filename=logfile,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')

#Obtain all data from the CLAM system (stored in $DATAFILE (clam.xml))
clamdata = clam.common.data.getclamdata(datafile)

clam.common.status.write(statusfile, "Iterating over " + str(len(clamdata.input)) + " input files...")
#Iterate over all inputfiles:
for inputfile in clamdata.input:
    resultname = outputdir + os.path.splitext(os.path.basename(str(inputfile)))[0] + "-result.xml"
    logging.info("blaaa " + resultname)
    if isinstance(inputfile.metadata, clam.common.formats.PlainTextFormat):
        query(str(inputfile), resultname)
    else:
        clam.common.status.write(statusfile, "Skipping " + str(inputfile) + ", invalid format")

clam.common.status.write(statusfile, "Done", 100)

sys.exit(0) #non-zero exit codes indicate an error!


