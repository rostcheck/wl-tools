# Compile summary stats on a markdown file
# Standard activity markdown format looks like this:
#
# Friday 11/5/21
# * [Area 1] Cadence - completed deck, reviewed w/ account team
# * [Area 2] [Workshop](https://quip.com/workshop12933) w/ team X
# * [Area 1] Wrote [architecture doc](https://quip.com/architecture192333)- Added details of component Z
# * [Area 2] Server migration - researched migration approaches, send instructions to Michael
#
# Note that the area field could also contain a category name like 'Admin' or 'Health'.
#
# Output will be a CSV like:
# Month, "Area 1", "Area 2", Admin, Recruiting
# Jan 2022, 50, 37, 8, 4
# Feb 2022, 68, 20, 10, 3
#
# You can supply a CSV mapping file using the --mapping argument to specify how to handle an area name.
# The mapping file specifies the result of the area field and what to map it to, or 'ignore' to ignore records
# with that entry. For example, this mapping file:
#
# Area,HandleAs
# travel,ignore
# health,ignore
# area X,OtherCX
# area Y,OtherCX
#
# ignores entries starting with [Travel] or [Health] and reports [area X] and [area Y] as "OtherCX"

import argparse
import re
import csv

month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
day_list = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def read_mapping(in_file):
    this_mapping = {}
    with open(in_file, 'r', newline='', encoding='utf-8-sig') as in_csvfile:
        reader = csv.reader(in_csvfile, dialect='excel')
        for row in reader:
            this_mapping[row[0].lower()] = row[1]
    return this_mapping


def get_year():
    return current_year


def contains_date(in_line):
    if re.search("\d+/\d+", in_line):
        if in_line[0:3].lower() in day_list:
            return True
    return False


def get_month_year(in_line):
    m = re.search("(\d+)/(\d+)/(\d+)", in_line)
    if not m:
        m = re.search("(\d+)/(\d+)", in_line)
        this_year = get_year()
    else:
        this_year = m.group(3)
    this_month = int(m.group(1))
    return [this_month, this_year]


def format_month_year(this_month, this_year):
    return "{0}/1/{1}".format(str(this_month), str(this_year))


def get_area(in_line):
    m = re.search("\* \[([\w\s\-]+)\]", in_line)
    if m:
        return m.group(1)
    else:
        return ""


parser = argparse.ArgumentParser(description='Compile stats on a markdown file in work tracker format')
parser.add_argument("file", help="file to parse")
parser.add_argument("--mapping", help="CSV file w/ header of mapping from area to another or 'ignore' to ignore that area")
args = parser.parse_args()
current_formatted_month_year = None
current_year = None
month_stats = {}
headers = ['date']
stats = []

if args.mapping:
    mapping = read_mapping(args.mapping)

with open(args.file) as fp:
    lines = fp.readlines()
    for line in lines:
        if len(line) <= 2:
            continue
        line_lower = line.lower()
        if contains_date(line_lower):
            [month, current_year] = get_month_year(line)
            formatted_month_year = format_month_year(month, current_year)
            if formatted_month_year != current_formatted_month_year:
                current_formatted_month_year = formatted_month_year
                if len(month_stats) > 0:
                    stats.append(month_stats)
                month_stats = {}
                month_stats['date'] = current_formatted_month_year
        else:
            area = get_area(line)
            if area == '':
                continue
            if mapping and area.lower() in mapping:
                area = mapping[area.lower()]
            if area == 'ignore':
                continue
            if area in month_stats:
                month_stats[area] = month_stats[area] + 1
            else:
                month_stats[area] = 1
            if area not in headers:
                headers.append(area)
    stats.append(month_stats)
    with open('stats.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers, dialect='excel')
        writer.writeheader()
        writer.writerows(stats)
