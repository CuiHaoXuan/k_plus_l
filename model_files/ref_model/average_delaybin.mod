param D >0 integer;
param E>0 integer;
param N>0 integer;
param Pd>0 integer;
param T>0 integer;
#average delay changes
param AD>0 integer;#average_delay parameter from 1to 5#
param i>0 integer;#used to represent the sum of g slopes
#param j>0 integer; # used to represent the sum of y slopes#

set Nodes:= 1..N;
set link_nos:= 1..E;
set demand_nos:= 1..D;
set route_nos:=  1..Pd;
set hours_nos:=1..T;
set aver_delay:=1..AD;# average delay parameter#
set iter:=1..i;

#generation of links
param link_src{link_nos} within Nodes;
param link_dest{link_nos} within Nodes;
#param capacity{link_nos} >=0 integer;
param j_val{iter} >=0;
param k_val{iter} >= 0;

#generation of demands
param demand_src{demand_nos} within Nodes;
param demand_dest{demand_nos} within Nodes;
param time_demand{hours_nos} within hours_nos;
param capacity{link_nos} >=0 integer;
#generation of routes
set Routes{demand_nos,route_nos,hours_nos} within link_nos;


param h{demand_nos,hours_nos}>=0 ;

#generation of variables 
var u{d in demand_nos,p in route_nos,t in hours_nos} binary;
var link_capacity{link_nos} >=0;
var z{link_nos} >= 0;
#var z{g in aver_delay} >=0;
#generation of variables required for optimization
param delta{e in link_nos,d in demand_nos,p in route_nos,t in hours_nos} = if e in Routes[d,p,t] then 1 else 0;

minimize average_delay:sum{e in link_nos}(z[e]/capacity[e]);
#subject to all_demands{d in demand_nos,t in hours_nos}:sum{p in route_nos}(u[d,p,t])=h[d,t];
subject to path_constraint{d in demand_nos,t in hours_nos}:sum{p in route_nos}(u[d,p,t])=1;
subject to capacity_constraints{e in link_nos,t in hours_nos}:sum{d in demand_nos}sum{p in route_nos}(delta[e,d,p,t]*u[d,p,t]*h[d,t])<=link_capacity[e];

subject to delay{e in link_nos,n in iter}:(z[e])-(j_val[n]*link_capacity[e])>=-(k_val[n]*capacity[e]);
          
         
    