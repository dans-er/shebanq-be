#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import unittest
from command import RenderObjects
from command import ContextHandlerType


class TestRenderObjects(unittest.TestCase):

    def test_version(self):
        ro = RenderObjects()
        version = ro.version()

        self.assertTrue(version.startswith("renderobjects from Emdros version "))
        print "Testing against " + version

    def test_execute(self):
        ro = RenderObjects()
        json_filename = "test_files/input/ro_01.json"
        result_filename = "test_files/output/" \
            + os.path.splitext(os.path.basename(json_filename))[0] \
            + "-result" \
            + ".xml"

        result_file = open(result_filename, "a")
        result_file.writelines("<ro>")
        result_file.flush()

        try:

            for x in range(1, 150, 7):
                ro.execute(json_filename, result_file, x, x + 4)

            result_file.writelines("</ro>")
            result_file.close()
            result_file = open(result_filename)
            result = result_file.read()
            #print result
            self.assertTrue("<s id_d=" in result)
        finally:
            result_file.close()
            os.remove(result_filename)

    def test_find_objects_by_level(self):
        ro = RenderObjects()
        json_filename = "test_files/input/ro_01.json"
        mql_result_filename = "test_files/input/bh_lq04-result.xml"


        result_filename = "test_files/output/" \
            + os.path.splitext(os.path.basename(mql_result_filename))[0] \
            + "-context_level" \
            + ".xml"

        result_file = open(result_filename, "a")
        result_file.writelines("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<context_list>")
        result_file.flush()

        ro.find_objects(mql_result_filename, json_filename, result_file, context_level=0)

        result_file.writelines("</context_list>")
        result_file.close()

    def test_find_objects_by_marks(self):
        ro = RenderObjects()
        json_filename = "test_files/input/ro_01.json"
        mql_result_filename = "test_files/input/bh_lq02_verse_mark-result.xml"

        result_filename = "test_files/output/" \
            + os.path.splitext(os.path.basename(mql_result_filename))[0] \
            + "-context_level" \
            + ".xml"

        result_file = open(result_filename, "a")
        result_file.writelines("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<context_list>")
        result_file.flush()

        ro.find_objects(mql_result_filename, json_filename, result_file, handler_type=ContextHandlerType.marks)

        result_file.writelines("\n</context_list>")
        result_file.close()


if __name__ == '__main__':
    unittest.main()

