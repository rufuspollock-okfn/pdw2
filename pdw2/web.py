from flask import Flask, jsonify, render_template, json, request, current_app
from functools import wraps
import subprocess, os
import csv, json
import re
import codecs, cStringIO

from datetime import timedelta
from flask import make_response
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


app = Flask(__name__)
# genshi = Genshi(app)

app.DEBUG=True

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/error.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('error logs')

@app.route("/")
def home():
    return render_template('index.html')
    return api_index()

@app.route("/list")
@crossdomain("*")
def list():
    qa = request.args.get('author', "");
    qw = request.args.get('work', "");
    f = open('/var/www/www.publicdomainworks.net/pdw/pdw2/pdw2/worklist/list.csv', 'r');
    fields = ("author", "title", "rdf")
    reader = UnicodeReader(f, delimiter="\t")
    dict_reader = [ dict(zip(fields, row)) for row in reader ]
    out = json.dumps([row for row in dict_reader if matches(row, qa, qw)])
    return out

def matches(row, qa, qw):
    return qa.lower() in row["author"].lower() and qw.lower() in row["title"].lower();

@app.route("/api/jurisdictions")
def jurisdictions():


    path_base = "/var/www/www.publicdomainworks.net/pdcalc"
    base_path = path_base + "/src/pd"

    venv_python_file = path_base + "/bin/python"
    venv_activator   = path_base + "/bin/activate"
    venv_deactivator   = path_base + "/bin/deactivate"
    env = os.environ.copy()
    path_comps = env['PATH'].split(':')[1:]
    #print path_comps
    path_comps.insert(0, path_base+"/bin")
    #print path_comps
    env['PATH'] = ":".join(path_comps)
    env['VIRTUAL_ENV'] = path_base
    env['PWD'] = base_path
    env["_"] = venv_python_file
    #print self.env['PATH']
    print env
    cmd = [venv_python_file, os.path.join(base_path, "pdcalc.py")]
    cmd.extend(['-o', "json"])
    cmd.extend(['-V'])

    print str(cmd)

    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=base_path)

    stdout, stderr = process.communicate()

    opts = json.loads(stdout)
    valid = {}
    for opt in opts:
    	valid[opt] = opt


    ret = {'valid':valid	}
    return jsonify(ret)


@app.route("/api")
def api_index():
    example = {
        "title": "An Example",
        "issued" : "19030101",
        "author" : [
            {
                "name" : "John Smith",
                "birth" : "1849",
            }
        ]
    }
    example_json = json.dumps(example, indent=2)
    example_query = 'jurisdiction=france/bnf&work=http://data.bnf.fr/15533097/2046___film/rdf.xml'
    return render_template('api.html', example=example_json, example_query=example_query)




def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

import threading
import subprocess

class API(threading.Thread):
    def __init__(self, detail, jurisdiction, work, flavor=None, language="en"):
        self.stdout = None
        self.stderr = None

        self.language = language
        self.detail = detail
        self.jurisdiction = jurisdiction
        self.work = work
        self.flavor = flavor
        threading.Thread.__init__(self)

    def run(self):
        path_base = "/var/www/www.publicdomainworks.net/pdcalc"
        base_path = path_base + "/src/pd"

        venv_python_file = path_base + "/bin/python"
        venv_activator   = path_base + "/bin/activate"
        venv_deactivator   = path_base + "/bin/deactivate"
        self.env = os.environ.copy()
        path_comps = self.env['PATH'].split(':')[1:]
        #print path_comps
        path_comps.insert(0, path_base+"/bin")
        #print path_comps
        self.env['PATH'] = ":".join(path_comps)
        self.env['VIRTUAL_ENV'] = path_base
        self.env['PWD'] = base_path
        self.env["_"] = venv_python_file
        #print self.env['PATH']
        print self.env
        cmd = [venv_python_file, os.path.join(base_path, "pdcalc.py")]
        cmd.extend(['-o', "json"])
        cmd.extend(['-f', "rdf"])
        
        cmd.extend(['-d', self.detail])
        cmd.extend(['-c', self.jurisdiction])

        cmd.extend(['-i', self.work])
        cmd.extend(['-L', self.language])
        if self.flavor is not None:
            cmd.extend(['-l', self.flavor])
        print str(cmd)

        #print " ".join(cmd)
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env, cwd=base_path)

        self.stdout, self.stderr = process.communicate()

    def get_out_err(self):
        return self.stdout, self.stderr 


@app.route("/api/pd")
@crossdomain("*")
@jsonp
def api_pd():
    
    if not 'jurisdiction' in request.args or not 'work' in request.args:
        return jsonify({
            'error': 'Missing jurisdiction or work parameter'
        })
    #jurisdiction + flavor combo
    jd = request.args.get('jurisdiction')
    jd = jd.split('/')
    jurisdiction = jd[0]
    jurisdiction = jurisdiction.lower()
    flavor = None
    if len(jd)>1:
        flavor = jd[1]
        flavor = flavor.lower()
    
    #work
    work = request.args.get('work')
    
    #detail level
    detail = request.args.get('detail', "low")

    language = request.args.get('lang', "en")
    

    
    process = API(detail,jurisdiction, work, flavor, language)
    process.start()
    process.join()
    out, err = process.get_out_err()
    output = {}
    output['out_raw'] = out

  #  os.system("cat '" + output['out_raw'] + "' > /var/www/www.publicdomainworks.net/stupid.log")

    output['error'] = err
    try:
        output['output'] = json.loads(out)
    except:
        output['output'] = ""
    
    return jsonify(output)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8001)
