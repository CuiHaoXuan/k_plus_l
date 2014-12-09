#!/bin/sh -
# ======================================================================
# This script is to run the experiments for different scenarios
# The arguments are:
# 	- topo_type: ring/grid/
# 	- model_type: mcr/lb/ad
#	- num_nodes: 4, 9, 16, 25, 36, 49, 64, 81, 100
# 	- num_paths: ring: 2, grid: 5
# 	- d_type (demand type): uniform, uniforme1n, uniformeij, nonuniform, 
# 							nonuniformh, nonuniforme1n, nonuniformeij
# 	- dc_type: ring: a (adjacent), f (far away); 
# 				grid: s (side adjacent), c (corner), a (inside adjacent)
# 	- bin (real variable or binary variable): yes, no
#   - cost_type: byhops/rand
#
# This script will call <topo>_run.sh to create cplex file based on the 
# scenario
#
#   Code by Xuan Liu
# 	Dec. 29, 2013
# ======================================================================

# treat unset variable as an error
set -o nonnset

# read arguments from cmd line
topo_type=$1
dc_type=$2
bin=$3
cost_type=$4


# topology specific run
run_topo=$topo_type'_run.sh'
echo "script" $run_topo

if [ $topo_type = "ring" ]
	then
	num_paths=2
fi

if [ $topo_type = "grid" ]
	then
	num_paths=5
fi

if [ $bin = "yes" ]
	then
	file_extend="_bin"
else
	file_extend=""
fi

echo "file extend name: " $file_extend

echo "topo_type =" $topo_type  " binary variable x? " $bin
echo "num_paths = " $num_paths


# create log information
HomeD=`pwd`
Date=`date +"%m-%d-%y"`
Time=`date +"%H-%M"`
expr_time=$Date-$Time
echo "experiment time: " $expr_time
mkdir $HomeD/$topo_type

# create result folder
#result=$HomeD/"result"-$expr_time-$$
result=$HomeD/"result"-$topo_type-$dc_type-$bin-$cost_type-$$
echo "result folder: " $result

# create result folder
if [ ! -d $result ]
then
	echo "create result folder" $result
    mkdir $result
else
    echo "result folder exists!"
fi

# Collect Result file
collect=$HomeD/$topo_type-$dc_type-$bin-$$.txt
echo "Collect results at " $collect
rm -f $collect
touch $collect

echo `date` >> $collect
echo $HomeD >> $collect
echo "scenario" $topo_type $dc_type $bin $cost_type >>$collect

