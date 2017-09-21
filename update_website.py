import build_buildboard
import get_reports

import os.path
import unicodedata

OUTPUT_PATH = "%s/%s" % (get_reports.OUTPUT_DIR, get_reports.OUTPUT_FILE)

def use_build_buildboard():
    build_buildboard.build_pages_from_scratch()
    build_buildboard.build_pages_from_existing()

if __name__ == '__main__':
    print OUTPUT_PATH
    with open(OUTPUT_PATH, 'w') as outfile:
        outfile.write(unicodedata.normalize('NFKD',
                    get_reports.create_index_page()).encode('ascii','ignore')
)
