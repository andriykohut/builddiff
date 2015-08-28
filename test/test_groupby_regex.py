import re
try:
    import unittest2 as uninttest
except ImportError:
    import unittest

from builddiff.utils import group_by_regex


class GroupByRegexTest(unittest.TestCase):

    console_output = (
        'test1.py test_case1\n'
        'test1.py test_case2\n'
        'test2.py test_case1\n'
        'test3.py test_case1\n'
    )

    def test_parse_tests_should_have_named_groups(self):
        self.assertRaises(
            ValueError,
            lambda: group_by_regex(self.console_output, re.compile('^(\w+)\.py\s(\w+)$', re.M), 'keys', 'values')
        )
        self.assertRaises(
            ValueError,
            lambda: group_by_regex(self.console_output, re.compile('^(?P<abra>\w+)\.py\s(?P<cadabra>\w+)$', re.M),
                                   'keys', 'values')
        )

    def test_parse_tests_should_return_proper_dict(self):
        tests = group_by_regex(self.console_output, re.compile('^(?P<test_file>\w+)\.py\s(?P<test_case>\w+)$', re.M),
                               'test_file', 'test_case')
        self.assertEquals(len(tests['test1']), 2)
        self.assertEquals(len(tests['test2']), 1)
        self.assertEquals(len(tests['test3']), 1)
        self.assertTrue('test_case1' in tests['test1'])
        self.assertTrue('test_case2' in tests['test1'])

    def test_compare_test_failures(self):
        # TODO
        pass

if __name__ == "__main__":
    unittest.main()
