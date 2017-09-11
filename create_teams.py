import github
import os
# import requests
# import shutil
# import yaml

from dotenv import load_dotenv
from os.path import join, dirname

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN', None)

TEAMS_FILE = "team-repos"
ORG_NAME = "ct-product-challenge-2017"

def create_team_repo(g, team_name):
    g.get_organization(ORG_NAME).create_repo(team_name)

if __name__ == '__main__':
    g = github.Github(GITHUB_ACCESS_TOKEN)
    g.get_organization(ORG_NAME).create_repo('cool-story-bro')
