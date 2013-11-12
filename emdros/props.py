#!/usr/bin/env python
#-*- coding:utf-8 -*-

#OPTIONS:
#   --xml                Output XML format
#   --cxml               Output compact XML format
#   --console            Output console-friendly format
#   --help               Show this help
#   -V , --version       Show version
#   -h , --host host     Set hostname to connect to
#   -u , --user user     Set database user to connect as (default: 'emdf')
#   -p , --password pwd  Set password to use for database user
#   -b , --backend bkend Use this backend. Valid values:
#                        For PostgreSQL: p, pg, postgres, postgresql
#                        For SQLite 2.X.X: 2, l, lt, sqlite, sqlite2, s
#                        For SQLite 3.X.X: 3, lt3, sqlite3, s3
#                        For MySQL: m, my, mysql
#                        ... all are case-IN-sensitive.
#   -e , --encoding enc  Can either be iso_8859-1 to iso_8859-15 or UTF8
#   -d , --dbname db     Set initial database to db
#   -n , --nop           Do not print results (no output)

outputFormat = "--xml"
host = ""
user = ""
password = ""
backEnd = "s3"
encoding = "UTF8"
dbName = "/data/emdros/wivu/s3/bhs3"


