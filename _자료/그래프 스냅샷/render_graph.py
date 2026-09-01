# -*- coding: utf-8 -*-
import os, re, math, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

VAULT = "/sessions/sweet-adoring-thompson/mnt/옵시디언/Vault"
OUT = os.path.join(VAULT, "_자료", "그래프 스냅샷", "2026-09-01 Before")
os.makedirs(OUT, exist_ok=True)
font = font_manager.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc")

EXCLUDE_DIRS = {".obsidian", ".trash", ".git", "Fast-EQA", "_템플릿", "_인박스"}
notes = {}  # name -> (zone, relpath)
links = []  # (src_name, dst_name)

for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        if not f.endswith(".md"): continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, VAULT).replace("\\", "/")
        if rel.split("/")[0] in EXCLUDE_DIRS: continue
        name = f[:-3]
        zone = rel.split("/")[0] if "/" in rel else "_ROOT_"
        notes[name] = (zone, rel)

wiki = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
for name, (zone, rel) in notes.items():
    try:
        body = open(os.path.join(VAULT, rel), encoding="utf-8", errors="ignore").read()
    except OSError: continue
    for m in wiki.finditer(body):
        tgt = m.group(1).strip().split("/")[-1]
        if tgt.endswith(".md"): tgt = tgt[:-3]
        if tgt in notes and tgt != name:
            links.append((name, tgt))

ZCOLOR = {
    "Java": "#F22626", "JavaScript": "#FEF848", "HTML": "#E67E22", "CSS": "#3498DB",
    "CS 이론": "#9B59B6", "Python": "#1ABC9C", "RPA": "#E84393", "AI": "#00BCD4",
    "프로젝트 코드 분석": "#D94F4F", "코드정리": "#FF8C42", "코드실습": "#B8E356",
    "프로젝트 노트": "#6952E0", "기술정리": "#4CAF50", "_규칙": "#8A8F98", "_ROOT_": "#FFFFFF",
    "_자료": "#555555",
}
KDT_ZONES = {"Java","JavaScript","HTML","CSS","CS 이론","Python","RPA","AI","_ROOT_"}

def layout(nodes_l, edges, it=900, seed=7):
    n = len(nodes_l)
    idx = {v:i for i,v in enumerate(nodes_l)}
    # 중복·양방향 링크 정리
    pairs = set()
    for a,b in edges:
        i,j = idx[a], idx[b]
        if i!=j: pairs.add((min(i,j), max(i,j)))
    E = np.array(sorted(pairs)) if pairs else np.zeros((0,2), int)
    rs = np.random.RandomState(seed)
    pos = rs.rand(n,2)*2-1
    k = 3.2*math.sqrt(4.0/n)      # FR 이상 거리 (넓게)
    t = 0.5
    for step in range(it):
        delta = pos[:,None,:]-pos[None,:,:]
        dist = np.linalg.norm(delta, axis=-1)+1e-9
        # 반발: k^2/d
        disp = ((k*k/dist)[:,:,None]*delta/dist[:,:,None]).sum(axis=1)
        if len(E):
            d = pos[E[:,0]]-pos[E[:,1]]
            dl = np.linalg.norm(d, axis=1, keepdims=True)+1e-9
            f = 0.25*(dl*dl/k)*d/dl  # 인력 완화
            np.add.at(disp, E[:,0], -f); np.add.at(disp, E[:,1], f)
        
        ln = np.linalg.norm(disp, axis=1, keepdims=True)+1e-9
        pos += disp/ln*np.minimum(ln, t)
        t *= 0.995
    return {v: pos[idx[v]] for v in nodes_l}, {tuple(sorted((nodes_l[i],nodes_l[j]))) for i,j in E}


def components(nodes_l, E):
    adj = {n:set() for n in nodes_l}
    for a,b in E: adj[a].add(b); adj[b].add(a)
    seen, comps = set(), []
    for n in nodes_l:
        if n in seen: continue
        stack, comp = [n], []
        while stack:
            v = stack.pop()
            if v in seen: continue
            seen.add(v); comp.append(v)
            stack.extend(adj[v]-seen)
        comps.append(comp)
    return sorted(comps, key=len, reverse=True)

def norm_box(pts, cx, cy, w, h):
    P = np.array(pts)
    lo, hi = P.min(axis=0), P.max(axis=0)
    span = np.maximum(hi-lo, 1e-6)
    return (P-lo)/span*np.array([w,h]) + np.array([cx-w/2, cy-h/2])

