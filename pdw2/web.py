from flask import Flask, jsonify, render_template

from pdcalc.bibliographica import Bibliographica, load
from pdcalc.uk import CalculatorUK
from pdcalc.work import Work

app = Flask(__name__)
# genshi = Genshi(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/api")
def api_index():
    return jsonify({'abc': 1})

@app.route("/bibliographica")
def bibliographica():
    return req("shakespeare")

@app.route("/<id>")
def req(id):
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
