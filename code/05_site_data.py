"""Step 5: page data. data/site.json (district counts, period meta, county rulers), data/counties.geojson, data/england.geojson."""
import pandas as pd, geopandas as gpd
from common import *

D = pd.read_csv(f"{DATA}/districts.csv"); R = jload(f"{DATA}/results.json"); CR = jload(f"{DATA}/county_rulers.json")
S = {"d": {}, "periods": [], "rulers": {}, "eng": {"rate": R["build"]["coin_rate"], "pm": [R["profile"][f"P{p}"]["per_mille"] for p in P21]}}
for r in D.itertuples():
    S["d"][r.district] = {"c": r.county, "g": r.region, "n": int(r.records), "k": int(r.coins), "d": int(r.dated),
                          "p": [int(getattr(r, f"P{p}")) for p in P21]}
for p in P21:
    S["periods"].append({"p": p, "who": RULERS[p], "when": pdates(p), "name": REECE[p][2]})
skip = ("Uncertain", "Unknown")
for c, L in CR.items():
    if c == "_national": continue
    S["rulers"][c] = [[n.replace(" (AD ", ", ").replace("-", " to ").replace(")", ""), v] for n, v in L if not n.startswith(skip)][:6]
assert not any("-" in n for L in S["rulers"].values() for n, _ in L)
jsave(S, f"{DATA}/site.json")
c = gpd.read_file(CTY); c = c[c.nation == "England"].copy()
c["geometry"] = c.geometry.simplify(0.003, preserve_topology=True)
c = c[["county", "geometry"]]
c.to_file(f"{SCR}/c.geojson", driver="GeoJSON")
e = c.copy(); e["geometry"] = e.geometry.buffer(0); e = e.dissolve()[["geometry"]]; e["name"] = "England"
e.to_file(f"{SCR}/e.geojson", driver="GeoJSON")
def rnd(o):
    if isinstance(o, list):
        return [rnd(x) for x in o] if o and isinstance(o[0], list) else [round(o[0], 4), round(o[1], 4)]
    return o
for src, dst in (("c", "counties"), ("e", "england")):
    g = jload(f"{SCR}/{src}.geojson"); g.pop("crs", None); g.pop("name", None)
    for f in g["features"]: f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    jsave(g, f"{DATA}/{dst}.geojson"); os.remove(f"{SCR}/{src}.geojson")
for fn in ("site.json", "counties.geojson", "england.geojson", "districts.geojson"):
    print(fn, os.path.getsize(f"{DATA}/{fn}") // 1024, "KB")
