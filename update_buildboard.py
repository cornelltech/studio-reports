import os.path
import build_buildboard
import shutil

SITE_HOME = "/home/ubuntu/www/mysite"
PWD = os.path.dirname(os.path.realpath(__file__))

def copy_to_site_directory(filename):
	src = os.path.join(PWD, build_buildboard.OUTPUT_DIR_NAME, filename)
	dst = os.path.join(SITE_HOME, filename)
	shutil.copyfile(src, dst)
	return dst

# NB this strategy will not work if you start using conditional requests!
def copy_dir_to_site_directory(dirname):
	src = os.path.join(PWD, build_buildboard.OUTPUT_DIR_NAME, dirname)
	dst = os.path.join(SITE_HOME, dirname)

	# remove old photos
	if os.path.exists(dst):
		shutil.rmtree(dst)

	# copy over new ones
	shutil.copytree(src, dst)

if __name__ == '__main__':
	build_buildboard.build_pages_from_scratch()
	build_buildboard.build_crit_pages()

	copy_to_site_directory(build_buildboard.INDEX_FILE_NAME)
	copy_to_site_directory(build_buildboard.CRIT_A_FILE_NAME)
	copy_to_site_directory(build_buildboard.CRIT_B_FILE_NAME)
	copy_to_site_directory(build_buildboard.XLSX_FILE_NAME % 'A')
	copy_to_site_directory(build_buildboard.XLSX_FILE_NAME % 'B')

	copy_dir_to_site_directory(build_buildboard.COMPANY_LOGOS_DIR_NAME)
	copy_dir_to_site_directory(build_buildboard.TEAM_PHOTOS_DIR_NAME)
