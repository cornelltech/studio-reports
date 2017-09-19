import get_reports
import unicodedata

OUTPUT_PATH = "%s/%s" % (get_reports.OUTPUT_DIR, get_reports.OUTPUT_FILE)

if __name__ == '__main__':
    print OUTPUT_PATH
    with open(OUTPUT_PATH, 'w') as outfile:
        outfile.write(unicodedata.normalize('NFKD',
                    get_reports.create_index_page()).encode('ascii','ignore')
)
