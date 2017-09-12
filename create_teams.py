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

STUDENTS_TO_TEAMS = "teams2students.txt"


TEAMS_FILE = "team-repos"
ORG_NAME = "ct-product-challenge-2017"
STUDIO_TEAM_ID = 2477099

def create_student_team(g, team_name, student_usernames):
    team = g.get_organization(ORG_NAME).create_team(team_name)
    for student in student_usernames:
        team.add_to_members(g.get_user(student))
    return team
    # try / catch for typos --> print to logs

def create_team_repo(g, repo_name, student_team):
    repo = g.get_organization(ORG_NAME).create_repo(repo_name,
        team_id=student_team, private=True, auto_init=True)
    studio_team = g.get_organization(ORG_NAME).get_team(id=STUDIO_TEAM_ID)
    studio_team.add_to_repos(g.get_organization(ORG_NAME).get_repo(repo_name))
    return repo

def create_teams_map():
    students = {}
    with open(STUDENTS_TO_TEAMS) as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            line = line.split('\t')
            if len(line) == 2:
                students[line[1]] = line[0]
            elif line[0]:
                print line, 'team member missing github username'
    teams = {}
    for student in students.keys():
        team = students[student]
        if team in teams:
            teams[team].append(student)
        else:
            teams[team] = [student]
    return teams

if __name__ == '__main__':
    # g = github.Github(GITHUB_ACCESS_TOKEN)
    # students = ['elanid', 'sahuguet']
    # t = create_student_team(g, 'example-product-team', students)
    # repo = create_team_repo(g, 'example-product-team', t)

    teams = create_teams_map()
    for team in teams.keys():
        print team
