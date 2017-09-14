import get_reports

OUTPUT_PATH = get_reports.OUTPUT_DIR + get_reports.OUTPUT_FILE

if __name__ == '__main__':
    with open(OUTPUT_PATH, 'w') as outfile:
        outfile.write(get_reports.create_index_page())
