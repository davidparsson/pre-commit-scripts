#!/usr/bin/python
import sys
import re
from svn_look_wrappers import get_option_parser, build_wrappers

# Sub path to check. Final path will result in root_module/<MIGRATION_PATH>, 
# e.g. mymodule/trunk/db/migrations/
MIGRATION_PATH = "trunk/db/migrations/"
# Incoming filename pattern in MIGRATION_PATH to check.
# "[0-9].rb" would match mymodule/trunk/db/migrations/1.rb
FILE_PATTERN = "[0-9]+.*\.rb$"
# Ignores the pre-commit check if the keyword is included in the commit message
SKIP_KEYWORD = "skip-migration-check"

# Path to svnlook executable
SVNLOOK_COMMAND = "svnlook"

def check_filenames(commit_details, repository_details):
    if should_skip_check_for_commit(commit_details):
        return 0
    error = 0
    last_existing_file = None
    added_files = commit_details.get_added_files()
    for added_file in added_files:
        if should_check_file(added_file):
            if last_existing_file is None:
                last_existing_filename = get_last_existing_matching_file(added_files, repository_details)
            if last_existing_filename and last_existing_filename > get_filename(added_file):
                sys.stderr.write("Error: The added file \"%s\" must have a filename \
alphabetically after the existing \"%s\".\n" % (added_file, last_existing_filename))
                error += 1
    if error > 0:
        output_ignore_message()
    return error

def should_skip_check_for_commit(commit_details):
    return SKIP_KEYWORD in commit_details.get_commit_message().split()

def output_ignore_message():
    sys.stderr.write("If you want to commit this anyway, include \"%s\" in the commit message.\n" % SKIP_KEYWORD)

def should_check_file(file_path):
    return bool(re.match("^[^/]+/" + MIGRATION_PATH + FILE_PATTERN, file_path))

def get_file_dir(filename):
    return filename[:filename.rfind("/") + 1]

def get_filename(filename):
    return filename[filename.rfind("/") + 1:]

def get_last_existing_matching_file(added_files, repository_details):
    existing_matched_files = get_existing_matching_filenames(added_files, repository_details)
    existing_matched_files.sort()
    if existing_matched_files:
        return existing_matched_files[-1]
    return ""

def get_existing_matching_filenames(added_files, repository_details):
    root_dirs = repository_details.get_files_in(".")
    all_filenames = []
    for root_dir in root_dirs:
        for file_path in repository_details.get_files_in(root_dir + MIGRATION_PATH):
            if should_check_file(file_path) and file_path not in added_files:
                all_filenames.append(get_filename(file_path))
    return all_filenames
    

def main():
    usage = """Usage: %prog REPOS TXN

Runs pre-commit verification on a repository transaction, verifying that
matching files are added last, alphabetically."""
    parser = get_option_parser(usage)
    try:
        commit_details, repository_details = build_wrappers(parser)
        return check_filenames(commit_details, repository_details)
    except:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
