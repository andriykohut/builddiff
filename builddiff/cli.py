from __future__ import print_function

import os
import argparse
from getpass import getpass

import yaml
from requests.auth import HTTPBasicAuth

from jenkins import Jenkins


def parse_args():
    """Parse command-line arguments.

    :returns: argparse.Namespace object

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('build_a', help='build A', metavar='A', type=int)
    parser.add_argument('build_b', help='build B', metavar='B', type=int)
    parser.add_argument('-c', '--config', default=os.path.expanduser("~/.bdiff"),
                        help='A path to configuration file [Default: ~/.bdiff]')
    return parser.parse_args()


def config_setup(config_path):
    """Write user configuration to a file.

    :config_path: A path to configuration file.
    :returns: dict with config data.

    """
    print("Setting up jenkins config")
    conf = {'jenkins': {}}
    conf['jenkins']['url'] = raw_input('Jenkins url (e.g.: http://build.mydomain.com): ').strip()
    conf['jenkins']['user'] = raw_input('User name: ').strip()
    conf['jenkins']['password'] = getpass('Password: ')
    with open(config_path, 'w') as f:
        yaml.dump(conf, f)
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
    print(conf)
    auth = HTTPBasicAuth(conf['jenkins']['user'], conf['jenkins']['password'])
    jenkins = Jenkins(auth, conf['jenkins']['url'])
    builds = {'build_a': None, 'build_b': None}
    for build in jenkins.builds('buzzfeed-selenium-downstream', ["fullDisplayName", "number", "timestamp"]):
        if build.number == args.build_a:
            builds['build_a'] = build
        elif build.number == args.build_b:
            builds['build_b'] = build
    for k, v in builds.items():
        if not v:
            raise Exception("Build #{} not found".format(args.__dict__[k]))
