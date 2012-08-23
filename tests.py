#!/usr/bin/python
import unittest
from mockito import mock, when, any
from svn_look_wrappers import CommitDetails, RepositoryDetails
from ordered_filename_pre_commit import check_filenames, MIGRATION_PATH, SKIP_KEYWORD, \
        sys

class OrderedFilenameTest(unittest.TestCase):
    
    def setUp(self):
        self.commit_details = mock(CommitDetails)
        self.added_files = []
        when(self.commit_details).get_added_files().thenReturn(self.added_files)
        self.given_commit_message("")
        
        self.repository_details = mock(RepositoryDetails)
        when(self.repository_details).get_files_in(any()).thenReturn([])
        self.files_in_root = ["/"]
        when(self.repository_details).get_files_in(".").thenReturn(self.files_in_root)
        
        self.original_stderr = sys.stderr
        sys.stderr = mock()
        
    def tearDown(self):
        sys.stderr = self.original_stderr
    
    def test_does_not_fail_when_committing_first_file(self):
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.number_of_errors_are(0)

    def test_fails_when_committing_file_before_existing_in_same_module(self):
        self.given_existing_files("module/", MIGRATION_PATH, "1.rb")
        self.given_file_added_in_commit("module/" + MIGRATION_PATH + "0.rb")
        self.number_of_errors_are(1)

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
        
    def given_commit_message(self, message):
        when(self.commit_details).get_commit_message().thenReturn(message)

    def given_existing_files(self, module, path, *filenames):
        self.files_in_root.append(module)
        file_paths = [module + path + filename for filename in filenames]
        when(self.repository_details).get_files_in(module + path).thenReturn(file_paths)
        
    def given_file_added_in_commit(self, file_path):
        self.added_files.append(file_path)
    
    def number_of_errors_are(self, number_of_errors):
        self.assertEquals(number_of_errors,
                          check_filenames(self.commit_details, self.repository_details))

if __name__ == '__main__':
    unittest.main()