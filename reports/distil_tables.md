# Distilling the closing policy — regenerated tables

`python -m learning.distil --folds 5 --per-fold 400`; 6372 certified witnesses, 1920 held-out instances, fits 59 s, evaluation 132 s. The `mcn` construction here and `satisfiability.heuristics.upper_bound(instance, 'mcn')` disagree on 0 of 1920 held-out instances.

## Held-out constructions over the optimum

| strategy | mae | exact | worst | gain_kept |
|---|---|---|---|---|
| mcn | 1.616 | 0.502 | 26 | 0.000 |
| lgbm | 0.519 | 0.750 | 34 | 1.000 |
| lgbm+mcn-ties | 0.507 | 0.756 | 34 | 1.010 |
| tree | 0.992 | 0.600 | 18 | 0.569 |
| tree+index-ties | 1.749 | 0.355 | 23 | -0.121 |
| tree-fid | 1.090 | 0.559 | 21 | 0.480 |
| linear | 0.719 | 0.640 | 16 | 0.817 |
| linear-r | 0.729 | 0.635 | 16 | 0.808 |
| linear-fid | 1.240 | 0.553 | 26 | 0.343 |
| lex-selected | 0.362 | 0.792 | 9 | 1.143 |
| lex:min newly_opened | 0.419 | 0.791 | 11 | 1.091 |
| lex:min newly_opened,max remaining_degree | 0.348 | 0.807 | 9 | 1.155 |
| fiedler | 0.886 | 0.645 | 21 | 0.665 |
| fiedler-rev | 1.041 | 0.616 | 25 | 0.524 |
| bfs-fifo | 2.063 | 0.407 | 39 | -0.407 |
| cuthill-mckee | 1.520 | 0.512 | 27 | 0.088 |
| rcm | 1.113 | 0.554 | 19 | 0.458 |
| elim-min-degree | 1.985 | 0.492 | 34 | -0.336 |
| cs-dfs | 0.311 | 0.812 | 7 | 1.189 |
| cs-dfs+lgbm | 0.157 | 0.910 | 6 | 1.329 |
| cs-dfs+rule | 0.127 | 0.927 | 6 | 1.357 |

## MAE by size band

| band | instances | mcn | lgbm | lgbm+mcn-ties | tree | tree+index-ties | tree-fid | linear | linear-r | linear-fid | lex-selected | lex:min newly_opened | lex:min newly_opened,max remaining_degree | fiedler | fiedler-rev | bfs-fifo | cuthill-mckee | rcm | elim-min-degree | cs-dfs | cs-dfs+lgbm | cs-dfs+rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-30 | 1768 | 1.069 | 0.282 | 0.271 | 0.662 | 1.365 | 0.710 | 0.466 | 0.474 | 0.826 | 0.221 | 0.239 | 0.207 | 0.548 | 0.628 | 1.434 | 1.014 | 0.768 | 1.317 | 0.194 | 0.065 | 0.051 |
| 31-60 | 96 | 4.812 | 1.573 | 1.573 | 2.781 | 4.073 | 3.010 | 1.865 | 1.917 | 3.573 | 1.052 | 1.469 | 1.010 | 2.469 | 3.010 | 5.115 | 4.177 | 2.833 | 5.708 | 0.990 | 0.500 | 0.333 |
| 61-200 | 56 | 13.411 | 6.179 | 6.125 | 8.321 | 9.893 | 9.768 | 6.750 | 6.750 | 10.304 | 3.625 | 4.321 | 3.679 | 8.857 | 10.696 | 16.679 | 12.929 | 9.054 | 16.679 | 2.857 | 2.482 | 2.179 |

## MAE by collection

| collection | instances | mcn | lgbm | lex:min newly_opened | lex:min newly_opened,max remaining_degree | linear | fiedler | cs-dfs | cs-dfs+lgbm | cs-dfs+rule |
|---|---|---|---|---|---|---|---|---|---|---|
| Challenge | 17 | 3.471 | 2.353 | 0.588 | 0.706 | 0.706 | 1.353 | 0.176 | 0.118 | 0.118 |
| Chu_Stuckey | 91 | 9.440 | 3.352 | 2.901 | 2.418 | 5.187 | 6.692 | 2.121 | 1.648 | 1.352 |
| Faggioli_Bentivoglio | 125 | 3.856 | 0.984 | 1.280 | 0.968 | 1.344 | 1.896 | 0.984 | 0.464 | 0.400 |
| Harvey | 812 | 1.225 | 0.326 | 0.282 | 0.248 | 0.579 | 0.602 | 0.229 | 0.069 | 0.062 |
| SCOOP | 10 | 3.600 | 1.300 | 2.100 | 1.300 | 1.100 | 1.600 | 0.700 | 0.500 | 0.500 |
| Shaw | 25 | 1.800 | 0.320 | 0.280 | 0.360 | 0.880 | 1.080 | 0.160 | 0.000 | 0.000 |
| Simonis | 829 | 0.702 | 0.201 | 0.136 | 0.111 | 0.265 | 0.356 | 0.097 | 0.036 | 0.017 |
| Wilson | 11 | 4.091 | 6.818 | 0.091 | 0.091 | 0.545 | 0.545 | 0.182 | 0.091 | 0.000 |

