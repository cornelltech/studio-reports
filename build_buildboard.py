import github
import jinja2
import os
import requests
import shutil
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

OUTPUT_DIR_NAME = "output"
YAML_DIR_NAME = "yaml"
TEAM_PHOTOS_DIR_NAME = "team_photos"
COMPANY_LOGOS_DIR_NAME = "logos"

# process teams file into list of teams
# download all the yaml files
# process yaml files
# create outputs

def get_photo_url(repo_name, img_name):
    return 'https://raw.githubusercontent.com/%s/%s/master/%s' % (ORG_NAME, repo_name, img_name)

def save_photo_path(output_dir_name, repo_name, img_name):
    save_photo_as = os.path.join(OUTPUT_DIR_NAME, output_dir_name, "%s-%s" % (repo_name, img_name))
    return save_photo_as

def save_photo(url, output_path):
    access_token = 'token %s' % GITHUB_ACCESS_TOKEN
    response = requests.get(url, stream=True, headers={'Authorization': access_token})
    with open(output_path, 'wb') as outfile:
        shutil.copyfileobj(response.raw, outfile)
    return os.path.relpath(output_path, OUTPUT_DIR_NAME)

def process_yaml_file(yaml_file):
    repo_name = os.path.splitext(os.path.basename(yaml_file))[0]
    try:
        with open(yaml_file, 'r') as report_contents:
            doc = yaml.safe_load(report_contents)
    except yaml.parser.ParserError, e:
        print 'repo', repo_name, 'contains bad report.yaml file', str(e)

    # save team photo and update yaml to hold relative path
    try:
        team_photo = doc['team']['picture']
        team_photo_url = get_photo_url(repo_name, team_photo)
        team_photo_path = save_photo_path(TEAM_PHOTOS_DIR_NAME, repo_name, team_photo)
        doc['team']['picture'] = save_photo(team_photo_url, team_photo_path)
    except KeyError, e:
        print 'repo', team, 'missing team photo:', str(e)

    # save company logo and update yaml to hold relative path
    try:
        company_logo = doc['company']['logo']
        logo_url = get_photo_url(repo_name, doc['company']['logo'])
        logo_path = save_photo_path(COMPANY_LOGOS_DIR_NAME, repo_name, company_logo)
        doc['company']['logo'] = save_photo(logo_url, logo_path)
    except KeyError, e:
        print 'repo', team, 'missing company logo:', str(e)

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

def create_output_directories():
    pwd = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(pwd, OUTPUT_DIR_NAME)
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

if __name__ == '__main__':
    (output_dir, yaml_dir, team_photos_dir, company_logos_dir) = create_output_directories()
    save_team_files(['example-product-team'], yaml_dir)
    yaml_files = os.listdir(yaml_dir)
    for yaml_file in yaml_files:
        yaml_file = os.path.join(yaml_dir, yaml_file)
        process_yaml_file(yaml_file)