def render(fname, title, zone_filter):
    sub = [n for n,(z,_) in notes.items() if zone_filter(z)]
    subset = set(sub)
    E = [(a,b) for a,b in links if a in subset and b in subset]
    if not sub: print("skip", fname); return
    deg = {n:0 for n in sub}
    for a,b in E: deg[a]+=1; deg[b]+=1
    comps = components(sub, E)
    Eall = set(map(lambda e: tuple(sorted(e)), E))
    pos = {}
    big = [c for c in comps if len(c) >= 4]
    rest = [n for c in comps if len(c) < 4 for n in c]
    # 큰 성분: 면적 비례 상자에 각자 레이아웃
    total = sum(len(c) for c in big) or 1
    x_cursor, y_row, row_h, W = -2.1, 1.5, 0.0, 4.2
    for c in big:
        cset = set(c)
        Ec = [(a,b) for a,b in Eall if a in cset and b in cset]
        p, _ = layout(c, Ec, it=700, seed=11)
        w = max(0.7, math.sqrt(len(c)/total)*3.4)
        h = w*0.75
        if x_cursor + w > 2.1: x_cursor = -2.1; y_row -= row_h + 0.25; row_h = 0.0
        pts = norm_box([p[n] for n in c], x_cursor + w/2, y_row - h/2, w*0.92, h*0.92)
        for n, pt in zip(c, pts): pos[n] = pt
        x_cursor += w + 0.2; row_h = max(row_h, h)
    strip_y = y_row - row_h - 0.45
    for i, n in enumerate(rest):
        pos[n] = np.array([-2.0 + (i%18)*0.235, strip_y - (i//18)*0.16])
    E = [e for e in Eall]
    fig, ax = plt.subplots(figsize=(16,12), dpi=110)
    fig.patch.set_facecolor("#1e1e1e"); ax.set_facecolor("#1e1e1e"); ax.axis("off")
    for a,b in E:
        xa,ya = pos[a]; xb,yb = pos[b]
        ax.plot([xa,xb],[ya,yb], color="#5a5a5a", lw=0.4, alpha=0.4, zorder=1)
    xs = [pos[n][0] for n in sub]; ys = [pos[n][1] for n in sub]
    cs = [ZCOLOR.get(notes[n][0], "#AAAAAA") for n in sub]
    ss = [14+deg[n]*7 for n in sub]
    ax.scatter(xs, ys, s=ss, c=cs, zorder=2, edgecolors="none")
    for n in sub:
        if deg[n] >= max(6, np.percentile(list(deg.values()), 92)):
            ax.annotate(n, pos[n], fontproperties=font, fontsize=8, color="#cccccc",
                        xytext=(0,-11), textcoords="offset points", ha="center", zorder=3)
    lo_x, hi_x = np.percentile(xs, 1), np.percentile(xs, 99)
    lo_y, hi_y = np.percentile(ys, 1), np.percentile(ys, 99)
    mx, my = (hi_x-lo_x)*0.06+1e-3, (hi_y-lo_y)*0.06+1e-3
    ax.set_xlim(lo_x-mx, hi_x+mx); ax.set_ylim(lo_y-my, hi_y+my)
    ax.set_title(f"{title}  ·  노트 {len(sub)} · 링크 {len(E)}", fontproperties=font,
                 color="#dddddd", fontsize=14, pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, fname), facecolor="#1e1e1e", bbox_inches="tight")
    plt.close()
    print("저장:", fname, f"({len(sub)}노드/{len(E)}링크)")

render("00 전체 (Fast-EQA 제외).png", "전체 그래프 — Before", lambda z: True)
render("01 KDT 학습 구역.png", "KDT 학습 구역 (언어 폴더 + 지도) — Before", lambda z: z in KDT_ZONES)
render("02 프로젝트 코드 분석.png", "프로젝트 코드 분석 — Before", lambda z: z=="프로젝트 코드 분석")
render("03 코드정리.png", "코드정리 — Before", lambda z: z=="코드정리")
render("04 프로젝트 노트.png", "프로젝트 노트 (수집기·트리, 대비용) — Before", lambda z: z=="프로젝트 노트")
render("05 기술정리.png", "기술정리 — Before", lambda z: z=="기술정리")
