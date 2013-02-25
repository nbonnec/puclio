#!/usr/bin/python3

#
# A Putio Utility, Command LIne Oriented.
#
# TODO:
#       - manage bad token,
#       - prettier tree.

import argparse
import collections
import configparser
import logging
import os
import sys
from ressources.lib.putio2 import putio2

DIR_CONFIG_PATH = "~/.config/puclio"
CONFIG_PATH = DIR_CONFIG_PATH + "/config"
PUTIO_APP_ID = "337"
PUTIO_TOKEN_PATH = "http://put.io/v2/oauth2/apptoken/" + PUTIO_APP_ID

def setup_account():
    config = configparser.ConfigParser()
    tok = input("To get your Oauth token go to: " + PUTIO_TOKEN_PATH +
                ".\nOauth token ? ")
    config.add_section('account')
    config.set('account', 'token', tok)
    if not os.path.exists(os.path.expanduser(CONFIG_PATH)):
        os.makedirs(os.path.expanduser(DIR_CONFIG_PATH), 0o775)
    with open(os.path.expanduser(CONFIG_PATH), 'w') as configfile:
        config.write(configfile)

def init_parser():
    p = argparse.ArgumentParser(description =
            "A Putio Utility, Command LIne Oriented.")
    subparsers = p.add_subparsers(dest='cmd')

    ls = subparsers.add_parser('ls', help = "list files")
    ls.add_argument("-a", "--all", help = "show more informations",
            action = "store_true")
    ls.add_argument("id", type = int, nargs = '?', default = 0,
            help = "ID to list")

    tree = subparsers.add_parser('tree', help = "list files as a tree")

    dl = subparsers.add_parser('dl', help = "dowload files")
    dl.add_argument("id", type = int, help = "ID to dowload")

    setup = subparsers.add_parser('setup',
            help = "setup your Oauth account")
    return p

def init_account():
    config = configparser.ConfigParser()

    try:
        config.read_file(open(os.path.expanduser(CONFIG_PATH)))
    except FileNotFoundError:
        print("No configuration file.")
        setup_account(config)

    try:
        token = config['account']['token']
    except KeyError:
        print("Problem with the configuration file. \n"
                "Try to run " + sys.argv[0] + " setup.")
        exit(1)

    return putio2.Client(token)

def list_files(putio, args = None):
    try:
        files = putio.File.list(args.id)
    except Exception:
        print("Something went wrong on the server. Check the ID.")
        exit(1)

    for idx, f in enumerate(files):
        s = "(" + str(idx + 1) +")"
        print("{0:>5} {2} {1}".format(s, f.name, f.id))


def tree_files(putio, args = None):
    # Maybe not print and search at the same time to improve formatting.
    def go_deep(tree, id, depth):
        for k, v in tree[id].items():
            print("|" + "    |" * depth + "––– " + v)
            if k in tree:
                go_deep(tree, k, depth + 1)

    try:
        files = putio.File.list(-1)
    except:
        print("Could not list all file; server response was not valid.")
        exit(1)

    tree = collections.defaultdict(dict)
    for idx, f in enumerate(files):
        tree[f.parent_id][f.id] = f.name
    print(".")
    go_deep(tree, 0, 0)

def download(putio, args = None):
    #use curl -J -O
    f = putio.File.get(args.id)
    url = f.download(ext = True)
    print(url)

if __name__ == "__main__":

    parser = init_parser()

    if len(sys.argv) == 1:
        parser.print_help();
        sys.exit(1)
    args = parser.parse_args()

    if args.cmd == 'setup':
        setup_account()
        exit(0)

    putio = init_account()

    if args.cmd == 'ls':
        list_files(putio, args)
    elif args.cmd == 'tree':
        tree_files(putio, args)
    elif args.cmd == 'dl':
        download(putio, args)

