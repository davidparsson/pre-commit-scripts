#!/usr/bin/python
import sys
import re
from svn_look_wrappers import get_option_parser, build_wrappers

# Files matching this pattern will be treated as tagged
TAGS_PATH_PATTERN = "^[^/]+/tags/.+"
# Check will be skipped if commit message contains the SKIP_KEYWORD
SKIP_KEYWORD = "skip-tag-check"

def fail_on_tag_changes(commit_details):
    if SKIP_KEYWORD in commit_details.get_commit_message().split():
        return 0
    for modified_file in commit_details.get_files():
        if re.match(TAGS_PATH_PATTERN, modified_file):
            copied_and_deleted_files = commit_details.get_copied_files()
            copied_and_deleted_files.extend(commit_details.get_deleted_files())
            if modified_file not in copied_and_deleted_files:
                sys.stderr.write("Error: Modifying tagged files is not permitted!\n")
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
