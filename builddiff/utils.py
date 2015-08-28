from collections import OrderedDict, namedtuple
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from colorama import Fore


def format_diff(diff, color=True):
    """Pretty format the diff.

    :diff: namedtuple dictdiff(a_only, b_only, diff)
    :color: colorize the diff
    :returns: StringIO with formatted diff

    """
    result = StringIO()
    result.write("A-only\n{}\n".format('-' * 50))
    if color:
        result.write(Fore.GREEN)
    for key, values in diff.a_only.items():
        result.write("+ {}\n".format(key))
        for value in values:
            result.write("+ \t{}\n".format(value))
    if color:
        result.write(Fore.RESET)
    result.write("B-only\n{}\n".format('-' * 50))
    if color:
        result.write(Fore.RED)
    for key, values in diff.b_only.items():
        result.write("- {}\n".format(key))
        for value in values:
            result.write("- \t{}\n".format(value))
    if color:
        result.write(Fore.RESET)
    result.write("Diff\n{}\n".format('-' * 50))
    for key, values in diff.diff.items():
        result.write('{}\n'.format(key))
        if 'a' in values:
            if color:
                result.write(Fore.GREEN)
            for value in values['a']:
                result.write("+ \t{}\n".format(value))
            if color:
                result.write(Fore.RESET)
        if 'b' in values:
            if color:
                result.write(Fore.RED)
            for value in values['b']:
                result.write("- \t{}\n".format(value))
            if color:
                result.write(Fore.RESET)
        if 'common' in values:
            if color:
                result.write(Fore.YELLOW)
            for value in values['common']:
                result.write("= \t{}\n".format(value))
            if color:
                result.write(Fore.RESET)
    return result


def dict_diff(a, b):
    """Takes two dictionaries (values should be lists) and compare them.

    :a: dict a
    :b: dict b
    :returns: namedtuple dictdiff(a_only, b_only, diff)

    """
    a_only_keys = set(a.keys()).difference(set(b.keys()))
    b_only_keys = set(b.keys()).difference(set(a.keys()))
    common_keys = set(a.keys()).intersection(set(b.keys()))
    a_only = dict((k, a[k]) for k in a_only_keys)
    b_only = dict((k, b[k]) for k in b_only_keys)
    diff = {}
    for k in common_keys:
        a_set = set(a[k])
        b_set = set(b[k])
        diff[k] = {}
        a_diff = set(a_set).difference(set(b_set))
        b_diff = set(b_set).difference(set(a_set))
        if a_diff:
            diff[k]['a'] = a_diff
        if b_diff:
            diff[k]['b'] = b_diff
        common = a_set.intersection(b_set)
        if common:
            diff[k]['common'] = common
    dictdiff = namedtuple('dictdiff', ('a_only', 'b_only', 'diff'))
    return dictdiff(a_only or None, b_only or None, diff or None)


def group_by_regex(text, regex, key_group, values_group):
    """Parse text with regex, and build where keys are matches for key group and values are lists of matches for value
    group.

    :text: string to parse into dict
    :regex: Compiled regexp, should contain the key_group and values_group
    :key_group: name of the key group from regex
    :values_group: name of the values group from regex
    :returns: dict, e.g.: { <key_group_match>: [<values_group_match1>, <values_group_m2>,...], ... }

    """
    failures = OrderedDict()
    required_groups = {key_group, values_group}
    if set(regex.groupindex.keys()) != required_groups:
        raise ValueError("regex should have following named groups: {}".format(','.join(required_groups)))
    for match in regex.finditer(text):
        try:
            failures[match.group(key_group)]
        except KeyError:
            failures[match.group(key_group)] = []
        failures[match.group(key_group)].append(match.group(values_group))
    return failures
