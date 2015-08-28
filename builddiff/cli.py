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

from builddiff.jenkins import Build
from builddiff.utils import group_by_regex, dict_diff, format_diff


RE_FLAGS = ('I', 'L', 'M', 'S', 'U', 'X')


def _parse_flags(arg):
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


def parse_args():
    """Parse command-line arguments.

    :returns: argparse.Namespace object

    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands', dest='command')
    diff = subparsers.add_parser('diff')
    diff.add_argument('build_a', help='build A', metavar='A', type=int)
    diff.add_argument('build_b', help='build B', metavar='B', type=int)
    diff.add_argument('--color', action='store_true', default=False, help='colored output')
    _list = subparsers.add_parser('list')
    _list.add_argument('build', help='build number', type=int)
    parser.add_argument('-c', '--config', default=os.path.expanduser("~/.bdiff"),
                        help='A path to configuration file [Default: ~/.bdiff]')
    parser.add_argument('-f', '--flags', help='Python regex flags, eg: "I" or "I|M"', default=0, type=_parse_flags)
    parser.add_argument('-r', '--re', help='Regex for parsing console output')
    parser.add_argument('-k', '--key', help='key group name [Default: %(default)s]', default='key', dest='key_group')
    parser.add_argument('-v', '--values', help='values group name [Default: %(default)s]', default='values',
                        dest='values_group')
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
    regex = re.compile(args.re, args.flags)
    if args.command == 'list':
        build = Build(auth, conf['jenkins']['url'], conf['jenkins']['job'], args.build)
        grouped = group_by_regex(build.console_output(), regex, args.key_group, args.values_group)
        for key, values in grouped.items():
            print(key)
            for value in values:
                print("\t{}".format(value))
            print()
    elif args.command == 'diff':
        build_a = Build(auth, conf['jenkins']['url'], conf['jenkins']['job'], args.build_a)
        build_b = Build(auth, conf['jenkins']['url'], conf['jenkins']['job'], args.build_b)
        groups_a = group_by_regex(build_a.console_output(), regex, args.key_group, args.values_group)
        groups_b = group_by_regex(build_b.console_output(), regex, args.key_group, args.values_group)
        diff = dict_diff(groups_a, groups_b)
        sys.stdout.write(format_diff(diff, color=args.color).getvalue())
