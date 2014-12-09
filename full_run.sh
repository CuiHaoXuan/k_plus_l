#!/bin/sh -
# =======================================
# This script is to run all scenarios
#  - topology: grid
#  - dc_type: 'n'/ 's' / 'c' / 'a'
#  - bin: 'no' / 'yes'
#  - cost_type: 'byhops' / 'rand'
#  
#  by Xuan Liu
#  Jan 3, 2014
# =======================================

topo_type=$1

expr_script="expr_run.sh"

if [ $topo_type = "grid" ]
	then

	for bin in no yes
	do
		for dc_type in c a #n s c a 
		do 
			for cost_type in byhops rand
			do
				echo `/bin/bash $expr_script $topo_type $dc_type $bin $cost_type`
			done
		done
	done
fi
