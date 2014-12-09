#!/bin/sh -
# ==========================================================
# This script is to run ring topology scenario
# The arguments are model, num of nodes, demand type
# It takes three models:
#    - mcr: minimum cost routing
#    - lb: load balancing
#  	 - ad: average network delay
# The number of nodes varies from 4, 9, 16, ..., 49
# The number of paths is based on the size and topo_type of 
# the network. 
# The demand type is uniform(fixed) or non-uniform, based on 
# topology type
# dc_type: based on the topology type
# bin: determin whether the variable is binary or not, selecting
# proper ampl model file 
#
# Code by Xuan Liu
# Dec. 22, 2013
# ==========================================================

set -o nounset                              # Treat unset variables as an error

topo_type="ring"
model_type=$1
num_nodes=$2
num_paths=$3
demand=$4
dc_type=$5
bin=$6
cap=$7
cost_type=$8

# declare directory info for results
result_folder=$topo_type
echo "Result Folder" $result_folder
sub_dir=$model_type
echo "Sub folder" $sub_dir

## -- existing folder --
# directory for ample data file
ampl_data_dir="data_files"
# directory for path file
path_dir="topo_info/path"
# corresponding path file
path_file=$path_dir/$topo_type'_'$num_nodes'_path.txt'
echo "Path file: " $path_file

# csv file directory
csv_dir="topo_info/topo_csv"
# corresonding csv file
csv_file=$csv_dir/$topo_type'_'$num_nodes'.csv'
echo "CSV file: " $csv_file

# ampl model directory
model_dir="model_files"
if [ $bin == "yes" ]
then 
	model_file=$model_dir/$model_type"_bin.mod"
	echo "model file with binary variable" $model_file
else
	model_file=$model_dir/$model_type".mod"
	echo "model file with no binary variable" $model_file
fi

## -- script information --
# python module to create ample data file
ampl_gen="model_create.py"
# python modeul to create model and generate ampl data file
model_gen="net_model.py"
# python module to convert expanded equations to .lp file
cplex_convert="convert_ampl.py"

## -- new files --
# new ampl data file
if [ $bin == "no" ]
then
	ampl_data=$topo_type'_'$num_nodes'_'$model_type'_'$demand'_'$dc_type'_'$cap".dat"
	expand_equa=$topo_type'_'$num_nodes'_'$model_type'_'$demand'_'$dc_type'_'$cap".txt"
	cplex_file=$topo_type'_'$num_nodes'_'$model_type'_'$demand'_'$dc_type'_'$cap".lp"
else
	ampl_data=$topo_type'_'$num_nodes'_'$model_type'_'$demand'_'$dc_type'_'$cap"_bin.dat"
	expand_equa=$topo_type'_'$num_nodes'_'$model_type'_'$demand'_'$dc_type'_'$cap"_bin.txt"
	cplex_file=$topo_type'_'$num_nodes'_'$model_type'_'$demand'_'$dc_type'_'$cap"_bin.lp"
fi

echo "new ampl data file: " $ampl_data
echo "new expanded equation file: " $expand_equa
echo "new cplex file: " $cplex_file


# create result folder
if [ ! -d $result_folder ]
then
	echo "create result folder" $result_folder
    mkdir $result_folder
else
    echo "result folder exists!"
fi


if [ ! -d $result_folder/$sub_dir ]
then
	echo "create sub folder" $sub_dir
    mkdir $result_folder/$sub_dir
else
    echo "sub folder exists!"
fi

# create ample data file
#echo `python $ampl_gen -w $result_folder/$sub_dir/$ampl_data \
#		--pfile $path_file --csv $csv_file -m $model_type \
#		-t $topo_type --np 2 --lc 100`

echo `python $model_gen -w $result_folder/$sub_dir/$ampl_data \
		--pfile $path_file --csv $csv_file -m $model_type  \
		-t $topo_type -d $demand --np $num_paths --lc $cap \
		--dc $dc_type --nn $num_nodes -c $cost_type`

# run ampl to create expanded equations
( echo "model $model_file;"; \
	echo "data $result_folder/$sub_dir/$ampl_data;"; \
	echo "expand;"; \
	echo "quit;" ) | ampl > $result_folder/$sub_dir/$expand_equa

# convert expanded equations to .lp file
model_dir="model_files"
if [ $bin == "no" ]
then 
	# do not print variables
	echo `python $cplex_convert -r $result_folder/$sub_dir/$expand_equa \
		 -w $result_folder/$sub_dir/$cplex_file --obj total_cost`
else
	# indicate x is binary variable
	echo `python $cplex_convert -r $result_folder/$sub_dir/$expand_equa \
		 -w $result_folder/$sub_dir/$cplex_file -b "['x']" \
		 --obj total_cost`
fi

