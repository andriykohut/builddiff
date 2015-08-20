from __future__ import print_function
try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass

import os
import sys
import re
import argparse
from getpass import getpass
from operator import or_
from functools import reduce

import yaml
from requests.auth import HTTPBasicAuth
from colorama import Fore

from builddiff.jenkins import Jenkins
from builddiff.groupby_regex import parse_tests, compare_sel_failures


RE_FLAGS = ('I', 'L', 'M', 'S', 'U', 'X')


def parse_flags(arg):
    """Parse flags from command line argument.

    :arg: Argument string
    :returns: flag value

    """
    flags = set(f.upper() for f in arg.split('|'))
    for f in flags:
        if f not in RE_FLAGS:
            raise argparse.ArgumentTypeError('Invalid re flags')
    flags = set(getattr(re, f) for f in flags)
    return reduce(or_, flags)


def print_diff(diff):
    """Pretty print the diff.

    :diff: Named tuple (failures_a, failures_b, cases_diff)

    """
    print("A-only failures")
    print("---------------")
    sys.stdout.write(Fore.RED)
    for test_file, cases in diff.failures_a.items():
        print("+ {}".format(test_file))
        for case in cases:
            print("\t+ {}".format(case))
    sys.stdout.write(Fore.RESET)
    print("B-only failures")
    print("---------------")
    sys.stdout.write(Fore.GREEN)
    for test_file, cases in diff.failures_b.items():
        print("- {}".format(test_file))
        for case in cases:
            print("\t- {}".format(case))
    sys.stdout.write(Fore.RESET)
    print("Cases diff")
    print("----------")
    for fname, diffs in diff.cases_diff.items():
        print(fname)
        if 'a' in diffs:
            sys.stdout.write(Fore.RED)
            for case in diffs['a']:
                print("\t+ {}".format(case))
            sys.stdout.write(Fore.RESET)
        if 'b' in diffs:
            sys.stdout.write(Fore.GREEN)
            for case in diffs['b']:
                print("\t- {}".format(case))
            sys.stdout.write(Fore.RESET)
        if 'common' in diffs:
            sys.stdout.write(Fore.YELLOW)
            for case in diffs['common']:
                print("\t= {}".format(case))
            sys.stdout.write(Fore.RESET)


def parse_args():
    """Parse command-line arguments.

    :returns: argparse.Namespace object

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('build_a', help='build A (good)', metavar='A', type=int)
    parser.add_argument('build_b', help='build B (bad)', metavar='B', type=int)
    parser.add_argument('-c', '--config', default=os.path.expanduser("~/.bdiff"),
                        help='A path to configuration file [Default: ~/.bdiff]')
    parser.add_argument('-f', '--flags', help='Python regex flags, eg: "I" or "I|M"', default=0, type=parse_flags)
    parser.add_argument('-r', '--re', help='Regex for parsing console output')
    return parser.parse_args()


def config_setup(config_path):
    """Write user configuration to a file.

    :config_path: A path to configuration file.
    :returns: dict with config data.

    """
    print("Setting up jenkins config")
    conf = {'jenkins': {}}
    conf['jenkins']['url'] = raw_input('Jenkins url (e.g.: http://build.mydomain.com): ').strip()
    conf['jenkins']['job'] = raw_input('Job name: ').strip()
    conf['jenkins']['user'] = raw_input('User name: ').strip()
    conf['jenkins']['password'] = getpass('Password: ')
    with open(config_path, 'w') as f:
        yaml.dump(conf, f, default_flow_style=False)
    print("Config saved to {}".format(config_path))
    return conf


def main():
    """Starting point of a program"""
    args = parse_args()
    if not os.path.isfile(args.config):
        conf = config_setup(args.config)
    else:
        with open(args.config) as f:
            conf = yaml.load(f)
    auth = HTTPBasicAuth(conf['jenkins']['user'], conf['jenkins']['password'])
    jenkins = Jenkins(auth, conf['jenkins']['url'])
    builds = {'build_a': None, 'build_b': None}
    for build in jenkins.builds(conf['jenkins']['job'], ["fullDisplayName", "number", "timestamp"]):
        if build.number == args.build_a:
            builds['build_a'] = build
        elif build.number == args.build_b:
            builds['build_b'] = build
    for k, v in builds.items():
        if not v:
            raise Exception("Build #{} not found".format(args.__dict__[k]))
    regex = re.compile(args.re, args.flags)
    tests_a = parse_tests(builds['build_a'].console_output(), regex)
    tests_b = parse_tests(builds['build_b'].console_output(), regex)
    diff = compare_sel_failures(tests_a, tests_b)
    print_diff(diff)
