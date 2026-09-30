"""Published values to compare against.

Coudert, Mazauric & Nisse, JEA 2016, Table 4 (TreewidthLIB, BAB-GPP, 10 min
cap; times on a 3.2 GHz Xeon): name -> (pathwidth, seconds). Only the graphs
present in the TreewidthLIB `coloring.zip` we hold. Mycielski values from their
Table 1 (DIMACS `mycielk` has 2^(k+1)−1 vertices: myciel3 = M4 ... myciel7 = M8).
"""

COUDERT_TABLE4 = {
    "david": (13, 99.47), "games120": (32, 148.4), "miles750": (36, 51.19),
    "miles1000": (49, 0.696), "miles1500": (77, 0.098), "mulsol.i.5": (31, 67.31),
    "queen5_5": (18, 0.004), "queen6_6": (25, 0.008), "queen7_7": (35, 0.022),
    "queen8_8": (45, 0.093), "queen8_12": (65, 4.262), "queen9_9": (58, 1.851),
    "queen10_10": (72, 25.92), "zeroin.i.1": (50, 0.937),
}
COUDERT_MYCIELSKI = {"myciel3": 5, "myciel4": 10, "myciel5": 20, "myciel6": 38, "myciel7": None}  # M8 <= 72, open

# VSPLIB (Coudert et al. §4.6): exact for grids gamma <= 13 (pw = gamma), trees
# with n <= 67 (pw 3 for 22 nodes, 4 for 67, 5 for 202), 26 of 73 hb graphs.
# Rome graphs (§4.4): 95.6% solved in 10 min, all with n <= 82.
