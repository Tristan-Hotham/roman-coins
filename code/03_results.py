"""Step 3: data/results.json, every number quoted anywhere, from build.json and results_models.json, with checks."""
import pandas as pd, numpy as np
from common import *

B = jload(f"{DATA}/build.json"); M = jload(f"{DATA}/results_models.json")
D = pd.read_csv(f"{DATA}/districts.csv"); P = pd.read_csv(f"{DATA}/periods_england.csv")
CR = jload(f"{DATA}/county_rulers.json")
R = {"build": B}
prof = {f"P{r['period']}": r for r in M["H1"]["profile"]}
R["profile"] = prof
py = {k: v["per_year"] for k, v in prof.items() if v["per_year"] is not None}
rank = sorted(py, key=py.get, reverse=True)
R["H1"] = {"top1": rank[0], "top2": rank[1], "top3": rank[2], "top1_py": py[rank[0]], "top2_py": py[rank[1]], "top3_py": py[rank[2]],
           "low1": rank[-1], "low1_py": py[rank[-1]], "mean_py": 1000 / (402 - 41),
           "p17_n": prof["P17"]["n"], "p17_pm": prof["P17"]["per_mille"], "p13_n": prof["P13"]["n"], "p13_pm": prof["P13"]["per_mille"],
           "p21_pm": prof["P21"]["per_mille"], "p20_pm": prof["P20"]["per_mille"], "p19_pm": prof["P19"]["per_mille"],
           "p13_17_pc": (prof["P13"]["per_mille"] + prof["P14"]["per_mille"] + prof["P16"]["per_mille"] + prof["P17"]["per_mille"]) / 10,
           "after260_pc": sum(prof[f"P{p}"]["per_mille"] for p in range(13, 22)) / 10,
           "p17_ratio_p20": py["P17"] / py["P20"]}
R["H1"]["p17_x_mean"] = py["P17"] / R["H1"]["mean_py"]
assert R["H1"]["top1"] == "P17", rank[:3]
R["shares"] = M["shares"]
for h in ("H2", "H3", "H4"):
    R[h] = {k: v for k, v in M[h].items() if k != "loro"}
    lo = M[h]["loro"]
    R[h]["loro_range"] = {c: [min(v[c]["or"] for v in lo.values()), max(v[c]["or"] for v in lo.values())] for c in ("east", "north")}
R["explore"] = {k: v for k, v in M["explore"].items() if k != "by_period"}
bp = {f"P{r['period']}": r for r in M["explore"]["by_period"]}
R["by_period"] = bp
R["H5"] = M["H5"]
reg = {r["region"]: r for r in M["regions"]}
R["regions"] = reg
nw = D[D.region.isin(["North East", "North West"])]
rest = D[~D.region.isin(["North East", "North West"])]
R["nw"] = {"late_pc": 100 * nw.late.sum() / nw.dated.sum(), "early_pc": 100 * nw.early.sum() / nw.dated.sum(),
           "rest_late_pc": 100 * rest.late.sum() / rest.dated.sum(), "rest_early_pc": 100 * rest.early.sum() / rest.dated.sum(),
           "dated": int(nw.dated.sum()), "districts": int(len(nw)), "rate": 1000 * nw.coins.sum() / nw.records.sum(),
           "rest_rate": 1000 * rest.coins.sum() / rest.records.sum()}
