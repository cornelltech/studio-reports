import argparse
import github
import handle_photos
import jinja2
import os
import requests
import shutil
import unicodedata
import xlsxwriter
import yaml

import pdb

from jinja2 import Environment, PackageLoader, select_autoescape
from names import *

parser = argparse.ArgumentParser(description="Top-level flags.")
parser.add_argument('--local', action='store_true')

env = Environment(loader=PackageLoader('buildboard', 'templates'),
                    autoescape=select_autoescape(['html', 'xml']))

def get_yaml_path(team_name):
    return os.path.join(PWD, OUTPUT_DIR_NAME, YAML_DIR_NAME, "%s.yaml" % team_name)

def get_yaml_doc(team_name):
    yaml_file = get_yaml_path(team_name)
    try:
        with open(yaml_file, 'r') as report_contents:
            doc = yaml.safe_load(report_contents)
            return doc
    except (yaml.parser.ParserError, yaml.scanner.ScannerError), e:
        print 'repo', team_name, 'contains bad report.yaml file', str(e)
        return

def process_yaml_file(yaml_file):
    repo_name = os.path.splitext(os.path.basename(yaml_file))[0]
    doc = get_yaml_doc(yaml_file)
    if doc:
        try:
            team_photo = doc['team']['picture']
            doc['team']['picture'] = \
                handle_photos.get_photo_path_for_web(handle_photos.save_photo_path(TEAM_PHOTOS_DIR_NAME,
                                                    repo_name, team_photo))
        except (KeyError, TypeError), e:
            print 'can\'t store team photo for', repo_name, str(e)

        try:
            company_logo = doc['company']['logo']
            doc['company']['logo'] = \
                handle_photos.get_photo_path_for_web(handle_photos.save_photo_path(COMPANY_LOGOS_DIR_NAME,
                                                    repo_name, company_logo))
        except (KeyError, TypeError), e:
            print 'can\'t store company logo for', repo_name, str(e)

        # add in repo name
        doc['repo'] = repo_name
    return doc

def save_team_files(team_names):
    g = github.Github(GITHUB_ACCESS_TOKEN)
    for team in team_names:
        print 'getting yaml file for %s...' % team
        try:
            repo_name = "%s/%s" % (ORG_NAME, team)
            repo = g.get_repo(repo_name)
            team_yaml_file = get_yaml_path(team)
            with open(team_yaml_file, 'w') as outfile:
                yaml_file = repo.get_file_contents(YAML_FILE_NAME)
                outfile.write(yaml_file.decoded_content)
        except github.GithubException, e:
            print "There's a problem with that repository's yaml file:", str(e)

def save_team_photos(team_names):
    for team in team_names:
        print 'downloading photos for %s...' % team
        doc = get_yaml_doc(team)
        if doc:
            try:
                team_photo = doc['team']['picture']
                team_photo_url = handle_photos.get_photo_url(team, team_photo)
                team_photo_path = handle_photos.save_photo_path(TEAM_PHOTOS_DIR_NAME, team, team_photo)
                handle_photos.save_photo(team_photo_url, team_photo_path)
            except (KeyError, TypeError), e:
                print 'repo', team, 'missing team photo:', str(e)
            try:
                company_logo = doc['company']['logo']
                logo_url = handle_photos.get_photo_url(team, doc['company']['logo'])
                logo_path = handle_photos.save_photo_path(COMPANY_LOGOS_DIR_NAME, team, company_logo)
                handle_photos.save_photo(logo_url, logo_path)
            except (KeyError, TypeError), e:
                print 'repo', team, 'missing company logo:', str(e)

def get_teams(teams_file):
    with open(teams_file) as tf:
        team_metadata = [team.strip() for team in tf.readlines()]
    team_names = [team.split("\t")[3] for team in team_metadata]
    return (team_names, team_metadata)

def get_sections(teams_metadata):
    sections = {}
    for section in SECTIONS:
        sections[section] = []
    for line in teams_metadata:
        team = line.split('\t')
        section = team[0]
        sections[section].append(team[3])
    return sections

def get_crit_groups_ordered_by_room(teams_metadata):
    crit_rooms = {'A': {}, 'B' : {}}
    for team_line in teams_metadata:
        team = team_line.split("\t")

        team_name = team[3]
        team_crit_group = team[4]
        team_room = team[5]

        crit_group = crit_rooms[team_crit_group]
        if team_room not in crit_group:
            crit_group[team_room] = [team_name]
        else:
            crit_group[team_room].append(team_name)
    return crit_rooms

def load_teams_data(team_names):
    team_data = {}
    for team_name in team_names:
        team_doc = process_yaml_file(team_name)
        team_data[team_name] = team_doc
    return team_data

def create_dir(dirname):
    if not os.path.exists(dirname):
        print 'creating new directory:', dirname
        os.makedirs(dirname)

