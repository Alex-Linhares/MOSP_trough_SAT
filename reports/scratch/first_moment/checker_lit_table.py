"""CHECKER: published lower bounds on pw/n (or tw/n) for G(n, c/n) at the table's c, against beta*(c)."""
from math import log, sqrt
import sys
sys.path.insert(0, '/home/al/dev/MOSP/reports/scratch/first_moment')
from checker_beta_star import beta_star
print("c | beta*(FM) | PS2014 tw: 1-sqrt(9ln3/(2c)) | DPST2001 (g5) as stated: 1/2-eps, eps=sqrt(3(1+ln3)/c) (gamma->1), needs eps<1/6 i.e. c>=226.6 | DPST improved (1-2eps) | DPST with exact empty-pair count 3^n: eps=sqrt(ln3/c), 1-2eps")
for c in (3,4,5,6,8,10,12,16,20,50,100,227,1000):
    b = beta_star(c)
    ps = 1 - sqrt(9*log(3)/(2*c)); ps = ps if c > 9*log(3)/2 else float('nan')
    eps = sqrt(3*(1+log(3))/c)
    dp = 0.5 - eps if eps < 1/6 else float('nan')
    dp_informal = 0.5 - eps if eps < 0.5 else float('nan')
    dpi = 1 - 2*eps if eps < 0.5 else float('nan')
    eps3 = sqrt(log(3)/c)
    dp3 = 1 - 2*eps3 if eps3 < 0.5 else float('nan')
    print(f"{c:5} | {b:.3f} | {ps:.3f} | {dp:.3f} (informal, eps<1/2 only: {dp_informal:.3f}) | {dpi:.3f} | {dp3:.3f}")
