#set path to real path
import os
base_path = "/var/www/www.publicdomainworks.net/pdw"
activate_this = os.path.join(base_path, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from web import app as application

import sys
sys.path.insert(0, os.path.join(base_path, "pdw2"))