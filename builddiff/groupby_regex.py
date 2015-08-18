from collections import namedtuple, defaultdict


SelDiff = namedtuple('SelDiff', ('failures_a', 'failures_b', 'cases_diff'))


def parse_tests(console_output, regex):
    """Parse build console output into dict (keys are test files, values are test cases)

    :console_output: string with console output of a build
    :regex: Compiled regexp for parsing builds, should contain following groups: number, test_file, test_case
    :returns: TODO

    """
    failures = defaultdict(list)
    required_groups = {'test_file', 'test_case'}
    if set(regex.groupindex.keys()) != required_groups:
        raise ValueError("regex should have following named groups: {}".format(','.join(required_groups)))
    for match in regex.finditer(console_output):
        failures[match.group('test_file')].append(match.group('test_case'))
    return failures


def compare_sel_failures(a, b):
    """Compare two dicts with sels failures.

    :a: dict a
    :b: dict b
    :returns: named tuple SelDiff(failures_a, failures_b, cases_diff)

    """
    a_only_files = set(a.keys()).difference(set(b.keys()))
    b_only_files = set(b.keys()).difference(set(a.keys()))
    common_files = set(a.keys()).intersection(set(b.keys()))
    a_only_failures = dict((k, a[k]) for k in a_only_files)
    b_only_failures = dict((k, b[k]) for k in b_only_files)
    cases_diff = {}
    for k in common_files:
        a_set = set(a[k])
        b_set = set(b[k])
        cases_diff[k] = {}
        a_diff = set(a_set).difference(set(b_set))
        b_diff = set(b_set).difference(set(a_set))
        if a_diff:
            cases_diff[k]['a'] = a_diff
        if b_diff:
            cases_diff[k]['b'] = b_diff
        common = a_set.intersection(b_set)
        if common:
            cases_diff[k]['common'] = common
    return SelDiff(
        failures_a=a_only_failures or None,
        failures_b=b_only_failures or None,
        cases_diff=cases_diff or None,
    )
