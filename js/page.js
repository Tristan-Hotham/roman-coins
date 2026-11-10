/* Lost money. Roman coin records on the Portable Antiquities Scheme by English district (ONS LAD 2023), on a plain MapLibre
 * base map (OpenFreeMap Positron). A slider steps through Reece's 21 coin periods. Counts of records only, findspots public to
 * district level. Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const fmt = n => Number(n).toLocaleString('en-GB');
  const SEQ = ['#F3E7C9', '#E8C27A', '#C9822F', '#9E4A22', '#5E2410'];
  const DIV = ['#2F6A9E', '#9DB8CF', '#EFE6D2', '#E2A27F', '#B4442E', '#6E1F12'];
  let map = null, G = null, S = null, mode = 'r', per = 0, timer = null, selName = null, popupObj = null;
  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => { ct.classList.toggle('folded', f); document.getElementById('ctToggle').setAttribute('aria-expanded', !f); };
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));

  // value for a district in the current mode and period
  function val(d) {
    const cnt = per === 0 ? d.k : d.p[per - 1];
    if (mode === 'r') return d.n >= 100 ? 1000 * cnt / d.n : null;
    if (per === 0) return d.n >= 100 && d.k > 0 ? Math.log2((1000 * d.k / d.n) / S.eng.rate) : null;
    if (d.d < 20) return null;
    return Math.log2(((1000 * cnt / d.d) + 0.5) / S.eng.pm[per - 1]);
  }
  let stops = [];
  function computeStops() {
    if (mode === 'e') { stops = [-1.6, -0.8, 0, 0.6, 1.2, 1.6]; return; }
    const v = Object.values(S.d).map(val).filter(x => x !== null).sort((a, b) => a - b);
    const q = f => v[Math.min(v.length - 1, Math.floor(f * (v.length - 1)))];
    let top = q(0.95); if (top <= 0) top = Math.max(1, v[v.length - 1]);
    const nice = x => x >= 100 ? Math.round(x / 50) * 50 : x >= 10 ? Math.round(x / 5) * 5 : x >= 1 ? Math.round(x) : +x.toFixed(1);
    stops = [0, nice(top * 0.25) || top * .25, nice(top * 0.5) || top * .5, nice(top * 0.75) || top * .75, nice(top) || top];
  }
  function colorExpr() {
    const pal = mode === 'e' ? DIV : SEQ, e = ['interpolate', ['linear'], ['get', 'v']];
    stops.forEach((s, i) => { e.push(s + i * 1e-6, pal[i]); });
    return ['case', ['==', ['get', 'ok'], 1], e, 'rgba(0,0,0,0)'];
  }
  function key() {
    const pm = S.periods[per - 1];
    document.getElementById('keyTitle').textContent = per === 0 ? 'All Roman coins' : `${pm.who}`;
    document.getElementById('keyBar').style.background = `linear-gradient(90deg,${(mode === 'e' ? DIV : SEQ).join(',')})`;
    if (mode === 'e') document.getElementById('keyEnds').innerHTML = '<span>a third</span><span>same as England</span><span>3x</span>';
    else document.getElementById('keyEnds').innerHTML = `<span>0</span><span>${fmt(stops[2])}</span><span>${fmt(stops[4])}+</span>`;
    document.getElementById('keySub').textContent = mode === 'e'
      ? (per === 0 ? 'Roman coin share of all finds, against England' : 'share of the district\'s dated coins, against England')
      : (per === 0 ? 'Roman coin records per 1,000 PAS records' : 'coin records of this period per 1,000 PAS records');
    document.getElementById('keyNote').textContent = mode === 'e' && per > 0 ? 'hatched: fewer than 20 dated coins' : 'hatched: fewer than 100 records';
    document.querySelectorAll('.chip[data-m]').forEach(x => x.setAttribute('aria-pressed', x.dataset.m === mode));
    document.getElementById('tlLab').textContent = per === 0 ? 'All periods' : `${pm.when}`;
    document.getElementById('tlSub').textContent = per === 0 ? 'Roman coins of every date' : `${pm.who} · period ${per}`;
  }
  function refresh() {
    computeStops();
    G.features.forEach(f => { const v = val(S.d[f.properties.nm]); f.properties.ok = v === null ? 0 : 1; f.properties.v = v === null ? 0 : Math.max(stops[0], Math.min(stops[stops.length - 1], v)); });
    map.getSource('s').setData(G);
    map.setPaintProperty('dist', 'fill-color', colorExpr());
    key();
    if (selName && popupObj && popupObj.isOpen()) popup(selName, popupObj.getLngLat());
  }
  function spark(d) {
    const W = 260, H = 64, n = 21, bw = W / n;
    if (d.d === 0) return '';
    const pm = d.p.map(x => 1000 * x / d.d), mx = Math.max(...pm, ...S.eng.pm);
    let s = `<svg class="spark" width="${W}" height="${H + 14}" viewBox="0 0 ${W} ${H + 14}" role="img" aria-label="Coin periods in this district against England">`;
    pm.forEach((v, i) => { const h = H * v / mx; s += `<rect x="${i * bw + 1}" y="${H - h}" width="${bw - 2}" height="${h}" fill="${i + 1 === per ? '#B4442E' : '#C9A27A'}"/>`; });
    let path = ''; S.eng.pm.forEach((v, i) => { path += `${i ? 'L' : 'M'}${i * bw + bw / 2},${H - H * v / mx}`; });
    s += `<path d="${path}" fill="none" stroke="#2B2119" stroke-width="1.3" stroke-dasharray="3 2"/>`;
    s += `<text x="0" y="${H + 12}" font-size="10" fill="#7A6A52">period 1</text><text x="${W}" y="${H + 12}" font-size="10" fill="#7A6A52" text-anchor="end">21</text></svg>`;
    return s;
  }
  function popup(name, ll) {
    selName = name;
    const d = S.d[name];
    let h = `<b class="t">${esc(name)}</b><div class="nt">${esc(d.c)} · ${esc(d.g)}</div><table>`;
    h += `<tr><td>All PAS records</td><td><b>${fmt(d.n)}</b></td></tr>`;
    h += `<tr><td>Roman coin records</td><td><b>${fmt(d.k)}</b> (${d.n ? (1000 * d.k / d.n).toFixed(0) : 0} per 1,000 records)</td></tr>`;
    h += `<tr><td>With a period</td><td>${fmt(d.d)}</td></tr>`;
    if (per > 0) {
      const c = d.p[per - 1], pm = S.periods[per - 1];
      h += `<tr><td>${esc(pm.when)}</td><td><b>${fmt(c)}</b>${d.d ? ` (${(100 * c / d.d).toFixed(1)}% of dated; England ${(S.eng.pm[per - 1] / 10).toFixed(1)}%)` : ''}</td></tr>`;
    }
    h += '</table>';
    if (d.d >= 20) h += spark(d) + '<p class="nt">Bars: share of the district\'s dated coins in each of Reece\'s 21 periods. Dashed line: England.</p>';
    else h += '<p class="nt">Fewer than 20 dated coin records: too few for a profile.</p>';
    const ru = S.rulers[d.c];
    if (ru && ru.length) h += `<p class="nt"><b>Commonest rulers in ${esc(d.c)}:</b> ${ru.slice(0, 5).map(x => `${esc(x[0])} (${fmt(x[1])})`).join(', ')}</p>`;
    h += '<p class="nt">Counts are records on the Portable Antiquities Scheme database (finds.org.uk), not individual coins. A record can hold several coins, and hoards can be recorded coin by coin.</p>';
    if (popupObj) popupObj.remove();
    popupObj = new maplibregl.Popup({ maxWidth: '320px', anchor: small ? 'bottom' : undefined }).setLngLat(ll).setHTML(h).addTo(map);
    map.setFilter('sel', ['==', ['get', 'nm'], name]);
  }
  function walk(f, fn) { (f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates).forEach(p => p[0].forEach(fn)); }
  function bounds(f) { let b = [180, 90, -180, -90]; walk(f, c => { b = [Math.min(b[0], c[0]), Math.min(b[1], c[1]), Math.max(b[2], c[0]), Math.max(b[3], c[1])]; }); return [[b[0], b[1]], [b[2], b[3]]]; }
  function centre(f) { const b = bounds(f); return [(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2]; }
  function setup(C, E) {
    G.features.forEach((f, i) => { f.id = i; });
    map.addSource('s', { type: 'geojson', data: G });
    map.addSource('c', { type: 'geojson', data: C });
    map.addSource('e', { type: 'geojson', data: E });
    const lbl = map.getStyle().layers.find(l => l.type === 'symbol');
    const cv = document.createElement('canvas'); cv.width = cv.height = 12; const cx = cv.getContext('2d');
    cx.fillStyle = 'rgba(255,255,255,0.7)'; cx.fillRect(0, 0, 12, 12); cx.strokeStyle = '#B9AE96'; cx.lineWidth = 1.2;
    cx.beginPath(); cx.moveTo(0, 12); cx.lineTo(12, 0); cx.moveTo(-6, 6); cx.lineTo(6, -6); cx.moveTo(6, 18); cx.lineTo(18, 6); cx.stroke();
    map.addImage('hatch', { width: 12, height: 12, data: cx.getImageData(0, 0, 12, 12).data });
    map.addLayer({ id: 'few', type: 'fill', source: 's', filter: ['==', ['get', 'ok'], 0], paint: { 'fill-pattern': 'hatch' } }, lbl && lbl.id);
    map.addLayer({ id: 'dist', type: 'fill', source: 's', filter: ['==', ['get', 'ok'], 1], paint: { 'fill-color': '#ccc', 'fill-opacity': ['case', ['boolean', ['feature-state', 'hover'], false], 0.96, 0.84] } }, lbl && lbl.id);
    map.addLayer({ id: 'lines', type: 'line', source: 's', paint: { 'line-color': '#FFFFFF', 'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.3, 10, 1.4], 'line-opacity': 0.9 } }, lbl && lbl.id);
    map.addLayer({ id: 'cty', type: 'line', source: 'c', paint: { 'line-color': '#6E604E', 'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.5, 10, 1.6], 'line-dasharray': [3, 2] } }, lbl && lbl.id);
    map.addLayer({ id: 'eng', type: 'line', source: 'e', paint: { 'line-color': '#2B2119', 'line-width': ['interpolate', ['linear'], ['zoom'], 5, 1.2, 10, 2.4] } });
    map.addLayer({ id: 'sel', type: 'line', source: 's', filter: ['==', ['get', 'nm'], ''], paint: { 'line-color': '#2B2119', 'line-width': 3 } });
    let hov = null;
    ['dist', 'few'].forEach(id => {
      map.on('click', id, e => popup(e.features[0].properties.nm, e.lngLat));
      map.on('mousemove', id, e => { map.getCanvas().style.cursor = 'pointer'; if (hov !== null) map.setFeatureState({ source: 's', id: hov }, { hover: false }); hov = e.features[0].id; map.setFeatureState({ source: 's', id: hov }, { hover: true }); });
      map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; if (hov !== null) map.setFeatureState({ source: 's', id: hov }, { hover: false }); hov = null; });
    });
    const tog = (box, ids) => document.getElementById(box).addEventListener('change', e => ids.forEach(id => map.setLayoutProperty(id, 'visibility', e.target.checked ? 'visible' : 'none')));
    tog('lyD', ['dist']); tog('lyF', ['few']); tog('lyO', ['lines']); tog('lyC', ['cty']); tog('lyE', ['eng']);
    tog('lyL', map.getStyle().layers.filter(l => l.type === 'symbol').map(l => l.id));
    // search: districts and counties
    const idx = G.features.map(f => ({ k: norm(f.properties.nm), t: f.properties.nm, sub: 'district, ' + S.d[f.properties.nm].c, f }));
    const cs = {}; G.features.forEach(f => { const c = S.d[f.properties.nm].c; (cs[c] = cs[c] || []).push(f); });
    Object.entries(cs).forEach(([c, L]) => idx.push({ k: norm(c), t: c, sub: `county, ${L.length} district${L.length > 1 ? 's' : ''}`, fs: L }));
    const q = document.getElementById('q'), sug = document.getElementById('sug');
    let hits = [], cur = -1;
    function go(h) {
      sug.style.display = 'none'; q.value = h.t;
      if (h.fs) { let b = [180, 90, -180, -90]; h.fs.forEach(f => walk(f, c => { b = [Math.min(b[0], c[0]), Math.min(b[1], c[1]), Math.max(b[2], c[0]), Math.max(b[3], c[1])]; })); map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: small ? 30 : 80, maxZoom: 10 }); return; }
      map.fitBounds(bounds(h.f), { padding: small ? 30 : 80, maxZoom: 9 });
      map.once('moveend', () => popup(h.t, centre(h.f)));
    }
    q.addEventListener('input', () => {
      const v = norm(q.value.trim()); cur = -1;
      if (v.length < 2) { sug.style.display = 'none'; return; }
      hits = idx.filter(x => x.k.includes(v)).sort((a, b) => (b.k.startsWith(v) - a.k.startsWith(v)) || a.k.length - b.k.length).slice(0, 8);
      sug.innerHTML = hits.map((h, i) => `<li role="option" data-i="${i}">${esc(h.t)} <span>${esc(h.sub)}</span></li>`).join('') || '<li>No match in England</li>';
      sug.style.display = 'block';
    });
    sug.addEventListener('click', e => { const li = e.target.closest('li[data-i]'); if (li) go(hits[+li.dataset.i]); });
    q.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); cur = Math.max(0, Math.min(hits.length - 1, cur + (e.key === 'ArrowDown' ? 1 : -1))); sug.querySelectorAll('li').forEach((l, i) => l.setAttribute('aria-selected', i === cur)); }
      if (e.key === 'Enter' && hits.length) go(hits[Math.max(cur, 0)]);
      if (e.key === 'Escape') sug.style.display = 'none';
    });
    document.querySelectorAll('.chip[data-m]').forEach(b => b.addEventListener('click', () => { mode = b.dataset.m; refresh(); }));
    const sl = document.getElementById('tl'), pb = document.getElementById('play');
    sl.addEventListener('input', () => { per = +sl.value; refresh(); });
    const stop = () => { clearInterval(timer); timer = null; pb.textContent = 'Play'; pb.setAttribute('aria-pressed', 'false'); };
    pb.addEventListener('click', () => {
      if (timer) { stop(); return; }
      pb.textContent = 'Pause'; pb.setAttribute('aria-pressed', 'true');
      if (per >= 21) per = 0;
      timer = setInterval(() => { per = per >= 21 ? 1 : per + 1; sl.value = per; refresh(); if (per === 21) stop(); }, 1300);
    });
    refresh();
  }
  const lb = document.getElementById('lyrBtn'), lp = document.getElementById('lp');
  lb.addEventListener('click', () => { const o = !lp.classList.contains('open'); lp.classList.toggle('open', o); lb.setAttribute('aria-expanded', o); });
  Promise.all(['data/districts.geojson', 'data/site.json', 'data/counties.geojson', 'data/england.geojson'].map(u => fetch(u).then(r => r.json()))).then(([g, s, c, e]) => {
    G = g; S = s;
    map = new maplibregl.Map({ container: 'map', style: STYLE, bounds: [[-6.4, 49.9], [1.9, 55.85]], fitBoundsOptions: { padding: small ? { top: 110, bottom: 70, left: 10, right: 10 } : { top: 40, bottom: 70, left: 360, right: 60 } }, attributionControl: { compact: true }, minZoom: 4, maxZoom: 13 });
    window.__map = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    map.on('load', () => { document.getElementById('nojs').style.display = 'none'; setup(c, e); });
  }).catch(() => { document.getElementById('nojs').textContent = 'The map data could not be loaded.'; });
})();
