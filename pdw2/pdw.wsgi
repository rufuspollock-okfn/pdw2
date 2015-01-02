
import os

#set path to real path
base_path = "/var/www/www.publicdomainworks.net/pdw"

#for virtualenv
activate_this = os.path.join(base_path, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

#imports
import sys
sys.path.insert(0, os.path.join(base_path, "pdw2"))

#go!!
from pdw2.web import app as application
application.debug = True

