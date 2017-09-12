import flask
import get_reports

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def report():
    teams = get_reports.get_teams()
    return render_template('buildboard.html', teams=teams)

if __name__ == '__main__':
    app.run()
