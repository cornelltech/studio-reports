import argparse
import github
import handle_photos
import jinja2
import logging
import constants
import os
import shutil
import sys
import unicodedata
import xlsxwriter
import yaml

import pdb

from jinja2 import Environment, PackageLoader, select_autoescape

parser = argparse.ArgumentParser(description="Top-level flags.")
parser.add_argument('--local-data', action='store_true')
parser.add_argument('--log-to-stdout', action='store_true')
parser.add_argument('--log-file', action='store')

g = github.Github(constants.GITHUB_ACCESS_TOKEN)
env = Environment(loader=PackageLoader('buildboard', 'templates'),
                    autoescape=select_autoescape(['html', 'xml']))
# # # # # # #
CRIT_T = 'crit.html'
DIRECTORY_T = 'directory.html'
TEAM_CARD_T = 'team_card.html'
TEMPLATE_NAMES = [CRIT_T, DIRECTORY_T, TEAM_CARD_T]
TEMPLATES = {}
# # # # # # #

def get_yaml_path(team_name):
    return os.path.join(constants.PWD, constants.OUTPUT_DIR_NAME, constants.YAML_DIR_NAME, "%s.yaml" % team_name)

def get_yaml_doc(team_name):
    yaml_file = get_yaml_path(team_name)
    try:
        with open(yaml_file, 'r') as report_contents:
            doc = yaml.safe_load(report_contents)
            return doc
    except (yaml.parser.ParserError, yaml.scanner.ScannerError), e:
        logging.error('repo %s contains bad report.yaml file: %s' % (team_name, str(e)))
        return
    except IOError, e:
        logging.error('no file for repo %s' % team_name)

def process_yaml_file(team_name):
    doc = get_yaml_doc(team_name)
    if doc:
        try:
            team_photo = doc['team']['picture']
            doc['team']['picture'] = \
                handle_photos.get_photo_path_for_web(handle_photos.save_photo_path(constants.TEAM_PHOTOS_DIR_NAME,
                                                    team_name, team_photo))
        except (KeyError, TypeError), e:
            logging.error("can't store team photo for %s: %s" % (team_name, str(e)))

        try:
            company_logo = doc['company']['logo']
            doc['company']['logo'] = \
                handle_photos.get_photo_path_for_web(handle_photos.save_photo_path(constants.COMPANY_LOGOS_DIR_NAME,
                                                    team_name, company_logo))
        except (KeyError, TypeError), e:
            logging.error("can't store company logo for %s: %s" % (team_name, str(e)))

        for teammate in doc['team']['roster']:
            try:
                individual_photo = teammate['picture']
                sanified_email = teammate['email'].replace('@', '-')
                teammate['picture'] = \
                    handle_photos.get_photo_path_for_web(handle_photos.save_photo_path(constants.INDIVIDUAL_PHOTOS_DIR_NAME,
                                                        sanified_email, individual_photo))
                logging.info(teammate['picture'])
            except (KeyError, TypeError), e:
                teammate['picture'] = 'static/member.png'
                logging.error("can't store individual photo for member of team %s: %s" % (team_name, str(e)))

        # add in repo name
        doc['repo'] = team_name
    else:
        logging.error("missing yaml: %s" % team_name)
    return doc

def save_team_files(team_constants):
    for team_name in team_constants:
        logging.info('getting yaml file for %s...' % team_name)
        try:
            repo_name = "%s/%s" % (constants.ORG_NAME, team_name)
            repo = g.get_repo(repo_name)
            team_yaml_file = get_yaml_path(team_name)
            with open(team_yaml_file, 'w') as outfile:
                yaml_file = repo.get_file_contents(constants.YAML_FILE_NAME)
                outfile.write(yaml_file.decoded_content)
        except github.GithubException, e:
            logging.error("There's a problem with the yaml file for %s: %s" % (team_name, str(e)))

def save_team_photos(team_constants):
    for team_name in team_constants:
        logging.info('downloading photos for %s...' % team_name)
        doc = get_yaml_doc(team_name)
        if doc:
            try:
                team_photo = doc['team']['picture']
                team_photo_url = handle_photos.get_photo_url(team_name, team_photo)
                team_photo_path = handle_photos.save_photo_path(constants.TEAM_PHOTOS_DIR_NAME, team_name, team_photo)
                handle_photos.save_photo(team_photo_url, team_photo_path)
            except (KeyError, TypeError), e:
                logging.error('repo %s missing team photo: %s' % (team_name, str(e)))

            try:
                company_logo = doc['company']['logo']
                logo_url = handle_photos.get_photo_url(team_name, doc['company']['logo'])
                logo_path = handle_photos.save_photo_path(constants.COMPANY_LOGOS_DIR_NAME, team_name, company_logo)
                handle_photos.save_photo(logo_url, logo_path)
            except (KeyError, TypeError), e:
                logging.error('repo %s missing company logo: %s' % (team_name, str(e)))

            for teammate in doc['team']['roster']:
                try:
                    individual_photo = teammate['picture']
                    sanified_email = teammate['email'].replace('@', '-')
                    individual_photo_url = handle_photos.get_photo_url(team_name, individual_photo)
                    individual_photo_path = handle_photos.save_photo_path(constants.INDIVIDUAL_PHOTOS_DIR_NAME, sanified_email, individual_photo)
                    handle_photos.save_photo(individual_photo_url, individual_photo_path)
                except (KeyError, TypeError), e:
                    logging.error('repo %s missing individual photo: %s' % (team_name, str(e)))
        else:
            logging.error("missing yaml: %s" % team_name)

