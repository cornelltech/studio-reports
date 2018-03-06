import constants

def get_teams(teams_file):
    with open(teams_file) as tf:
        team_metadata = [team.strip() for team in tf.readlines()]
    team_constants = [team.split("\t")[3] for team in team_metadata]
    return team_constants

BASE = 'http://buildboard-10044.cornelltech.io/team'

teams = get_teams(constants.TEAMS_FILE_NAME)
for team in teams:
    print '%s/%s.html' % (BASE, team)
