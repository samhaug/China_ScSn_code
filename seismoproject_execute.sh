#/bin/bash 
                                                                                
#--read_catalog $read_catalog                                                   
echo "# Sample PBS for parallel jobs'" > execute_submit.pbs 
echo "#PBS -A seismoproject_fluxod"    >>execute_submit.pbs
echo "#PBS -q fluxod"                  >>execute_submit.pbs 
echo "#PBS -l qos=flux"                >>execute_submit.pbs     
echo "#PBS -N h5_submit"               >>execute_submit.pbs 
echo "#PBS -l nodes=1:ppn=1,pmem=8gb,walltime=48:00:00">>execute_submit.pbs    
echo "#PBS -d ."                       >>execute_submit.pbs  
echo "#PBS -m n"                       >>execute_submit.pbs   
echo "#PBS -V"                         >>execute_submit.pbs   
echo "#PBS -o execute.out"             >>execute_submit.pbs    
echo "#PBS -e execute.err"             >>execute_submit.pbs  
echo "ulimit -s unlimited "            >>execute_submit.pbs  
echo "./execute_data_moveout.sh"       >> execute_submit.pbs
qsub execute_submit.pbs                                                      
