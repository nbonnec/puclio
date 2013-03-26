#!/usr/bin/env python3
#-*-coding:utf-8-*-

#
# A putio2. Utility, Command LIne Oriented.
#
# TODO:
#       - manage bad token,
#       - prettier tree.
#       - too much sys.exit

import argparse
import collections
import configparser
import logging
import os
import signal
import subprocess
import sys
from ressources.lib.putio2 import putio2

logger = logging.getLogger(__name__)

DESCRIPTION = "A Putio Utility, Command LIne Oriented."
SOURCE = "https://github.com/thevegeta/puclio"
VERSION = "0.2"

DIR_CONFIG_PATH = "~/.config/puclio"
CONFIG_PATH = DIR_CONFIG_PATH + "/config"
PUTIO_APP_ID = "337"
PUTIO_TOKEN_PATH = "http://put.io/v2/oauth2/apptoken/" + PUTIO_APP_ID
ID_SIZE = 7

BOLD = '[1m'
NC = '[0m'

file_alias = {}
is_interactive = False

def config():
    """ Configure the Oauth token of the account """
    config = configparser.ConfigParser()
    tok = input("To get your Oauth token go to: " + PUTIO_TOKEN_PATH +
                ".\nYOUR TOKEN WILL BE STORE IN PLAIN TEXT !"
                "\nOauth token ? ")
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
    """ Initialize parser with all arguments and subcommands. """
    p = argparse.ArgumentParser(description = DESCRIPTION + "\n\n" +
                                SOURCE,
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("-v", "--version", action="version",
                   version="puclio version {}".format(VERSION))

    p.add_argument("-d", "--debug", action="store_true",
                   help = "print debug informations")

    subparsers = p.add_subparsers(title="Commands", dest="cmd",
                                  metavar="[<command>]")

    add = subparsers.add_parser("add", help="add an url to the transfer list")
    add.add_argument("url", nargs="+", help="file's url to retrieve"
                        " (put quotes to avoid problems with your console).")
    add.add_argument("--pid", help="parent ID for the final file")

    config = subparsers.add_parser("config", help="config your Oauth account")

    dl = subparsers.add_parser("dl", help="dowload files")
    dl.add_argument("id", type=int, nargs="+", help="ID to dowload")
    dl.add_argument("-o", "--output", metavar="file", type=str,
                    help="write output to file instead of"
                         "the current directory")

    info = subparsers.add_parser("info", help="get informations on account")

    ls = subparsers.add_parser("ls", help="list files")
    ls.add_argument("-a", "--all", help="list more informations",
                    action="store_true")
    ls.add_argument("id", type=int, nargs="?", default=0,
                    help="ID to list")

    lt = subparsers.add_parser("lt", help="list transfers")

    rm = subparsers.add_parser("rm", help="delete a file")
    rm.add_argument("id", type=int, nargs="+", help="ID to delete")

    tree = subparsers.add_parser("tree", help="list files as an (ugly) tree")

    up = subparsers.add_parser("up", help="upload a file on put.io")
    up.add_argument("file", nargs="+", help="file to upload")

    return p

def get_client():
    """ Get an instanciation of a Client object from the put.io API. """
    config = configparser.ConfigParser()

    try:
        config.read_file(open(os.path.expanduser(CONFIG_PATH)))
        token = config['account']['token']
        logger.debug("token: {}".format(token))
    except IOError as e:
        print("Error with " + e.filename + ": " + e.strerror)
        print("Please run " + sys.argv[0] + " config.")
        sys.exit(1)
    except KeyError as e:
        print("Error with the config file structure.")
        print("Please run " + sys.argv[0] + " config.")
        sys.exit(1)

    return putio2.Client(token)

def list_files(putio, args=None):
    """ List client files with their IDs. """
    if is_interactive and args.id > 0:
        try:
            args.id = file_alias[args.id]
        except KeyError:
            pass

    try:
        files = putio.File.list(args.id)
    except (putio2.StatusError, putio2.JSONError):
        print("Something went wrong on the server. Check the ID.")
        return 1

    if is_interactive:
        file_alias.clear()

    for i, f in enumerate(files):
        if is_interactive:
            idx = "(" + str(i + 1) + ")"
            file_alias[i + 1] = f.id
        else:
            idx = "(" + str(f.id) + ")"
        print(" {}  {}".format(
            BOLD + str(idx).rjust(5 if is_interactive else 10) + NC,
            f.name))

    return 0

def list_transfers(putio, args=None):
    """ List all transfers. """
    try:
        transfers = putio.Transfer.list()
    except (putio2.StatusError, putio2.JSONError):
        print("Something went wrong on the server. Check the ID.")
        return 1

    for t in transfers:
        print(" {:>7}  {}".format(BOLD + "(" + str(t.id) + ")" + NC, t.name))

    return 0

def tree_files(putio, args=None):
    """ List all files as a tree. """
    # Maybe not print and search at the same time to improve formatting.
    def go_deep(tree, id, depth):
        for k, v in tree[id].items():
            print("|" + "    |" * depth + "––– " + v)
            if k in tree:
                go_deep(tree, k, depth + 1)

    try:
        files = putio.File.list(-1)
    except (putio2.StatusError, putio2.JSONError):
        print("Could not list all files; server response was not valid.")
        return 1

    tree = collections.defaultdict(dict)
    for idx, f in enumerate(files):
        tree[f.parent_id][f.id] = "{} ({})".format(f.name, f.id)
    print(".")
    go_deep(tree, 0, 0)

    return 0

def download(putio, args):
    """ Download a file from put.io. """

    if is_interactive:
        for idx, i in enumerate(args.id):
            if i > 0:
                try:
                    args.id[idx] = file_alias[i]
                except KeyError:
                    pass

    if args.output and len(args.id) > 1:
        print(sys.argv[0] +
              ": error: -o, --output can only be set with one ID.")
        return 1

    err = 0
    for i in args.id:
        try:
            f = putio.File.get(i)
        except (putio2.StatusError, putio2.JSONError):
            print("Impossible to retrieve ID {}.".format(i))
            err = 1
        else:
            url = f.download(ext=True)
            subprocess.call(["wget", "--content-disposition", url])

    return err

def upload(putio, args):
    """ Upload files to put.io. """
    err = 0
    for f in args.file:
        try:
            putio.File.upload(f, os.path.basename(f))
        except (putio2.StatusError, putio2.JSONError):
            print("Problem with the server.")
            err = 1
        except IOError as e:
            print("Error with " + e.filename + ": " + e.strerror)
            err = 1

    return err

def delete(putio, args):
    """ Delete a file on put.io. """
    if is_interactive:
        for idx, i in enumerate(args.id):
            if i > 0:
                try:
                    args.id[idx] = file_alias[i]
                except KeyError:
                    pass

    err = 0
    for i in args.id:
        try:
            putio.File.get(i).delete()
        except (putio2.StatusError, putio2.JSONError):
            print("Impossible to retrieve ID {}.".format(i))
            err = 1

    return err

def add_transfer(putio, args):
    """ Add a file to the transfer list, using an url. """
    err = 0
    for u in args.url:
        try:
            putio.Transfer.add(u, args.pid)
        except (putio2.StatusError, putio2.JSONError):
            print("Problem with the server.")
            err = 1

    return err

def sizeof_fmt(size):
    """ Get the byte size in a human readable way. """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "{:3.1f} {}".format(size, x)
        size /= 1024

def list_info(putio, args):
    """ List informations about the account. """
    try:
        infos = putio.Account.info()
    except (putio2.StatusError, putio2.JSONError):
        print("Problem with the server.")
        return 1

    print()
    print("{} ({})".format(infos.username, infos.mail))
    print()
    print("Disk infos:")
    print("     avail: {:>10}".format(sizeof_fmt(infos.disk['avail'])))
    print("     used:  {:>10}".format(sizeof_fmt(infos.disk['used'])))
    print("     total: {:>10}".format(sizeof_fmt(infos.disk['size'])))

def sigint_handler(signal, frame):
    """ Exit nicely on SIGINT. """

    print("Program interrupted...")
    sys.exit(0)

def run_interactive(parser):
    putio = get_client()
    while True:
        try:
            cli = input("puclio> ")
        except EOFError:
            print()
            break;
        try:
            args = parser.parse_args(cli.split())
        except SystemExit:
            # don't exit when help is print
            pass
        else:
            run_command(args)

def run_command(args):
    commands = {
        'add': add_transfer,
        'dl': download,
        'info': list_info,
        'ls': list_files,
        'lt': list_transfers,
        'rm': delete,
        'tree': tree_files,
        'up': upload
    }

    putio = get_client()

    if args.cmd in commands:
        return commands[args.cmd](putio, args)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, sigint_handler)

    parser = init_parser()

    if len(sys.argv) == 1:
        is_interactive = True
        run_interactive(parser)
        sys.exit(0)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.cmd == 'config':
        config()
        sys.exit(0)

    sys.exit(run_command(args))

