#!/usr/bin/env python
# -*- coding: utf8 -*-

""" An interface to help to synchronize files and folders contents using rsync """

import argparse
import os
import subprocess
import shlex

__author__ = "Marlom Oliveira"
__email__ = "marlomjobsom@gmail.com"
__version__ = "1.6"

# Descriptions and Help messages
DESCRIPTION_INFO = 'A simple interface to help to synchronize files and folders using rsync'
HELP_ORIGIN = 'Where folders/files come from'
HELP_DEST = 'Where folders/files go to'
HELP_FOLDERS = 'Folders to synchronize their contents'
HELP_FILES = 'Files to be synchronized'
HELP_DELETE = 'Delete extraneous files from destination dirs'
HELP_VERBOSE = 'Increase verbosity'
HELP_PROGRESS = 'Show progress during transfer'
HELP_OWNER = 'Preserves owners'
HELP_GROUP = 'Preserves groups'
HELP_EXEC = 'Preserves executability'
HELP_DRY_RUN = 'Performs a trial run with no changes made'
HELP_DELETE_EXCLUDED = 'Deletes excluded files from destination folders'
HELP_ENABLE_ALL = 'Enable delete, verbose, progress, owner, group, executability, and delete-excluded options'
HELP_EXCLUDE = 'Folders to be ignored'

# This command will be updated based on arguments
RSYNC_CMD = 'rsync -rulHt'


def init_args():
    """ Initialize arguments """
    parser = argparse.ArgumentParser(prog=DESCRIPTION_INFO, description=DESCRIPTION_INFO)

    parser.add_argument('--origin', type=str, help=HELP_ORIGIN, required=True)
    parser.add_argument('--dest', type=str, help=HELP_DEST, required=True)
    parser.add_argument('--folders', type=str, nargs='+', help=HELP_FOLDERS, default=[])
    parser.add_argument('--files', type=str, nargs='+', help=HELP_FILES, default=[])
    parser.add_argument('--exclude', type=str, nargs='+', help=HELP_EXCLUDE, default=[])

    parser.add_argument('--delete', action='store_true', help=HELP_DELETE, required=False)
    parser.add_argument('--verbose', action='store_true', help=HELP_VERBOSE, required=False)
    parser.add_argument('--progress', action='store_true', help=HELP_PROGRESS, required=False)
    parser.add_argument('--owner', action='store_true', help=HELP_OWNER, required=False)
    parser.add_argument('--group', action='store_true', help=HELP_GROUP, required=False)
    parser.add_argument('--executability', action='store_true', help=HELP_EXEC, required=False)
    parser.add_argument('--dry-run', action='store_true', help=HELP_DRY_RUN, required=False)
    parser.add_argument('--delete-excluded', action='store_true', help=HELP_DELETE_EXCLUDED, required=False)
    parser.add_argument('--enable_all', action='store_true', help=HELP_ENABLE_ALL, required=False)

    parser.set_defaults(delete=False)
    parser.set_defaults(verbose=False)
    parser.set_defaults(progress=False)
    parser.set_defaults(owner=False)
    parser.set_defaults(group=False)
    parser.set_defaults(executability=False)
    parser.set_defaults(dry_run=False)
    parser.set_defaults(delete_excluded=False)

    args = parser.parse_args()

    args.origin = remove_ending_separator(args.origin)
    args.dest = remove_ending_separator(args.dest)

    folders = []
    files = []
    excludes = []

    for _folder in args.folders:
        _folder = remove_ending_separator(_folder)

        # In case beginning of path matches with origin, remove it from folder path
        if _folder.startswith(args.origin):
            _folder = _folder.replace(args.origin, '').strip()

        if not os.path.exists(os.path.join(args.origin, _folder)):
            raise FileNotFoundError(
                'Folder does not exist on origin: {}'.format(
                    os.path.join(args.origin, _folder)
                )
            )

        folders.append(_folder)

    for _file in args.files:
        _file = remove_ending_separator(_file)

        # In case beginning of path matches with origin, remove it from file path
        if _file.startswith(args.origin):
            _file = _file.replace(args.origin, '').strip()

        if not os.path.isfile(os.path.join(args.origin, _file)):
            raise FileNotFoundError(
                'File does not exist on origin: {}'.format(
                    os.path.join(args.origin, _file)
                )
            )

        files.append(_file)

    for _exclude in args.exclude:
        excludes.append('--exclude "{}"'.format(_exclude))

    args.folders = folders
    args.files = files
    args.exclude = excludes

    if args.enable_all:
        args.delete = True
        args.verbose = True
        args.progress = True
        args.owner = True
        args.group = True
        args.executability = True
        args.delete_excluded = True
        args.enable_all = True

    return args


