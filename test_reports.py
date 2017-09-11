import get_reports

if __name__ == '__main__':
    roster = [{'name': 'J McLoughlin', 'email': 'j@cornell.edu'},
            {'name': 'Khoa', 'email': 'khoa@cornell.edu'},
            {'name': 'Leland Rechis', 'email': 'leland@cornell.edu'}]

    team = get_reports.build_team(roster)
    for person in team:
        print person.name
        print person.email
