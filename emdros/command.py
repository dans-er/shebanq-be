#!/usr/bin/env python
#-*- coding:utf-8 -*-

import subprocess
import xml.sax
import props


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

    def __init__(self):
        self.process = EmdrosProcess.mql

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


class UnknownContextHandlerError(Exception):
    """Indicates that an AbstractContextHandler is unknown"""

class ContextHandlerType():
    level = "level"
    marks = "marks"

class RenderObjects(EmdrosProcess):
    """Handles renderobjects processing"""

    def __init__(self):
        self.process = EmdrosProcess.render_objects

    def execute(self, json_filename, result_file, first_monad, last_monad, stylesheet_name = props.ro_stylesheet):
        """Execute renderobjects.
           Method is often (and repeatedly) called from context handlers.

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


    def find_objects(self, mql_result_filename, json_filename, result_file,
                     stylesheet_name = props.ro_stylesheet,
                     handler_type = ContextHandlerType.level,
                     context_level = 0,
                     context_mark = props.context_mark_keyword):
        """Find context objects for mql result.

           As a default a ContextLevelHandler is used for parsing the result.
           At what level in the hierarchy of a result a particular straw is treated as context
           can be set with the parameter context_level.

           Alternatively a ContextMarksHandler can be used. A matched_object marked as context
           is treated as context by this handler. Set parameter use_marks to True if marks determine the context.

        :param mql_result_filename: the mql result for which context is to be found.
        :param json_filename: the stylesheet file to use.
        :param result_file: an open file in append-mode for writing the results.
        :param stylesheet_name: the name of the stylesheet within the stylesheet file.
            Defaults to props.ro_stylesheet
        :param handler_type: What implementation of AbstractContextHandler to use. ('level' | 'marks' )
            Defaults to 'level'.
        :param context_level: at what level in the hierarchy of a result a particular straw is treated as context.
            Used for the 'level' handler_type.
            Defaults to 0, first straw in the hierarchy is context.
        :param context_mark: the keyword indicating a matched_object as context.
            Used for the 'marks' handler_type.
            Defaults to props.context_mark_keyword.
        """
        if handler_type == ContextHandlerType.level:
            handler = ContextLevelHandler(self, json_filename, result_file, stylesheet_name, context_level)
        elif handler_type == ContextHandlerType.marks:
            handler = ContextMarksHandler(self, json_filename, result_file, stylesheet_name, context_mark)
        else:
            raise UnknownContextHandlerError("Unknown handler_type: " + handler_type)
        source = open(mql_result_filename)
        try:
            xml.sax.parse(source, handler)
        finally:
            source.close()


class AbstractContextHandler(xml.sax.ContentHandler):
    """
    The AbstractContextHandler keeps lists of monatsets for focus and context_parts
    and writes the complete context elements to the result_file.
    Subclasses of this class only need to keep track of a context match flag for their particular implementation.
    """
    def __init__(self, ro, json_filename, result_file, stylesheet_name):
        xml.sax.ContentHandler.__init__(self)
        assert isinstance(ro, RenderObjects)
        assert isinstance(result_file, file)
        self.ro = ro
        self.json_filename = json_filename
        self.result_file = result_file
        self.stylesheet_name = stylesheet_name

        self.context_monatset = []
        self.focus = False
        self.focus_monatset = []

    def write_context(self):
        """
        Write the a context element and its children to the result_file.
        :return: None
        """
        self.result_file.writelines("\n<context>")
        for first_monad, last_monad in self.focus_monatset:
            self.result_file.writelines("\n<focus first=\"" + str(first_monad)
                                        + "\" last=\"" + str(last_monad) + "\"/>")
        self.result_file.flush()
        for first_monad, last_monad in self.context_monatset:
            self.ro.execute(self.json_filename, self.result_file, first_monad, last_monad, self.stylesheet_name)
        self.result_file.writelines("\n</context>")
        self.result_file.flush()
        self.focus_monatset = []
        self.context_monatset = []

    def reset_context_match(self):
        """
        Reset the context match trigger.
        :return: None
        """
        raise NotImplementedError("Please Implement this method")

    def is_context_match(self):
        """
        Answer if the context match trigger is set.
        :return: True if it is a context match, False otherwise.
        """
        raise NotImplementedError("Please Implement this method")

    def doStartElement(self, name, attrs):
        """
        - Sets the focus flag for <matched_object>.
        - Adds the monatset to focus_monatset if focus flag set.
        - Adds the monatset to context_monatset if it is a context match
        :param name: the name of the element
        :param attrs: the attributes of the element
        :return: None
        """
        if name == "matched_object":
            self.focus = attrs.getValue("focus") == "true"

        if name == "mse" and self.focus:
            first_monad = int(attrs.getValue("first"))
            last_monad = int(attrs.getValue("last"))
            self.focus_monatset.append((first_monad, last_monad))

        if name == "mse" and self.is_context_match():
            first_monad = int(attrs.getValue("first"))
            last_monad = int(attrs.getValue("last"))
            self.context_monatset.append((first_monad, last_monad))

    def doEndElement(self, name):
        """
        - Writes the context if it is a context match.
        - Resets the focus and context triggers.
        :param name: name of the element.
        :return: None
        """
        if name == "matched_object" and self.is_context_match():
            self.write_context()
            self.reset_context_match()

        if name == "matched_object":
            self.focus = False


class ContextMarksHandler(AbstractContextHandler):
    """Context handler for finding context based on 'marks' attributes in matched objects.
    """
    def __init__(self, ro, json_filename, result_file, stylesheet_name, context_mark):
        AbstractContextHandler.__init__(self, ro, json_filename, result_file, stylesheet_name)
        self.keyword = context_mark
        self.marked_context_level = -1
        self.matched_object_level = -1

    def reset_context_match(self):
        self.marked_context_level = -1

    def is_context_match(self):
        return self.marked_context_level == self.matched_object_level

    def startElement(self, name, attrs):
        if name == "matched_object":
            self.matched_object_level += 1
            if attrs.has_key("marks"):
                if attrs.getValue("marks").find(self.keyword) > -1:
                    self.marked_context_level = self.matched_object_level

        self.doStartElement(name, attrs)

    def endElement(self, name):
        self.doEndElement(name)

        if name == "matched_object":
            self.matched_object_level -= 1


class ContextLevelHandler(AbstractContextHandler):
    """Content handler for finding context on the basis of hierarchy level.
       A context_level of 0 means: treat the first straw found in mql-query result hierarchy as context.
       A context_level of 1 means: treat the second straw found in mql-query result hierarchy as context.
       .. etc.

    """
    def __init__(self, ro, json_filename, result_file, stylesheet_name, context_level):
        AbstractContextHandler.__init__(self, ro, json_filename, result_file, stylesheet_name)
        self.context_level = context_level
        self.straw_level = -1

    def reset_context_match(self):
        pass

    def is_context_match(self):
        return self.straw_level == self.context_level

    def startElement(self, name, attrs):
        if name == "straw":
            self.straw_level += 1

        self.doStartElement(name, attrs)

    def endElement(self, name):
        if name == "straw":
            self.straw_level -= 1

        self.doEndElement(name)




