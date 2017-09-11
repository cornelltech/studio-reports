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

STUDENTS_FILE = 'github-student-usernames.txt'
OUTPUT_FILE = 'bad-github-usernames.txt'

def is_valid_user(g, username):
    try:
        g.get_user(username)
        return True
    except:
        return False

def verify_github_users():
    g = github.Github(GITHUB_ACCESS_TOKEN)
    out = open(OUTPUT_FILE, 'w')
    with open(STUDENTS_FILE) as rd:
        student_usernames = [username.strip() for username in rd.readlines()]
    for student in student_usernames:
        if student:
            if not is_valid_user(g, student):
                print student
                out.write(student + '\n')
    out.close()


if __name__ == '__main__':
    verify_github_users()
