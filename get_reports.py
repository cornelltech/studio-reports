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

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN', None)
TEAMS_FILE = "teams"

# output paths
OUTPUT_DIR = "www/mysite"
# OUTPUT_DIR = "output"
OUTPUT_TEAM_PHOTOS = "team_photos"
# % OUTPUT_DIR
OUTPUT_COMPANY_LOGOS = "logos"
 # % OUTPUT_DIR
OUTPUT_INDEX = "%s/index.html" % OUTPUT_DIR

ORG_NAME = "ct-product-challenge-2017"
# TEAMS_FILE = "testing-only-teams"
# ORG_NAME = "cornelltech"
FILE_NAME = "report.yaml"

TEAM_PHOTO_DIR = "team_photos"
COMPANY_LOGO_DIR = "logos/"

# OUTPUT_DIR = "www/mysite/"
OUTPUT_FILE = "index.html"

SECTIONS = ['S1', 'S2', 'S3', 'S4']


def create_output_directories():
    if (not os.path.exists(OUTPUT_DIR)):
        os.makedirs(OUTPUT_DIR)
    if (not os.path.exists(OUTPUT_TEAM_PHOTOS)):
        os.makedirs("%s/%s" % (OUTPUT_DIR, OUTPUT_TEAM_PHOTOS))
    if (not os.path.exists(OUTPUT_COMPANY_LOGOS)):
        os.makedirs("%s/%s" % (OUTPUT_DIR, OUTPUT_COMPANY_LOGOS))


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
    g = github.Github(GITHUB_ACCESS_TOKEN)
    for team in section:
	print 'getting repo for', team, '......'
        try:
            team_name = ORG_NAME + "/" + team
            repo = g.get_repo(team_name)
            yaml_file = repo.get_file_contents(FILE_NAME)
            doc = yaml.safe_load(yaml_file.decoded_content)
            doc['repo'] = repo.name
            try:
                team_photo_url = get_photo_url(repo.name, doc['team']['picture'])
                team_photo_path = save_photo_path(OUTPUT_TEAM_PHOTOS, repo.name, doc['team']['picture'])
                doc['team']['picture'] = save_photo(team_photo_url, team_photo_path)
                print doc['team']['picture']

                logo_url = get_photo_url(repo.name, doc['company']['logo'])
                logo_path = save_photo_path(OUTPUT_COMPANY_LOGOS, repo.name, doc['company']['logo'])
                doc['company']['logo'] = save_photo(logo_url, logo_path)

            except KeyError, e:
                print 'repo', team, 'missing photo:', str(e)
            teams.append(doc)
        except yaml.parser.ParserError, e:
            print 'repo', team, 'contains bad report.yaml file', str(e)
        except Exception, e:
            print 'repo', team, 'does not contain report.yaml', str(e)
    return teams

def get_photo_url(repo_name, img_name):
    return 'https://raw.githubusercontent.com/%s/%s/master/%s' % (ORG_NAME, repo_name, img_name)

def save_photo_path(output_dir, repo_name, img_name):
    return '%s/%s-%s' % (output_dir, repo_name, img_name)

def save_photo(url, output_path):
    access_token = 'token %s' % GITHUB_ACCESS_TOKEN
    response = requests.get(url, stream=True, headers={'Authorization': access_token})
    full_output_path = "%s/%s" % (OUTPUT_DIR, output_path)
    with open(full_output_path, 'wb') as outfile:
        shutil.copyfileobj(response.raw, outfile)
    return output_path

def save_picture(repo, target_dir_name, img_name):
    url = 'https://raw.githubusercontent.com/' + repo.full_name + '/master/' + img_name
    access_token = 'token ' + GITHUB_ACCESS_TOKEN
    response = requests.get(url, stream=True, headers={'Authorization': access_token})
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
