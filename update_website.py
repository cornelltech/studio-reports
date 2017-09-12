import get_reports

# OUTPUT_PATH = "/home/ubuntu/www/mysite/index.html"
OUTPUT_PATH = "index.html"

if __name__ == '__main__':
    with open(OUTPUT_PATH, 'w') as outfile:
        outfile.write(get_reports.create_index_page())
