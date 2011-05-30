from flask import Flask
from flaskext.genshi import Genshi
from flaskext.genshi import render_response

from PDC.Bibliographica import Bibliographica, load
from PDC.CalculatorUK import CalculatorUK
from PDC.CalculatorBase import Work
from data import W

app = Flask(__name__)
genshi = Genshi(app)

@app.route("/ciao")
def ciao():
    return "ciao"

@app.route("/")
def index():
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

    return render_response('index.html', dict(title=title, results=results))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
