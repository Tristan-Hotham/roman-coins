"""Step 6: index.html from code/page_template.html, code/page.css and the full-screen snippet, filled from data/results.json.
10.5281/zenodo.24115196 and https://blog.tristanhotham.com/2026/10/31/roman-coins/ stay for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
reg = R["regions"]
assert max(reg, key=lambda r: reg[r]["late_pc"]) == "South West"
assert R["rulers"]["county_top_counts"][0][0] == "Constantine I"
assert R["top_rate"][0]["district"] == "Huntingdonshire"
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{CSS}}", open(os.path.join(ROOT, "code", "page.css"), encoding="utf-8").read())
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "2026a")
t = fill(t, R)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= set(KEEP), set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "D" "SIT", "D" "CMS", "civil" " serv", "pre-" "registered"):
    assert bad not in vis, bad
assert 'site-nav.js' in t and 'data-fullscreen-map' in t
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
