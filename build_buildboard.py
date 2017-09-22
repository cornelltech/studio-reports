import github
import jinja2
import os
import requests
import shutil
import unicodedata
import yaml

import pdb

from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape
from os.path import join, dirname

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN', None)
ORG_NAME = "ct-product-challenge-2017"
YAML_FILE_NAME = "report.yaml"
TEAMS_FILE_NAME = "teams"
SECTIONS = ['S1', 'S2', 'S3', 'S4']

PWD = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR_NAME = "output"
YAML_DIR_NAME = "yaml"
TEAM_PHOTOS_DIR_NAME = "team_photos"
COMPANY_LOGOS_DIR_NAME = "logos"
INDEX_FILE_NAME = "index.html"

# process teams file into list of teams
# download all the yaml files
# process yaml files
# create outputs

def get_photo_url(repo_name, img_name):
    return 'https://raw.githubusercontent.com/%s/%s/master/%s' % (ORG_NAME, repo_name, img_name)

def save_photo_path(output_dir_name, repo_name, img_name):
    return os.path.join(PWD, OUTPUT_DIR_NAME, output_dir_name,
                        "%s-%s" % (repo_name, img_name))

def get_photo_path_for_web(photo_path):
    web_path = os.path.relpath(photo_path, os.path.join(PWD, OUTPUT_DIR_NAME))
    print web_path
    return web_path

def save_photo(url, output_path):
    print 'saving %s' % os.path.basename(output_path)
    access_token = 'token %s' % GITHUB_ACCESS_TOKEN
    response = requests.get(url, stream=True, headers={'Authorization': access_token})
    with open(output_path, 'wb') as outfile:
        shutil.copyfileobj(response.raw, outfile)
    return get_photo_path_for_web(output_path)

def process_yaml_file(yaml_file, download_imgs=False):
    repo_name = os.path.splitext(os.path.basename(yaml_file))[0]
    try:
        with open(yaml_file, 'r') as report_contents:
            doc = yaml.safe_load(report_contents)
    except yaml.parser.ParserError, e:
        print 'repo', repo_name, 'contains bad report.yaml file', str(e)

    try:
        team_photo = doc['team']['picture']
    except KeyError, e:
        print 'repo', team, 'missing team photo:', str(e)

    try:
        company_logo = doc['company']['logo']
    except KeyError, e:
        print 'repo', team, 'missing company logo:', str(e)

    if download_imgs:
        # save team photo and update yaml to hold relative path
        team_photo_url = get_photo_url(repo_name, team_photo)
        team_photo_path = save_photo_path(TEAM_PHOTOS_DIR_NAME, repo_name, team_photo)
        doc['team']['picture'] = save_photo(team_photo_url, team_photo_path)

        # save company logo and update yaml to hold relative path
        logo_url = get_photo_url(repo_name, doc['company']['logo'])
        logo_path = save_photo_path(COMPANY_LOGOS_DIR_NAME, repo_name, company_logo)
        doc['company']['logo'] = save_photo(logo_url, logo_path)

    else:  # update paths anyway
        doc['team']['picture'] = \
            get_photo_path_for_web(save_photo_path(TEAM_PHOTOS_DIR_NAME,
                                                    repo_name, team_photo))
        doc['company']['logo'] = \
            get_photo_path_for_web(save_photo_path(COMPANY_LOGOS_DIR_NAME,
                                                    repo_name, company_logo))

    # add team name to yaml
    doc['repo'] = repo_name
    return doc

def save_team_files(teams, yaml_dir):
    g = github.Github(GITHUB_ACCESS_TOKEN)
    for team in teams:
        print 'getting yaml file for %s...' % team
        try:
            repo_name = "%s/%s" % (ORG_NAME, team)
            repo = g.get_repo(repo_name)
            team_yaml_file = os.path.join(yaml_dir, "%s.yaml" % team)
            with open(team_yaml_file, 'w') as outfile:
                yaml_file = repo.get_file_contents(YAML_FILE_NAME)
                outfile.write(yaml_file.decoded_content)
        except github.GithubException, e:
            print "There's a problem with that repository's yaml file:", str(e)

