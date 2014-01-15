#!/usr/bin/env python
#-*- coding:utf-8 -*-

#general python modules:
import sys
import os
import logging
from emdros.command import MQL
from emdros.command import RenderObjects
from emdros.command import EmdrosException
from emdros.command import ContextHandlerType

#import CLAM-specific modules:
import clam.common.data
import clam.common.status


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

total_filecount = len(clamdata.input)
context_handler_name = clamdata.parameter("contexthandlername").value
context_level = clamdata.parameter("contextlevel").value
context_mark = clamdata.parameter("contextmark").value

clam.common.status.write(statusfile, "Iterating over " + str(total_filecount) + " input files..." )
clam.common.status.write(statusfile, "Context handler name: '" + context_handler_name + "'" )
if context_handler_name == "level":
    clam.common.status.write(statusfile, "Context level: " + str(context_level))
elif context_handler_name == "marks":
    clam.common.status.write(statusfile, "Context mark: '" + context_mark + "'")
mql = MQL()
ro = RenderObjects()


def execute_query(inputfile, result_filename, queryname):
    try:
        mql.execute_file(str(inputfile), result_filename)

        logging.info("Successfully queried file '" + queryname + "'")
        return True
    except EmdrosException:
        os.rename(result_filename, result_filename + ".error")
        msg = "Error while executing query '" + queryname + "'. See " \
              + os.path.basename(result_filename) + ".error for details."
        print >> sys.stderr, "[emdroswrapper02] ERROR: " + msg
        logging.error(msg)
        clam.common.status.write(statusfile, msg)
        pass
        return False

def find_context(result_filename, context_filename, stylesheet_name, queryname):
    directory = os.path.dirname(os.path.realpath(__file__))
    json_filename = directory + "/fetchinfo.json"
    context_file = open(context_filename, "a")
    context_file.writelines("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    if context_handler_name == "level":
        context_handler_type = ContextHandlerType.level
        context_file.writelines("<context_list context_level=\"" + str(context_level) + "\">")
    elif context_handler_name == "marks":
        context_handler_type = ContextHandlerType.marks
        context_file.writelines("<context_list context_mark=\"" + context_mark + "\">")
    context_file.flush()

    try:
        ro.find_objects(result_filename, json_filename, context_file, stylesheet_name, context_handler_type,
                        context_level=context_level,
                        context_mark=context_mark)

        logging.info("Found context list for file '" + queryname + "'")
    except EmdrosException as eex:
        context_file.writelines("<error>\n" + str(eex.args) + "\n</error>")
        raise eex
    finally:
        context_file.writelines("</context_list>")
        context_file.close()


#Iterate over all inputfiles:
count = 0
for inputfile in clamdata.input:
    queryname = os.path.basename(str(inputfile))     # bh_lq01.mql
    filename = os.path.splitext(queryname)           # [ bh_lq01, .mql ]
    result_filename = outputdir + filename[0] + "-result.xml"
    context_filename = outputdir + filename[0] + "-context.xml"

    result = execute_query(inputfile, result_filename, queryname)
    count += 1
    if (result):
        clam.common.status.write(statusfile, "Executed query " + queryname, (count/total_filecount) * 50)
        try:
            clam.common.status.write(
                statusfile, "Trying to find context for query " + queryname, (count/total_filecount) * 50)
            find_context(result_filename, context_filename, "base", queryname)
            clam.common.status.write(statusfile, "Found context for " + queryname, (count/total_filecount) * 100)
        except EmdrosException as eex:
            os.rename(context_filename, context_filename + ".error")
            msg = "Error while gathering context for '" + queryname + "'.\n" + str(eex.args) + "\nSee " \
                 + os.path.basename(context_filename) + ".error for details."
            print >> sys.stderr, "[emdroswrapper02] ERROR: " + msg
            logging.error(msg)
            clam.common.status.write(statusfile, msg)
            pass


clam.common.status.write(statusfile, "Done", 100)

sys.exit(0) #non-zero exit codes indicate an error!


