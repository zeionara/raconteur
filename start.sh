#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/opt/raconteur
VENV_ROOT=/opt/marude/.venv

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

. /home/zeio/.oh-my-zsh/custom/bashrc/creds/personal.sh

if test -f $LOG_FILE; then
  echo >> $LOG_FILE
fi

date +"%Y-%m-%d %H:%M:%S" >> $LOG_FILE

cd $PROJECT_ROOT

$VENV_ROOT/bin/python -m rr start $SNAPSHOTS_PATH \
    --alternation-list-path $DATASET_ROOT/index.txt \
    --alternation-target $DATASET_ROOT/threads 1>> $LOG_FILE 2>&1
