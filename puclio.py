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
import subprocess
import sys
from ressources.lib.putio2 import putio2

DIR_CONFIG_PATH = "~/.config/puclio"
CONFIG_PATH = DIR_CONFIG_PATH + "/config"
PUTIO_APP_ID = "337"
PUTIO_TOKEN_PATH = "http://put.io/v2/oauth2/apptoken/" + PUTIO_APP_ID

BOLD = '[1m'
NC = '[0m'

def setup_account():
    config = configparser.ConfigParser()
    tok = input("To get your Oauth token go to: " + PUTIO_TOKEN_PATH +
                ".\nOauth token ? ")
    config.add_section('account')
    config.set('account', 'token', tok)
    try:
        if not os.path.exists(os.path.expanduser(CONFIG_PATH)):
            os.makedirs(os.path.expanduser(DIR_CONFIG_PATH), 0o775)
        with open(os.path.expanduser(CONFIG_PATH), 'w') as configfile:
            config.write(configfile)
    except EnvironmentError as e:
        print(e.strerror)

def init_parser():
    p = argparse.ArgumentParser(description =
            "A Putio Utility, Command LIne Oriented.")
    subparsers = p.add_subparsers(dest='cmd')

    ls = subparsers.add_parser('ls', help = "list files")
    ls.add_argument("-a", "--all", help = "show more informations",
            action = "store_true")
    ls.add_argument("id", type = int, nargs = '?', default = 0,
            help = "ID to list")

    lt = subparsers.add_parser('lt', help = "list transfers")

    rm = subparsers.add_parser("rm", help = "delete a file")
    rm.add_argument("id", type = int, nargs = '+', help = "ID to delete")

    tree = subparsers.add_parser('tree', help = "list files as a tree")

    up = subparsers.add_parser('up', help = "upload a file on put.io")
    up.add_argument("file", type = str, nargs = '+',  help = "file to upload")

    dl = subparsers.add_parser('dl', help = "dowload files")
    dl.add_argument("id", type = int, nargs = '+', help = "ID to dowload")

    setup = subparsers.add_parser('setup',
            help = "setup your Oauth account")
    return p

def init_account():
    config = configparser.ConfigParser()

    try:
        config.read_file(open(os.path.expanduser(CONFIG_PATH)))
        token = config['account']['token']
    except IOError as e:
        print("Error with " + e.filename + ":")
        print(e.strerror)
        print("Please run " + sys.argv[0] + " setup.")
        sys.exit(1)
    except KeyError as e:
        print("Error with the config file structure.")
        print("Please run " + sys.argv[0] + " setup.")
        sys.exit(1)

    return putio2.Client(token)

def list_files(putio, args = None):
    try:
        files = putio.File.list(args.id)
    except Exception:
        print("Something went wrong on the server. Check the ID.")
        sys.exit(1)

    for f in files:
        print(" {:>8}  {}".format(BOLD + str(f.id) + NC, f.name))

def list_transfers(putio, args = None):
    try:
        transfers = putio.Transfer.list()
    except Exception:
        print("Something went wrong on the server. Check the ID.")
        sys.exit(1)

    for t in transfers:
        print(" {:>7}  {}".format(BOLD + str(t.id) + NC, t.name))

def tree_files(putio, args = None):
    # Maybe not print and search at the same time to improve formatting.
    def go_deep(tree, id, depth):
        for k, v in tree[id].items():
            print("|" + "    |" * depth + "––– " + v)
            if k in tree:
                go_deep(tree, k, depth + 1)

    try:
        files = putio.File.list(-1)
    except Exception:
        print("Could not list all file; server response was not valid.")
        sys.exit(1)

    tree = collections.defaultdict(dict)
    for idx, f in enumerate(files):
        tree[f.parent_id][f.id] = f.name
    print(".")
    go_deep(tree, 0, 0)

def download(putio, args):
    for i in args.id:
        try:
            f = putio.File.get(i)
        except Exception:
            print("Impossible to retrieve ID {}.".format(i))
        else:
            url = f.download(ext = True)
            subprocess.call(["curl", "-J", "-O", url])

def upload(putio, args):
    for f in args.file:
        putio.File.upload(f, os.path.basename(f))

def delete(putio, args):
    for i in args.id:
        try:
            putio.File.get(i).delete()
        except Exception:
            print("Impossible to retrieve ID {}.".format(i))

if __name__ == "__main__":

    parser = init_parser()

    if len(sys.argv) == 1:
        parser.print_help();
        sys.sys.exit(1)
    args = parser.parse_args()

    if args.cmd == 'setup':
        setup_account()
        sys.exit(0)

    putio = init_account()

    if args.cmd == 'ls':
        list_files(putio, args)
    elif args.cmd == 'tree':
        tree_files(putio, args)
    elif args.cmd == 'dl':
        download(putio, args)
    elif args.cmd == 'rm':
        delete(putio, args)
    elif args.cmd == 'up':
        upload(putio, args)
    elif args.cmd == 'lt':
        list_transfers(putio, args)

