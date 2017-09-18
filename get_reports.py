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

TEAMS_FILE = "/home/ubuntu/studio-reports/teams"

ORG_NAME = "ct-product-challenge-2017"
# TEAMS_FILE = "testing-only-teams"
# ORG_NAME = "cornelltech"
FILE_NAME = "report.yaml"

TEAM_PHOTO_DIR = "team_photos/"
COMPANY_LOGO_DIR = "logos/"

OUTPUT_DIR = "www/mysite/"
OUTPUT_FILE = "index.html"

SECTIONS = ['S1', 'S2', 'S3', 'S4']

def get_photo_name(repo, img_name):
    team_img_file = repo.name + '-' + img_name
    return team_img_file

def get_sections():
    sections = {}
    for section in SECTIONS:
        sections[section] = []
    with open(TEAMS_FILE) as rd:
        team_repos = [repo.strip() for repo in rd.readlines()]
        for repo in team_repos:
            team = repo.split('\t')
            section = team[0]
            sections[section].append(team[3])
    return sections

def get_teams(section):
    teams = []
    g = github.Github(GITHUB_USER, GITHUB_PASSWORD)
    for team in section:
	print 'getting repo for', team, '......'
        try:
            team_name = ORG_NAME + "/" + team
            repo = g.get_repo(team_name)
            yaml_file = repo.get_file_contents(FILE_NAME)
            doc = yaml.safe_load(yaml_file.decoded_content)
            doc['repo'] = repo.name
            try:
                doc['company']['logo'] = save_picture(repo, COMPANY_LOGO_DIR,
                                                        doc['company']['logo'])
                doc['team']['picture'] = save_picture(repo, TEAM_PHOTO_DIR,
                                                        doc['team']['picture'])
            except KeyError, e:
                print 'repo', team, 'missing photo:', str(e)
            teams.append(doc)
        except yaml.parser.ParserError, e:
            print 'repo', team, 'contains bad report.yaml file', str(e)
        except Exception, e:
            print 'repo', team, 'does not contain report.yaml', str(e)
    return teams

def save_picture(repo, target_dir_name, img_name):
    url = 'https://raw.githubusercontent.com/' + repo.full_name + '/master/' + img_name
    response = requests.get(url, stream=True, auth=(GITHUB_USER, GITHUB_PASSWORD))
    output_location = OUTPUT_DIR + target_dir_name
    if (not os.path.exists(output_location)):
        os.makedirs(output_location)
    img_file_name = get_photo_name(repo, img_name)
    output_file_location = output_location + img_file_name
    with open(output_file_location, 'wb') as outfile:
        shutil.copyfileobj(response.raw, outfile)
    return target_dir_name + img_file_name

def create_index_page():
    sections = get_sections()
    for section in sections:
        teams = get_teams(sections[section])
        sections[section] = teams
    env = Environment(loader=PackageLoader('get_reports', 'templates'),
                        autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template('buildboard.html')
    return template.render(sections=sections)

if __name__ == '__main__':
    print create_index_page()
