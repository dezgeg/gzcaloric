#!/usr/bin/env bash

for inputFile in testcases/*.in; do
    refFile=$(echo "$inputFile" | sed -e "s/\.in$/.ref/")
    outputFile=$(echo "$inputFile" | sed -e "s/\.in$/.out/")
    cat "$inputFile" | tr -d "\n"| gzip > /tmp/compr.in
    python2 main.py -n /tmp/compr.in > "$outputFile"
    if ! diff -u "$refFile" "$outputFile" > /tmp/diff; then
        echo "$inputFile: BAD:"
        cat /tmp/diff
    else
        echo "$inputFile: OK"
    fi
done
