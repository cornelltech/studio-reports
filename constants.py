import os

from dotenv import load_dotenv
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
CRIT_FILE_NAME = "crit-%s.html"
XLSX_FILE_NAME = "narratives-%s.xlsx"

# new site design names
DIRECTORY_PAGE_NAME = "index.html"
TEAM_PAGES_DIR_NAME = "team"
STATIC_DIR_NAME = "static"
