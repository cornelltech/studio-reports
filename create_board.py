import requests
import logging
import json
import csv
import time

"""
    Python script to add Trello-like projects to student repositories.
"""

logging.basicConfig(level=logging.DEBUG)

import os
import sys
from dotenv import load_dotenv
from os.path import join, dirname
import emoji

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

TEAM_BOARD = 'Product Challenge Studio Board'
BOARD_BLURB = 'This is where you keep track of your Todo, Doing and Done tasks.'
CARD_MSG = emoji.emojize("Update your report.yaml file\r\n:construction:") #.encode('ascii',errors='ignore')

def add_project_to_repo(repo_name):
    repo = {'owner': 'ct-product-challenge-2017', 'repo': repo_name}
    url = GITHUB_API + '/repos/%(owner)s/%(repo)s/projects' % repo
    logging.info('Creating new board for %s' % url)

    payload = json.dumps({ 'name': TEAM_BOARD, 'body': BOARD_BLURB })
    response = requests.request('POST', url, headers=HEADERS,
                                data=payload, auth=(GITHUB_USER, GITHUB_PASSWORD))
    return (response.status_code, response.json())


def add_card_to_column(column_id):
    url = GITHUB_API + '/projects/columns/%(column_id)d/cards' % {'column_id': column_id}
    logging.info('Creating new card for %s' % url)
    payload = json.dumps({ 'note': CARD_MSG})
    response = requests.request('POST', url, headers=HEADERS,
                                data=payload, auth=(GITHUB_USER, GITHUB_PASSWORD))
    print response.status_code 
    if response.status_code not in [200, 201]:
        logging.error('Card creation failed.')
    else:
        logging.info('Card created successfully.') 

def add_columns_to_project(project_id):
    url = GITHUB_API + '/projects/%(project_id)d/columns' % {'project_id': project_id}
    logging.info('Creating new column for %s' % url)
    for col in ['Todo', 'Doing', 'Done']:
        payload = json.dumps({ 'name': col})
        response = requests.request('POST', url, headers=HEADERS,
                                data=payload, auth=(GITHUB_USER, GITHUB_PASSWORD))
        if response.status_code != 201:
            logging.error('Column creation not successful.')
        else:
            logging.info('Column creation successful.')
            column_id = int(response.json()['id'])
            if col == 'Todo':
                add_card_to_column(column_id)

if __name__ == '__main__':
    with open('teams', 'r') as team_file:
        reader = csv.reader(team_file, delimiter='\t')
        for row in reader:
            time.sleep(0.5)
            (section, company, challenge, repo_name) = row
            logging.info('Processing %s ...' % repo_name)
            (code, response_as_json) = add_project_to_repo(repo_name)
            if code != 201:
                logging.error('Project creation FAILED for %s.' % repo_name)
                continue
            logging.info('Project creation successful for %s.' % repo_name)
            project_id = int(response_as_json['id'])
            add_columns_to_project(project_id) 