"""Shared paths, constants and helpers for roman-coins ("Lost money").

Inputs (read where they sit, never copied):
  RAW      pas_roman_coins.json: facet counts from the Portable Antiquities Scheme public search API (api.finds.org.uk),
           retrieved 2026. Keys: "nat" {reece, ruler, ceremonial, county}; per English ceremonial county "all|<county>"
           (all records by district), "coin|<county>" (Roman coin records by district), "ruler|<county>" (top 50 rulers),
           "reececty|<county>" (Reece periods), "reece|Period N|<county>" (Roman coin records of period N by district).
           Values are [name, count, flag]. Counts are records, not coins.
  LAD      ONS Local Authority Districts (December 2023) Boundaries UK BSC (Open Government Licence v3.0).
  TOPO     ONS boundaries topojson (regions layer "rgn"), Open Government Licence v3.0.
  CTY      Ceremonial counties of England (outline layer only).
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
REL = os.path.join(ROOT, "release")
SCR = os.environ.get("RC_SCRATCH", "/home/claude/scratch/roman-coins")
RAW = os.environ.get("RC_RAW", "/home/claude/newdata/raw_new14/coins/pas_roman_coins.json")
GEO = os.environ.get("RC_GEO", "/home/claude/newdata/raw/geo")
LAD = f"{GEO}/lad23_bsc.geojson"
TOPO = f"{GEO}/uk_topo.json"
CTY = f"{GEO}/counties_uk.geojson"
FONTS = os.environ.get("RC_FONTS", "/home/claude/ref/fonts")
for d in (DATA, IMG):
    os.makedirs(d, exist_ok=True)

SLUG = "roman-coins"
TITLE = "Lost money"
SUBTITLE = "Roman coins found in England, reign by reign"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"

# Reece periods (Nomisma.org reece1 to reece24, matching finds.org.uk/romancoins/reeceperiods)
REECE = {1: (None, 41, "Pre-Claudian and Iron Age"), 2: (41, 54, "Claudian"), 3: (54, 68, "Neronian"), 4: (69, 96, "Flavian"),
         5: (96, 117, "Trajanic"), 6: (117, 138, "Hadrianic"), 7: (138, 161, "Antonine I"), 8: (161, 180, "Antonine II"),
         9: (180, 193, "Antonine III"), 10: (193, 222, "Severus to Elagabalus"), 11: (222, 238, "Later Severan"),
         12: (238, 260, "Gordian III to Valerian"), 13: (260, 275, "Gallienus sole reign to Aurelian"),
         14: (275, 296, "Tacitus to Allectus"), 15: (296, 317, "The Tetrarchy"), 16: (317, 330, "Constantinian I"),
         17: (330, 348, "Constantinian II"), 18: (348, 364, "Constantinian III"), 19: (364, 378, "Valentinianic"),
         20: (378, 388, "Theodosian I"), 21: (388, 402, "Theodosian II"), 22: (402, 445, "Fifth century I"),
         23: (445, 498, "Fifth century II"), 24: (498, 565, "Anastasius to Justinian")}
# short reader-friendly labels for the page and figures
RULERS = {1: "Republic and Iron Age, to AD 41", 2: "Claudius", 3: "Nero", 4: "Vespasian, Titus, Domitian", 5: "Nerva, Trajan",
          6: "Hadrian", 7: "Antoninus Pius", 8: "Marcus Aurelius", 9: "Commodus", 10: "Severus to Elagabalus",
          11: "Severus Alexander, Maximinus", 12: "Gordian III to Valerian", 13: "Gallienus, Gallic Empire, Claudius II, Aurelian",
          14: "Probus, Carausius, Allectus", 15: "The Tetrarchy", 16: "Constantine I", 17: "Constantine I and his sons",
          18: "Constantius II, Magnentius, Julian", 19: "Valentinian I and Valens", 20: "Gratian, Theodosius, Magnus Maximus",
          21: "Theodosius I, Arcadius, Honorius"}
EARLY = list(range(1, 11))
LATE = list(range(19, 22))
P21 = list(range(1, 22))


def plen(p):
    a, b, _ = REECE[p]
    return None if a is None else b - a


def pdates(p):
    a, b, _ = REECE[p]
    return f"to AD {b}" if a is None else f"AD {a} to {b}"


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jsave(obj, p, indent=None):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(nonan(obj), f, ensure_ascii=False, allow_nan=False, indent=indent,
                  separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "abs0": return f"{abs(float(v)):.0f}"
    if f == "abs1": return f"{abs(float(v)):.1f}"
    raise ValueError(f)


KEEP = ("DOI", "DOI_URL", "BLOG_URL")


def fill(t, R, keep=KEEP):
    return re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}",
                  lambda m: m.group(0) if m.group(1) in keep or m.group(1).startswith("IMG") or m.group(1).startswith("TABLE")
                  else fmt(get(R, m.group(1)), m.group(3)), t)
