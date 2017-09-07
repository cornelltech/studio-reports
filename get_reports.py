import github
import os

from os.path import join, dirname
from dotenv import load_dotenv

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

GITHUB_USER = os.environ.get('GITHUB_USER', None)
GITHUB_PASSWORD = os.environ.get('GITHUB_PASSWORD', None)

REPO_NAME = "cornelltech/studio-reports"
FILE_NAME = "README.md"

if __name__ == '__main__':
    g = github.Github(GITHUB_USER, GITHUB_PASSWORD)
    repo = g.get_repo(REPO_NAME)
    yaml_file = repo.get_file_contents(FILE_NAME)

    print yaml_file.decoded_content

    # out = open("out.txt", 'w')
    # out.write(yaml_file.decoded_content)
    # out.close()
