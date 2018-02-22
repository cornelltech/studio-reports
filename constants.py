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
INDIVIDUAL_PHOTOS_DIR_NAME = "individual_pictures"
# TODO: deprecate in favor of futuristic version
# CRIT_FILE_NAME = "crit-%s.html"
# XLSX_FILE_NAME = "narratives-%s.xlsx"

# new site design names
DIRECTORY_PAGE_NAME = "index.html"
TEAM_PAGES_DIR_NAME = "team"
STATIC_DIR_NAME = "static"

# directories that need to be created for output
OUTPUT_DIRS = [TEAM_PAGES_DIR_NAME, TEAM_PHOTOS_DIR_NAME,
                COMPANY_LOGOS_DIR_NAME,
                INDIVIDUAL_PHOTOS_DIR_NAME]

# for generating the site
LOCAL_OUTPUT_DIRS = [YAML_DIR_NAME] + OUTPUT_DIRS

# content that will be served from the site
SITE_OUTPUT_DIRS = [STATIC_DIR_NAME] + OUTPUT_DIRS

# save photo sizes
PHOTO_SIZES = {}
PHOTO_SIZES[INDIVIDUAL_PHOTOS_DIR_NAME] = (300,300)
PHOTO_SIZES[TEAM_PHOTOS_DIR_NAME] = (800,800)
PHOTO_SIZES[COMPANY_LOGOS_DIR_NAME] = (400,400)
