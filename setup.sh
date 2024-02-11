#!/bin/bash

set -e

if test -z "$CONDA_ROOT"; then
    if test -d "$HOME/miniconda3"; then
        CONDA_ROOT="$HOME/miniconda3"
    elif test -d "$HOME/anaconda3"; then
        CONDA_ROOT="$HOME/anaconda3"
    else
        echo "Can't infer conda installation root"
        exit 1
    fi
fi

echo "Using conda at $CONDA_ROOT"

source "$CONDA_ROOT/etc/profile.d/conda.sh"

conda create --name raconteur python=3.11.5
conda activate raconteur

conda install click pandas numpy tqdm scipy ipython requests pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch-nightly -c nvidia
pip install music-tag pydub num2words transliterate omegaconf 'python-telegram-bot[job-queue]' beautifulsoup4