R["nw"]["late_ratio"] = R["nw"]["rest_late_pc"] / R["nw"]["late_pc"]
R["nw"]["early_ratio"] = R["nw"]["early_pc"] / R["nw"]["rest_early_pc"]
# districts
D["late_pc"] = 100 * D.late / D.dated.replace(0, np.nan); D["early_pc"] = 100 * D.early / D.dated.replace(0, np.nan)
top = D.sort_values("coins", ascending=False).head(10)
R["top_coins"] = top[["district", "county", "coins", "records", "rate"]].to_dict("records")
D100 = D[D.records >= 500]
tr = D100.sort_values("rate", ascending=False)
R["top_rate"] = tr.head(10)[["district", "county", "coins", "records", "rate"]].to_dict("records")
R["low_rate"] = tr.tail(5)[["district", "county", "coins", "records", "rate"]].to_dict("records")
R["n_rate500"] = int(len(D100))
D20 = D[D.dated >= 100]
R["top_late"] = D20.sort_values("late_pc", ascending=False).head(8)[["district", "county", "dated", "late", "late_pc"]].to_dict("records")
R["top_early"] = D20.sort_values("early_pc", ascending=False).head(8)[["district", "county", "dated", "early", "early_pc"]].to_dict("records")
R["n_dated100"] = int(len(D20))
R["rate_median"] = float(D[D.records >= 500].rate.median())
R["rate_iqr"] = [float(D[D.records >= 500].rate.quantile(.25)), float(D[D.records >= 500].rate.quantile(.75))]
R["spearman_coins_rate"] = float(D[["coins", "rate"]].rank().corr().iloc[0, 1])
# rulers
nat = CR["_national"]
R["rulers"] = {"national_top": nat[:12], "imitation_radiates": dict(nat).get("Radiate (imitation)"),
               "imitation_rank": [n for n, _ in nat].index("Radiate (imitation)") + 1,
               "constantine_house": dict(nat).get("House of Constantine (AD 307-361)"), "constantine_i": dict(nat).get("Constantine I")}
named = [(n, v) for n, v in nat if not any(w in n for w in ("House", "Uncertain", "imitation", "Republic", "Gallic Empire", "Unknown", "Iron Age", "Tetrarchy"))]
R["rulers"]["top_named"] = named[:5]
ctop = {}
for c, L in CR.items():
    if c == "_national": continue
    nm = [(n, v) for n, v in L if not any(w in n for w in ("House", "Uncertain", "imitation", "Unknown", "Iron Age"))]
    if nm: ctop[c] = nm[0]
R["rulers"]["county_top_named"] = ctop
from collections import Counter
R["rulers"]["county_top_counts"] = Counter(v[0] for v in ctop.values()).most_common()
# robustness span for the planned tests
def span(h, c):
    vals = [v[c]["or"] for k, v in M[h].items() if isinstance(v, dict) and c in v and isinstance(v[c], dict)]
    vals += [v[c]["or"] for v in M[h]["loro"].values()]
    return [min(vals), max(vals)]
R["span"] = {h: {c: span(h, c) for c in ("east", "north")} for h in ("H2", "H3", "H4")}
R["robust_n"] = {h: sum(1 for k, v in M[h].items() if isinstance(v, dict) and "east" in v and k != "main") + len(M[h]["loro"]) for h in ("H2", "H3", "H4")}
x = R["explore"]
R["x"] = {"nw_late_or": x["nw_late"]["nw"]["or"], "nw_late_lo": x["nw_late"]["nw"]["lo"], "nw_late_hi": x["nw_late"]["nw"]["hi"],
          "nw_early_or": x["nw_early"]["nw"]["or"], "nw_early_lo": x["nw_early"]["nw"]["lo"], "nw_early_hi": x["nw_early"]["nw"]["hi"],
          "sw_rate": reg["South West"]["rate"], "lon_rate": reg["London"]["rate"], "nwr_rate": reg["North West"]["rate"],
          "eng_rate": B["coin_rate"], "sw_late": reg["South West"]["late_pc"], "ne_late": reg["North East"]["late_pc"],
          "nwr_late": reg["North West"]["late_pc"], "ne_early": reg["North East"]["early_pc"], "nwr_early": reg["North West"]["early_pc"],
          "wm_late": reg["West Midlands"]["late_pc"], "wm_early": reg["West Midlands"]["early_pc"]}
R["sample"] = {"districts": 296, "d20": M["shares"]["n20"], "d100": M["H5"]["n"]}
jsave(R, f"{DATA}/results.json", indent=1)
print(R["H1"]); print(R["nw"]); print(R["x"]); print(R["rulers"]["top_named"], R["rulers"]["county_top_counts"][:6])
print(R["top_rate"][:3], R["low_rate"]); print(R["span"]); print(R["robust_n"])
