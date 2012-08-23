import subprocess
import os
import optparse

# Path to svnlook executable
SVNLOOK_COMMAND = "svnlook"

def get_option_parser(usage):
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-r", "--revision",
                      help="Test mode. Specify a revision instead of a transaction.",
                      action="store_true", default=False)
    return parser

def build_wrappers(option_parser):
    (options, (repos, transaction_or_revision)) = option_parser.parse_args()
    commit_details = CommitDetails(repos, transaction_or_revision, test_mode=options.revision)
    repository_details = RepositoryDetails(repos, transaction_or_revision, test_mode=options.revision)
    return commit_details, repository_details

def command_output(cmd):
  "Captures a command's standard output."
  dev_null = open(os.devnull, "w")
  result = []
  try:
    result = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=dev_null).communicate()[0].split("\n")
  finally:
    dev_null.close()
  return result

class SvnLookWrapper(object):
    def __init__(self, repository, transaction, test_mode=False):
        self._repository = repository
        self._transaction = transaction
        self._test_mode = test_mode
        pass
    
    def _svn_look(self, command, args=None):
        "Captures a command's standard output."
        look_option = "--revision" if self._test_mode else "--transaction"
        look_command = "%s %s %s %s %s" % (SVNLOOK_COMMAND, command, self._repository, look_option, self._transaction)
        if args:
            look_command = "%s %s" % (look_command, args)
        dev_null = open(os.devnull, "w")
        result = []
        try:
            if self._test_mode:
                print "[debug]$ %s" % look_command
            result = subprocess.Popen(look_command.split(), stdout=subprocess.PIPE, stderr=dev_null).communicate()[0].split("\n")
            if result and result[-1] == "":
                result.pop()
        finally:
            dev_null.close()
        return result

class CommitDetails(SvnLookWrapper):
    def get_added_files(self):
        files = []
        for change in self._get_changes():
            if change[0] == "A":
                files.append(change[1])
        return files
    
    def get_commit_message(self):
        return "\n".join(self._svn_look("log"))

    def _get_changes(self):
        changes = []
        for change in self._svn_look("changed"):
            status = change[:4].strip()
            file = change[4:]
            changes.append((status, file))
        return changes

class RepositoryDetails(SvnLookWrapper):
    def get_files_in(self, repository_directory):
        return self._svn_look("tree --full-paths --non-recursive", repository_directory)
