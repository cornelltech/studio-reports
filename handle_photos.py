import constants
import logging
import os
import requests
import shutil

from PIL import Image

def get_photo_url(repo_name, img_name):
    return 'https://raw.githubusercontent.com/%s/%s/master/%s' % (constants.ORG_NAME,
                                                                    repo_name,
                                                                    img_name)

def save_photo_path(output_dir_name, repo_name, img_name):
    if img_name:
        img_name = img_name.replace('/', '-')
    return os.path.join(constants.PWD, constants.OUTPUT_DIR_NAME, output_dir_name,
                        "%s-%s" % (repo_name, img_name))

def get_photo_path_for_web(photo_path):
    web_path = os.path.relpath(photo_path, os.path.join(constants.PWD,
                                constants.OUTPUT_DIR_NAME))
    return web_path

def save_photo(url, output_path, size):
    logging.info('saving %s' % os.path.basename(output_path))
    access_token = 'token %s' % constants.GITHUB_ACCESS_TOKEN
    response = requests.get(url, stream=True, headers={'Authorization': access_token})
    with Image.open(response.raw) as image:
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(output_path, image.format)
    return get_photo_path_for_web(output_path)