def setup_output_directories(target_directory):
    output_dir = os.path.join(target_directory, OUTPUT_DIR_NAME)
    create_dir(output_dir)

    # copy over static directory so that you can view files locally
    src = os.path.join(PWD, 'static')
    dst = os.path.join(PWD, OUTPUT_DIR_NAME, 'static')
    if os.path.exists(dst):
		shutil.rmtree(dst)
    shutil.copytree(src, dst)

    yaml_dir = os.path.join(output_dir, YAML_DIR_NAME)
    create_dir(yaml_dir)

    team_photos_dir = os.path.join(output_dir, TEAM_PHOTOS_DIR_NAME)
    create_dir(team_photos_dir)

    company_logos_dir = os.path.join(output_dir, COMPANY_LOGOS_DIR_NAME)
    create_dir(company_logos_dir)

    team_pages_dir = os.path.join(output_dir, TEAM_PAGES_DIR_NAME)
    create_dir(team_pages_dir)

    return (output_dir, yaml_dir, team_photos_dir, company_logos_dir, team_pages_dir)

def create_index_page(sections):
    template = env.get_template('buildboard.html')
    return template.render(sections=sections)

def create_crit_pages(crit_groups, teams):
    template = env.get_template('crit.html')
    crit_A = template.render(group='Crit Group A',
                            rooms=crit_groups['A'],
                            teams=teams)

    crit_B = template.render(group='Crit Group B',
                            rooms=crit_groups['B'],
                            teams=teams)

    return (crit_A, crit_B)

def create_directory_page(teams):
    template = env.get_template('directory.html')
    return template.render(teams=teams)

def create_team_page(team):
    template = env.get_template('team-card.html')
    return template.render(team=team)

def output_crit_groups_xlsx(group, rooms, teams):
    workbook = xlsxwriter.Workbook(os.path.join(PWD, OUTPUT_DIR_NAME, XLSX_FILE_NAME % group))
    worksheet = workbook.add_worksheet()
    columns = {'Team Name': 'A%d', 'Narrative': 'B%d', 'Room': 'C%d'}
    row = 1
    for col in columns:
        worksheet.write(columns[col] % row, col)
    row += 1
    for room in rooms:
        for team in rooms[room]:
            worksheet.write(columns['Team Name'] % row, team)
            team_data = teams[team]
            if team_data:
                worksheet.write(columns['Narrative'] % row, team_data['product_narrative'])
                worksheet.write(columns['Room'] % row, room)
                row += 1
    workbook.close()

def build_pages_from_scratch():
    # setup output directories
    setup_output_directories(PWD)

    # extract teams data
    teams_file = os.path.join(PWD, TEAMS_FILE_NAME)
    (team_names, team_metadata) = get_teams(teams_file)

    # save teams yaml
    save_team_files(team_names)
    save_team_photos(team_names)

    # create index page
    sections = get_sections(team_metadata)
    for section in sections:
        teams = sections[section]
        team_docs = []
        for team in teams:
            team_doc = process_yaml_file(team)
            if team_doc:
                team_docs.append(team_doc)
        sections[section] = team_docs
    index = create_index_page(sections)

    output_index = os.path.join(PWD, OUTPUT_DIR_NAME, INDEX_FILE_NAME)
    write_template_output_to_file(index, output_index)

def build_index_page(teams_metadata):
    sections = get_sections(teams_metadata)
    for section in sections:
        teams = sections[section]
        team_docs = []
        for team in teams:
            team_doc = process_yaml_file(team)
            if team_doc:
                team_docs.append(team_doc)
        sections[section] = team_docs

    index = create_index_page(sections)
    output_index = os.path.join(PWD, OUTPUT_DIR_NAME, INDEX_FILE_NAME)
    write_template_output_to_file(index, output_index)

# TODO: atm only works if you've built the index pages
def build_crit_pages(teams, teams_metadata):
    crit_groups = get_crit_groups_ordered_by_room(teams_metadata)
    (crit_A, crit_B) = create_crit_pages(crit_groups, teams)

    crit_a_file = os.path.join(PWD, OUTPUT_DIR_NAME, CRIT_FILE_NAME % 'A')
    write_template_output_to_file(crit_A, crit_a_file)

    crit_b_file = os.path.join(PWD, OUTPUT_DIR_NAME, CRIT_FILE_NAME % 'B')
    write_template_output_to_file(crit_B, crit_b_file)

    # excel formatted files
    output_crit_groups_xlsx('A', crit_groups['A'], teams)
    output_crit_groups_xlsx('B', crit_groups['B'], teams)

def build_new_site_design(teams):
    directory = create_directory_page(teams)
    directory_file = os.path.join(PWD, OUTPUT_DIR_NAME, DIRECTORY_PAGE_NAME)
    write_template_output_to_file(directory, directory_file)

    for team in teams:
        team_content = teams[team]
        team_page = create_team_page(team_content)
        team_page_file = os.path.join(PWD, OUTPUT_DIR_NAME, TEAM_PAGES_DIR_NAME,
                                        "%s.html" % team)
        write_template_output_to_file(team_page, team_page_file)

def create_all_pages(local):
    setup_output_directories(PWD)

    teams_file = os.path.join(PWD, TEAMS_FILE_NAME)
    (team_names, teams_metadata) = get_teams(teams_file)

    if not local:
        save_team_files(team_names)
        save_team_photos(team_names)

    teams = load_teams_data(team_names)
    build_new_site_design(teams)
    build_crit_pages(teams, teams_metadata)
    build_index_page(teams_metadata)

def write_template_output_to_file(output, dst):
    with open(dst, 'w') as outfile:
        outfile.write(unicodedata.normalize('NFKD', output).encode('ascii','ignore'))
    print outfile

if __name__ == '__main__':
    args = parser.parse_args()
    create_all_pages(args.local)
