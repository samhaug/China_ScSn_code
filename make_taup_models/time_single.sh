#!/bin/bash
#remove double column in every time file if it exists
for d in *;
do
    cp $d file_in
    awk -F" " '{print $1}' file_in > $d;
done

rm file_in

