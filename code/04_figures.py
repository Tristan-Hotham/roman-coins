"""Step 4: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px), the paper (release/paper/f_*.pdf)
and header.png (1200 x 630). Light paper."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm, TwoSlopeNorm, LogNorm
from matplotlib.patches import Patch
import numpy as np, pandas as pd, geopandas as gpd
from PIL import Image
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
SERIF = "Source Serif 4"; DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name(); MONO = "IBM Plex Mono"
PAPER, INK, MUT, RULE = "#F6EED8", "#2B2119", "#6E604E", "#D9C9A3"
HOT, COOL, GOLD, GREY, SEA = "#B4442E", "#2F6A9E", "#C08A2B", "#9C9384", "#E6ECEC"
SHORT = {13: "Gallienus to Aurelian", 4: "Vespasian, Titus, Domitian", 21: "Theodosius I, Arcadius, Honorius"}
SEQ = LinearSegmentedColormap.from_list("s", ["#F3E7C9", "#E8C27A", "#C9822F", "#9E4A22", "#5E2410"])
DIV = LinearSegmentedColormap.from_list("d", ["#2F6A9E", "#9DB8CF", "#EFE6D2", "#E2A27F", "#B4442E", "#6E1F12"])
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": MUT, "axes.labelcolor": INK, "xtick.color": MUT,
                     "ytick.color": MUT, "axes.facecolor": PAPER, "figure.facecolor": PAPER, "axes.unicode_minus": False,
                     "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
R = jload(f"{DATA}/results.json"); M = jload(f"{DATA}/results_models.json")
D = pd.read_csv(f"{DATA}/districts.csv")
BLOG, PAPD = f"{REL}/blog", f"{REL}/paper"
for d_ in (BLOG, PAPD): os.makedirs(d_, exist_ok=True)
SRC = ("Data: Portable Antiquities Scheme (finds.org.uk), records to 2026, by district; ONS boundaries (OGL v3.0)\n"
       "England · maps.tristanhotham.com/roman-coins")


def out(fig, name, page=True, blog=True, paper=True):
    if paper: fig.savefig(f"{PAPD}/f_{name}.pdf", facecolor=fig.get_facecolor())
    fig.savefig(f"{SCR}/{name}.png", dpi=220, facecolor=fig.get_facecolor()); plt.close(fig)
    im = Image.open(f"{SCR}/{name}.png").convert("RGB")
    if page:
        w = min(1500, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=85, optimize=True)
    if blog:
        im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    os.remove(f"{SCR}/{name}.png")


def title(fig, t, sub, y=0.965):
    fig.text(0.04, y, t, fontsize=21, fontweight="bold", family=DISP, color=INK, va="top")
    fig.text(0.04, y - 0.055, sub, fontsize=12, color=MUT, va="top")


def foot(fig, s=SRC):
    fig.text(0.04, 0.012, s, fontsize=8, family=MONO, color=MUT, va="bottom", linespacing=1.4)


# geometry in BNG
G = gpd.read_file(f"{DATA}/districts.geojson").to_crs(27700).rename(columns={"nm": "district"}).merge(D, on="district")
lad = gpd.read_file(LAD); other = lad[~lad.LAD23CD.str.startswith("E")].to_crs(27700)
wales = other[other.LAD23CD.str.startswith("W")].dissolve(); scot = other[other.LAD23CD.str.startswith("S")].dissolve()
G["geometry"] = G.geometry.buffer(0)
eng = lad[lad.LAD23CD.str.startswith("E")].to_crs(27700).dissolve()
XL, YL = (80000, 670000), (0, 665000)


def basemap(ax):
    ax.set_facecolor(SEA)
    for g_ in (wales, scot):
        g_.plot(ax=ax, color="#E4DED0", edgecolor="#C9BFAA", linewidth=.4)
    tidy(ax)


def tidy(ax):
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_visible(False)


# ---------------------------------------------------------------- 1. national profile
prof = R["profile"]
fig = plt.figure(figsize=(11, 6.6)); ax = fig.add_axes([0.07, 0.19, 0.9, 0.6])
mean = R["H1"]["mean_py"]
for p in range(2, 22):
    a, b, _ = REECE[p]; v = prof[f"P{p}"]["per_year"]
    col = HOT if p in (13, 17, 19) else ("#C9A27A" if p >= 13 else "#B9AE96")
    ax.bar(a, v, width=b - a, align="edge", color=col, edgecolor=PAPER, linewidth=1)
ax.axhline(mean, color=INK, lw=1, ls=(0, (4, 3)))
ax.text(52, mean + .25, "flat loss (same rate every year)", fontsize=10, color=INK, path_effects=HALO)
lab = {13: "Gallienus, Gallic Empire,\nClaudius II: 260 to 275", 17: "Constantine I and his sons:\n330 to 348", 19: "Valentinian I and Valens:\n364 to 378",
       4: "Flavians", 14: "Carausius,\nAllectus", 16: "Constantine I"}
for p, t in lab.items():
    a, b, _ = REECE[p]; v = prof[f"P{p}"]["per_year"]
    ax.text((a + b) / 2, v + .3, t, ha="center", va="bottom", fontsize=9.5 if p in (13, 17, 19) else 9, color=INK, path_effects=HALO)
ax.set_xlim(40, 405); ax.set_ylim(0, max(v["per_year"] or 0 for v in prof.values()) * 1.32)
ax.set_xlabel("Year AD (Reece periods 2 to 21)"); ax.set_ylabel("Coins per 1,000 per year of the period")
ax.grid(axis="y", color=RULE, lw=.6); ax.set_axisbelow(True)
title(fig, "When Roman coins were lost in England", f"Dated Roman coin records on the PAS by Reece period: per 1,000 dated coins, divided by the years in the period. N = {R['build']['dated']:,}")
foot(fig); out(fig, "profile")

# ---------------------------------------------------------------- 2. map: coins per 1,000 records
fig = plt.figure(figsize=(8.6, 10)); ax = fig.add_axes([0.02, 0.07, 0.96, 0.8]); basemap(ax)
bounds = [0, 50, 100, 150, 200, 250, 300, 350, 400, 700]
norm = BoundaryNorm(bounds, SEQ.N)
G.plot(ax=ax, column="rate", cmap=SEQ, norm=norm, edgecolor="#FFFFFF", linewidth=.25)
G[G.records < 100].plot(ax=ax, facecolor="none", edgecolor=GREY, hatch="////", linewidth=0)
eng.boundary.plot(ax=ax, color=INK, linewidth=.7); tidy(ax)
ax.text(0.03, 0.55, "Wales:\nnot in\nthis data", transform=ax.transAxes, fontsize=10, color=MUT, ha="left", va="center")
ax.text(560000, 620000, "North\nSea", fontsize=11, color="#7C8C90", style="italic", ha="center")
cax = fig.add_axes([0.56, 0.105, 0.38, 0.016])
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=SEQ), cax=cax, orientation="horizontal", ticks=bounds[:-1] + [700])
cb.ax.tick_params(labelsize=8); cb.outline.set_visible(False)
cax.set_title("Roman coins per 1,000 PAS records", fontsize=9.5, loc="left", color=INK)
fig.text(0.635, 0.158, "Hatched: fewer than 100 records of any kind", fontsize=8.5, color=MUT)
title(fig, "Roman coins among everything found", f"Share of all Portable Antiquities Scheme records that are Roman coins, by district. England: {R['build']['coin_rate']:.0f} per 1,000.", y=0.975)
foot(fig); out(fig, "map")

# ---------------------------------------------------------------- 3. regions: early and late shares
reg = pd.DataFrame(R["regions"].values()).set_index("region")
order = reg.sort_values("late_pc").index.tolist()
fig = plt.figure(figsize=(11, 6.6))
a1 = fig.add_axes([0.25, 0.19, 0.33, 0.6]); a2 = fig.add_axes([0.63, 0.19, 0.33, 0.6])
y = np.arange(len(order))
nwset = {"North East", "North West"}
a1.barh(y, reg.loc[order, "early_pc"], color=[COOL if r in nwset else "#9DB8CF" for r in order])
a2.barh(y, reg.loc[order, "late_pc"], color=[HOT if r not in nwset else "#E2A27F" for r in order])
a1.axvline(R["shares"]["early_eng"], color=INK, lw=1, ls=(0, (4, 3))); a2.axvline(R["shares"]["late_eng"], color=INK, lw=1, ls=(0, (4, 3)))
a1.set_yticks(y); a1.set_yticklabels(order); a2.set_yticks([])
for a_, k in ((a1, "early_pc"), (a2, "late_pc")):
    for i, r in enumerate(order):
        a_.text(reg.loc[r, k] + .8, i, f"{reg.loc[r, k]:.0f}%", va="center", fontsize=10, color=INK, path_effects=HALO, zorder=5)
    a_.grid(axis="x", color=RULE, lw=.6); a_.set_axisbelow(True)
a1.set_xlim(0, 72); a2.set_xlim(0, 22)
a1.set_title("Early: before AD 222 (periods 1 to 10)", fontsize=12, loc="left", color=COOL)
a2.set_title("Late: AD 364 to 402 (periods 19 to 21)", fontsize=12, loc="left", color=HOT)
a1.set_xlabel("% of dated Roman coins"); a2.set_xlabel("% of dated Roman coins")
title(fig, "The northern frontier keeps early coins, not late ones", "Share of each English region's dated Roman coin records from the first two centuries and from the last decades. Dashed: England.")
foot(fig); out(fig, "regions")

# ---------------------------------------------------------------- 4. small multiples by period (relative to England)
sel = [4, 10, 13, 14, 17, 21]
fig = plt.figure(figsize=(11, 10.4))
G20 = G[G.dated >= 20].copy()
eng_pm = {p: R["profile"][f"P{p}"]["per_mille"] for p in P21}
dn = TwoSlopeNorm(vmin=-1.6, vcenter=0, vmax=1.6)
for i, p in enumerate(sel):
    ax = fig.add_axes([0.02 + (i % 3) * 0.325, 0.53 - (i // 3) * 0.375, 0.31, 0.32]); basemap(ax)
    lq = np.log2(((1000 * G20[f"P{p}"] / G20.dated) + 0.5) / eng_pm[p])
    G[G.dated < 20].plot(ax=ax, color="#EDE6D6", edgecolor="#FFFFFF", linewidth=.15)
    G20.assign(lq=lq.clip(-1.6, 1.6)).plot(ax=ax, column="lq", cmap=DIV, norm=dn, edgecolor="#FFFFFF", linewidth=.15)
    eng.boundary.plot(ax=ax, color=INK, linewidth=.5); tidy(ax)
    ax.text(0.0, 1.075, f"{SHORT.get(p, RULERS[p])}", transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom", color=INK)
    ax.text(0.0, 1.01, f"{pdates(p)} · period {p}", transform=ax.transAxes, fontsize=9.5, va="bottom", color=MUT)
cax = fig.add_axes([0.36, 0.1, 0.3, 0.013])
cb = plt.colorbar(plt.cm.ScalarMappable(norm=dn, cmap=DIV), cax=cax, orientation="horizontal", ticks=[-1.58, -1, 0, 1, 1.58])
cb.ax.set_xticklabels(["a third", "half", "same as England", "twice", "3x"], fontsize=8.5); cb.outline.set_visible(False)
cax.set_title("Share of the district's dated coins from this period, against England", fontsize=9.5, color=INK)
fig.text(0.36, 0.055, "Pale: fewer than 20 dated coin records", fontsize=8.5, color=MUT)
title(fig, "Each reign has its own map", "Where coins of six periods are over- and under-represented, district by district, compared with the English profile.", y=0.985)
foot(fig); out(fig, "periods")

# ---------------------------------------------------------------- 5. per-period gradients (exploratory)
bp = pd.DataFrame(R["by_period"].values())
fig = plt.figure(figsize=(11, 6.6)); ax = fig.add_axes([0.08, 0.19, 0.88, 0.58])
x = bp.period.values
ax.axhline(1, color=INK, lw=1)
ax.errorbar(x - .14, bp.north_or, yerr=[bp.north_or - bp.north_lo, bp.north_hi - bp.north_or], fmt="o", color=COOL, ms=6, capsize=0, lw=1.6, label="per 100 km further north")
ax.errorbar(x + .14, bp.east_or, yerr=[bp.east_or - bp.east_lo, bp.east_hi - bp.east_or], fmt="s", color=HOT, ms=5.5, capsize=0, lw=1.6, label="per 100 km further east")
ax.set_xticks(x); ax.set_xticklabels([f"{p}" for p in x]); ax.set_yscale("log")
ax.set_yticks([.6, .8, 1, 1.25, 1.5, 1.8]); ax.set_yticklabels(["0.6", "0.8", "1", "1.25", "1.5", "1.8"]); ax.minorticks_off()
ax.set_xlabel("Reece period (1 = before AD 41 ... 21 = AD 388 to 402)"); ax.set_ylabel("Odds ratio of a coin being from this period")
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=10.5)
ax.annotate("Severan coins\nlean north", (10.86, bp.north_or[9]), xytext=(7.2, 1.66), fontsize=10, color=COOL, arrowprops=dict(arrowstyle="-", color=COOL, lw=.8))
ax.annotate("Carausius and\nAllectus lean east", (14.14, bp.east_or[13]), xytext=(15.6, 1.62), fontsize=10, color=HOT, arrowprops=dict(arrowstyle="-", color=HOT, lw=.8))
ax.grid(axis="y", color=RULE, lw=.6); ax.set_axisbelow(True)
title(fig, "Which periods lean north or east?", f"Exploratory: binomial models of each period's share of a district's dated coins on easting and northing, {R['sample']['d20']} districts, 95% intervals.")
foot(fig); out(fig, "gradients")

# ---------------------------------------------------------------- 6. robustness forest (planned tests)
lab = {"main": "Main (planned)", "min0": "All districts", "min50": "At least 50 dated", "min100": "At least 100 dated", "wls": "Weighted least squares",
       "cl_region": "Clustered by region", "drop_top10": "Without 10 biggest districts", "drop_spiky": "Without hoard-like districts",
       "intensity": "Control: records per km²", "negbin": "Negative binomial", "alt_after378": "Late = after 378", "alt_after330": "Late = after 330"}
fig = plt.figure(figsize=(11, 7.4))
for j, (h, nm) in enumerate((("H2", "Late share (AD 364 to 402)"), ("H3", "Early share (before AD 222)"))):
    rows = [k for k in lab if k in M[h]]
    for c, (cc, ttl) in enumerate((("east", "per 100 km east"), ("north", "per 100 km north"))):
        ax = fig.add_axes([0.24 + c * 0.2 + j * 0.39 - (0.0 if c == 0 else 0.0), 0.12, 0.17, 0.66]) if False else fig.add_axes([0.25 + (j * 2 + c) * 0.185, 0.14, 0.16, 0.62])
        for i, k in enumerate(rows):
            r = M[h][k][cc]
            ax.plot([r["lo"], r["hi"]], [i, i], color=HOT if j == 0 else COOL, lw=1.6)
            ax.plot(r["or"], i, "o", color=HOT if j == 0 else COOL, ms=5 if k != "main" else 7)
        ax.axvline(1, color=INK, lw=.9); ax.set_xscale("log"); ax.set_xlim(.5, 2); ax.minorticks_off()
        ax.set_xticks([.5, .7, 1, 1.4, 2]); ax.set_xticklabels(["0.5", "0.7", "1", "1.4", "2"], fontsize=9)
        ax.set_ylim(len(lab) - .5, -.7); ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([lab[k] for k in rows] if (j == 0 and c == 0) else [], fontsize=10)
        ax.set_title(f"{nm}\n{ttl}" if c == 0 else f"\n{ttl}", fontsize=10, loc="left", color=INK)
        ax.grid(axis="x", color=RULE, lw=.6); ax.set_axisbelow(True)
title(fig, "Little sign of a smooth gradient", "Pre-specified tests: odds ratios per 100 km east and north for the late and early shares, with 95% intervals. 1 = no gradient.")
foot(fig); out(fig, "robust")

# ---------------------------------------------------------------- 7. rulers
nat = R["rulers"]["national_top"]
fig = plt.figure(figsize=(11, 6.8)); ax = fig.add_axes([0.33, 0.17, 0.62, 0.62])
names = [n.replace("House of Constantine (AD 307-361)", "House of Constantine, 307 to 361 (no single ruler)").replace("Uncertain - AD 260-402", "Uncertain, AD 260 to 402")
         .replace("Uncertain - 4th century AD", "Uncertain, 4th century").replace("Radiate (imitation)", "Copies of radiates (local imitations)")
         .replace("House of Valentinian (AD 364-378)", "House of Valentinian, 364 to 378").replace("House of Theodosius (AD 379-457)", "House of Theodosius, 379 to 457") for n, _ in nat]
assert not any("-" in n for n in names), names
vals = [v for _, v in nat]
cols = [GOLD if "imitation" in n else (GREY if ("House" in n or "Uncertain" in n) else HOT) for n, _ in nat]
ax.barh(range(len(nat)), vals, color=cols); ax.set_yticks(range(len(nat))); ax.set_yticklabels(names, fontsize=10.5); ax.invert_yaxis()
for i, v in enumerate(vals): ax.text(v + 400, i, f"{v:,}", va="center", fontsize=9.5, color=INK)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")); ax.set_xlim(0, max(vals) * 1.15); ax.set_xlabel("PAS records (all of England and Wales)"); ax.grid(axis="x", color=RULE, lw=.6); ax.set_axisbelow(True)
ax.legend(handles=[Patch(color=HOT, label="a named ruler"), Patch(color=GREY, label="a dynasty or date range only"), Patch(color=GOLD, label="local copies")],
          frameon=False, loc="lower right", fontsize=10)
title(fig, "Whose face is on the coin?", "The 12 commonest ruler entries on Roman coin records in the PAS database.")
foot(fig, "Data: Portable Antiquities Scheme (finds.org.uk), national ruler facet, records to 2026 (includes Wales)\nmaps.tristanhotham.com/roman-coins"); out(fig, "rulers")

# ---------------------------------------------------------------- header.png
fig = plt.figure(figsize=(12, 6.3))
ax = fig.add_axes([0.53, 0.02, 0.46, 0.96]); basemap(ax); ax.set_facecolor(PAPER)
for g_ in (wales, scot): g_.plot(ax=ax, color="#EDE6D6", edgecolor="#D6CCB5", linewidth=.3)
G.plot(ax=ax, column="rate", cmap=SEQ, norm=norm, edgecolor="#FFFFFF", linewidth=.2); eng.boundary.plot(ax=ax, color=INK, linewidth=.6); tidy(ax)
fig.text(0.05, 0.80, "DATA STUDY · 2026", fontsize=12, family=MONO, color=MUT)
fig.text(0.05, 0.62, "Lost money", fontsize=58, fontweight="bold", family=DISP, color=HOT)
fig.text(0.05, 0.50, "Roman coins found in England,\nreign by reign", fontsize=24, family=DISP, color=INK, va="top", linespacing=1.1)
fig.text(0.05, 0.25, f"{R['build']['coins']:,} coin records\nin {R['build']['records']:,} finds", fontsize=17, color=INK, va="top", linespacing=1.3)
fig.text(0.05, 0.06, "Dr Tristan Hotham · maps.tristanhotham.com/roman-coins", fontsize=11, family=MONO, color=MUT)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER); plt.close(fig)
print(Image.open(f"{ROOT}/header.png").size, sorted(os.listdir(IMG)))
