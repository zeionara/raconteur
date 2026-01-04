#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/opt/raconteur
CONDA_ROOT=/opt/conda

DATASET_ROOT=$PROJECT_ROOT/assets/auch

SNAPSHOTS_PATH=$DATASET_ROOT/shapshots
THREADS_PATH=$DATASET_ROOT/threads

if test ! -d $SNAPSHOTS_PATH; then
  mkdir -p $SNAPSHOTS_PATH
fi

if test ! -d $THREADS_PATH; then
  mkdir -p $THREADS_PATH
fi

. "$CONDA_ROOT/etc/profile.d/conda.sh"

. /home/zeio/bashrc/creds/personal.sh

python -m rr start $SNAPSHOTS_PATH --alternation-list-path $DATASET_ROOT/index.txt --alternation-target $DATASET_ROOT/threads
