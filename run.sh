#!/bin/bash

python -m rr start /mnt/outer-world/raconteur-bot \
    -a /mnt/outer-world/patch/alternation-list.txt \
    -t /mnt/outer-world/patch/audible \
    -c /2ch \
    --hf-cache /mnt/outer-world/patch/hf-cache
