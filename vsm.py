# -*- coding: utf-8 -*-
"""Video Snapshot Maker (VSM)
VSM uses ffmpeg to automatically take snapshots of video files.
VSM works fine with python 3.6+.

for installing ffmpeg on an ubuntu system run the following command in the shell:
`$ sudo apt install ffmpeg`

save this file somewhere and call it from the shell.

Examples:
    # take snapshots of the video.mp4 every 5 seconds and save them on /home
    $ python vsm.py avideo.mp4 /home 5

    # take snapshots of all mp4 files in the current directory every 3 seconds
    # and save them on snapshots directory
    $ python vsm.py . ./snapshots 3 -e mp4

    # take snapshots of all mp4/mkv files in /home/user1/videos/ and all it's
    # subdirectories, every 3 seconds and save them on /home/user1/snapshots/
    $ python vsm.py /home/user1/videos/ /home/user1/snapshots/ 3 -w 1 -e "mp4,mkv"

    # use --help for more information
    $ python vsm.py --help
    usage: vsm.py [-h] [-e EXTENSIONS] [-f FORMAT] [-p PREFIX] [-w WALK]
                  input output interval

    positional arguments:
      input                 input file/directory
      output                output directory
      interval              snapshots intervals in seconds

    optional arguments:
      -h, --help            show this help message and exit
      -e EXTENSIONS, --extensions EXTENSIONS
                            file extensions to process, e.g: mp4. More than one
                            values must be comma separated. e.g, "mp4,mkv"
      -f FORMAT, --format FORMAT
                            output file's extension e.g, png
      -p PREFIX, --prefix PREFIX
                            Prefix for output files names
      -w WALK, --walk WALK  1: process all files in subdirectories, 0:don't
                            process subdirectories

"""

import os
import subprocess
import re
import argparse


def snapshot(args):
    # print(args.__dict__)

    for filename in args.files:
        if not re.search(args.pattern, filename):
            continue
        ffmpeg = [
            'ffmpeg',
            '-i',
            os.path.join(args.path, filename),
            '-vf',
            'fps=1/{}'.format(args.interval),
            os.path.join(
                args.output, '{}{}_img%d.{}'.format(
                    args.prefix, '.'.join(filename.split('.')[:-1]), args.format)),
        ]
        print(' '.join(ffmpeg))
        print()
        subprocess.run(ffmpeg, stdout=subprocess.PIPE)


def video_snapshot_maker():
    try:
        subprocess.run('ffmpeg -version'.split(' '), stdout=subprocess.DEVNULL)
    except Exception:
        print(
            "ffmpeg is not installed!\n"
            "It can be installed on an ubuntu system by following code:\n"
            "sudo apt install ffmpeg\n"
        )

    DEFAULT_EXTENSIONS = ['mp4', 'vlc', 'mpeg', 'mkv', 'avi', 'flv', 'wmv', 'mov']

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="input file/directory")
    parser.add_argument('output', help="output directory", default='.')
    parser.add_argument('interval', type=int,
        help="snapshots intervals in seconds")
    parser.add_argument('-e', '--extensions',
        help=('file extensions to process, e.g:  mp4. More than one values must'
              ' be comma separated. e.g, "mp4,mkv"'))
    parser.add_argument('-f', '--format', help="output file's extension e.g, png", default='jpg')
    parser.add_argument('-p', '--prefix', default='', help="prefix for output files names")
    parser.add_argument('-w', '--walk', default=0, type=int,
        help="1: process all files in subdirectories, 0:don't process subdirectories")
    args = parser.parse_args()

    args.target = os.path.realpath(args.input)
    args.target_is_a_dir = os.path.isdir(args.target)

    if os.path.isdir(args.output):
        args.output = os.path.realpath(args.output)
    else:
        print('the output directory does not exists')
        exit(1)
    if args.extensions:
        try:
            args.extensions = list(map(str.strip, args.extensions.strip().split(',')))
        except Exception:
            print('File extensions to process, e.g:  mp4. More than one values'
                  ' must be comma separated. e.g, "mp4,mkv"')
            exit(1)

        if not args.target_is_a_dir:
            print("'extensions' argument is provided but input argument is not a directory")
            exit(1)

    if args.walk == 1 and not args.target_is_a_dir:
        print("walk' argument is 1 but input argument is not a directory")
        exit(1)
    if args.interval <= 0:
        print('interval value should be greater than 0')
        exit(1)

    if args.extensions:
        args.pattern = re.compile(r'({})$'.format('|'.join(args.extensions)), re.A.IGNORECASE)
    elif args.target_is_a_dir:
        args.pattern = re.compile(r'({})$'.format('|'.join(DEFAULT_EXTENSIONS)), re.A.IGNORECASE)
    else:
        args.pattern = re.compile(r'^{}$'.format(re.escape(args.target)))

    if args.walk:
        for path, _, files in os.walk(args.target):
            args.path = path
            args.files = files
            snapshot(args)
    elif args.target_is_a_dir:
        args.path = args.target
        args.files = [f for f in os.listdir(args.target) if os.path.isfile(f)]
        snapshot(args)
    else:
        args.path = os.path.dirname(args.target)
        args.files = [args.target]
        snapshot(args)


if __name__ == '__main__':
    video_snapshot_maker()
