#!/usr/bin/python
import sys
import re
import subprocess
import optparse

# Sub path to check. Will become root_module/<MIGRATION_PATH>, e.g. module/trunk/db/migrations/
MIGRATION_PATH = "trunk/db/migrations/"
# Incoming file pattern to check.
FILE_PATTERN = "^.*/" + MIGRATION_PATH + "[0-9]+.*\.rb$"
# Ignore this pre-commit check if the keyword is included in commit message
SKIP_KEYWORD = "skip-migration-check"

# Path to svnlook executable
SVNLOOK_COMMAND = "svnlook"

def check_filenames(file_pattern, skip_keyword, look_command):
  if should_skip_check_for_commit(skip_keyword, look_command):
    return 0
  error = 0
  added_files = get_files_added_in_commit(look_command)
  last_existing_file = None
  for added_file in added_files:
    if should_check_file(file_pattern, added_file):
      if last_existing_file is None:
        last_existing_filename = get_last_existing_matching_file(added_files, file_pattern, look_command)
      if last_existing_filename and last_existing_filename > get_filename(added_file):
        sys.stderr.write("Error: The added file \"%s\" must have a filename \
alphabetically after the existing \"%s\".\n" % (added_file, last_existing_filename))
        error += 1
  if error > 0:
    output_ignore_message(skip_keyword)
  return error

def should_skip_check_for_commit(skip_keyword, look_command):
  return skip_keyword in " ".join(get_commit_message(look_command)).split(" ")

def output_ignore_message(skip_keyword):
  sys.stderr.write("If you want to commit this anyway, include \"%s\" in the commit message.\n" % skip_keyword)

def should_check_file(file_pattern, filename):
  return bool(re.match(file_pattern, filename))

def get_file_dir(filename):
  return filename[:filename.rfind("/") + 1]

def get_filename(filename):
  return filename[filename.rfind("/") + 1:]

def get_files_added_in_commit(look_command):
  def added(line):
    return line and line[0] == "A"
  def filename(line):
    return line[4:]
  return [filename(line) for line in get_changed_files(look_command) if added(line)]

def get_last_existing_matching_file(added_files, file_pattern, look_command):
  existing_matched_files = get_existing_matching_filenames(added_files, file_pattern, look_command)
  existing_matched_files.sort()
  if existing_matched_files:
    return existing_matched_files[-1]
  return ""

def get_existing_matching_filenames(added_files, file_pattern, look_command):
  root_dirs = get_files_in(".", look_command)
  all_filenames = []
  for root_dir in root_dirs:
    for file_path in get_files_in(root_dir + MIGRATION_PATH, look_command):
      if should_check_file(file_pattern, file_path) and file_path not in added_files:
        all_filenames.append(get_filename(file_path))
  return all_filenames

def get_files_in(svn_directory, look_command):
  return command_output("%s %s" % (look_command % "tree --full-paths --non-recursive", svn_directory))
  
def get_changed_files(look_command):
  return command_output(look_command % "changed")

def get_commit_message(look_command):
  return command_output(look_command % "log")

def command_output(cmd):
  "Captures a command's standard output."
  dev_null = open("/dev/null","w")
  result = []
  try:
    result = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=dev_null).communicate()[0].split("\n")
  finally:
    dev_null.close()
  return result

def main():
  usage = """Usage: %prog REPOS TXN

Runs pre-commit verification on a repository transaction, verifying that
matching files are added last, alphabetically."""
  parser = optparse.OptionParser(usage=usage)
  parser.add_option("-r", "--revision",
                    help="Test mode. Specify a revision instead of a transaction.",
                    action="store_true", default=False)

  try:
    (options, (repos, transaction_or_revision)) = parser.parse_args()
    look_option = ("--transaction", "--revision")[options.revision]
    look_command = "%s %s %s %s %s" % (SVNLOOK_COMMAND, "%s", repos, look_option, transaction_or_revision)
    return check_filenames(FILE_PATTERN, SKIP_KEYWORD, look_command)
  except:
    parser.print_help()
    return 1

if __name__ == "__main__":
  sys.exit(main())
