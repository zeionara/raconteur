#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/opt/raconteur
CONDA_ROOT=/opt/conda

DATASET_ROOT=$PROJECT_ROOT/assets/auch

LOG_ROOT=$PROJECT_ROOT/assets/logs
LOG_FILE=$LOG_ROOT/start.txt

SNAPSHOTS_PATH=$DATASET_ROOT/shapshots
THREADS_PATH=$DATASET_ROOT/threads

export PYTHONUNBUFFERED=True

if test ! -d $SNAPSHOTS_PATH; then
  mkdir -p $SNAPSHOTS_PATH
fi

if test ! -d $THREADS_PATH; then
  mkdir -p $THREADS_PATH
fi

if test ! -d $LOG_ROOT; then
  mkdir $LOG_ROOT
fi

. "$CONDA_ROOT/etc/profile.d/conda.sh"
. /home/zeio/bashrc/creds/personal.sh

if test -f $LOG_FILE; then
  echo >> $LOG_FILE
fi

date +"%Y-%m-%d %H:%M:%S" >> $LOG_FILE

cd $PROJECT_ROOT

conda run -n raconteur --no-capture-output \
    python -m rr start $SNAPSHOTS_PATH \
        --alternation-list-path $DATASET_ROOT/index.txt \
        --alternation-target $DATASET_ROOT/threads 1>> $LOG_FILE 2>&1
