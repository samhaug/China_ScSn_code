#!/bin/bash
h=578.7
t=taup_path
                              
$t -mod prem -ph ScSScS -h $h -o ./paths/PURE_ScS2 < degrees.dat >/dev/null;
$t -mod prem -ph ScSScSScS -h $h -o ./paths/PURE_ScS3 < degrees.dat >/dev/null;
$t -mod prem -ph sScS -h $h -o ./paths/PURE_sScS < degrees.dat >/dev/null;
$t -mod prem -ph sScSScS -h $h -o ./paths/PURE_sScS2 < degrees.dat >/dev/null;
$t -mod prem -ph sScSScSScS -h $h -o ./paths/PURE_sScS3 < degrees.dat >/dev/null;

for i in $(seq 50 5 1800); 
do
    echo $i
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


    $t -mod $mod -ph $sScS_1 -h $h -o ./paths/sScS_1_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS_2 -h $h -o ./paths/sScS_2_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $ScS2 -h $h -o ./paths/ScS2_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS2_1 -h $h -o ./paths/sScS2_1_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS2_2 -h $h -o ./paths/sScS2_2_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS2_3 -h $h -o ./paths/sScS2_3_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $ScS3_1 -h $h -o ./paths/ScS3_1_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $ScS3_2 -h $h -o ./paths/ScS3_2_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS3_1 -h $h -o ./paths/sScS3_1_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS3_2 -h $h -o ./paths/sScS3_2_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS3_3 -h $h -o ./paths/sScS3_3_$i < degrees.dat >/dev/null;
    $t -mod $mod -ph $sScS3_4 -h $h -o ./paths/sScS3_4_$i < degrees.dat >/dev/null;
done



