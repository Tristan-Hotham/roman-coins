"""Step 2: the pre-specified analysis (NOTES.md). Output data/results_models.json, data/profiles_region.csv, data/district_profiles.csv."""
import numpy as np, pandas as pd, statsmodels.api as sm, warnings
from common import *
warnings.filterwarnings("ignore")

D = pd.read_csv(f"{DATA}/districts.csv")
PS = [f"P{p}" for p in P21]
M = {}

# ---------- H1: national profile ----------
tot = D[PS].sum()
pm = 1000 * tot / tot.sum()
prof = []
for p in P21:
    L = plen(p)
    prof.append({"period": p, "n": int(tot[f"P{p}"]), "per_mille": pm[f"P{p}"], "years": L,
                 "per_year": (pm[f"P{p}"] / L) if L else None})
M["H1"] = {"profile": prof, "dated": int(tot.sum())}

# ---------- model helpers ----------
def glm(df, num, den, X=("east", "north"), cluster="county", extra=None):
    df = df.copy()
    cols = list(X) + (extra or [])
    y = np.column_stack([df[num], df[den] - df[num]])
    Xm = sm.add_constant(df[cols].astype(float))
    m0 = sm.GLM(y, Xm, family=sm.families.Binomial()).fit()
    groups = pd.factorize(df[cluster])[0]
    m = sm.GLM(y, Xm, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups})
    out = {"n": int(len(df)), "clusters": int(len(set(groups))), "dispersion": float(m0.pearson_chi2 / m0.df_resid)}
    for c in cols:
        b, se = m.params[c], m.bse[c]
        out[c] = {"or": float(np.exp(b)), "lo": float(np.exp(b - 1.96 * se)), "hi": float(np.exp(b + 1.96 * se)),
                  "b": float(b), "se": float(se), "p": float(m.pvalues[c])}
    return out

def wls_elogit(df, num, den, cluster="county"):
    df = df.copy()
    y = np.log((df[num] + .5) / (df[den] - df[num] + .5))
    w = 1 / (1 / (df[num] + .5) + 1 / (df[den] - df[num] + .5))
    Xm = sm.add_constant(df[["east", "north"]])
    m = sm.WLS(y, Xm, weights=w).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df[cluster])[0]})
    return {"n": int(len(df)), **{c: {"or": float(np.exp(m.params[c])), "lo": float(np.exp(m.conf_int().loc[c, 0])),
                                       "hi": float(np.exp(m.conf_int().loc[c, 1])), "p": float(m.pvalues[c])} for c in ("east", "north")}}

def negbin(df, num, den):
    df = df[df[num] >= 0].copy()
    Xm = sm.add_constant(df[["east", "north"]])
    m = sm.NegativeBinomial(df[num], Xm, offset=np.log(df[den])).fit(disp=0, cov_type="cluster",
                                                                      cov_kwds={"groups": pd.factorize(df["county"])[0]})
    return {"n": int(len(df)), **{c: {"or": float(np.exp(m.params[c])), "lo": float(np.exp(m.conf_int().loc[c, 0])),
                                       "hi": float(np.exp(m.conf_int().loc[c, 1])), "p": float(m.pvalues[c])} for c in ("east", "north")}}

def perm(df, num, den, k=999, seed=2026):
    rng = np.random.default_rng(seed)
    y = np.column_stack([df[num], df[den] - df[num]])
    Xm = sm.add_constant(df[["east", "north"]])
    b0 = sm.GLM(y, Xm, family=sm.families.Binomial()).fit().params
    be, bn = [], []
    for _ in range(k):
        i = rng.permutation(len(df))
        b = sm.GLM(y[i], Xm, family=sm.families.Binomial()).fit().params
        be.append(b["east"]); bn.append(b["north"])
    be, bn = np.array(be), np.array(bn)
    return {"k": k, "p_east": float((1 + (np.abs(be) >= abs(b0["east"])).sum()) / (k + 1)),
            "p_north": float((1 + (np.abs(bn) >= abs(b0["north"])).sum()) / (k + 1))}

D["late2"] = D[["P20", "P21"]].sum(axis=1)
D["late17"] = D[[f"P{p}" for p in range(17, 22)]].sum(axis=1)
D["maxshare"] = D[PS].max(axis=1) / D.dated.replace(0, np.nan)
D["logdens"] = np.log(D.records / D.area_km2)
top10 = set(D.nlargest(10, "coins").district)

def suite(num, den, base_min, hyp):
    B = D[D[den] >= base_min] if base_min else D[D[den] > 0]
    r = {"main": glm(B, num, den)}
    for mn in (0, 50, 100):
        if mn != base_min:
            r[f"min{mn}"] = glm(D[D[den] >= max(mn, 1)], num, den)
    r["wls"] = wls_elogit(B, num, den)
    r["cl_region"] = glm(B, num, den, cluster="region")
    r["loro"] = {reg: glm(B[B.region != reg], num, den) for reg in sorted(D.region.unique())}
    r["drop_top10"] = glm(B[~B.district.isin(top10)], num, den)
    if den == "dated":
        r["drop_spiky"] = glm(B[B.maxshare <= .4], num, den)
        r["drop_spiky"]["dropped"] = int((B.maxshare > .4).sum())
    r["intensity"] = glm(B, num, den, extra=["logdens"])
    r["negbin"] = negbin(B, num, den)
    r["perm"] = perm(B, num, den)
    return r