## Head to head, held out

| first | second | first better | equal | first worse |
|---|---|---|---|---|
| lex:min newly_opened,max remaining_degree | lgbm | 253 | 1558 | 109 |
| lex:min newly_opened,max remaining_degree | mcn | 896 | 1016 | 8 |
| lex:min newly_opened,max remaining_degree | lex:min newly_opened | 159 | 1675 | 86 |
| lex-selected | lgbm | 238 | 1562 | 120 |
| linear | lgbm | 141 | 1334 | 445 |
| tree | lgbm | 121 | 1203 | 596 |
| fiedler | lgbm | 156 | 1263 | 501 |
| lex:min newly_opened,max remaining_degree | cs-dfs | 126 | 1641 | 153 |
| cs-dfs+rule | cs-dfs+lgbm | 82 | 1800 | 38 |
| cs-dfs+rule | cs-dfs | 285 | 1633 | 2 |
| cs-dfs+lgbm | cs-dfs | 243 | 1674 | 3 |

## Step-level agreement with the witness and with the ranker

| strategy | imitation | fidelity |
|---|---|---|
| lex:min newly_opened | 0.623 | 0.599 |
| lex:min newly_opened,max remaining_degree | 0.607 | 0.451 |
| tree | 0.585 | 0.555 |
| tree-fid | 0.551 | 0.503 |
| mcn | 0.525 | 0.468 |
| lgbm+mcn-ties | 0.520 | 0.863 |
| tree+index-ties | 0.467 | 0.516 |
| linear-r | 0.465 | 0.620 |
| lgbm | 0.453 | 1.000 |
| linear | 0.435 | 0.595 |
| linear-fid | 0.416 | 0.509 |

## Lexicographic rule selected per fold on training instances

| fold | rule | train_mae | held_out_mae | held_out_mcn | held_out_lgbm |
|---|---|---|---|---|---|
| 1 | lex:min newly_opened,max already_open,max remaining_degree | 0.280 | 0.220 | 0.865 | 0.302 |
| 2 | lex:min newly_opened,max remaining_degree,min already_open | 0.260 | 0.318 | 1.427 | 0.430 |
| 3 | lex:min newly_opened,max total_degree,min patterns | 0.265 | 0.722 | 3.247 | 1.259 |
| 4 | lex:min newly_opened,max remaining_degree,min already_open | 0.233 | 0.390 | 1.853 | 0.468 |
| 5 | lex:max already_open,min newly_opened,min patterns | 0.320 | 0.233 | 1.015 | 0.282 |

## Every lexicographic rule, pooled held out (descriptive; top 15)

| strategy | mae | exact | worst | gain_kept |
|---|---|---|---|---|
| lex:min newly_opened,max remaining_degree,min total_degree | 0.338 | 0.812 | 9 | 1.165 |
| lex:min newly_opened,max remaining_degree,min already_open | 0.346 | 0.808 | 9 | 1.157 |
| lex:min newly_opened,max remaining_degree,max already_open | 0.347 | 0.807 | 9 | 1.156 |
| lex:min newly_opened,max remaining_degree,max total_degree | 0.348 | 0.806 | 9 | 1.156 |
| lex:min newly_opened,max already_open,max remaining_degree | 0.348 | 0.807 | 9 | 1.155 |
| lex:min newly_opened,max remaining_degree | 0.348 | 0.807 | 9 | 1.155 |
| lex:min newly_opened,max remaining_degree,min patterns | 0.348 | 0.807 | 9 | 1.155 |
| lex:min newly_opened,max remaining_degree,max patterns | 0.351 | 0.805 | 10 | 1.153 |
| lex:min newly_opened,max already_open,max total_degree | 0.352 | 0.802 | 9 | 1.152 |
| lex:min newly_opened,max total_degree | 0.352 | 0.802 | 9 | 1.152 |
| lex:min newly_opened,max total_degree,max already_open | 0.352 | 0.802 | 9 | 1.152 |
| lex:min newly_opened,max total_degree,min remaining_degree | 0.352 | 0.802 | 9 | 1.152 |
| lex:min newly_opened,max total_degree,min patterns | 0.353 | 0.802 | 9 | 1.151 |
| lex:min newly_opened,max total_degree,max remaining_degree | 0.354 | 0.804 | 9 | 1.150 |
| lex:min newly_opened,max total_degree,min already_open | 0.354 | 0.802 | 9 | 1.150 |
| lex:min newly_opened,max total_degree,max patterns | 0.355 | 0.798 | 9 | 1.150 |
| lex:min newly_opened,min patterns,max total_degree | 0.365 | 0.799 | 11 | 1.140 |

