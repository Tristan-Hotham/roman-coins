"""Step 1: district table and map geometry from the PAS facet file and ONS boundaries.
Outputs: data/districts.csv, data/periods_england.csv, data/county_rulers.json, data/districts.geojson, data/build.json"""
import pandas as pd, geopandas as gpd, numpy as np
from collections import defaultdict
from common import *

d = jload(RAW)
nat = d["nat"]
counties = [c for c, _, _ in nat["ceremonial"]]
assert len(counties) == 47
lad = gpd.read_file(LAD)
lad = lad[lad.LAD23CD.str.startswith("E")].copy()
assert len(lad) == 296
names = set(lad.LAD23NM)

rec = defaultdict(lambda: defaultdict(int))
home = defaultdict(lambda: defaultdict(int))      # district -> county -> records
for c in counties:
    for n, v, fl in d[f"all|{c}"]:
        rec[n]["records"] += v; home[n][c] += v
    for n, v, fl in d[f"coin|{c}"]:
        rec[n]["coins"] += v
    for p in range(1, 25):
        for n, v, fl in d.get(f"reece|Period {p}|{c}", []):
            rec[n][f"P{p}"] += v
allnames = set(rec)
unmatched = sorted(allnames - names)
assert not unmatched, unmatched
multi = {n: dict(h) for n, h in home.items() if len(h) > 1}
maxlen = max(len(d[k]) for k in d if k != "nat" and not k.startswith("ruler|"))
assert maxlen < 50

rows = []
for n in sorted(names):
    r = rec.get(n, {})
    row = {"lad23cd": lad.loc[lad.LAD23NM == n, "LAD23CD"].iloc[0], "district": n,
           "county": max(home[n], key=home[n].get) if n in home else None,
           "records": r.get("records", 0), "coins": r.get("coins", 0)}
    for p in range(1, 25):
        row[f"P{p}"] = r.get(f"P{p}", 0)
    rows.append(row)
D = pd.DataFrame(rows)
D["dated"] = D[[f"P{p}" for p in P21]].sum(axis=1)
D["late"] = D[[f"P{p}" for p in LATE]].sum(axis=1)
D["early"] = D[[f"P{p}" for p in EARLY]].sum(axis=1)

# geometry: centroids in BNG, area, region
g = lad.to_crs(27700)
g["area_km2"] = g.geometry.area / 1e6
cen = g.geometry.representative_point()
g["east"] = cen.x / 1e5; g["north"] = cen.y / 1e5
rg = gpd.read_file(TOPO, layer="rgn").set_crs(4326, allow_override=True).to_crs(27700)
rg = rg[rg.areacd.str.startswith("E12")][["areanm", "geometry"]]
pts = gpd.GeoDataFrame(g[["LAD23NM"]], geometry=cen, crs=27700)
j = gpd.sjoin(pts, rg, how="left", predicate="within")
miss = j.areanm.isna()
if miss.any():   # coastal points falling outside generalised region polygons: nearest region
    jn = gpd.sjoin_nearest(pts[miss.values], rg, how="left")
    j.loc[miss, "areanm"] = jn.areanm.values
g["region"] = j.areanm.values
D = D.merge(g[["LAD23NM", "area_km2", "east", "north", "region"]].rename(columns={"LAD23NM": "district"}), on="district")
assert D.region.notna().all()
D["rate"] = 1000 * D.coins / D.records
D.to_csv(f"{DATA}/districts.csv", index=False, float_format="%.4f")

# England national profile by period (sum of county reece facets) and the PAS national figure (incl. Wales and unlocated)
E = defaultdict(int)
for c in counties:
    for n, v, fl in d[f"reececty|{c}"]:
        E[int(n.split()[1])] += v
NAT = {int(n.split()[1]): v for n, v, fl in nat["reece"]}
P = pd.DataFrame({"period": range(1, 25)})
P["start"] = [REECE[p][0] for p in P.period]; P["end"] = [REECE[p][1] for p in P.period]
P["name"] = [REECE[p][2] for p in P.period]; P["rulers"] = [RULERS.get(p, REECE[p][2]) for p in P.period]
P["england_county_sum"] = [E.get(p, 0) for p in P.period]
P["england_district_sum"] = [int(D[f"P{p}"].sum()) for p in P.period]
P["pas_national"] = [NAT.get(p, 0) for p in P.period]
P.to_csv(f"{DATA}/periods_england.csv", index=False)

# rulers: top 50 per county and nationally (descriptive)
CR = {c: d[f"ruler|{c}"][:50] for c in counties}
CR["_national"] = nat["ruler"]
jsave({k: [[n, v] for n, v, *_ in L] for k, L in CR.items()}, f"{DATA}/county_rulers.json")

# map geometry: England LADs (BSC), 4 decimals
gm = lad[["LAD23CD", "LAD23NM", "geometry"]].copy()
gm["geometry"] = gm.geometry.simplify(0.0008, preserve_topology=True)
gm.to_file(f"{SCR}/districts_tmp.geojson", driver="GeoJSON")
gj = jload(f"{SCR}/districts_tmp.geojson")
def rnd(o):
    if isinstance(o, list):
        return [rnd(x) for x in o] if o and isinstance(o[0], list) else [round(o[0], 4), round(o[1], 4)]
    return o
for f in gj["features"]:
    f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    f["properties"] = {"cd": f["properties"]["LAD23CD"], "nm": f["properties"]["LAD23NM"]}
gj.pop("crs", None); gj.pop("name", None)
jsave(gj, f"{DATA}/districts.geojson")
os.remove(f"{SCR}/districts_tmp.geojson")

tot_cty = {c: v for c, v, _ in nat["ceremonial"]}
B = {"counties": 47, "districts": 296, "names_in_pas": len(allnames), "unmatched": len(unmatched),
     "multi_county_names": len(multi), "multi_county_records": int(sum(sum(h.values()) - max(h.values()) for h in multi.values())),
     "records": int(D.records.sum()), "records_county_total": int(sum(tot_cty.values())),
     "records_no_district": int(sum(tot_cty.values()) - D.records.sum()),
     "coins": int(D.coins.sum()), "dated": int(D.dated.sum()), "dated_pc": 100 * D.dated.sum() / D.coins.sum(),
     "p22_24": int(D[["P22", "P23", "P24"]].sum().sum()),
     "pas_nat_reece": int(sum(NAT.values())), "pas_nat_reece_1_21": int(sum(v for k, v in NAT.items() if k <= 21)),
     "england_reece_1_21": int(sum(v for k, v in E.items() if k <= 21)),
     "max_list": maxlen, "coin_rate": 1000 * D.coins.sum() / D.records.sum(),
     "zero_coin_districts": int((D.coins == 0).sum())}
jsave(B, f"{DATA}/build.json", indent=1)
print(B)
print("multi-county names:", multi)
print(os.path.getsize(f"{DATA}/districts.geojson") // 1024, "KB geojson")
