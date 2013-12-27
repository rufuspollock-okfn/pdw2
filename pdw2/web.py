from flask import Flask, jsonify, render_template, json, request, current_app
from functools import wraps
import subprocess, os

app = Flask(__name__)
# genshi = Genshi(app)

@app.route("/")
def home():
    return render_template('index.html')
    return api_index()

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
    example_query = 'jurisdiction=france&work=http://data.bnf.fr/15533097/2046___film/rdf.xml'
    return render_template('api.html', example=example_json,
            example_query=example_query)

@app.route("/api/jurisdictions")
def jurisdictions():
    ret = {'valid':["france"]}
    return jsonify(ret)


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



@app.route("/api/pd")
@jsonp
def api_pd():
    base_path = "/home/ya/okfn/pdcalc_new/pd/"
    if not 'jurisdiction' in request.args or not 'work' in request.args:
        return jsonify({
            'error': 'Missing jurisdiction or work parameter'
        })
    #jurisdiction + flavor combo
    jd = request.args.get('jurisdiction')
    jd = jd.split('/')
    jurisdiction = jd[0]
    flavor = None
    if len(jd)>1:
        flavor = jd[1]
    
    #work
    work = request.args.get('work')
    
    #detail level
    detail = request.args.get('detail', "low")

    
    cmd = ['python', os.path.join(base_path, "pdcalc.py")]
    cmd.extend(['-o', "json"])
    cmd.extend(['-f', "xml"])
    
    cmd.extend(['-d', detail])
    cmd.extend(['-c', jurisdiction])

    cmd.extend(['-i', work])
    if flavor is not None:
        cmd.extend(['-l', flavor])

    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    output = {}
    output['output'] = out
    output['error'] = err
    return jsonify(output)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=8001)
