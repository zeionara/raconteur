#!/bin/bash

n_workers=${2:-16}

for _ in $(seq 1 10); do
    python -m rr iterate "$HOME/batch/threads/$1" "$HOME/batch/threads-spoken/$1" -w $n_workers
done
