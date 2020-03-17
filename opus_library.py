#!/usr/bin/python3
import argparse
from os import path

src = path.expanduser("~/Music/Library")
dst = path.expanduser("~/Music/LossyLibrary")

parser = argparse.ArgumentParser(
    description=
    "Utility to maintain parallel copy of music library, compressing all files (if specified); or only lossless/uncompressed files (default) to .opus"
)

parser.add_argument(
    "--compress_all",
    help="Encode all source files to Opus (even those already compressed).",
    action="store_true")

parser.add_argument("--src", default=src)
parser.add_argument("--dst", default=dst)

args = parser.parse_args()

