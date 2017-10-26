import argparse
import os.path
import build_buildboard
import shutil

PWD = os.path.dirname(os.path.realpath(__file__))

parser = build_buildboard.parser
parser.add_argument('dir', type=str, action='store',
					help='the directory to copy all the site files to')
args = parser.parse_args()

def copy_to_site_directory(filename):
	src = os.path.join(PWD, build_buildboard.OUTPUT_DIR_NAME, filename)
	dst = os.path.join(args.dir, filename)
	shutil.copyfile(src, dst)
	return dst

# NB this strategy will not work if you start using conditional requests!
def copy_dir_to_site_directory(dirname):
	src = os.path.join(PWD, build_buildboard.OUTPUT_DIR_NAME, dirname)
	dst = os.path.join(args.dir, dirname)

	# remove old photos
	if os.path.exists(dst):
		shutil.rmtree(dst)

	# copy over new ones
	shutil.copytree(src, dst)

if __name__ == '__main__':
	build_buildboard.config_logging(args)
	build_buildboard.create_dir(args.dir)
	build_buildboard.create_all_pages(args.local)

	copy_to_site_directory(build_buildboard.INDEX_FILE_NAME)
	copy_to_site_directory(build_buildboard.CRIT_FILE_NAME % 'A')
	copy_to_site_directory(build_buildboard.CRIT_FILE_NAME % 'B')
	copy_to_site_directory(build_buildboard.XLSX_FILE_NAME % 'A')
	copy_to_site_directory(build_buildboard.XLSX_FILE_NAME % 'B')

	# new site directory
	copy_to_site_directory(build_buildboard.DIRECTORY_PAGE_NAME)

	# new site individual team pages
	copy_dir_to_site_directory(build_buildboard.TEAM_PAGES_DIR_NAME)

	# static files
	copy_dir_to_site_directory(build_buildboard.STATIC_DIR_NAME)

	copy_dir_to_site_directory(build_buildboard.COMPANY_LOGOS_DIR_NAME)
	copy_dir_to_site_directory(build_buildboard.TEAM_PHOTOS_DIR_NAME)