def remove_ending_separator(path):
    """ Remove folder separator from end """
    if path.endswith(os.sep):
        path = path[:-1]

    return path


def set_boolean_params(args, rsync_cmd):
    """ Enable bool parameters on the line command """
    opts = ['delete', 'verbose', 'progress', 'owner', 'group', 'executability', 'dry_run', 'delete_excluded']

    for opt in opts:
        if args.__getattribute__(opt):
            rsync_cmd = '{} --{}'.format(rsync_cmd, opt.replace('_', '-'))

    return rsync_cmd


def bold_msg(msg):
    """ Boldfacing a text """
    return '\033[1m{}\033[0m'.format(msg)


def color_msg(msg, color_option='white'):
    """ Coloring a text """
    colors = {
        'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
        'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7
    }
    return '\033[{}m{}\033[0m'.format(colors[color_option] + 30, msg)


def run_cmd(cmd):
    """ Execute command """
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)

    while process.poll() is None:
        print(process.stdout.readline().decode('utf-8').strip())

    return process.communicate()


def sync(args, rsync_cmd):
    """ Perform sync """

    # Set what should be ignored during sync
    rsync_cmd = '{} {}'.format(rsync_cmd, ' '.join(args.exclude))

    for folder in args.folders:
        try:
            os.makedirs(os.path.join(args.dest, folder))
        except FileExistsError:
            pass

        print(
            bold_msg(color_msg('rsync is synchronizing', 'green')),
            bold_msg(color_msg(folder, 'blue'))
        )

        cmd = '{} "{}{}" "{}{}"'.format(
            rsync_cmd,
            os.path.join(args.origin, folder), os.sep,
            os.path.join(args.dest, folder), os.sep
        )
        print(bold_msg(color_msg('Command:', 'blue')), bold_msg(color_msg(cmd, 'cyan')))
        run_cmd(cmd)

    for _file in args.files:
        try:
            os.makedirs(os.path.join(args.dest, os.path.dirname(_file)))
        except FileExistsError:
            pass

        print(
            bold_msg(color_msg('rsync is synchronizing ', 'green')),
            bold_msg(color_msg(_file, 'magenta'))
        )

        cmd = '{} "{}" "{}"'.format(
            rsync_cmd,
            os.path.join(args.origin, _file),
            os.path.join(args.dest, _file)
        )
        print(bold_msg(color_msg('Command:', 'magenta')), bold_msg(color_msg(cmd, 'cyan')))
        run_cmd(cmd)

    # rsync working over all origin folder
    if not args.folders and not args.files:
        print(
            bold_msg(color_msg('rsync is synchronizing', 'green')),
            bold_msg(color_msg(args.origin, 'blue')),
            bold_msg(color_msg('to', 'red')),
            bold_msg(color_msg(args.dest, 'blue'))
        )

        cmd = '{} "{}" "{}"'.format(rsync_cmd, args.origin, args.dest)
        print(bold_msg(color_msg('Command:', 'red')), bold_msg(color_msg(cmd, 'cyan')))
        run_cmd(cmd)


def main():
    """ Sync """
    args = init_args()
    sync(args, set_boolean_params(args, RSYNC_CMD))


if __name__ == '__main__':
    main()