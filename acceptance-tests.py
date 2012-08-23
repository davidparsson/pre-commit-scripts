#!/usr/bin/python
"""Note: Currently depends on local data"""
import os
from svn_look_wrappers import CommitDetails, RepositoryDetails
from ordered_filename_pre_commit import check_filenames

REPO = "dummy-svn-server/repository"

if not os.path.isdir(REPO):
    raise AssertionError("Test SVN repository required!")

for i in range(40, 57):
    print "Revision %d" % i
    cd = CommitDetails(REPO, i, test_mode=True)
    rd = RepositoryDetails(REPO, i, test_mode=True)
    result = check_filenames(cd, rd)
#    look_command = "%s %s %s %s %s" % ("svnlook", "%s", REPO, "--revision", i)
#    result = check_filenames(look_command)
    print "Result: %d" % result
    if i in (45, 49, 52):
        assert result == 1
    elif i in (51,):
        assert result == 2
    else:
        assert result == 0
    print

print "Success!"
