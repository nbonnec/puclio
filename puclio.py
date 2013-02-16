#!/usr/bin/python3

#
# A Putio Utility, Command LIne Oriented.
#
# TODO:
#       - setup,
#       - manage bad token,
#       - use config parser.

import argparse
import configparser
import logging
import os
import sys
from ressources.lib.putio2 import putio2

CONFIG_PATH = "~/.config/puclio/config"
PUTIO_APP_ID = "337"
PUTIO_TOKEN_PATH = "http://put.io/v2/oauth2/apptoken/" + PUTIO_APP_ID

def setup_account(config):
    tok = input("To get your Oauth token go to: " + PUTIO_TOKEN_PATH +
                ".\nOauth token ? ")
    config.add_section('account')
    config.set('account', 'token', tok)
    with open(os.path.expanduser(CONFIG_PATH), 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description =
            "A Putio Utility, Command LIne Oriented.")
    subparsers = parser.add_subparsers(dest='cmd')

    parser_ls = subparsers.add_parser('ls')
    parser_setup = subparsers.add_parser('setup')

    if len(sys.argv) == 1:
        parser.print_help();
        sys.exit(1)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    if args.cmd == 'setup':
        setup_account(config)
        exit(1)
    else:
        try:
            config.read_file(open(os.path.expanduser(CONFIG_PATH)))
        except FileNotFoundError:
            print("No configuration file.")
            setup_account(config)

    o_token = config['account']['token']

    if args.cmd == 'ls':
        putio = putio2.Client(o_token)
        files = putio.File.list()
        for idx, f in enumerate(files):
            print(str(idx + 1) + "    " + f.name)

