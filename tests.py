#!/usr/bin/python
import unittest
import sys
from mockito import mock, when, verify, any, times
from svn_look_wrappers import CommitDetails, RepositoryDetails
from ordered_filename_pre_commit import check_filenames, MIGRATION_PATH, SKIP_KEYWORD
from require_commit_message_pre_commit import check_commit_message
from no_changes_in_tags_pre_commit import fail_on_tag_changes


class SvnLookWrapperTestCase(unittest.TestCase):

    def setUp(self):
        self.commit_details = mock(CommitDetails)
        self.added_files = []
        when(self.commit_details).get_added_files().thenReturn(self.added_files)
        self.modified_files = []
        when(self.commit_details).get_modified_files().thenReturn(self.modified_files)
        self.given_commit_message("")

        self.repository_details = mock(RepositoryDetails)
        when(self.repository_details).get_files_in(any()).thenReturn([])
        self.files_in_root = ["/"]
        when(self.repository_details).get_files_in(".").thenReturn(self.files_in_root)

        self.original_stderr = sys.stderr
        self.stderr = mock()
        sys.stderr = self.stderr

    def tearDown(self):
        sys.stderr = self.original_stderr

    def given_commit_message(self, message):
        when(self.commit_details).get_commit_message().thenReturn(message)

    def given_existing_files(self, module, path, *filenames):
        self.files_in_root.append(module)
        file_paths = [module + path + filename for filename in filenames]
        when(self.repository_details).get_files_in(module + path).thenReturn(file_paths)

    def given_file_added_in_commit(self, file_path):
        self.added_files.append(file_path)

    def given_file_modified_in_commit(self, file_path):
        self.modified_files.append(file_path)


class NoChangesInTagsTest(SvnLookWrapperTestCase):

    def test_does_not_fail_when_committing_to_trunk(self):
        self.given_file_modified_in_commit("module/trunk/file.txt")
        self.then_error_code_is(0)

    def test_fails_when_committing_to_a_tag(self):
        self.given_file_modified_in_commit("module/tags/tagname/file.txt")
        self.then_error_code_is(1)

    def test_prints_error_message_when_committing_to_tag(self):
        self.given_file_modified_in_commit("module/tags/tagname/file.txt")
        fail_on_tag_changes(self.commit_details)
        verify(self.stderr).write("Error: Committing modified files to tags is not permitted!")

    def then_error_code_is(self, error_code):
        self.assertEqual(error_code,
                         fail_on_tag_changes(self.commit_details))


class RequireCommitMessageTest(SvnLookWrapperTestCase):

    def test_fails_when_commit_message_missing(self):
        self.given_commit_message("")
        self.then_error_code_is(1)

    def test_fails_when_commit_message_too_short(self):
        self.given_commit_message("..")
        self.then_error_code_is(1)

    def test_does_not_fail_when_commit_message_long_enough(self):
        self.given_commit_message("...")
        self.then_error_code_is(0)

    def test_prints_error_message_when_message_to_short(self):
        self.given_commit_message("..")
        check_commit_message(self.commit_details)
        verify(self.stderr).write("Error: Please enter a descriptive commit message!")

    def then_error_code_is(self, number_of_errors):
        self.assertEquals(number_of_errors,
                          check_commit_message(self.commit_details))


class OrderedFilenameTest(SvnLookWrapperTestCase):

    def test_does_not_fail_when_committing_first_file(self):
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.number_of_errors_are(0)

    def test_fails_when_committing_file_before_existing_in_same_module(self):
        self.given_existing_files("module/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.number_of_errors_are(1)

    def test_does_not_print_to_stderr_when_successful(self):
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        check_filenames(self.commit_details, self.repository_details)
        verify(sys.stderr, times(0)).write(any())

    def test_prints_to_stderr_when_failing(self):
        self.given_existing_files("module/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        check_filenames(self.commit_details, self.repository_details)
        verify(sys.stderr, times(2)).write(any())

    def test_does_not_fail_when_commit_message_contains_skip_keyword(self):
        self.given_existing_files("module/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.given_commit_message(SKIP_KEYWORD)
        self.number_of_errors_are(0)

    def test_fails_when_committing_file_before_existing_in_other_module(self):
        self.given_existing_files("module1/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module2/" + MIGRATION_PATH + "0.rb")
        self.number_of_errors_are(1)

    def test_does_not_fail_when_committing_file_not_matching_pattern(self):
        self.given_existing_files("module/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "NO_MIGRATION")
        self.number_of_errors_are(0)

    def test_does_not_fail_when_committing_file_outside_path(self):
        self.given_existing_files("module/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module/" + "any_folder/" + "0.rb")
        self.number_of_errors_are(0)

    def test_does_not_fail_when_existing_file_outside_path(self):
        self.given_existing_files("module/", "any_folder/", "1.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.number_of_errors_are(0)

    def test_counts_errors(self):
        self.given_existing_files("module/", MIGRATION_PATH, "10.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "1.rb")
        self.number_of_errors_are(2)

    def number_of_errors_are(self, number_of_errors):
        self.assertEquals(number_of_errors,
                          check_filenames(self.commit_details, self.repository_details))


if __name__ == '__main__':
    unittest.main()