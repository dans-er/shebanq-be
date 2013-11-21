#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from clam.common.parameters import *
from clam.common.formats import *
from clam.common.data import *

REQUIRE_VERSION = 0.7

#The System ID, a short alphanumeric identifier for internal use only
SYSTEM_ID = "clamdros"

#System name, the way the system is presented to the world
SYSTEM_NAME = "Emdros02"

#An informative description for this system:
SYSTEM_DESCRIPTION = "Interface for issuing mql-queries on an Emdros database and building context."

#The root directory for CLAM, all project files, (input & output) and
#pre-installed corpora will be stored here. Set to an absolute path:
ROOT = "/tmp/clamdros02/"

#The URL of the system
#URL = "http://localhost:8080"
PORT= 8080

#Users and passwords
USERS = None #no user authentication
#USERS = { 'admin': pwhash('admin', SYSTEM_ID, 'secret'), 'proycon': pwhash('proycon', SYSTEM_ID, 'secret'), 'antal': pwhash('antal', SYSTEM_ID, 'secret') , 'martin': pwhash('martin', SYSTEM_ID, 'secret') }

#ADMINS = ['admin'] #Define which of the above users are admins
#USERS = { 'username': pwhash('username', SYSTEM_ID, 'secret') } #Using pwhash and plaintext password in code is not secure!!

#Do you want all projects to be public to all users? Otherwise projects are
#private and only open to their owners and users explictly granted access.
PROJECTS_PUBLIC = True

PROFILES = [
    Profile(
        InputTemplate('mql-query', PlainTextFormat, "MQL Query",
            StaticParameter(id='encoding', name='Encoding', description='The character encoding of the file', value='utf-8'),
            extension='.mql',
            multi=True
        ),
        OutputTemplate('mql-result', UndefinedXMLFormat, 'MQL Query Results',
            SetMetaField('encoding','utf-8'),
            removeextension='.mql',
            extension='.xml',
            multi=True
        )
    )
]

COMMAND = sys.path[0] + "/wrappers/emdroswrapper02.py $DATAFILE $STATUSFILE $OUTPUTDIRECTORY $PARAMETERS > $OUTPUTDIRECTORY/log"

PARAMETERS =  [
    ('Context level', [
        #BooleanParameter(id='createlexicon',name='Create Lexicon',description='Generate a separate overall lexicon?'),
        #ChoiceParameter(id='casesensitive',name='Case Sensitivity',description='Enable case sensitive behaviour?', choices=['yes','no'],default='no'),
        #StringParameter(id='author',name='Author',description='Sign output metadata with the specified author name',maxlength=255),
        IntegerParameter(id='contextlevel',name='Offset',description='Limit result context to straw depth',default=0)
    ] )
]

