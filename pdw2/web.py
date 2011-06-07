from flask import Flask, jsonify, render_template, json, request

import pdcalc
# import these so they register themselves
import pdcalc.fr
import pdcalc.uk
import pdcalc.work
import solr

app = Flask(__name__)
# genshi = Genshi(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/search")
def search():
    s = solr.SolrConnection('http://solr.okfn.org/solr/bibliographica.org')
    q = request.args.get('q', '')
    works = []
    if q:
        response = s.query(q)
        works = response.results
        count = response.numFound
    return render_template('search.html', q=q, works=works, count=count)

@app.route("/api")
def api_index():
    example = {
        "title": "Oliver Twist",
        "type": "literary",
        "date" : "19030101",
        "authors" : [
            {
                "type" : "person",
                "birth_date" : "18490101",
            }
        ]
    }
    example_json = json.dumps(example, indent=2)
    example_query = 'jurisdiction=fr&work=' + json.dumps(example)
    return render_template('api.html', example=example_json,
            example_query=example_query, work_types=pdcalc.work.WORK_TYPES)

@app.route("/api/pd")
def api_pd():
    # TODO: proper validation (e.g. with colander)
    if not 'jurisdiction' in request.args or not 'work' in request.args:
        return jsonify({
            'error': 'Missing jurisdiction or work parameter'
            })
    jurisdiction = request.args['jurisdiction']
    workdata = json.loads(request.args['work'])
    calculator = pdcalc.get_calculator(jurisdiction)
    if calculator is None:
        return jsonify({
            'error': 'No calculator for that jurisdiction'
            })
    work = pdcalc.work.Work(workdata)
    try:
        status = calculator.get_status(work)
    except Exception, inst:
        if app.debug:
            raise
        return jsonify({
            'error': '%s' % inst
            })

    return jsonify({
        jurisdiction: {
            'pd': status,
            'assumptions': calculator.assumptions
            }
        })

@app.route("/bibliographica")
def bibliographica():
    return req("shakespeare")

@app.route("/req/<id>")
def req(id):
    from pdcalc.bibliographica import Bibliographica, load
    title = "Public Domain Works"
    
    calcUK = CalculatorUK()
    data = load(id)
    results = []
    for i in data:
        test = Bibliographica(i)
        work = Work(test.data)
        status = calcUK.get_status(work)
	w = W(", ".join([author.name for author in work.authors]), work.title, status)
	results.append(w)

    return render_template('index.html', dict(title=title, results=results))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
