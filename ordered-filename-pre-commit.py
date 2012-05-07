#!/usr/bin/python
import sys
import subprocess
import re
from optparse import OptionParser

SVNLOOK_COMMAND = "svnlook"

def check_filenames(file_pattern, skip_keyword, look_command):
  if should_skip_check_for_commit(skip_keyword, look_command):
    return 0
  error = 0
  added_filenames = get_files_added_in_commit(look_command)
  for added_filename in added_filenames:
    if should_check_file(file_pattern, added_filename):
      last_existing_file = get_last_existing_file_after(added_filename, added_filenames, file_pattern, look_command)
      if last_existing_file:
        sys.stderr.write("Error: The added file \"%s\" must have a filename \
alphabetically after the existing \"%s\".\n" % (added_filename, last_existing_file))
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
  return filename[0:filename.rfind("/") + 1]

def get_files_added_in_commit(look_command):
  def added(line):
    return line and line[0] == "A"
  def filename(line):
    return line[4:]
  return [filename(line) for line in get_changed_files(look_command) if added(line)]

def get_last_existing_file_after(filename, added_filenames, file_pattern, look_command):
  existing_files = get_existing_files_in(get_file_dir(filename), added_filenames, look_command)
  existing_matched_files = [f for f in existing_files if should_check_file(file_pattern, f)]
  existing_matched_files.sort()
  if existing_matched_files and filename < existing_matched_files[-1]:
    return existing_matched_files[-1]
  return None

def get_existing_files_in(path, added_filenames, look_command):
  all_files = command_output("%s %s" % (look_command % "tree --full-paths", path))
  return [filename for filename in all_files if filename not in added_filenames]
  
def get_changed_files(look_command):
  return command_output(look_command % "changed")

def get_commit_message(look_command):
  return command_output(look_command % "log")

def command_output(cmd):
  "Captures a command's standard output."
  return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).communicate()[0].split("\n")

def main():
  usage = """Usage: %prog REPOS TXN FILE_PATTERN SKIP_KEYWORD

Run pre-commit verification on a repository transaction."""
  parser = OptionParser(usage=usage)
  parser.add_option("-r", "--revision",
                    help="Test mode. Specify a revision instead of a transaction.",
                    action="store_true", default=False)

  (options, (repos, transaction_or_revision, file_pattern, skip_keyword)) = parser.parse_args()
  look_option = ("--transaction", "--revision")[options.revision]
  look_command = "%s %s %s %s %s" % (SVNLOOK_COMMAND, "%s", repos, look_option, transaction_or_revision)
  try:
    return check_filenames(file_pattern, skip_keyword, look_command)
  except:
    parser.print_help()
    return 1

if __name__ == "__main__":
  sys.exit(main())