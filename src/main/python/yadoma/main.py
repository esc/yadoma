"""yadoma

Usage:
  yadoma [options] link <config>

Options:
  -d --debug  Activate debug
  --dry-run   Dry run

"""

import os

from docopt import docopt
import yaml

LINK = 'link'
SUBCOMMANDS = [LINK]
DEBUG = False
DRY_RUN = False


class CMDLineExit(Exception):
    pass


class ConfigError(Exception):
    pass


def debug(message):
    if DEBUG:
        print(message)


def info(message):
    print(message)


def get_subcommand(arguments):
    for subcommand in SUBCOMMANDS:
        if arguments[subcommand]:
            return subcommand
    else:
        raise CMDLineExit


def link(file_, base_dir, target_dir):
    try:
        src = os.path.abspath(os.path.join(base_dir, file_['src']))
    except KeyError:
        raise ConfigError("Missing 'src' entry")
    try:
        dest = os.path.join(target_dir, file_['dest'])
    except KeyError:
        dest = os.path.join(target_dir, file_['src'])
    message = "Will try to symlink '{0}' to '{1}'...".format(src, dest)
    if DRY_RUN:
        info(message)
    else:
        debug(message)
        try:
            os.symlink(src, dest)
        except OSError as ose:
            if ose.errno == 17:
                debug("symlink exists")
            else:
                raise
        else:
            debug("successful")


def main():
    arguments = docopt(__doc__)
    global DEBUG
    global DRY_RUN
    if arguments['--debug']:
        DEBUG = True
    if arguments['--dry-run']:
        DRY_RUN = True
    config_path = arguments['<config>']
    base_dir = os.path.dirname(arguments['<config>'])
    target_dir = os.environ['HOME']
    loaded_config = yaml.load(open(config_path).read())
    debug(loaded_config)
    subcommand = get_subcommand(arguments)
    if subcommand == LINK:
        for program, program_config in loaded_config.items():
            for file_ in program_config['files']:
                link(file_, base_dir, target_dir)
