#set path to real path
import os
base_path = "/var/www/www.calculateurdomainepublic.fr/cdp"
activate_this = os.path.join(base_path, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

import web.app as application

import sys
sys.path.insert(0, os.path.join(base_path, "pdw2"))