## The fitted linear scorer, per fold (feature units, higher closes first)

| fold | remaining_degree | newly_opened | already_open | total_degree | rounded |
|---|---|---|---|---|---|
| 1 | -0.097 | -0.037 | 1.424 | 0.017 | -0.07·remaining_degree -0.03·newly_opened +1.00·already_open +0.01·total_degree |
| 2 | -0.092 | -0.061 | 1.317 | 0.015 | -0.07·remaining_degree -0.05·newly_opened +1.00·already_open +0.01·total_degree |
| 3 | -0.104 | -0.041 | 1.397 | 0.018 | -0.07·remaining_degree -0.03·newly_opened +1.00·already_open +0.01·total_degree |
| 4 | -0.095 | -0.059 | 1.286 | 0.015 | -0.07·remaining_degree -0.05·newly_opened +1.00·already_open +0.01·total_degree |
| 5 | -0.097 | -0.080 | 1.479 | 0.016 | -0.07·remaining_degree -0.05·newly_opened +1.00·already_open +0.01·total_degree |

Full coefficients including the per-step constants:

| fold | remaining_degree | newly_opened | already_open | open_after | open_now | progress | total_degree | n_customers |
|---|---|---|---|---|---|---|---|---|
| 1.000 | -0.097 | -0.033 | 1.424 | -0.004 | -0.000 | -0.138 | 0.017 | -0.010 |
| 2.000 | -0.092 | -0.056 | 1.317 | -0.005 | 0.001 | -0.017 | 0.015 | -0.010 |
| 3.000 | -0.104 | -0.036 | 1.397 | -0.005 | -0.001 | -0.239 | 0.018 | -0.010 |
| 4.000 | -0.095 | -0.053 | 1.286 | -0.006 | 0.000 | -0.107 | 0.015 | -0.009 |
| 5.000 | -0.097 | -0.070 | 1.479 | -0.009 | -0.000 | -0.385 | 0.016 | -0.008 |

## The linear scorer fitted to the ranker's scores (`linear-fid`), per fold

| fold | remaining_degree | newly_opened | already_open | total_degree |
|---|---|---|---|---|
| 1.000 | -0.094 | -0.055 | 1.403 | 0.079 |
| 2.000 | -1.449 | 0.658 | 8.928 | 0.246 |
| 3.000 | -1.921 | -0.376 | -2.267 | 0.536 |
| 4.000 | -0.380 | 0.002 | 6.226 | 0.208 |
| 5.000 | -0.073 | -0.061 | 1.587 | 0.063 |

## The depth-3 tree of fold 1 (leaf value = probability the candidate closes next)

```
|--- open_after <= 6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 2.50
|   |   |   |--- value: 0.411  (rows 36,201)
|   |   |--- remaining_degree >  2.50
|   |   |   |--- value: 0.189  (rows 111,319)
|   |--- newly_opened >  1.50
|   |   |--- already_open <= 0.50
|   |   |   |--- value: 0.046  (rows 47,182)
|   |   |--- already_open >  0.50
|   |   |   |--- value: 0.117  (rows 6,637)
|--- open_after >  6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 10.50
|   |   |   |--- value: 0.126  (rows 220,221)
|   |   |--- remaining_degree >  10.50
|   |   |   |--- value: 0.052  (rows 719,802)
|   |--- newly_opened >  1.50
|   |   |--- n_customers <= 30.50
|   |   |   |--- value: 0.025  (rows 382,636)
|   |   |--- n_customers >  30.50
|   |   |   |--- value: 0.006  (rows 439,716)
```

<details><summary>fold 2</summary>

```
|--- open_after <= 6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 2.50
|   |   |   |--- value: 0.408  (rows 34,518)
|   |   |--- remaining_degree >  2.50
|   |   |   |--- value: 0.191  (rows 99,088)
|   |--- newly_opened >  1.50
|   |   |--- n_customers <= 20.50
|   |   |   |--- value: 0.088  (rows 23,785)
|   |   |--- n_customers >  20.50
|   |   |   |--- value: 0.038  (rows 32,458)
|--- open_after >  6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 10.50
|   |   |   |--- value: 0.125  (rows 177,416)
|   |   |--- remaining_degree >  10.50
|   |   |   |--- value: 0.049  (rows 506,774)
|   |--- newly_opened >  1.50
|   |   |--- n_customers <= 20.50
|   |   |   |--- value: 0.038  (rows 116,136)
|   |   |--- n_customers >  20.50
|   |   |   |--- value: 0.009  (rows 582,411)
```
</details>

