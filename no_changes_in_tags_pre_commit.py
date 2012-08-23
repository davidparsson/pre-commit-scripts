#!/usr/bin/python
import sys
import re
from svn_look_wrappers import get_option_parser, build_wrappers

TAGS_PATH_PATTERN = "^[^/]+/tags/"

def fail_on_tag_changes(commit_details):
    for modified_file in commit_details.get_modified_files():
        if re.match(TAGS_PATH_PATTERN, modified_file):
            sys.stderr.write("Error: Modifying tagged files is not permitted!")
            return 1
    return 0

def main():
    usage = """Usage: %prog REPOS TXN

Runs pre-commit verification on a repository transaction, disallowing modification
of tagged files."""
    parser = get_option_parser(usage)
    try:
        commit_details, repository_details = build_wrappers(parser)
        return fail_on_tag_changes(commit_details)
    except:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
