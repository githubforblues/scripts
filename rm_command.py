import argparse
import shutil
import pathlib
import time
import sys
import re

dst = '/tmp/.trash/'

parser = argparse.ArgumentParser(prog='rm', add_help=False)
parser.add_argument('-f', dest='force', help='', action='store_true')
parser.add_argument('-r', dest='recursive', help='', action='store_true')
parser.add_argument('--version', dest='version', help='', action='store_true')
parser.add_argument('--help', dest='help', help='', action='store_true')
parser.add_argument('path', nargs='*')

args = parser.parse_args()

def cmdversion(args):
    if args.version:
        print('This rm command made by Python3, and version 1.0.0\nIt will put files in the trash, and can also use in crontab for clean trash.')
        sys.exit()

def cmdhelp(args):
    if args.help:
        print('Usage: rm [OPTION]... FILE...\nRemove (unlink) the FILE(s).')
        sys.exit()

def pathcheck(file):
    if not pathlib.Path(file).exists():
        print("rm: cannot remove '%s': No such file or directory" % file)
        sys.exit(1)

    try:
        m = re.search('[/]$',file)
        m.group()
    except AttributeError:
        if pathlib.Path(file).is_dir():
            file = file + '/'
    finally:
        if file in ['/','/root/','/boot/','/data/','/dev/','/etc/','/lib/','/lib64/','/opt/','/sbin/','/usr/','/var/','/bin/']:
            print("rm: Error: you can not delete '%s'." % file)
            sys.exit(1)

def getpath(args, dst):
    dst_path = pathlib.Path(dst)
    if not dst_path.is_dir():
        dst_path.mkdir(0o755)

    for file in args.path:
        pathcheck(file)

        file_path = pathlib.Path(file)
        rm_path = dst + str(file_path.name) + str(time.time())

        if not args.force and file_path.is_symlink():
            choice = input("rm: remove symbolic link '%s' ? " % str(file_path.name))
            if choice == 'y':
                shutil.move(file, rm_path)
        elif not args.force and file_path.is_file():
            choice = input("rm: remove regular file '%s' ? " % str(file_path.name))
            if choice == 'y':
                shutil.move(file, rm_path)
        elif not args.force and args.recursive and file_path.is_dir():
            choice = input("rm: remove directory '%s' ? " % str(file_path.name))
            if choice == 'y':
                shutil.move(file, rm_path)
        elif ( not args.force and not args.recursive and file_path.is_dir() ) or ( args.force and not args.recursive and file_path.is_dir() ):
            print("rm: cannot remove '%s': Is a directory" % str(file_path.name))
            sys.exit(1)
        else:
            shutil.move(file, rm_path)

if __name__ == '__main__':
    cmdversion(args)
    cmdhelp(args)
    getpath(args, dst) 


