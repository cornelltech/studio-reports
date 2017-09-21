import build_buildboard
import get_reports

import os.path
import unicodedata

# OUTPUT_PATH = "%s/%s" % (get_reports.OUTPUT_DIR, get_reports.OUTPUT_FILE)

# PWD = os.path.dirname(os.path.realpath(__file__))
# OUTPUT_FILE = os.path.join(PWD, build_buildboard.OUTPUT_DIR_NAME,
                            # build_buildboard.INDEX_FILE_NAME)

if __name__ == '__main__':
    build_buildboard.build_page_from_scratch()
    # print OUTPUT_FILE
    # with open(OUTPUT_FILE, 'w') as outfile:
    #     outfile.write(unicodedata.normalize('NFKD',
    #                 build_buildboard.build_page_from_scratch()).encode('ascii','ignore')


# if __name__ == '__main__':
#     print OUTPUT_PATH
#     with open(OUTPUT_PATH, 'w') as outfile:
#         outfile.write(unicodedata.normalize('NFKD',
#                     get_reports.create_index_page()).encode('ascii','ignore')
# )
