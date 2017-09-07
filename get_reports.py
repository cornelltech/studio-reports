import github
import flask
import os
import requests
import shutil
import yaml

from dotenv import load_dotenv
from flask import Flask, render_template
from os.path import join, dirname

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

GITHUB_USER = os.environ.get('GITHUB_USER', None)
GITHUB_PASSWORD = os.environ.get('GITHUB_PASSWORD', None)

TEAMS_FILE = "team-repos"

REPO_NAME = "cornelltech/studio-reports"
FILE_NAME = "report.yaml"

TOP_LEVEL_KEYS = ['product_narrative', 'company', 'how_might_we',
                    'assets', 'team']

COMPANY_KEYS = ['logo', 'name']
TEAM_KEYS = ['picture', 'roster']
TEAM_MEMBER_KEYS = ['name', 'email']
ASSETS_KEYS = ['url', 'title']

class Team:
    def __init__(self, doc):
        self.roster = make_team_map(doc['team']['roster'])
        self.how_might_we = doc['how_might_we']
        self.product_narrative = doc['product_narrative']
        self.company = doc['company']
        self.assets = doc['assets']

def make_team_map(roster):
    team = {}
    for person in roster:
        team[person['name']] = person['email']
    return team

app = Flask(__name__)

@app.route('/')
def report():
    teams = get_teams()
    return render_template('full_report.html', teams=teams)

def get_teams():
    teams = []
    g = github.Github(GITHUB_USER, GITHUB_PASSWORD)
    with open(TEAMS_FILE) as rd:
        team_repos = [repo.strip() for repo in rd.readlines()]
    for team in team_repos:
        repo = g.get_repo(REPO_NAME)
        yaml_file = repo.get_file_contents(FILE_NAME)
        doc = yaml.load(yaml_file.decoded_content)
        save_team_picture(repo, doc['team']['picture'])
        # teams.append(doc)
        teams.append(Team(doc))
    return teams

def save_team_picture(repo, img_name):
    url = 'https://raw.githubusercontent.com/' + repo.full_name + '/master/' + img_name
    response = requests.get(url, stream=True, auth=(GITHUB_USER, GITHUB_PASSWORD))
    team_img_file = repo.name + '-' + img_name
    with open(team_img_file, 'wb') as outfile:
        shutil.copyfileobj(response.raw, outfile)

if __name__ == '__main__':
    app.run()
