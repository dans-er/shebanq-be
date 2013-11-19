#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import unittest
import sys
from command import MQL
from command import RenderObjects
from command import EmdrosException


class TestMQL(unittest.TestCase):

    def test_version(self):
        mql = MQL()
        version = mql.version()

        self.assertTrue(version.startswith("mql from Emdros version "))
        print "Testing against " + version

    def test_properties(self):
        mql = MQL()
        properties = mql.properties()

        self.assertEqual(7, len(properties))
        backend = properties["mql_backend"] # KeyError for unknown key
        assert isinstance(backend, str)
        self.assertFalse(backend == None)
        self.assertNotEqual("", backend)
        #self.assertTrue("s3" in backend)
        #print properties

    def test_execute_file(self):
        query_filename = "test_files/input/bh_lq01.mql"
        mql = MQL()

        expectations = {MQL.ResultFormat.console: "[ phrase",
                        MQL.ResultFormat.compact_xml: "<sheaf><straw><matched_object",
                        MQL.ResultFormat.xml: "<sheaf>\n"}
        for output_format, expected in expectations.iteritems():
            result_filename = "test_files/output/" \
                              + os.path.splitext(os.path.basename(query_filename))[0] \
                              + "-result" \
                              + output_format

            mql.execute_file(query_filename, result_filename, output_format)
            result_file = open(result_filename)
            result = result_file.read()
            result_file.close()
            #print result
            self.assertTrue(expected in result)

    def test_execute_invalid_file(self):
        mql = MQL()
        query_filename = "test_files/input/bh_lq06.mql"
        result_filename = "test_files/output/" \
            + os.path.splitext(os.path.basename(query_filename))[0] \
            + "-result" \
            + "-test"
        exception_thrown = False

        try:
            mql.execute_file(query_filename, result_filename)
        except EmdrosException as eex:
            exception_thrown = True
            self.assertTrue("Query finished with exit code " in eex.args[0])
            sys.exc_clear()
            # caller of method should mv result-file-name.xxx to result-file-name.xxx.error

        self.assertTrue(exception_thrown)


class TestRenderObjects(unittest.TestCase):

    def test_version(self):
        ro = RenderObjects()
        version = ro.version()



        self.assertTrue(version.startswith("renderobjects from Emdros version "))
        print "Testing against " + version

if __name__ == '__main__':
    unittest.main()