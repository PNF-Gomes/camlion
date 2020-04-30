#!/usr/bin/env python

import numpy as np

COLORS = np.array([])
LABELS = []

def setup(args):
    global LABELS, COLORS

    labelsPath = args["labels"]
    LABELS = open(labelsPath).read().strip().split("\n")

    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
