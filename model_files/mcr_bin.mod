##  AMPL Model File
#   min-cost routing model

## -- Define set boundary --
# number of demand pairs
param D > 0 integer;

# number of links
param L > 0 integer;

# number of nodes
param N > 0 integer;

## -- Define sets --
# demand volume of demand index d = 1 ... D
set demand := 1 .. D by 1;

# link sets
set links := 1 .. L by 1;

# Node sets
set nodes := 1 .. N by 1;

# number of paths by demand d
param Pd{d in demand} > 0 integer;

# Paths sets per demand pair
set P{d in demand} := 1 .. Pd[d] by 1;


## -- Define Links Parameters --
param link_src{l in links} within nodes;
param link_dst{l in links} within nodes;
param link_capacity{l in links} >= 0;

## -- Define Demand Pairs --
param demand_src{d in demand} within nodes;
param demand_dst{d in demand} within nodes;


## -- Define Paths set --
set paths{d in demand, p in P[d]} within links;

## -- Define Path Parameters --
# unit cost of flow on path for demand d
param cost{d in demand, p in P[d]} >= 0;

## -- Define node-pair demand volume --
param h{d in demand} > 0 ;

# link-path indicator, set to 1 if path p for demand pair d uses link l; otherwise is 0
param delta{d in demand, p in P[d], l in links} = if l in paths[d,p] then 1 else 0;


## -- Define Variables --
# flow amount on path p for demand k
var x{d in demand, p in P[d]} >= 0 integer;


## -- Objective Equation --
minimize total_cost:
sum{d in demand, p in P[d]} cost[d,p]*h[d]*x[d,p];

## -- Constraints --
subject to d_pair{d in demand}: sum{p in P[d]} x[d,p] = 1;

subject to cl{l in links}: sum{d in demand, p in P[d]} delta[d,p,l] * h[d] * x[d,p] <= link_capacity[l];




