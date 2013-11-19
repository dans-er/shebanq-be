#!/usr/bin/env python
#-*- coding:utf-8 -*-

import subprocess
import xml.sax
import props
import io


def version(process):
    """Return version information."""
    p = subprocess.Popen([process, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

    errmsg = p.stderr.read()
    rc = p.returncode
    if rc != 0:
        raise EmdrosException("Process finished with exit code " + str(rc) + "\n" + errmsg)

    temp = [line[:-1] for line in p.stdout]
    if len(temp) < 1:
        raise EmdrosException("No output from process.")

    return temp[0]


class EmdrosException(Exception):
    """Indicates an exception while executing an Emdros process"""


class EmdrosProcess():
    mql = "mql"
    render_objects = "renderobjects"

    process = ""

    def version(self):
        """Return Emdros version information."""
        return version(self.process)


class MQL(EmdrosProcess):
    """Handles mql-queries"""
    process = EmdrosProcess.mql

    def __init__(self):
        pass

    class ResultFormat():
        xml = "--xml"
        compact_xml = "--cxml"
        console = "--console"

    def execute_file(self, query_filename, result_filename, output_format = props.mql_outputFormat):
        """Execute the query in the file indicated with query_filename.

        Args:
            query_filename  --  path denoting a file containing the mql query.
            result_filename --  path denoting a file to dump the result.
            output_format   --  one of MQL.ResultFormat.
                                Defaults to value of props.mql_outputFormat.

        Raises:
            EmdrosException: The query could not be executed due to invalid query syntax or system failure.
        """

        result_file = open(result_filename, "w")

        try:
            p = subprocess.Popen([self.process,
                                  "-h", props.emdros_host,
                                  "-u", props.emdros_user,
                                  "-p", props.emdros_password,
                                  "-b", props.emdros_backend,
                                  "-e", props.mql_encoding,
                                  "-d", props.emdros_dbName,
                                  query_filename,
                                  output_format],
                                  stdout=result_file,
                                  stderr=subprocess.PIPE)
            p.wait(timeout=props.mql_timeout)

            errmsg = p.stderr.read()
            rc = p.returncode
            if rc != 0:
                raise EmdrosException("Query finished with exit code " + str(rc) + "\n" + errmsg)

        finally:
            result_file.close()


class RenderObjects(EmdrosProcess):
    """Handles renderobjects processing"""
    process = EmdrosProcess.render_objects

    def __init__(self):
        pass

    def execute(self, json_filename, result_file, first_monad, last_monad, stylesheet_name = props.ro_stylesheet):
        """Execute renderobjects

        Args:
        json_filename   --  path denoting a file containing json 'fetchinfo' object
        result_file     --  file to append the result to. Caller is responsible for closing the file
        first_monad     --  integer indicating first monad in the result.
        last_monad      --  integer indicating last monad in the result.
        stylesheet_name --  name of the stylesheet within json 'fetchinfo' object.
                            Defaults to value of props.ro_stylesheet
        """
        p = subprocess.Popen([self.process,
                              "-h", props.emdros_host,
                              "-u", props.emdros_user,
                              "-p", props.emdros_password,
                              "-b", props.emdros_backend,
                              "--fm", str(first_monad),
                              "--lm", str(last_monad),
                              "-s", stylesheet_name,
                              json_filename,
                              props.emdros_dbName],
                             stdout=result_file,
                             stderr=subprocess.PIPE)
        p.wait(timeout=props.ro_timeout)

        errmsg = p.stderr.read()
        rc = p.returncode
        if rc != 0:
            raise EmdrosException("Render objects finished with exit code " + str(rc) + "\n" + errmsg)


    def find_objects(self, mql_result_filename, json_filename, result_file, stylesheet_name = props.ro_stylesheet):
        """Find context objects for mql result.


        """
        handler = FindObjectsHandler(self, json_filename, result_file, stylesheet_name)
        source = open(mql_result_filename)
        try:
            xml.sax.parse(source, handler)
        finally:
            source.close()


class FindObjectsHandler(xml.sax.ContentHandler):
    """Content handler for finding context objects.

    """
    #ro = None
    #json_filename = ""
    #result_file = None
    #stylesheet_name = ""
    #straw_level = 0
    def __init__(self, ro, json_filename, result_file, stylesheet_name):
        xml.sax.ContentHandler.__init__(self)
        assert isinstance(ro, RenderObjects)
        assert isinstance(result_file, file)
        self.ro = ro
        self.json_filename = json_filename
        self.result_file = result_file
        self.stylesheet_name = stylesheet_name
        self.straw_level = 0

    def startElement(self, name, attrs):
        if name == "straw":
            self.straw_level += 1
        if name == "mse" and self.straw_level == 1:
            first_monad = int(attrs.getValue("first"))
            last_monad = int(attrs.getValue("last"))

            self.ro.execute(self.json_filename, self.result_file, first_monad, last_monad, self.stylesheet_name)


    def endElement(self, name):
        if name == "straw":
            self.straw_level -= 1










