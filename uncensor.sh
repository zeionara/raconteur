#!/bin/bash

username=${1:-foo}
password=${2:-bar}
path=${3:-baz}

python -m rr uncensor ../baneks-distinct/baneks-distinct.tsv assets/speech-uncensored -c $path -u $username -p $password
