#!/usr/bin/python
"""Note: Currently depends on local data"""
import os
from svn_look_wrappers import CommitDetails, RepositoryDetails
from ordered_filename_pre_commit import check_filenames
from require_commit_message_pre_commit import check_commit_message
from no_changes_in_tags_pre_commit import fail_on_tag_changes


REPO = "dummy-svn-server/repository"

if not os.path.isdir(REPO):
    raise AssertionError("Test SVN repository required!")

def revisions(first, last):
    for i in range(first, last + 1):
        print "Revision %d" % i
        yield i
        print

def print_header(header):
    print header
    print ''.ljust(len(header), "=")
    print

print_header("Testing require_commit_message_pre_commit")

for i in revisions(20, 30):
    cd = CommitDetails(REPO, i, test_mode=True)
    result = check_commit_message(cd)
    print "Result: %d" % result
    if i in (22, 26, 29,):
        assert result == 1
    else:
        assert result == 0

print_header("Testing ordered_filename_pre_commit")

for i in revisions(40, 56):
    cd = CommitDetails(REPO, i, test_mode=True)
    rd = RepositoryDetails(REPO, i, test_mode=True)
    result = check_filenames(cd, rd)
    print "Result: %d" % result
    if i in (45, 49,):
        assert result == 1
    elif i in (51, 52,): # 52 is a rename, without order change. Could be allowed
        assert result == 2
    else:
        assert result == 0

for i in revisions(50, 66):
    cd = CommitDetails(REPO, i, test_mode=True)
    result = fail_on_tag_changes(cd)
    print "Result: %d" % result
    if i in (60, 65, 66,):
        assert result == 1
    else:
        assert result == 0

print "Success!"