# def save_team_file(team, yaml_dir, g):
#     print 'getting yaml file for %s...' % team
#     try:
#         repo_name = "%s/%s" % (ORG_NAME, team)
#         repo = g.get_repo(repo_name)
#         team_yaml_file = os.path.join(yaml_dir, "%s.yaml" % team)
#         with open(team_yaml_file, 'w') as outfile:
#             yaml_file = repo.get_file_contents(YAML_FILE_NAME)
#             outfile.write(yaml_file.decoded_content)
#     except github.GithubException, e:
#         print "There's a problem with that repository's yaml file:", str(e)

def get_teams(teams_file):
    with open(teams_file) as tf:
        team_metadata = [team.strip() for team in tf.readlines()]
    team_names = [team.split("\t")[3] for team in team_metadata]
    return (team_names, team_metadata)

def get_sections(teams_metadata):
    sections = {}
    for section in SECTIONS:
        sections[section] = []
    for line in teams_metadata:
        team = line.split('\t')
        section = team[0]
        sections[section].append(team[3])
    return sections

def create_output_directories(target_directory):
    output_dir = os.path.join(target_directory, OUTPUT_DIR_NAME)
    if not os.path.exists(output_dir):
        print 'creating new directory:', output_dir
        os.makedirs(output_dir)
    yaml_dir = os.path.join(output_dir, YAML_DIR_NAME)
    if not os.path.exists(yaml_dir):
        print 'creating new directory:', yaml_dir
        os.makedirs(yaml_dir)
    team_photos_dir = os.path.join(output_dir, TEAM_PHOTOS_DIR_NAME)
    if not os.path.exists(team_photos_dir):
        print 'creating new directory:', team_photos_dir
        os.makedirs(team_photos_dir)
    company_logos_dir = os.path.join(output_dir, COMPANY_LOGOS_DIR_NAME)
    if not os.path.exists(company_logos_dir):
        print 'creating new directory:', company_logos_dir
        os.makedirs(company_logos_dir)
    return (output_dir, yaml_dir, team_photos_dir, company_logos_dir)


def create_index_page(sections):
    env = Environment(loader=PackageLoader('get_reports', 'templates'),
                        autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template('buildboard.html')
    return template.render(sections=sections)

def build_pages_from_scratch():
    # setup output directories
    pwd = os.path.dirname(os.path.realpath(__file__))
    print 'PWD=', PWD
    print 'pwd=', pwd
    (output_dir, yaml_dir, team_photos_dir, company_logos_dir) = \
        create_output_directories(pwd)

    # extract teams data
    teams_file = os.path.join(pwd, TEAMS_FILE_NAME)
    (team_names, team_metadata) = get_teams(teams_file)

    # save teams yaml
    save_team_files(team_names, yaml_dir)

    # create index page
    sections = get_sections(team_metadata)
    for section in sections:
        teams = sections[section]
        team_docs = []
        for team in teams:
            team_doc = process_yaml_file(os.path.join(yaml_dir, "%s.yaml" % team),
                                        download_imgs=True)
            team_docs.append(team_doc)
        sections[section] = team_docs
    index = create_index_page(sections)

    output_index = os.path.join(pwd, OUTPUT_DIR_NAME, INDEX_FILE_NAME)
    with open(output_index, 'w') as outfile:
        outfile.write(unicodedata.normalize('NFKD', index).encode('ascii','ignore'))
    print outfile

# yaml files assumed to live in OUTPUT_DIR_NAME/YAML_DIR_NAME
def build_pages_from_existing():
    pwd = os.path.dirname(os.path.realpath(__file__))

    # extract teams data
    teams_file = os.path.join(pwd, TEAMS_FILE_NAME)
    (team_names, team_metadata) = get_teams(teams_file)

    # This is where it will look for yaml data files.
    # TODO: control with parameter instead?
    yaml_dir = os.path.join(pwd, OUTPUT_DIR_NAME, YAML_DIR_NAME)

    # create index page
    sections = get_sections(team_metadata)
    for section in sections:
        teams = sections[section]
        team_docs = []
        for team in teams:
            team_doc = process_yaml_file(os.path.join(yaml_dir, "%s.yaml" % team),
                                        download_imgs=False)
            team_docs.append(team_doc)
        sections[section] = team_docs
    index = create_index_page(sections)

    output_index = os.path.join(pwd, OUTPUT_DIR_NAME, INDEX_FILE_NAME)
    with open(output_index, 'w') as outfile:
        outfile.write(unicodedata.normalize('NFKD', index).encode('ascii','ignore'))
    print outfile

if __name__ == '__main__':
    build_pages_from_scratch()
