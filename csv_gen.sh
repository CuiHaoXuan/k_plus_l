#!/bin/sh -
# ======================================================================
# This script is to create csv file for each case
# The input is the result folder name
#   Code by Xuan Liu
# 	Jan. 5, 2013
# ======================================================================



res_folder=$1
topo_type=$2

HomeD=`pwd`
res_dir=$HomeD/$res_folder/$topo_type
res_file=`ls $res_dir/*.txt`
echo $res_file
dc_type=$(echo $1 | cut -f3 -d-)
bin=$(echo $1 | cut -f4 -d-)
cost_type=$(echo $1 | cut -f5 -d-)
echo $dc_type $bin $cost_type

#generate csv files
for obj_type in lb ad mcr
do
	for load_type in  nonuniformh #uniform uniformeij nonuniform nonuniformh #nonuniformh #uniform uniformeij nonuniform nonuniformh #uniforme1n uniformeij nonuniform nonuniformh nonuniforme1n nonuniformeij  
	do
		csv_file=$res_dir/$topo_type-$dc_type-$bin-$cost_type-$obj_type-$load_type".csv"
		obj_csvfile=$res_dir/$topo_type-$dc_type-$bin-$cost_type-$obj_type-$load_type"_obj.csv"
		echo $csv_file
		echo "python parse_result.py -r $res_file -w $csv_file -W $obj_csvfile --obj $obj_type --load $load_type"
		echo `python parse_result.py -r $res_file -w $csv_file -W $obj_csvfile --obj $obj_type --load $load_type`
	done
done
