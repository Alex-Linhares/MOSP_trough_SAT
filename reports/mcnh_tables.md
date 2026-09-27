# MCNh (2004) against `mcn` and the two-key rule: tables

*Written by `python -m learning.mcnh --stage report`; every table of `reports/ml_nature.md` §29 in full. Over the optimum, 6,376 certified instances at 9–134 customers.*

## The paper's example

```
{
 "loops": 7,
 "xi": 4,
 "loop_arcs_match": true,
 "arc_match": true,
 "states_match": true,
 "sequence_match:nodes": true,
 "fig2_match:nodes": true,
 "sequence:nodes": [
  11,
  10,
  14,
  2,
  4,
  6,
  12,
  3,
  9,
  1,
  7,
  5,
  8,
  13
 ],
 "sequence_match:arcs": true,
 "fig2_match:arcs": true,
 "sequence:arcs": [
  11,
  10,
  14,
  2,
  4,
  6,
  12,
  3,
  9,
  1,
  7,
  5,
  8,
  13
 ]
}
```

## Over the optimum, whole corpus

| strategy | instances | MAE | exact | worst | total over | ms |
|---|---|---|---|---|---|---|
| mcnh | 6,376 | 0.361 | 79.6% | 13 | 2,302 | 0.94 |
| mcnh-arcs | 6,376 | 0.361 | 79.6% | 13 | 2,302 | 1.12 |
| mcn | 6,376 | 1.343 | 54.9% | 32 | 8,564 | 0.38 |
| rule | 6,376 | 0.279 | 83.3% | 10 | 1,781 | 0.27 |

## By size band

| customers | instances | MAE mcnh | exact mcnh | MAE mcnh-arcs | exact mcnh-arcs | MAE mcn | exact mcn | MAE rule | exact rule |
|---|---|---|---|---|---|---|---|---|---|
| 9–30 | 5,938 | 0.231 | 83.1% | 0.231 | 83.1% | 0.924 | 57.8% | 0.177 | 86.8% |
| 31–60 | 318 | 1.255 | 40.9% | 1.255 | 40.9% | 4.311 | 21.7% | 0.940 | 46.9% |
| 61–134 | 120 | 4.442 | 10.0% | 4.442 | 10.0% | 14.217 | 0.0% | 3.608 | 10.0% |

## By collection

| collection | instances | MAE mcnh | MAE mcnh-arcs | MAE mcn | MAE rule |
|---|---|---|---|---|---|
| ChallengeInstances2005/Harvey | 2,130 | 0.305 | 0.305 | 1.124 | 0.223 |
| ChallengeInstances2005/Miller | 1 | 0.000 | 0.000 | 1.000 | 0.000 |
| ChallengeInstances2005/Shaw | 25 | 0.360 | 0.360 | 1.800 | 0.360 |
| ChallengeInstances2005/Simonis | 3,630 | 0.154 | 0.154 | 0.699 | 0.127 |
| ChallengeInstances2005/Wilson | 20 | 0.600 | 0.600 | 5.700 | 0.900 |
| MOSP_Instances/Challenge | 46 | 0.457 | 0.457 | 3.478 | 0.587 |
| MOSP_Instances/Chu_Stuckey | 200 | 3.000 | 3.000 | 9.620 | 2.350 |
| MOSP_Instances/Faggioli_Bentivoglio | 300 | 1.343 | 1.343 | 4.280 | 0.967 |
| MOSP_Instances/SCOOP | 24 | 1.958 | 1.958 | 4.292 | 1.208 |

## Head to head (instances where the first is below / equal / above the second)

| first | second | better | equal | worse |
|---|---|---|---|---|
| mcnh | mcn | 2,528 | 3,787 | 61 |
| mcnh | rule | 242 | 5,542 | 592 |
| mcnh | mcnh-arcs | 0 | 6,376 | 0 |
| rule | mcn | 2,663 | 3,686 | 27 |

## Is the rule MCNh under another name?

| quantity | value |
|---|---|
| instances | 6,376.000 |
| same value (mcnh = rule) | 5,542.000 |
| same closing order | 37.000 |
| same pattern sequence | 51.000 |
| mean positional agreement of closing orders | 0.223 |
| steps with a choice | 134,077.000 |
| MCNh pick attains rule key 1 | 0.988 |
| MCNh pick attains rule keys 1+2 | 0.792 |
| MCNh pick attains MCN key (min degree) | 0.734 |
| mcnh = mcnh-arcs sequence | 628.000 |
| mcnh = mcnh-arcs value | 6,376.000 |

| customers | instances | steps | key 1 | keys 1+2 | MCN key | same closing order |
|---|---|---|---|---|---|---|
| 9–30 | 5,938 | 108,746 | 99.2% | 83.3% | 78.0% | 0.6% |
| 31–60 | 318 | 13,584 | 97.4% | 72.2% | 66.0% | 0.0% |
| 61–134 | 120 | 11,747 | 96.2% | 49.0% | 39.8% | 0.0% |

## Frinhani et al. (2018) Table 2, MCNh column, against `mcnh` (MOSP_Instances/Challenge)

