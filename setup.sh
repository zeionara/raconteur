#!/bin/bash

set -euo pipefail

conda create -n raconteur 'python<3.12' -y

conda run -n much --no-capture-output pip install chatterbox-tts
conda run -n much --no-capture-output pip install kokoro
conda run -n much --no-capture-output pip install ipython
conda run -n much --no-capture-output pip install music-tag
conda run -n much --no-capture-output pip install num2words
conda run -n much --no-capture-output pip install transliterate
conda run -n much --no-capture-output pip install "python-telegram-bot[job-queue]"
conda run -n much --no-capture-output pip install 'russian-text-stresser @ git+https://github.com/Vuizur/add-stress-to-epub'
conda run -n much --no-capture-output pip install peft
conda run -n much --no-capture-output pip install sentencepiece

# much deps

conda run -n much --no-capture-output pip install beautifulsoup4

# much deps, which are required to run much/alternate.sh

conda run -n much --no-capture-output pip install flask
conda run -n much --no-capture-output pip install google-images-search

git submodule update --init

sudo bash -c 'apt-get update && apt-get install ffmpeg -y'
