"""Step 7: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_Lost_Money_Roman_Coins.pdf and .tex. The DOI stays the placeholder https://doi.org/10.5281/zenodo.24115196 unless the environment
variable DOI is set:  DOI=10.5281/zenodo.N python3 code/07_paper.py"""
import subprocess, pandas as pd
from common import *

R = jload(f"{DATA}/results.json"); M = jload(f"{DATA}/results_models.json")
OUT = os.path.join(REL, "paper"); NAME = "Hotham_Lost_Money_Roman_Coins"
B = R["build"]
def p3(p): return "$<$0.001" if p < 0.001 else f"{p:.3f}"
def ci(c, d=2): return f"{c['or']:.{d}f} [{c['lo']:.{d}f}, {c['hi']:.{d}f}]"
TD = ("\\begin{table}[tbp]\\centering\\small\\caption{The data: PAS facet counts for England, retrieved 2026.}\\label{tab:data}\\begin{tabular}{lr}\\toprule Item & Number\\\\\\midrule\n"
      f"Ceremonial counties queried & {B['counties']}\\\\\nDistricts (ONS 2023) & {B['districts']}\\\\\n"
      f"District names in the PAS data matched to ONS names & {B['names_in_pas']} of {B['names_in_pas']}\\\\\n"
      f"All PAS records, county totals & {B['records_county_total']:,}\\\\\n\\quad with a district & {B['records']:,}\\\\\n"
      f"Roman coin records & {B['coins']:,}\\\\\n\\quad with a Reece period 1 to 21 & {B['dated']:,}\\\\\n\\quad Reece periods 22 to 24 (excluded) & {B['p22_24']:,}\\\\\n"
      f"Roman coin records per 1,000 records & {B['coin_rate']:.1f}\\\\\n"
      f"Districts with at least 20 dated coin records & {R['sample']['d20']}\\\\\nDistricts with at least 100 dated coin records & {R['sample']['d100']}\\\\\n"
      f"Districts with no Roman coin record & {B['zero_coin_districts']}\\\\\n"
      f"PAS national Reece facet, periods 1 to 21 (incl.\\ Wales) & {B['pas_nat_reece_1_21']:,}\\\\\\bottomrule\\end{{tabular}}\\end{{table}}")
rows = ""
for p in P21:
    v = R["profile"][f"P{p}"]
    rows += (f"{p} & {pdates(p).replace('AD ', '')} & {RULERS[p]} & {v['n']:,} & {v['per_mille']:.1f} & "
             + (f"{v['per_year']:.2f}" if v['per_year'] else "") + "\\\\\n")