def get_teams(teams_file):
    with open(teams_file) as tf:
        team_metadata = [team.strip() for team in tf.readlines()]
    team_constants = [team.split("\t")[3] for team in team_metadata]
    return (team_constants, team_metadata)

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

def load_teams_data(team_constants):
    team_data = {}
    for team_name in team_constants:
        team_doc = process_yaml_file(team_name)
        team_data[team_name] = team_doc
    return team_data

def create_dir(dirname):
    if not os.path.exists(dirname):
        logging.info('creating new directory: %s' % dirname)
        os.makedirs(dirname)

def setup_output_directories(target_directory):
    output_dir = os.path.join(target_directory, constants.OUTPUT_DIR_NAME)
    create_dir(output_dir)

    # copy over static directory so that you can view files locally
    src = os.path.join(target_directory, constants.STATIC_DIR_NAME)
    dst = os.path.join(target_directory, constants.OUTPUT_DIR_NAME, constants.STATIC_DIR_NAME)
    if os.path.exists(dst):
		shutil.rmtree(dst)
    shutil.copytree(src, dst)

    output_dirs = [constants.YAML_DIR_NAME, constants.TEAM_PAGES_DIR_NAME,
                    constants.TEAM_PHOTOS_DIR_NAME, constants.COMPANY_LOGOS_DIR_NAME,
                    constants.INDIVIDUAL_PHOTOS_DIR_NAME]

    for directory in output_dirs:
        dir_path = os.path.join(output_dir, directory)
        create_dir(dir_path)

def create_crit_pages(crit_groups, teams):
    template = TEMPLATES[CRIT_T]
    if template:
        crit_A = template.render(group='Crit Group A',
                                rooms=crit_groups['A'],
                                teams=teams)

        crit_B = template.render(group='Crit Group B',
                                rooms=crit_groups['B'],
                                teams=teams)

        return (crit_A, crit_B)

def create_directory_page(teams):
    template = TEMPLATES[DIRECTORY_T]
    if template:
        return template.render(teams=teams)

def create_team_page(team):
    template = TEMPLATES[TEAM_CARD_T]
    if template:
        return template.render(team=team)

def output_crit_groups_xlsx(group, rooms, teams):
    workbook = xlsxwriter.Workbook(os.path.join(constants.PWD, constants.OUTPUT_DIR_NAME, constants.XLSX_FILE_NAME % group))
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

def build_crit_pages(teams, teams_metadata):
    def create_crit_group_pages(group, data):
        crit_file = os.path.join(constants.PWD, constants.OUTPUT_DIR_NAME, constants.CRIT_FILE_NAME % group)
        write_template_output_to_file(data, crit_file)
        output_crit_groups_xlsx(group, crit_groups[group], teams)

    crit_groups = get_crit_groups_ordered_by_room(teams_metadata)
    crit_groups_data = create_crit_pages(crit_groups, teams)
    if crit_groups:
        create_crit_group_pages('A', crit_groups_data[0])
        create_crit_group_pages('B', crit_groups_data[1])

def build_new_site_design(teams):
    directory = create_directory_page(teams)
    directory_file = os.path.join(constants.PWD, constants.OUTPUT_DIR_NAME, constants.DIRECTORY_PAGE_NAME)
    write_template_output_to_file(directory, directory_file)

    for team in teams:
        team_content = teams[team]
        team_page = create_team_page(team_content)
        team_page_file = os.path.join(constants.PWD, constants.OUTPUT_DIR_NAME, constants.TEAM_PAGES_DIR_NAME,
                                        "%s.html" % team)
        write_template_output_to_file(team_page, team_page_file)

def create_all_pages(local_data):
    setup_output_directories(constants.PWD)

    teams_file = os.path.join(constants.PWD, constants.TEAMS_FILE_NAME)
    (team_constants, teams_metadata) = get_teams(teams_file)

    if not local_data:
        save_team_files(team_constants)
        save_team_photos(team_constants)

    teams = load_teams_data(team_constants)
    build_new_site_design(teams)
    build_crit_pages(teams, teams_metadata)

def write_template_output_to_file(output, dst):
    if output:
        with open(dst, 'w') as outfile:
            outfile.write(unicodedata.normalize('NFKD', output).encode('ascii','ignore'))
        logging.info(outfile)
    else:
        logging.error('there is no content for file %s' % dst)

def config_logging(args):
    # config basics
    format_style = '%(asctime)s - %(levelname)s - %(message)s'
    if args.log_file:
        filename = args.log_file
    else:
        # use default name
        filename = 'output.log'
    logging.basicConfig(filename=filename, format=format_style, level=logging.INFO)

    # if you're also logging to stdout, set up additional handler
    if args.log_to_stdout:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(format_style)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def verify_templates():
    existing_templates = env.list_templates()
    for template_name in TEMPLATE_NAMES:
        if template_name not in existing_templates:
            logging.error('%s template is missing' % template_name)
            TEMPLATES[template_name] = None
        else:
            template = env.get_template(template_name)
            TEMPLATES[template_name] = template

if __name__ == '__main__':
    args = parser.parse_args()
    config_logging(args)
    verify_templates()
    create_all_pages(args.local_data)
