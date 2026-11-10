"""Reddit collage for roman-coins: the coin curve on top, early and late shares by district below. Light paper, labels on sea."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import numpy as np, pandas as pd, geopandas as gpd
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "IBMPlexMono-Regular.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name()
PAPER, INK, MUT, SEA, RULE = "#F6EED8", "#2B2119", "#6E604E", "#E6ECEC", "#D9C9A3"
HOT, COOL = "#B4442E", "#2F6A9E"
plt.rcParams.update({"font.family": "Source Serif 4", "figure.facecolor": PAPER, "axes.facecolor": PAPER, "pdf.fonttype": 42})
HALO = [pe.withStroke(linewidth=4, foreground=SEA)]
R = jload(f"{DATA}/results.json"); D = pd.read_csv(f"{DATA}/districts.csv")
G = gpd.read_file(f"{DATA}/districts.geojson").to_crs(27700).rename(columns={"nm": "district"}).merge(D, on="district")
G["geometry"] = G.geometry.buffer(0)
lad = gpd.read_file(LAD); other = lad[~lad.LAD23CD.str.startswith("E")].to_crs(27700)
wal = other[other.LAD23CD.str.startswith("W")]; sco = other[other.LAD23CD.str.startswith("S")]
eng = lad[lad.LAD23CD.str.startswith("E")].to_crs(27700).dissolve()
G["early_pc"] = 100 * G.early / G.dated.replace(0, np.nan); G["late_pc"] = 100 * G.late / G.dated.replace(0, np.nan)

fig = plt.figure(figsize=(12, 14.4), dpi=220)
fig.text(0.05, 0.968, "Lost money", fontsize=40, family=DISP, fontweight="bold", color=HOT, va="top")
fig.text(0.05, 0.925, f"{R['build']['coins']:,} Roman coin records from England in the Portable Antiquities Scheme,\nreign by reign and district by district", fontsize=16, color=INK, va="top", linespacing=1.3)

# top: coin curve
ax = fig.add_axes([0.08, 0.64, 0.87, 0.2])
prof = R["profile"]
for p in range(2, 22):
    a, b, _ = REECE[p]; v = prof[f"P{p}"]["per_year"]
    ax.bar(a, v, width=b - a, align="edge", color=HOT if p in (13, 17, 19) else "#C9A27A", edgecolor=PAPER, linewidth=1)
ax.axhline(R["H1"]["mean_py"], color=INK, lw=1, ls=(0, (4, 3)))
ax.text(45, R["H1"]["mean_py"] + .35, "if coins had been lost at an even rate", fontsize=11, color=INK)
for p, t in ((13, "Gallic emperors,\n260 to 275"), (17, "Constantine and\nhis sons, 330 to 348"), (19, "Valentinian,\n364 to 378")):
    a, b, _ = REECE[p]; v = prof[f"P{p}"]["per_year"]
    ax.text((a + b) / 2, v + .35, t, ha="center", va="bottom", fontsize=11, color=INK)
ax.set_xlim(40, 405); ax.set_ylim(0, 17.5); ax.spines[["top", "right"]].set_visible(False)
ax.set_ylabel("coins lost per year\nper 1,000 dated", fontsize=11, color=MUT); ax.tick_params(colors=MUT, labelsize=11)

ax.set_title("When: three peaks, all after AD 260", loc="left", fontsize=18, family=DISP, fontweight="bold", color=INK, pad=12)

# bottom: two maps
cm_e = LinearSegmentedColormap.from_list("e", ["#EEF1F2", "#A9C4DC", "#5D8EBB", "#2F6A9E", "#173B5C"])
cm_l = LinearSegmentedColormap.from_list("l", ["#FBEAE2", "#E9B49E", "#C8644A", "#8E2D1C", "#5A160B"])
for i, (col, cm, bnds, ttl, lab) in enumerate((("early_pc", cm_e, [0, 10, 20, 30, 45, 60, 80], "Where: early coins (before AD 222)", "% of dated coins before AD 222"),
                                               ("late_pc", cm_l, [0, 5, 10, 15, 20, 25, 30], "and late coins (AD 364 to 402)", "% of dated coins AD 364 to 402"))):
    ax = fig.add_axes([0.03 + i * 0.48, 0.1, 0.46, 0.46]); ax.set_facecolor(SEA)
    for g_ in (wal, sco): g_.plot(ax=ax, color="#E4DED0", edgecolor="#D3C9B2", linewidth=.3)
    nrm = BoundaryNorm(bnds, 256)
    G[G.dated < 20].plot(ax=ax, color="#EAE4D6", edgecolor="white", linewidth=.15)
    G[G.dated >= 20].plot(ax=ax, column=col, cmap=cm, norm=nrm, edgecolor="white", linewidth=.15)
    eng.boundary.plot(ax=ax, color=INK, linewidth=.6)
    ax.set_xlim(120000, 670000); ax.set_ylim(0, 665000); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(ttl, loc="left", fontsize=18, family=DISP, fontweight="bold", color=INK, pad=10)
    if col == "early_pc":
        ax.text(135000, 520000, f"North West\nand North East:\n{R['nw']['early_pc']:.0f}% early", fontsize=13, color=COOL, fontweight="bold", path_effects=HALO, va="center")
        ax.text(560000, 520000, f"Rest of\nEngland:\n{R['nw']['rest_early_pc']:.0f}%", fontsize=13, color=INK, path_effects=HALO, va="center", ha="center")
    else:
        ax.text(135000, 520000, f"North West\nand North East:\n{R['nw']['late_pc']:.0f}% late", fontsize=13, color=HOT, fontweight="bold", path_effects=HALO, va="center")
        ax.text(560000, 520000, f"Rest of\nEngland:\n{R['nw']['rest_late_pc']:.0f}%", fontsize=13, color=INK, path_effects=HALO, va="center", ha="center")
    ax.text(140000, 160000, "Wales:\nno data", fontsize=11, color=MUT, path_effects=HALO, ha="left")
    cax = fig.add_axes([0.06 + i * 0.48, 0.092, 0.38, 0.012])
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=nrm, cmap=cm), cax=cax, orientation="horizontal", ticks=bnds)
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=10, colors=MUT)
    cax.set_xlabel(lab + ". Grey: fewer than 20 dated coins", fontsize=10.5, color=INK)
fig.text(0.05, 0.598, "Not a smooth slope from south east to north west (the planned test found none), but a step at the old frontier.",
         fontsize=13, color=MUT)
fig.text(0.05, 0.018, "Data: Portable Antiquities Scheme (finds.org.uk), 2026 · Reece periods: Nomisma.org · ONS boundaries (OGL v3.0)\n"
         "Counts are records, not individual coins. England only. Dr Tristan Hotham · maps.tristanhotham.com/roman-coins",
         fontsize=10, family="IBM Plex Mono", color=MUT, linespacing=1.5)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roman_coins_collage.png")
fig.savefig(out, dpi=220, facecolor=PAPER); plt.close(fig)
from PIL import Image
print(Image.open(out).size)
