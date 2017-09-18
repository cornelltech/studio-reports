import requests
import logging
import json

"""
    Python script to add Trello-like projects to student repositories.
"""

logging.basicConfig(level=logging.DEBUG)

import os
import sys
from dotenv import load_dotenv
from os.path import join, dirname

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

GITHUB_USER = os.environ.get('GITHUB_USER', None)
GITHUB_PASSWORD = os.environ.get('GITHUB_PASSWORD', None)
if GITHUB_USER is None or  GITHUB_PASSWORD is None:
    logging.error('Missing Github credentials')
    sys.exit(-1)

HEADERS = {'Accept': 'application/vnd.github.inertia-preview+json'}
GITHUB_API = 'https://api.github.com'

def add_project_to_repo(repo_name):
    repo = {'owner': 'ct-product-challenge-2017', 'repo': repo_name}
    url = GITHUB_API + '/repos/%(owner)s/%(repo)s/projects' % repo
    logging.info('Creating new board for %s' % url)

    payload = json.dumps({ 'name': 'Team Project Board', 'body': 'This is where you keep track of your Todo, Doing and Done tasks.' })
    response = requests.request('POST', url, headers=HEADERS,
                                data=payload, auth=(GITHUB_USER, GITHUB_PASSWORD))
    if response.status_code != 201:
        logging.error('Creation not successful.')
    else:
        logging.info('Creation successful.')
    return response.json()

if __name__ == '__main__':
    repo_name = 'example-product-team'
    response_as_json = add_project_to_repo(repo_name)
    print(json.dumps(response_as_json, indent=2))