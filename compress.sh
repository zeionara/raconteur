#!/bin/bash

input=${1:-assets/speech}
output=${2:-assets/baneks-speech}

for folder in "$input"/*; do
    src=`basename $folder`
    path="$output/$src.tar.xz"

    # echo $path

    if [ ! -f "$path" ]; then
        echo "Generating file $path..."
        tar -C "$folder" -cJvf "$path" '.'
    else
        echo "File $path already exists. Skipping..."
    fi

    # To extract with the output folder as root:
    #
    # extracted="$output/$src"
    # mkdir "$extracted"
    # tar -C "$extracted" -xJvf "$path"

    # exit 0
done
