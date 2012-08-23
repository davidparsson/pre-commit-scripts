#!/usr/bin/python
import sys
from svn_look_wrappers import get_option_parser, build_wrappers

REQUIRED_COMMIT_MESSAGE_LENGTH = 3

def check_commit_message(commit_details):
    if len(commit_details.get_commit_message()) < REQUIRED_COMMIT_MESSAGE_LENGTH:
        sys.stderr.write("Error: Please enter a descriptive commit message!\n")
        return 1
    return 0

def main():
    usage = """Usage: %prog REPOS TXN

Runs pre-commit verification on a repository transaction, verifying that
the commit message is descriptive."""
    parser = get_option_parser(usage)
    try:
        commit_details, repository_details = build_wrappers(parser)
        return check_commit_message(commit_details)
    except:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
