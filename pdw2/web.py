from flask import Flask, jsonify, render_template, json

from pdcalc.uk import CalculatorUK
from pdcalc.work import Work

app = Flask(__name__)
# genshi = Genshi(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/api")
def api_index():
    example = {
        "type": "text",
        "date" : "1903-01-01",
        "persons" : [
            {
                "type" : "person",
                "birth_date" : "1849-01-01",
                "death_date" : "None"
            }
        ]
    }
    example_json = json.dumps(example, indent=2)
    example_query = 'jurisdiction=fr&work=' + json.dumps(example)
    return render_template('api.html', example=example_json,
            example_query=example_query)

@app.route("/api/pd")
def api_pd():
    return jsonify({'abc': 1})

@app.route("/bibliographica")
def bibliographica():
    return req("shakespeare")

@app.route("/<id>")
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
