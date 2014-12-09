param D >0 integer;
param E>0 integer;
param N>0 integer;
param Pd>0 integer;
param T>0 integer;

set Nodes:= 1..N;
set link_nos:= 1..E;
set demand_nos:= 1..D;
set route_nos:=  1..Pd;
set hours_nos:=1..T;

#generation of links
param link_src{link_nos} within Nodes;
param link_dest{link_nos} within Nodes;
param link_capacity{link_nos} >=0 integer;

#generation of demands
param demand_src{demand_nos} within Nodes;
param demand_dest{demand_nos} within Nodes;
param time_demand{hours_nos} within hours_nos;

#generation of routes
set Routes{demand_nos,route_nos,hours_nos} within link_nos;


param h{demand_nos,hours_nos}>=0 ;

#generation of variables 
var x{d in demand_nos,p in route_nos,t in hours_nos}>=0;
var r;

#generation of variables required for optimization
param delta{e in link_nos,d in demand_nos,p in route_nos,t in hours_nos} = if e in Routes[d,p,t] then 1 else 0;


minimize link_utilization: r;

subject to all_demands{d in demand_nos,t in hours_nos}:sum{p in route_nos}(x[d,p,t])=h[d,t];

#formulation for minimizing link_utilization
subject to capacity_constraints{e in link_nos,t in hours_nos}:sum{d in demand_nos}sum{p in route_nos}(delta[e,d,p,t]*x[d,p,t])-link_capacity[e]*r<=0;



