import argparse
import build_buildboard
import constants
import os.path
import shutil

PWD = os.path.dirname(os.path.realpath(__file__))

parser = build_buildboard.parser
parser.add_argument('dir', type=str, action='store',
					help='the directory to copy all the site files to')
args = parser.parse_args()

# official site: "/home/ubuntu/www/mysite"

def copy_to_site_directory(filename):
	src = os.path.join(PWD, constants.OUTPUT_DIR_NAME, filename)
	dst = os.path.join(args.dir, filename)
	shutil.copyfile(src, dst)
	return dst

# NB this strategy will not work if you start using conditional requests!
def copy_dir_to_site_directory(dirname):
	src = os.path.join(PWD, constants.OUTPUT_DIR_NAME, dirname)
	dst = os.path.join(args.dir, dirname)

	# remove old photos
	if os.path.exists(dst):
		shutil.rmtree(dst)

	# copy over new ones
	shutil.copytree(src, dst)

if __name__ == '__main__':
	build_buildboard.config_logging(args)
	build_buildboard.verify_templates()
	build_buildboard.create_dir(args.dir)
	build_buildboard.create_all_pages(args.local_data)

	copy_to_site_directory(constants.INDEX_FILE_NAME)
	copy_to_site_directory(constants.CRIT_FILE_NAME % 'A')
	copy_to_site_directory(constants.CRIT_FILE_NAME % 'B')
	copy_to_site_directory(constants.XLSX_FILE_NAME % 'A')
	copy_to_site_directory(constants.XLSX_FILE_NAME % 'B')

	# new site directory
	copy_to_site_directory(constants.DIRECTORY_PAGE_NAME)

	# new site individual team pages
	copy_dir_to_site_directory(constants.TEAM_PAGES_DIR_NAME)

	# static files
	copy_dir_to_site_directory(constants.STATIC_DIR_NAME)

	copy_dir_to_site_directory(constants.COMPANY_LOGOS_DIR_NAME)
	copy_dir_to_site_directory(constants.TEAM_PHOTOS_DIR_NAME)