M["H2"] = suite("late", "dated", 20, "late")
M["H2"]["alt_after378"] = glm(D[D.dated >= 20], "late2", "dated")
M["H2"]["alt_after330"] = glm(D[D.dated >= 20], "late17", "dated")
M["H3"] = suite("early", "dated", 20, "early")
M["H4"] = suite("coins", "records", 0, "coins")

# headline shares
B = D[D.dated >= 20]
M["shares"] = {"late_eng": 100 * D.late.sum() / D.dated.sum(), "early_eng": 100 * D.early.sum() / D.dated.sum(),
               "n20": int(len(B))}

# ---------- exploratory (added after the planned results; labelled exploratory everywhere) ----------
from scipy import stats
B = D[D.dated >= 20].copy()
B["nw"] = B.region.isin(["North East", "North West"]).astype(int)
E = {}
for num in ("late", "early"):
    E[f"nw_{num}"] = glm(B, num, "dated", X=("nw",))
B["wm"] = (B.region == "West Midlands").astype(int)
for num in ("late", "early"):
    E[f"nwwm_{num}"] = glm(B, num, "dated", X=("nw", "wm"))
# region dummies: Wald test that all regions share one late share
regs = sorted(B.region.unique()); base = "South East"
Xr = pd.get_dummies(B.region)[[r for r in regs if r != base]].astype(float)
y = np.column_stack([B.late, B.dated - B.late])
mr = sm.GLM(y, sm.add_constant(Xr), family=sm.families.Binomial()).fit(cov_type="cluster",
                                                                      cov_kwds={"groups": pd.factorize(B.county)[0]})
w = mr.wald_test(np.eye(len(mr.params))[1:], scalar=True)
E["region_wald"] = {"chi2": float(w.statistic), "df": int(len(regs) - 1), "p": float(w.pvalue), "n": int(len(B))}
# period by period: share of period p, northing and easting gradients
pp = []
for p in P21:
    r = glm(B, f"P{p}", "dated")
    pp.append({"period": p, "north_or": r["north"]["or"], "north_lo": r["north"]["lo"], "north_hi": r["north"]["hi"],
               "east_or": r["east"]["or"], "east_lo": r["east"]["lo"], "east_hi": r["east"]["hi"]})
E["by_period"] = pp
M["explore"] = E

# ---------- regions ----------
R = D.groupby("region")[PS + ["dated", "coins", "records", "late", "early"]].sum()
R["rate"] = 1000 * R.coins / R.records
R["late_pc"] = 100 * R.late / R.dated; R["early_pc"] = 100 * R.early / R.dated
for p in P21:
    R[f"pm{p}"] = 1000 * R[f"P{p}"] / R.dated
R.reset_index().to_csv(f"{DATA}/profiles_region.csv", index=False, float_format="%.3f")
M["regions"] = R[["dated", "coins", "records", "rate", "late_pc", "early_pc"]].reset_index().to_dict("records")

# ---------- H5 PCA (exploratory) ----------
P = D[D.dated >= 100].copy()
X = P[PS].div(P.dated, axis=0).values * 1000
Xc = (X - X.mean(0)) / X.std(0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
ev = S ** 2 / (S ** 2).sum()
load = Vt[0]
if load[-3:].mean() < 0:   # orient PC1 so that late periods load positively
    load = -load; U[:, 0] = -U[:, 0]
P["pc1"] = U[:, 0] * S[0]
M["H5"] = {"n": int(len(P)), "ev1": float(ev[0]), "ev2": float(ev[1]), "loadings": {f"P{p}": float(l) for p, l in zip(P21, load)},
           "r_east": float(np.corrcoef(P.pc1, P.east)[0, 1]), "r_north": float(np.corrcoef(P.pc1, P.north)[0, 1]),
           "r_late": float(np.corrcoef(P.pc1, P.late / P.dated)[0, 1])}
D = D.merge(P[["district", "pc1"]], on="district", how="left")
D.to_csv(f"{DATA}/district_profiles.csv", index=False, float_format="%.4f")
jsave(M, f"{DATA}/results_models.json", indent=1)
for h in ("H2", "H3", "H4"):
    m = M[h]["main"]
    print(h, m["n"], "east", {k: round(v, 3) for k, v in m["east"].items() if k in ("or", "lo", "hi", "p")},
          "north", {k: round(v, 3) for k, v in m["north"].items() if k in ("or", "lo", "hi", "p")}, "perm", M[h]["perm"])
print(M["shares"], M["H5"]["ev1"], M["H5"]["r_east"], M["H5"]["r_north"], M["H5"]["r_late"])