| instance | OPT | Frinhani MCNh | mcnh | mcnh-arcs | mcn | rule |
|---|---|---|---|---|---|---|
| GP1 | 45.000 | 45.000 | 45.000 | 45.000 | 45.000 | 45.000 |
| GP2 | 40.000 | 40.000 | 40.000 | 40.000 | 43.000 | 40.000 |
| GP3 | 40.000 | 40.000 | 40.000 | 40.000 | 45.000 | 43.000 |
| GP4 | 30.000 | 30.000 | 30.000 | 30.000 | 43.000 | 30.000 |
| GP5 | 95.000 | 96.000 | 96.000 | 96.000 | 98.000 | 96.000 |
| GP6 | 75.000 | 75.000 | 75.000 | 75.000 | 89.000 | 75.000 |
| GP7 | 75.000 | 75.000 | 75.000 | 75.000 | 96.000 | 75.000 |
| GP8 | 60.000 | 60.000 | 60.000 | 60.000 | 67.000 | 60.000 |
| Miller | 13.000 | 13.000 | 13.000 | 13.000 | 14.000 | 13.000 |
| NWRS1 | 3.000 | 3.000 | 3.000 | 3.000 | 3.000 | 3.000 |
| NWRS2 | 4.000 | 4.000 | 4.000 | 4.000 | 6.000 | 4.000 |
| NWRS3 | 7.000 | 7.000 | 7.000 | 7.000 | 7.000 | 7.000 |
| NWRS4 | 7.000 | 7.000 | 7.000 | 7.000 | 7.000 | 7.000 |
| NWRS5 | 12.000 | 12.000 | 12.000 | 12.000 | 12.000 | 12.000 |
| NWRS6 | 12.000 | 12.000 | 12.000 | 12.000 | 12.000 | 12.000 |
| NWRS7 | 10.000 | 10.000 | 10.000 | 10.000 | 10.000 | 10.000 |
| NWRS8 | 16.000 | 16.000 | 16.000 | 16.000 | 16.000 | 16.000 |
| SP1 | 9.000 | 9.000 | 9.000 | 9.000 | 12.000 | 10.000 |
| SP2 | 19.000 | 23.000 | 23.000 | 23.000 | 26.000 | 22.000 |
| SP3 | 34.000 | 37.000 | 37.000 | 37.000 | 49.000 | 40.000 |
| SP4 | 53.000 | 57.000 | 57.000 | 57.000 | 74.000 | 57.000 |
| Shaw (mean of 25) | 13.680 | 14.000 | 14.040 | 14.040 | 15.480 | 14.040 |

Named rows: `mcnh` equals Frinhani's MCNh on 21 of 21, below it on 0, above it on 0; sums 671 against 671 (OPT 659).

## Frinhani et al. (2018) Fig. 6, SCOOP: MCNh gap buckets

| method | instances | optimal | 1–10% | 11–25% | >25% | total value | total gap % | largest gap % |
|---|---|---|---|---|---|---|---|---|
| mcnh | 24 | 7 | 0 | 8 | 9 | 233 | 25.27 | 57.14 |
| mcnh-arcs | 24 | 7 | 0 | 8 | 9 | 233 | 25.27 | 57.14 |
| mcn | 24 | 2 | 0 | 1 | 21 | 289 | 55.38 | 142.86 |
| rule | 24 | 12 | 1 | 8 | 3 | 215 | 15.59 | 45.45 |
| Frinhani MCNh (Fig. 6) | 24 | 8 | 0 | 7 | 9 | 233 | 25.27 | 60.00 |

SCOOP total optimum here: 186 (Frinhani: 186).

`mcnh` gaps, sorted: [57.14, 45.45, 44.44, 41.18, 38.46, 36.36, 33.33, 33.33, 27.27, 25.0, 22.22, 20.0, 20.0, 16.67, 16.67, 16.67, 16.67, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

Frinhani's labelled MCNh gaps: [60.0, 57.14, 47.06, 45.0, 44.44, 38.46, 36.36, 33.33, 33.33, 20.0, 18.18, 16.67, 16.67, 16.67, 16.67, 11.11] plus 8 zeros.

## Where `mcnh` and the rule differ most (over the optimum)

| instance | n_customers | optimum | value:mcnh | value:mcn | value:rule | d |
|---|---|---|---|---|---|---|
| Random-125-125-4-5_0 | 125 | 46 | 59 | 78 | 51 | 8 |
| Random-100-100-2-5_0 | 100 | 19 | 29 | 39 | 24 | 5 |
| Random-100-100-4-1_0 | 100 | 46 | 52 | 62 | 47 | 5 |
| Random-125-125-2-3_0 | 125 | 21 | 34 | 47 | 29 | 5 |
| Random-40-40-2-4_0 | 40 | 7 | 13 | 15 | 8 | 5 |
| Warwick 1022: balanced orders, 2 orders per product | 20 | 3 | 7 | 5 | 3 | 4 |
| Warwick 1713: balanced orders, 2 orders per product | 30 | 3 | 8 | 9 | 4 | 4 |
| Warwick 1729: balanced orders, 3 orders per product | 30 | 9 | 13 | 13 | 9 | 4 |
| Warwick 1346: balanced orders, 11 orders per product | 30 | 20 | 20 | 24 | 23 | -3 |
| Warwick 1471: balanced orders, 4 orders per product | 30 | 7 | 7 | 13 | 10 | -3 |
| HS problem 1114 size 30 10 density  0.20 | 30 | 13 | 13 | 19 | 16 | -3 |
| GP3:  50 customers,  50 products,  medium path width | 50 | 40 | 40 | 45 | 43 | -3 |
