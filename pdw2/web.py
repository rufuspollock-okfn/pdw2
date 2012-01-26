from flask import Flask, jsonify, render_template, json, request
import urllib2, subprocess, os

app = Flask(__name__)
# genshi = Genshi(app)

@app.route("/")
def home():
    # return render_template('index.html')
    return api_index()

@app.route("/api")
def api_index():
    example = {
        "title": "An Example",
        "issued" : "19030101",
        "authors" : [
            {
                "name" : "John Smith",
                "birth" : "1849",
            }
        ]
    }
    example_json = json.dumps(example, indent=2)
    example_query = 'jurisdiction=france&work=' + json.dumps(example)
    return render_template('api.html', example=example_json,
            example_query=example_query)


@app.route("/api/pd")
def api_pd():
    # TODO: proper validation (e.g. with colander)
    if not 'jurisdiction' in request.args or not 'work' in request.args:
        return jsonify({
            'error': 'Missing jurisdiction or work parameter'
            })
    jurisdiction = request.args['jurisdiction']
    workdata = json.loads(request.args['work'])
    if not os.path.exists(os.path.join('pdcalc', jurisdiction)):
        return jsonify({
            'error': 'No calculator for that jurisdiction'
            })
    
    try:
        country_dir = 'pdcalc/%s/' % jurisdiction
        maparg = country_dir+jurisdiction+'.map'
        flowarg = country_dir+jurisdiction[0].upper() + jurisdiction[1:] +'.rdf'
        open('pdcalc/pdw2tmp.json', 'w').write(json.dumps(workdata))
        process = subprocess.Popen(['python', 'pdcalc/reasoner.py', maparg, flowarg, 'pdcalc/pdw2tmp.json'  ], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            raise Exception(err)
    except Exception, inst:
        if app.debug:
            raise
        return jsonify({
            'error': '%s' % inst
            })
    return jsonify({'out':out})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