# run experiment
# /bin/bash ring_run.sh lb 16 2 uniform n yes 100 byhops(ring topology with binary variable)
# Grid Topology: /bin/bash grid_run.sh mcr 9 5 uniform n no 100 byhops (minimum 9 nodes, five paths)
for node in 9 #4 9 16 25 36 49 64 #81
do
	if [ $node = 4 ]
		then
		num_paths=2
		if [ $2 != 'n' ]
			then
			dc_type='c'
		else
			dc_type=$2
		fi 
	else
		num_paths=5
		dc_type=$2
	fi

	if [ $dc_type = 'n' ] 
		then
		# for non-DC cases, the total demand pairs are C(n,2), where n is the number of nodes
		d_pairs=`echo $node \\* \($node-1\) \\* 0.5 | bc -l`
    	echo "Number of Nodes = " $node "Number of Demand Pairs = " $d_pairs
    else
    	# for with DC cases, the total demand pairs are (n-2)*2, where n is the number of nodes
  		d_pairs=`echo \($node-2\) \\* 2 | bc -l`
    	echo "Number of Nodes = " $node "Number of Demand Pairs = " $d_pairs
    fi 
	for load_type in uniform #uniformeij nonuniform nonuniformh #uniformeij nonuniform nonuniformh #uniforme1n uniformeij nonuniform nonuniformh nonuniforme1n nonuniformeij #uniforme1n uniformeij 
	do
		# first find feasible capacity
		capacity=100
		for obj_type in lb #ad mcr
		do
			currdata_dir=$HomeD/$topo_type/$obj_type
			echo "current data dir: " $currdata_dir
			if [ ! -d $currdata_dir ]
				then
					echo "create run folder" $currdata_dir
					mkdir $currdata_dir
				else
					echo $currdata_dir "aleady exists"
				fi 
			for count in 37  #101 239 457 919
			do		
				echo "seed # " $count
				obj_lb=lb
				#echo "/bin/bash" $run_topo $obj_lb $node 5 $load_type $dc_type "no 100" $cost_type
				echo "/bin/bash" $run_topo $obj_lb $node $num_paths $load_type $dc_type "no 100" $cost_type
				echo `/bin/bash $run_topo $obj_lb $node $num_paths $load_type $dc_type no 100 $cost_type $count`
				#echo `/bin/bash $run_topo $obj_lb $node 5 $load_type $dc_type no 100 $cost_type $count`
				# create folder for each run
				run_dir=$currdata_dir/"seed"$count
				echo "RUN: " $run_dir
				if [ ! -d $run_dir ]
				then
					echo "create run folder" $run_dir
					mkdir $run_dir
				else
					echo $run_dir "aleady exists"
				fi 
				# run lb first to get the base capacity information, the file is created at $HomeD/$topo_type/lb/.
				lpfilename=$HomeD/$topo_type/$obj_lb/$topo_type'_'$node'_'$obj_lb'_'$load_type'_'$dc_type'_'$capacity".lp"
				echo "new lp file: " $lpfilename
				RR=`(echo "read $lpfilename"; echo "set mip limits nodes 30000"; echo "opt"; echo "dis sol var -")| cplex | grep RR | awk '{print $2}'`
				CapBase=`echo $RR \\* $capacity | bc -l | awk '{ printf("%.4f\n",$1) }'`
				echo "Base Capacity = " $CapBase
				echo "RR capacity base-capacity" $RR $capacity $CapBase >> $collect
				rm -f $lpfilename
				redun_dat=$HomeD/$topo_type/$obj_lb/$topo_type'_'$node'_'$obj_lb'_'$load_type'_'$dc_type'_'$capacity".dat"
				redun_expand=$HomeD/$topo_type/$obj_lb/$topo_type'_'$node'_'$obj_lb'_'$load_type'_'$dc_type'_'$capacity".txt"
				echo $redun_expand $redun_dat
				rm $redun_dat
				rm $redun_expand
				for load_level in 0.4 #0.6 0.8 0.9 0.95 #0.999
				do
					echo "Current Run DIR: " $run_dir
					new_cap=`echo $CapBase \/ $load_level  | bc -l | awk '{ printf("%.4f\n",$1) }'`
					echo "new capacity = " $new_cap
					lpfile_newcap=$currdata_dir/$topo_type'_'$node'_'$obj_type'_'$load_type'_'$dc_type'_'$new_cap$file_extend".lp"
					echo "lp file with new capacity: " $lpfile_newcap
					echo "/bin/bash $run_topo $obj_type $node $num_paths $load_type $dc_type $bin $new_cap $cost_type $count"
					echo `/bin/bash $run_topo $obj_type $node $num_paths $load_type $dc_type $bin $new_cap $cost_type $count`
					(echo "read $lpfile_newcap"; echo "set mip limits nodes 30000"; echo "opt";echo "dis sol var -") | cplex > $lpfile_newcap.log
					echo "LOG:" $lpfile_newcap.log
					#MPMc=`egrep x_ $lpfile_newcap.log | wc -l`
					if [ $bin = "no" ]
						then
						MPMc=`egrep x_ $lpfile_newcap.log | awk ' BEGIN { last=""} { split($1,a,"_"); aa = a[1] "_" a[2]; if ( aa != last ) \
							{ count++; last = aa; track=0 } else { if (track == 0) {count++; track=1} }} END { print count } '`
					else
						MPMc=`egrep x_ $lpfile_newcap.log | awk ' BEGIN{ count = 0 } { if ($2 > 0.0) count++} END { print count }'`
					fi
					echo $MPMc
					# the code below only works for ring topology
					MPM=`echo \($MPMc \- $d_pairs\) \/ $d_pairs \\* 100 | bc -l | awk '{ printf("%.2f\n",$1) }'`
					echo $MPM

					# the following pattern for using egrep is important as it works for both real and binary solution generated from cplex
               		#  Note Optimal, or, Infeasible (mainly for binary case)
               		Optimal=`egrep ":  Objective =|infeasible" $lpfile_newcap.log | awk ' END {  {print $NF}  }'`
               		echo "TEST: " $Optimal
               		#             
               		DualityGap=`fgrep gap  $lpfile_newcap.log |  awk ' { gap = substr($NF,1,length($NF)-2) + 0; if ( gap > 1.0 ) print gap }'`
               		echo "TEST: " $DualityGap
               		echo "file: " $lpfile_newcap.log $count " : " $topo_type $dc_type $bin $obj_type $Optimal $load_type $load_level $new_cap $node $d_pairs $MPMc $MPM $DualityGap >> $collect

               		rm -f $currdata_dir/cplex.log
               		#echo "Run DIR: " $run_dir 
               		#echo "New Cap LP FILE: " $lpfile_newcap 
               		#echo "New Cap LP RUN LOG: " $lpfile_newcap.log
               		mv $lpfile_newcap $run_dir/.
               		mv $lpfile_newcap.log $run_dir/.
               		#compress $run_dir/. $lpfile_newcap
               		other_file=$currdata_dir/$topo_type'_'*
               		#echo "other files" $other_file
               		mv $other_file $run_dir/.
				done

			done
		done
	done
done
mv $collect $HomeD/$topo_type/.
mv $HomeD/$topo_type $result/.
rm $HomeD/cplex.log



