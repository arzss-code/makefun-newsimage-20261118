#!/usr/bin/env python3
"""make.fun news-image-20261118 entry.

The program is a one-file, standard-library-only copier: the finished artwork
lives beside it as entry.png and is written byte-for-byte to $MAKEFUN_OUTPUT_DIR
(default /output; <repo>/output only if that default cannot be created).
RULES.txt of this competition says the simplest entry is a repository holding
the image and a one-line program that copies it there; the grader's image has
no third-party packages, so nothing is drawn at run time.

Determinism: no network, no clock, no randomness - the same bytes every run.
tools/build_image.py is the Pillow program that produced entry.png offline.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR")
if OUT_DIR:
    os.makedirs(OUT_DIR, exist_ok=True)
else:
    OUT_DIR = "/output"
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
    except OSError:
        OUT_DIR = os.path.join(HERE, "output")
        os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"), os.path.join(OUT_DIR, "entry.png"))
print("wrote", os.path.join(OUT_DIR, "entry.png"))