TP = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{England's Roman coin profile by Reece period: dated PAS coin records, per mille and per mille per year. "
      f"N = {B['dated']:,}.}}\\label{{tab:profile}}"
      "\\begin{tabular}{rllrrr}\\toprule Period & Years AD & Main issuers & Records & Per mille & Per year\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for h, lab in (("H2", "H2: late share, AD 364 to 402"), ("H3", "H3: early share, to AD 222"), ("H4", "H4: Roman coins of all records")):
    m = R[h]["main"]
    rows += f"{lab} & {ci(m['east'])} & {p3(m['east']['p'])} & {ci(m['north'])} & {p3(m['north']['p'])} & {m['n']} & {m['clusters']} & {m['dispersion']:.1f}\\\\\n"
TM = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Planned tests: binomial GLM odds ratios per 100 km east and north, 95\\% CI, standard errors clustered by ceremonial county. "
      "H2 and H3: districts with at least 20 dated coin records. Dispersion is the Pearson statistic over residual degrees of freedom of the unclustered model.}\\label{tab:main}"
      "\\begin{tabular}{lrrrrrrr}\\toprule Outcome & East OR [95\\% CI] & $p$ & North OR [95\\% CI] & $p$ & N & Clusters & Disp.\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
lab = {"main": "Main (planned)", "min0": "All districts with a dated coin", "min50": "At least 50 dated", "min100": "At least 100 dated", "wls": "WLS, empirical logit",
       "cl_region": "Clustered by region", "drop_top10": "Without 10 largest districts", "drop_spiky": "Without hoard-like districts",
       "intensity": "Control: log records per km$^2$", "negbin": "Negative binomial", "alt_after378": "Late = AD 378 to 402", "alt_after330": "Late = AD 330 to 402"}
rows = ""
for k, l in lab.items():
    cells = []
    for h in ("H2", "H3"):
        m = M[h].get(k)
        cells += [ci(m["east"]), ci(m["north"])] if m else ["", ""]
    n = M["H2"].get(k, M["H3"].get(k))["n"]
    rows += f"{l} & " + " & ".join(cells) + f" & {n}\\\\\n"
rows += "\\midrule\n"
for h in ("H2", "H3"):
    pm = M[h]["perm"]
    rows += f"Permutation $p$, {h} & \\multicolumn{{4}}{{l}}{{east {pm['p_east']:.3f}, north {pm['p_north']:.3f} (999 shuffles)}} & \\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\scriptsize\\caption{Robustness of the planned tests: odds ratios per 100 km [95\\% CI]. The leave-one-region-out fits are in Table~\\ref{tab:loro}.}\\label{tab:robust}"
      "\\begin{tabular}{lrrrrr}\\toprule & \\multicolumn{2}{c}{H2: late share} & \\multicolumn{2}{c}{H3: early share} & \\\\ Check & East & North & East & North & N\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for r, v in sorted(R["regions"].items()):
    rows += f"{r} & {v['records']:,} & {v['coins']:,} & {v['rate']:.0f} & {v['dated']:,} & {v['early_pc']:.1f} & {v['late_pc']:.1f}\\\\\n"
TG = ("\\begin{table}[htbp]\\centering\\small\\caption{English regions: all records, Roman coin records, coins per 1,000 records, dated coin records and early and late shares (\\%).}\\label{tab:regions}"
      "\\begin{tabular}{lrrrrrr}\\toprule Region & Records & Coins & Per 1,000 & Dated & Early & Late\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for reg in sorted(M["H2"]["loro"]):
    a, b, c = M["H2"]["loro"][reg], M["H3"]["loro"][reg], M["H4"]["loro"][reg]
    rows += f"{reg} & {ci(a['east'])} & {ci(a['north'])} & {ci(b['east'])} & {ci(b['north'])} & {ci(c['north'])}\\\\\n"
TL = ("\\begin{table}[htbp]\\centering\\scriptsize\\caption{Leaving out one region at a time: odds ratios per 100 km [95\\% CI].}\\label{tab:loro}"
      "\\begin{tabular}{lrrrrr}\\toprule Region left out & H2 east & H2 north & H3 east & H3 north & H4 north\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(f"{ROOT}/code/paper_template.tex", encoding="utf-8").read()
for k, v in (("TABLE_DATA", TD), ("TABLE_PROFILE", TP), ("TABLE_MAIN", TM), ("TABLE_ROBUST", TR), ("TABLE_REGIONS", TG), ("TABLE_LORO", TL)):
    assert "{{" + k + "}}" in t, k
    t = t.replace("{{" + k + "}}", v)
t = t.replace("{{AI}}", AI)
# region names with spaces in paths: handle "H3.loro.South East.north.or"
t = re.sub(r"\{\{(H\d)\.loro\.([A-Za-z ]+)\.(east|north)\.(or|lo|hi)\|f2\}\}", lambda m: f"{M[m.group(1)]['loro'][m.group(2)][m.group(3)][m.group(4)]:.2f}", t)
doi = os.environ.get("DOI")
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)).replace("%", "\\%"), t)
t_out = t.replace("https://doi.org/10.5281/zenodo.24115196", f"https://doi.org/{doi}" if doi else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t_out.replace("\\{\\{DOI\\_URL\\}\\}", ""), re.findall(r"\{\{[^}]*\}\}", t_out)[:5]
for bad in ("—", "–", "D" "SIT", "D" "CMS", "pre-" "registered"):
    assert bad not in t_out, bad
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/{NAME}.tex", "w", encoding="utf-8").write(t_out)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", f"{NAME}.tex"], cwd=OUT, capture_output=True, text=True)
log = open(f"{OUT}/{NAME}.log", encoding="utf-8", errors="ignore").read()
print("undefined refs:", log.count("undefined"), "| pages:", re.findall(r"Output written on .*?\((\d+) pages", log), "| errors:", log.count("\n! "))
for e in ("aux", "log", "out"):
    p = f"{OUT}/{NAME}.{e}"
    if os.path.exists(p): os.remove(p)
txt = subprocess.run(["pdftotext", f"{OUT}/{NAME}.pdf", "-"], capture_output=True, text=True).stdout
body = txt.split("\nReferences\n")[0]
print("words (whole pdf):", len(txt.split()), "| before references:", len(body.split()))
ab = re.search(r"Abstract(.*?)Keywords", txt, re.S)
print("abstract words:", len(ab.group(1).split()) if ab else None)
