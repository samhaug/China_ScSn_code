#!/bin/bash
# 
# Make directory of traveltimes for event at depth h
#
h=$1
time_dir=/home/samhaug/work1/China_ScSn_data/time_$h"_km"
mkdir $time_dir
echo $time_dir

t=taup_time
                              
$t -mod prem --time -ph ScSScS -h $h -o $time_dir/PURE_ScS2 < degrees.dat > /dev/null;
$t -mod prem --time -ph ScSScSScS -h $h -o $time_dir/PURE_ScS3 < degrees.dat > /dev/null;
$t -mod prem --time -ph sScS -h $h -o $time_dir/PURE_sScS < degrees.dat > /dev/null;
$t -mod prem --time -ph sScSScS -h $h -o $time_dir/PURE_sScS2 < degrees.dat > /dev/null;
$t -mod prem --time -ph sScSScSScS -h $h -o $time_dir/PURE_sScS3 < degrees.dat > /dev/null;

for i in $(seq 50 5 800); 
do
    mod=prem$i
    sScS_1=sSv$i"SScS"
    ScS2=ScS^$i"ScS"
    sScS2_1=sSv$i"SScSScS"
    ScS3_1=ScS^$i"ScSScS"
    sScS3_1=sSv$i"SScSScSScS"

    $t -mod $mod --time -ph $sScS_1 -h $h -o $time_dir/sScS_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $ScS2 -h $h -o $time_dir/ScS2_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $sScS2_1 -h $h -o $time_dir/sScS2_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $ScS3_1 -h $h -o $time_dir/ScS3_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $sScS3_1 -h $h -o $time_dir/sScS3_$i < degrees.dat > /dev/null;
done