<details><summary>fold 3</summary>

```
|--- open_after <= 6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 2.50
|   |   |   |--- value: 0.407  (rows 41,779)
|   |   |--- remaining_degree >  2.50
|   |   |   |--- value: 0.190  (rows 127,824)
|   |--- newly_opened >  1.50
|   |   |--- already_open <= 0.50
|   |   |   |--- value: 0.048  (rows 51,583)
|   |   |--- already_open >  0.50
|   |   |   |--- value: 0.121  (rows 7,705)
|--- open_after >  6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 10.50
|   |   |   |--- value: 0.125  (rows 235,992)
|   |   |--- remaining_degree >  10.50
|   |   |   |--- value: 0.053  (rows 701,939)
|   |--- newly_opened >  1.50
|   |   |--- progress <= 0.00
|   |   |   |--- value: 0.041  (rows 113,896)
|   |   |--- progress >  0.00
|   |   |   |--- value: 0.012  (rows 712,112)
```
</details>

<details><summary>fold 4</summary>

```
|--- open_after <= 6.50
|   |--- open_after <= 2.50
|   |   |--- already_open <= 0.50
|   |   |   |--- value: 0.120  (rows 4,129)
|   |   |--- already_open >  0.50
|   |   |   |--- value: 0.417  (rows 29,802)
|   |--- open_after >  2.50
|   |   |--- already_open <= 0.50
|   |   |   |--- value: 0.052  (rows 41,704)
|   |   |--- already_open >  0.50
|   |   |   |--- value: 0.199  (rows 129,010)
|--- open_after >  6.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 10.50
|   |   |   |--- value: 0.125  (rows 214,243)
|   |   |--- remaining_degree >  10.50
|   |   |   |--- value: 0.052  (rows 620,769)
|   |--- newly_opened >  1.50
|   |   |--- n_customers <= 22.00
|   |   |   |--- value: 0.037  (rows 135,042)
|   |   |--- n_customers >  22.00
|   |   |   |--- value: 0.011  (rows 655,141)
```
</details>

<details><summary>fold 5</summary>

```
|--- open_after <= 5.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 2.50
|   |   |   |--- value: 0.411  (rows 27,733)
|   |   |--- remaining_degree >  2.50
|   |   |   |--- value: 0.207  (rows 56,829)
|   |--- newly_opened >  1.50
|   |   |--- already_open <= 0.50
|   |   |   |--- value: 0.051  (rows 28,579)
|   |   |--- already_open >  0.50
|   |   |   |--- value: 0.151  (rows 3,466)
|--- open_after >  5.50
|   |--- newly_opened <= 1.50
|   |   |--- remaining_degree <= 8.50
|   |   |   |--- value: 0.150  (rows 132,120)
|   |   |--- remaining_degree >  8.50
|   |   |   |--- value: 0.056  (rows 602,000)
|   |--- newly_opened >  1.50
|   |   |--- n_customers <= 30.50
|   |   |   |--- value: 0.024  (rows 310,909)
|   |   |--- n_customers >  30.50
|   |   |   |--- value: 0.007  (rows 429,722)
```
</details>

## The depth-3 tree of fold 1 fitted to the ranker's scores (`tree-fid`)

```
|--- newly_opened <= 2.50
|   |--- open_after <= 16.50
|   |   |--- open_after <= 6.50
|   |   |   |--- value: -1.368  (rows 162,160)
|   |   |--- open_after >  6.50
|   |   |   |--- value: -2.479  (rows 469,312)
|   |--- open_after >  16.50
|   |   |--- newly_opened <= 0.50
|   |   |   |--- value: -3.097  (rows 397,281)
|   |   |--- newly_opened >  0.50
|   |   |   |--- value: -4.623  (rows 209,717)
|--- newly_opened >  2.50
|   |--- n_customers <= 64.00
|   |   |--- progress <= 0.06
|   |   |   |--- value: -3.778  (rows 174,711)
|   |   |--- progress >  0.06
|   |   |   |--- value: -6.210  (rows 286,353)
|   |--- n_customers >  64.00
|   |   |--- open_after <= 25.50
|   |   |   |--- value: -6.891  (rows 85,295)
|   |   |--- open_after >  25.50
|   |   |   |--- value: -9.630  (rows 178,885)
```
