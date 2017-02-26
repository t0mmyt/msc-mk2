"""
Main Web Interface
"""
import os
import json
import requests
from collections import OrderedDict
from requests import ConnectionError
from flask import Flask, render_template, abort, request, jsonify
from jinja2 import TemplateNotFound
from interface.nav import SimpleNavigator
from interface.importer import Importer


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['TEMPLATES_AUTO_RELOAD'] = True
nav = SimpleNavigator(OrderedDict(
    Home="/",
    Import="/import",
    Explore="/explore",
    Sax="/sax",
))


@app.route("/")
def render_index():
    try:
        return render_template("index.html", nav=nav.render_as('Home'))
    except TemplateNotFound:
        abort(404)

@app.route("/import", methods=['GET', 'POST'])
def render_import():
    try:
        if request.method == "GET":
            return render_template("import.html", nav=nav.render_as('Import'))
        elif request.method == "POST":
            importer = Importer()
            files = request.files.getlist("files")
            for f in files:
                importer.add(f.read())
            status = importer.send()
            results = dict(zip([f.filename for f in files], status))
            results_html = "<table>"
            for filename, result in results.items():
                if result:
                    results_html += '<tr class="success"><td>{}</td></tr>'.format(filename)
                else:
                    results_html += '<tr class="failure"><td>{}</td></tr>'.format(filename)
            results_html += "</table>"

            return render_template(
                "import.html",
                nav=nav.render_as("Import"),
                results=results_html,
            )
    except TemplateNotFound:
        abort(404)

@app.route("/explore")
def render_explore():
    try:
        return render_template("explore.html", nav=nav.render_as('Explore'))
    except TemplateNotFound:
        abort(404)

@app.route("/sax")
def render_sax():
    try:
        return render_template("sax.html", nav=nav.render_as('Sax'))
    except TemplateNotFound:
        abort(404)

@app.route("/raw_json/<channel>")
def raw_json(channel):
    try:
        r = requests.get(
            "{}/v1/metrics/{}".format(TSDATASTORE, channel),
            params = request.args
        )
        if r.status_code != 200:
            abort(r.status_code)
        return jsonify(r.json())
    except ConnectionError:
        abort(503)


if __name__ == "__main__":
    TSDATASTORE = os.getenv('TSDATASTORE', "http://localhost:8163")
    app.run(debug=True)
