import os.path
import build_buildboard 
import shutil

if __name__ == '__main__':
	build_buildboard.build_pages_from_scratch()
	pwd = os.path.dirname(os.path.realpath(__file__))
	src = os.path.join(pwd, build_buildboard.OUTPUT_DIR_NAME, build_buildboard.INDEX_FILE_NAME)
	shutil.copyfile(src, "/home/ubuntu/www/mysite/index.html")

	# remove old team photos
	teams_dst = os.path.join("/home/ubuntu/www/mysite", build_buildboard.TEAM_PHOTOS_DIR_NAME)
	if os.path.exists(teams_dst):
		shutil.rmtree(teams_dst)

	# copy over new ones
	team_photos = os.path.join(pwd, build_buildboard.OUTPUT_DIR_NAME, build_buildboard.TEAM_PHOTOS_DIR_NAME)
	shutil.copytree(team_photos, teams_dst)


	# remove old logos
	logos_dst = os.path.join("/home/ubuntu/www/mysite", build_buildboard.COMPANY_LOGOS_DIR_NAME)
	if os.path.exists(logos_dst):
		shutil.rmtree(logos_dst)

	# copy over new ones
	logos = os.path.join(pwd, build_buildboard.OUTPUT_DIR_NAME, build_buildboard.COMPANY_LOGOS_DIR_NAME)
	shutil.copytree(logos, logos_dst)
