# Grep a markdown file for data
# Standard  activity markdown format looks like this:
#
# Friday 11/5/21
# * [Area 1] Cadence - completed deck, reviewed w/ account team
# * [Area 2] [Workshop](https://quip.com/workshop12933) w/ team X
# * [Area 1] Wrote [architecture doc](https://quip.com/architecture192333)- Added details of component Z
# * [Area 2] Server migration - researched migration approaches, send instructions to Michael
import argparse
import re


def contains_date(in_line):
    maybe_date = re.search("\d+/\d+", in_line)
    if maybe_date and "http" not in in_line:
        return True
    else:
        return False


parser = argparse.ArgumentParser(description='Grep through a markdown file in work tracker format')
parser.add_argument("file", help="file to parse")
parser.add_argument("--search-string", help="string to search for")
parser.add_argument("--area", help="filter for specified area")
parser.add_argument("--project", help="filter for project (work item) exactly")
parser.add_argument("--suppress-urls", help="remove urls strings from output", action="store_true")
parser.add_argument("--suppress-area", help="remove area string from output", action="store_true")
parser.add_argument("--show-dates", help="show dates on each output line", action="store_true")
args = parser.parse_args()
current_date = None
search_string = None

if args.area:
    cx_match_string = '* [' + args.area.lower()
if args.project:
    project_match_string = ' ' + args.project.lower() + ' -' # Ex. "EC2 classic migration" in above example
if args.search_string:
    search_string = args.search_string.lower()

with open(args.file) as fp:
    lines = fp.readlines()
    for line in lines:
        if len(line) <= 2:
            continue
        line_lower = line.lower()
        if contains_date(line_lower):
            current_date = line
        if args.area:
            if cx_match_string not in line_lower:
                continue
        if args.project:
            if project_match_string not in line_lower:
                continue
        if search_string:
            if search_string not in line_lower:
                continue
        if args.suppress_area and args.area:
            line = re.sub('\[' + args.area + '\]\s*','', line)
        if args.show_dates:
            line = '* ' + current_date.replace('\n', '') + ':' + line.replace('*', '')
        if args.suppress_urls:
            # Find markdown links, like: [thing](http://thing)
            m = re.findall(r"\[([\s\w\d\:]+)\]\(", line)
            if m:
                for mx in m:
                    str = '[' + mx + ']'
                    line = line.replace(str, mx) # Remove the brackets
                    line = re.sub('\(http([^)]+)\)', '', line) # remove the link (in parens)
            # Find email links, like <[rostdavi@amazon.com](mailto:rostdavi@amazon.com)>
            #m = re.findall(r"\<\[([\s\w\d\@\-\_]+)\]\(mailto:[\s\w\d\@\-\_]+\)\>", line)
            m = re.findall(r"mailto:([\w\d\@\-\_\.]+)\)", line)
            if m:
                for mx in m:
                    str = '<[' + mx + '](' + 'mailto:' + mx + ')>'
                    line = line.replace(str, mx) # Replace the link with just the email address
        print(line, end="")

