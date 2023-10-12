#!/bin/bash

username=${1:-foo}
password=${2:-bar}
path=${3:-baz}

retry "python -u -m rr handle-aneks -n 47000 -o 46000 -e crt -k -u $username -p $password -x '$path'" 'identity\|JSONDecodeError' 60
