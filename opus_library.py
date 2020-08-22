#!/usr/bin/python3
import argparse
from os import path, remove
import pathlib
from subprocess import run
from sys import exit
from shutil import copyfile

src = path.expanduser("~/Music/Library")
dst = path.expanduser("~/Music/LossyLibrary")

parser = argparse.ArgumentParser(
    description="Utility to maintain parallel copy of music library,\
    compressing all files (if specified); or only lossless/uncompressed files\
    (default) to .opus"
)

parser.add_argument(
    "--compress_all",
    help="Encode all source files to Opus (even those already compressed).",
    action="store_true")

parser.add_argument("--no_delete",
                    help="Do not delete files in dst removed from src.",
                    action="store_true")

parser.add_argument("--dry_run",
                    help="Print all actions rather than performing them",
                    action="store_true")

parser.add_argument("--src",
                    help="Destination; default is %s" % src,
                    default=src)
parser.add_argument("--dst", help="Source; default is %s" % dst, default=dst)

parser.add_argument("--bitrate", help="Bitrate in kbps", default="128")

args = parser.parse_args()

if not path.isdir(args.src):
    print("Source %s is not a valid path!" % src)
    exit(1)
if not path.isdir(args.dst):
    print("Destination %s is not a valid path!" % dst)
    exit(1)


def safe_run(cmd):
    """Run safely"""
    if args.dry_run:
        print("Run:", " ".join(cmd))
    else:
        run(cmd)


def safe_remove(p):
    """Remove safely"""
    if args.dry_run:
        print("Remove:", p)
    elif args.no_delete:
        print("Not removing:", p)
    else:
        remove(p)


def safe_copyfile(src, dst):
    """Copy, unless told not to"""
    if args.dry_run:
        print("Copy %s to %s" % (src, dst))
    else:
        copyfile(src, dst)


src_files = run(["find", args.src, "-type", "f"],
                encoding="utf8",
                capture_output=True).stdout.strip().split("\n")

dst_files = run(["find", args.dst, "-type", "f"],
                encoding="utf8",
                capture_output=True).stdout.strip().split("\n")

for track in src_files:
    parts = track.replace(args.src, "").split("/")
    f = parts[-1]
    subdirs = "/".join(parts[1:-1])
    pathlib.Path(path.join(args.dst, subdirs)).mkdir(parents=True,
                                                     exist_ok=True)

# testing!

to_encode = []

for track in dst_files:
    if track == "":
        continue
    f = "/".join(track.replace(
        args.dst, "").split("/")[1:])  # perhaps don't drop leading slash?
    dotparts = f.split(".")
    if dotparts[-1] != "opus":
        if args.compress_all:
            safe_remove(track)
            continue
        else:
            srcf = path.join(args.src, f)
    else:
        srcf = path.join(args.src, ".".join(dotparts[:-1]))
    for i in (srcf, srcf + ".opus"):
        if i in src_files:
            srcmtime = path.getmtime(i)
            dstmtime = path.getmtime(track)
            if srcmtime > dstmtime:
                print("mtimes:", srcmtime, dstmtime)
                to_encode.append(i)
                safe_remove(track)
            src_files.remove(i)
            break

lossless_suffixes = ["flac", "wav"]

to_encode += src_files
to_copy = []
tmp = []

if not args.compress_all:
    for track in to_encode:
        suffix = track.split(".")[-1]
        if suffix not in lossless_suffixes:
            to_copy.append(track)
        else:
            tmp.append(track)
to_encode = tmp

total = len(to_encode)
i = 0
for track in to_encode:
    i += 1
    print(" == Encoding %i of %i ... ==" % (i, total))
    safe_run([
        "ffmpeg", "-v", "quiet", "-i", track, "-c:a", "libopus", "-b:a",
        "128k",
        track.replace(args.src, args.dst) + ".opus"
    ])

total = len(to_copy)
i = 0
for track in to_copy:
    i += 1
    print(" == Copying %i of %i ... ==" % (i, total))
    print(track)
    safe_copyfile(track, track.replace(args.src, args.dst))

#  find and remove empty dirs
