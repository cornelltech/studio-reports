import github
import jinja2
import os
import requests
import shutil
import yaml

from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape
from os.path import join, dirname

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

GITHUB_USER = os.environ.get('GITHUB_USER', None)
GITHUB_PASSWORD = os.environ.get('GITHUB_PASSWORD', None)

TEAMS_FILE = "team-repos"

FILE_NAME = "report.yaml"
OUTPUT_PATH = "index.html"

TEAM_PHOTO_DIR = "team_photos/"

TOP_LEVEL_KEYS = ['product_narrative', 'company', 'how_might_we',
                    'assets', 'team']

COMPANY_KEYS = ['logo', 'name']
TEAM_KEYS = ['picture', 'roster']
TEAM_MEMBER_KEYS = ['name', 'email']
ASSETS_KEYS = ['url', 'title']

class Team:
    def __init__(self, doc, repo):
        self.roster = build_team(doc['team']['roster'])
        self.how_might_we = doc['how_might_we']
        self.product_narrative = doc['product_narrative']
        self.company = doc['company']['name']
        self.company_logo = doc['company']['logo']
        self.assets = build_assets(doc['assets'])
        self.team_photo_file = get_photo_name(repo, doc['team']['picture'])

    class Teammate:
        def __init__(self, name, email):
            self.name = name
            self.email = email

    class Asset:
        def __init__(self, title, url):
            self.title = title
            self.url = url

def build_team(roster):
    team = []
    for person in roster:
        team.append(Team.Teammate(person['name'], person['email']))
    return team

def build_assets(assets):
    list_of_assets = []
    for asset in assets:
        list_of_assets.append(Team.Asset(asset['title'], asset['url']))
    return list_of_assets

def get_photo_name(repo, img_name):
    team_img_file = repo.name + '-' + img_name
    return TEAM_PHOTO_DIR + team_img_file

def get_teams():
    teams = []
    g = github.Github(GITHUB_USER, GITHUB_PASSWORD)
    with open(TEAMS_FILE) as rd:
        team_repos = [repo.strip() for repo in rd.readlines()]
    for team in team_repos:
        repo = g.get_repo(team)
        yaml_file = repo.get_file_contents(FILE_NAME)
        doc = yaml.load(yaml_file.decoded_content)
        save_team_picture(repo, doc['team']['picture'])
        # teams.append(doc)
        teams.append(Team(doc, repo))
    return teams

def save_team_picture(repo, img_name):
    url = 'https://raw.githubusercontent.com/' + repo.full_name + '/master/' + img_name
    response = requests.get(url, stream=True, auth=(GITHUB_USER, GITHUB_PASSWORD))
    team_img_file = get_photo_name(repo, img_name)
    if (not os.path.exists(TEAM_PHOTO_DIR)):
        os.makedirs(TEAM_PHOTO_DIR)
    with open(team_img_file, 'wb') as outfile:
        shutil.copyfileobj(response.raw, outfile)

# def save_company_picture(repo, img_url):
#     response = requests.get(img_url, stream=True)
#     company_img_file = repo.name + '-' +
#     with open(team_img_file, 'wb') as outfile:
#         shutil.copyfileobj(response.raw, outfile)

def create_index_page():
    teams = get_teams()
    env = Environment(loader=PackageLoader('get_reports', 'templates'),
                        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('buildboard.html')
    return template.render(teams=teams)


if __name__ == '__main__':
    print create_index_page()
