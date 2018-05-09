#!/bin/bash
h=551
t=taup_time
                              
$t -mod prem --time -ph ScSScS -h $h -o ./time/PURE_ScS2 < degrees.dat > /dev/null;
$t -mod prem --time -ph ScSScSScS -h $h -o ./time/PURE_ScS3 < degrees.dat > /dev/null;
$t -mod prem --time -ph sScS -h $h -o ./time/PURE_sScS < degrees.dat > /dev/null;
$t -mod prem --time -ph sScSScS -h $h -o ./time/PURE_sScS2 < degrees.dat > /dev/null;
$t -mod prem --time -ph sScSScSScS -h $h -o ./time/PURE_sScS3 < degrees.dat > /dev/null;

for i in $(seq 50 5 800); 
do
    #echo $i
    mod=prem$i
    sScS_1=sSv$i"SScS"
    sScS_2=sScSSv$i"S"
    ScS2=ScS^$i"ScS"
    sScS2_1=sSv$i"SScSScS"
    sScS2_2=sScSSv$i"SScS"
    sScS2_3=sScSScSSv$i"S"
    ScS3_1=ScS^$i"ScSScS"
    ScS3_2=ScSScS^$i"ScS"
    sScS3_1=sSv$i"SScSScSScS"
    sScS3_2=sScSSv$i"SScSScS"
    sScS3_3=sScSScSSv$i"SScS"
    sScS3_4=sScSScSScSSv$i"S"

    $t -mod $mod --time -ph $sScS_1 -h $h -o ./time/sScS_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $sScS_2 -h $h -o ./time/sScS_2_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $ScS2 -h $h -o  ./time/ScS2_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $sScS2_1 -h $h -o ./time/sScS2_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $sScS2_2 -h $h -o ./time/sScS2_2_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $sScS2_3 -h $h -o ./time/sScS2_3_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $ScS3_1 -h $h -o ./time/ScS3_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $ScS3_2 -h $h -o ./time/ScS3_2_$i < degrees.dat > /dev/null;
    $t -mod $mod --time -ph $sScS3_1 -h $h -o ./time/sScS3_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $sScS3_2 -h $h -o ./time/sScS3_2_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $sScS3_3 -h $h -o ./time/sScS3_3_$i < degrees.dat > /dev/null;
    #$t -mod $mod --time -ph $sScS3_4 -h $h -o ./time/sScS3_4_$i < degrees.dat > /dev/null;
done



