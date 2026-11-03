# -*- coding: utf-8 -*-
"""obsidian-til README 자동 갱신.

Vault 를 훑어서 실제 데이터로 애니메이션 SVG 를 만든다 (.github/assets/).
  header.svg   — 별자리처럼 연결되는 헤더 + 노트·링크 수
  pipeline.svg — VS Code → Obsidian → GitHub / Notion 흐름
  graph.svg    — 실제 위키링크로 그린 지식 그래프 (노드가 서가별로 피어남)
  shelves.svg  — 서가별 노트 수를 책장으로
  growth.svg   — 누적 노트 수 성장 곡선 (git 기록 기반)
그리고 README.md 의 <!-- NAME:START --> ~ <!-- NAME:END --> 구간만 교체한다.
직접 쓴 나머지 README 내용은 건드리지 않는다.

의존성: numpy 만 필요. (python .github/scripts/update_readme.py)
"""
import math
import os
import random
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import quote

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, ".github", "assets")
README = os.path.join(ROOT, "README.md")
REPO_URL = "https://github.com/SeungMinShin01/obsidian-til"
KST = timezone(timedelta(hours=9))

EXCLUDE_TOP = {"_템플릿", "_자료", "Claude outputs"}
EXCLUDE_ANY = {"_인박스"}
EXCLUDE_ROOT_FILES = {"README.md", "CLAUDE.md"}

# (서가 이름, 짧은 영문, 색, 최상위 폴더들, 진입점 노트)
SHELVES = [
    ("KDT 수업 노트", "Bootcamp", "#F2C14E",
     ["Java", "JavaScript", "HTML", "CSS", "CS 이론", "Python", "RPA", "AI", "React", "Spring"],
     "KDT_2026 학습 지도.md"),
    ("기술 블로그 정리", "Tech Blog", "#4ADE80", ["기술정리"], "기술정리/기술정리 MOC.md"),
    ("프로젝트 결정 로그", "Projects", "#A78BFA", ["프로젝트 노트"], "프로젝트 노트/프로젝트 노트 MOC.md"),
    ("프로젝트 코드 분석", "Code Review", "#F87171", ["프로젝트 코드 분석"],
     "프로젝트 코드 분석/프로젝트 코드 분석 안내.md"),
    ("코드 레퍼런스", "Reference", "#FB923C", ["코드정리", "코드실습", "개념", "개인정리"], "코드정리/코드정리.md"),
    ("운영 규칙", "Rules", "#94A3B8", ["_규칙", "_ROOT_"], "Vault 홈.md"),
]
ZONE_TO_SHELF = {z: s[0] for s in SHELVES for z in s[3]}
SHELF_COLOR = {s[0]: s[2] for s in SHELVES}

KO = "'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR',sans-serif"
MONO = "'JetBrains Mono','D2Coding','Consolas','Menlo',monospace"
BG = "#0b1020"
WIKI = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
HUB = re.compile(r"MOC|인덱스|지도|홈")


# ── 공통 ────────────────────────────────────────────────────────────────
def gh_link(rel):
    return f"{REPO_URL}/blob/main/{quote(rel)}"


def git(*args):
    return subprocess.run(["git", "-c", "core.quotepath=false", "-C", ROOT, *args],
                          capture_output=True, text=True, encoding="utf-8").stdout


def zone_of(rel):
    return rel.split("/")[0] if "/" in rel else "_ROOT_"


def shelf_of(rel):
    return ZONE_TO_SHELF.get(zone_of(rel), "운영 규칙")


def svg_open(w, h, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/>'
            f'<feMergeNode in="SourceGraphic"/></feMerge></filter>{extra_defs}</defs>'
            f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>')


def fade(begin, dur=0.5):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'


def write(name, svg):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 데이터 수집 ──────────────────────────────────────────────────────────
def collect():
    notes = {}
    for root, dirs, files in os.walk(ROOT):
        rel_root = os.path.relpath(root, ROOT).replace("\\", "/")
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in EXCLUDE_ANY
                   and not (rel_root == "." and d in EXCLUDE_TOP)]
        for f in files:
            if not f.endswith(".md") or (rel_root == "." and f in EXCLUDE_ROOT_FILES):
                continue
            notes[f[:-3]] = f if rel_root == "." else f"{rel_root}/{f}"
    return notes


def collect_links(notes):
    edges = set()
    for name, rel in notes.items():
        try:
            body = open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in WIKI.finditer(body):
            tgt = m.group(1).strip().split("/")[-1]
            tgt = tgt[:-3] if tgt.endswith(".md") else tgt
            if tgt in notes and tgt != name:
                edges.add(tuple(sorted((name, tgt))))
    return edges


def growth_series(notes):
    """지금 남아 있는 노트만, 처음 추가된 날짜 기준으로 누적한다 (최종값 = 현재 노트 수)."""
    rels = set(notes.values())
    log = git("log", "--diff-filter=A", "--name-only", "--format=@%ad", "--date=short", "--reverse")
    first, day = {}, None
    for line in log.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line in rels and line not in first:
            first[line] = day
    per_day = Counter(first.values())
    per_day[max(per_day) if per_day else "2026-08-11"] += len(rels) - len(first)  # 기록에 없는 파일 보정
    days = sorted(per_day)
    return days, [int(v) for v in np.cumsum([per_day[d] for d in days])]


def recent(notes, limit=8):
    rels = set(notes.values())
    log = git("log", "-n", "400", "--name-only", "--format=@%ad", "--date=short")
    seen, rows, day = set(), [], None
    for line in log.splitlines():
        if line.startswith("@"):
            day = line[1:]
            continue
        line = line.strip()
        if line in rels and line not in seen and not HUB.search(line) and "규칙" not in line:
            seen.add(line)
            rows.append((day, line))
            if len(rows) >= limit:
                break
    return rows


# ── SVG 1. 헤더 ──────────────────────────────────────────────────────────
def header_svg(total, n_links, since):
    W, H = 900, 260
    rnd = random.Random(3)
    pts = [(rnd.uniform(20, W - 20), rnd.uniform(15, H - 15)) for _ in range(46)]
    out = [svg_open(W, H,
                    '<linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">'
                    '<stop offset="0" stop-color="#1e1b4b"/><stop offset="0.6" stop-color="#0b1020"/>'
                    '<stop offset="1" stop-color="#052e2b"/></linearGradient>'
                    '<linearGradient id="tg" x1="0" y1="0" x2="1" y2="0">'
                    '<stop offset="0" stop-color="#c4b5fd"/><stop offset="0.5" stop-color="#f0abfc"/>'
                    '<stop offset="1" stop-color="#5eead4"/></linearGradient>')]
    out.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#hg)"/>')
    # 별자리: 가까운 점끼리 선이 그어진다
    k = 0
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1:]:
            d = math.hypot(x1 - x2, y1 - y2)
            if d < 105:
                out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#a78bfa" '
                           f'stroke-width="0.8" stroke-opacity="0.35" stroke-dasharray="{d:.0f}" '
                           f'stroke-dashoffset="{d:.0f}"><animate attributeName="stroke-dashoffset" '
                           f'to="0" begin="{0.2 + k * 0.03:.2f}s" dur="0.8s" fill="freeze"/></line>')
                k += 1
    for i, (x, y) in enumerate(pts):
        r = rnd.uniform(1.2, 3.2)
        c = rnd.choice(["#c4b5fd", "#5eead4", "#f0abfc", "#fde68a"])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{c}">'
                   f'<animate attributeName="opacity" values="0.25;1;0.25" dur="{rnd.uniform(2, 4.5):.1f}s" '
                   f'begin="{rnd.uniform(0, 2):.1f}s" repeatCount="indefinite"/></circle>')
    # 가운데 판넬
    out.append(f'<rect x="170" y="62" width="560" height="136" rx="16" fill="#0b1020" fill-opacity="0.72" '
               f'stroke="#a78bfa" stroke-opacity="0.35"/>')
    out.append(f'<g opacity="0">{fade(0.4, 0.8)}'
               f'<text x="450" y="112" text-anchor="middle" font-family="{MONO}" font-size="36" '
               f'font-weight="700" fill="url(#tg)" filter="url(#glow)">Dev Knowledge Vault</text></g>')
    out.append(f'<g opacity="0">{fade(1.0)}'
               f'<text x="450" y="146" text-anchor="middle" font-family="{KO}" font-size="16" fill="#cbd5e1">'
               f'배운 것을 쌓고, 잇고, 다시 꺼내 쓰는 개발 지식 저장소</text></g>')
    chips = [(f"{total} notes", "#a78bfa"), (f"{n_links} links", "#5eead4"), (f"since {since}", "#fde68a")]
    x = 450 - (len(chips) * 140 - 12) / 2
    for i, (label, c) in enumerate(chips):
        out.append(f'<g opacity="0">{fade(1.5 + i * 0.25)}'
                   f'<rect x="{x:.0f}" y="162" width="128" height="24" rx="12" fill="{c}" fill-opacity="0.12" '
                   f'stroke="{c}" stroke-opacity="0.6"/><text x="{x + 64:.0f}" y="179" text-anchor="middle" '
                   f'font-family="{MONO}" font-size="12" fill="{c}">{escape(label)}</text></g>')
        x += 140
    out.append("</svg>")
    return "".join(out)


# ── SVG 2. 파이프라인 ────────────────────────────────────────────────────
def pipeline_svg():
    W, H = 900, 230
    boxes = {
        "src": (30, 40, "수업 · 프로젝트 코드", "VS Code (읽기 전용)", "#60a5fa"),
        "ai": (30, 140, "AI 세션 (역할 분담)", "Claude Cowork · Code", "#f0abfc"),
        "vault": (345, 90, "Obsidian Vault", "원본 · Single Source of Truth", "#a78bfa"),
        "gh": (660, 40, "GitHub", "obsidian-git · 30분 자동 커밋", "#e2e8f0"),
        "notion": (660, 140, "Notion", "Sync Engine · 미러", "#5eead4"),
    }
    bw, bh = 210, 54
    out = [svg_open(W, H)]

    def center_right(k):
        x, y = boxes[k][:2]
        return x + bw, y + bh / 2

    def center_left(k):
        x, y = boxes[k][:2]
        return x, y + bh / 2

    flows = [("src", "vault", "#60a5fa"), ("ai", "vault", "#f0abfc"),
             ("vault", "gh", "#e2e8f0"), ("vault", "notion", "#5eead4")]
    for i, (a, b, c) in enumerate(flows):
        x1, y1 = center_right(a)
        x2, y2 = center_left(b)
        mx = (x1 + x2) / 2
        d = f"M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} {x2:.0f},{y2:.0f}"
        out.append(f'<path id="f{i}" d="{d}" fill="none" stroke="{c}" stroke-opacity="0.35" stroke-width="2" '
                   f'stroke-dasharray="5 5"/>')
        for j in range(3):
            out.append(f'<circle r="3.5" fill="{c}" filter="url(#glow)"><animateMotion dur="2.4s" '
                       f'begin="{j * 0.8 + i * 0.3:.1f}s" repeatCount="indefinite"><mpath href="#f{i}"/>'
                       f'</animateMotion></circle>')
    for i, (k, (x, y, title, sub, c)) in enumerate(boxes.items()):
        big = k == "vault"
        out.append(f'<g opacity="0">{fade(0.15 * i)}'
                   f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="{c}" '
                   f'fill-opacity="{0.16 if big else 0.08}" stroke="{c}" stroke-width="{2 if big else 1.2}"'
                   f'{" filter=" + chr(34) + "url(#glow)" + chr(34) if big else ""}/>'
                   f'<text x="{x + bw / 2}" y="{y + 23}" text-anchor="middle" font-family="{KO}" font-size="15" '
                   f'font-weight="700" fill="{c}">{escape(title)}</text>'
                   f'<text x="{x + bw / 2}" y="{y + 42}" text-anchor="middle" font-family="{KO}" font-size="11" '
                   f'fill="#94a3b8">{escape(sub)}</text></g>')
    out.append("</svg>")
    return "".join(out)


# ── SVG 3. 지식 그래프 ──────────────────────────────────────────────────
def layout(nodes, edges, it=500, seed=7):
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    E = np.array([(idx[a], idx[b]) for a, b in edges]) if edges else np.zeros((0, 2), int)
    rs = np.random.RandomState(seed)
    pos = rs.rand(n, 2) * 2 - 1
    k = 1.6 / math.sqrt(n)
    t = 0.25
    for _ in range(it):
        delta = pos[:, None, :] - pos[None, :, :]
        d2 = (delta ** 2).sum(-1) + 1e-6
        disp = ((k * k / d2)[:, :, None] * delta).sum(axis=1)
        if len(E):
            d = pos[E[:, 0]] - pos[E[:, 1]]
            dl = np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
            f = (dl / k) * d
            np.add.at(disp, E[:, 0], -f)
            np.add.at(disp, E[:, 1], f)
        disp -= pos * 1.2  # 중력: 섬들이 화면 밖으로 흩어지지 않게
        ln = np.linalg.norm(disp, axis=1, keepdims=True) + 1e-9
        pos += disp / ln * np.minimum(ln, t)
        t = max(t * 0.99, 0.003)
    return pos, idx


def graph_svg(notes, edges):
    W, H, PAD, TOP, BOTTOM = 1000, 600, 30, 50, 70
    nodes = sorted(notes, key=lambda v: ([s[0] for s in SHELVES].index(shelf_of(notes[v])), v))
    pos, idx = layout(nodes, edges)
    lo, hi = np.percentile(pos, 1, axis=0), np.percentile(pos, 99, axis=0)
    span = np.maximum(hi - lo, 1e-9)
    P = (pos - lo) / span
    P = np.clip(P, -0.02, 1.02)
    xy = np.column_stack([PAD + P[:, 0] * (W - 2 * PAD), TOP + P[:, 1] * (H - TOP - BOTTOM)])

    deg = Counter()
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1

    out = [svg_open(W, H)]
    out.append(f'<text x="{PAD}" y="32" font-family="{KO}" font-size="16" font-weight="700" fill="#e2e8f0">'
               f'Knowledge Graph</text><text x="{PAD + 150}" y="32" font-family="{MONO}" font-size="12" '
               f'fill="#64748b">{len(nodes)} notes · {len(edges)} links · 위키링크 기준</text>')
    # 엣지: 서가별 path 하나로 묶어 가볍게
    by_shelf = {}
    for a, b in edges:
        p, q = xy[idx[a]], xy[idx[b]]
        by_shelf.setdefault(shelf_of(notes[a]), []).append(f"M{p[0]:.0f} {p[1]:.0f}L{q[0]:.0f} {q[1]:.0f}")
    out.append(f'<g opacity="0">{fade(2.2, 1.2)}')
    for s, segs in by_shelf.items():
        out.append(f'<path d="{"".join(segs)}" stroke="{SHELF_COLOR[s]}" stroke-opacity="0.22" '
                   f'stroke-width="0.6" fill="none"/>')
    out.append("</g>")
    # 노드: 서가 순서대로 피어난다
    n = len(nodes)
    for i, v in enumerate(nodes):
        x, y = xy[idx[v]]
        r = 1.8 + 1.3 * math.sqrt(deg[v])
        c = SHELF_COLOR[shelf_of(notes[v])]
        b = 0.2 + 2.0 * i / max(n, 1)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0" fill="{c}" fill-opacity="0.9">'
                   f'<animate attributeName="r" values="0;{r * 1.6:.1f};{r:.1f}" begin="{b:.2f}s" dur="0.5s" '
                   f'fill="freeze"/></circle>')
    # 상위 허브: 맥박 + 라벨
    hubs, placed = [], []
    for v in sorted([v for v in nodes if HUB.search(v)], key=lambda v: -deg[v]):
        x, y = xy[idx[v]]
        if all(abs(x - px) > 120 or abs(y - py) > 16 for px, py in placed):
            hubs.append(v)
            placed.append((x, y))
        if len(hubs) >= 9:
            break
    for j, v in enumerate(hubs):
        x, y = xy[idx[v]]
        r = 1.8 + 1.3 * math.sqrt(deg[v])
        c = SHELF_COLOR[shelf_of(notes[v])]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{c}" stroke-width="1.5">'
                   f'<animate attributeName="r" values="{r:.1f};{r + 12:.1f}" dur="2.4s" begin="{3 + j * 0.3:.1f}s" '
                   f'repeatCount="indefinite"/><animate attributeName="stroke-opacity" values="0.8;0" dur="2.4s" '
                   f'begin="{3 + j * 0.3:.1f}s" repeatCount="indefinite"/></circle>')
        anchor = "end" if x > W * 0.8 else "start"
        dx = -(r + 4) if anchor == "end" else r + 4
        out.append(f'<g opacity="0">{fade(2.8 + j * 0.1)}<text x="{x + dx:.0f}" y="{y + 4:.0f}" '
                   f'text-anchor="{anchor}" font-family="{KO}" font-size="11" fill="#e2e8f0" '
                   f'stroke="{BG}" stroke-width="3" paint-order="stroke">{escape(v)}</text></g>')
    # 범례
    counts = Counter(shelf_of(r) for r in notes.values())
    x = PAD
    for s in SHELVES:
        label = f"{s[0]} {counts.get(s[0], 0)}"
        out.append(f'<circle cx="{x + 5}" cy="{H - 28}" r="5" fill="{s[2]}"/>'
                   f'<text x="{x + 15}" y="{H - 24}" font-family="{KO}" font-size="12" fill="#cbd5e1">'
                   f'{escape(label)}</text>')
        x += 22 + len(label) * 10.5
    out.append("</svg>")
    return "".join(out)


# ── SVG 4. 책장 ──────────────────────────────────────────────────────────
def shelves_svg(notes):
    W, H = 900, 300
    counts = Counter(shelf_of(r) for r in notes.values())
    out = [svg_open(W, H)]
    out.append(f'<text x="30" y="36" font-family="{KO}" font-size="16" font-weight="700" fill="#e2e8f0">'
               f'Bookshelf</text><text x="125" y="36" font-family="{MONO}" font-size="12" fill="#64748b">'
               f'책 한 권 = 노트 5개</text>')
    base, slot = 230, (W - 60) / len(SHELVES)
    rnd = random.Random(11)
    for si, (name, en, c, _z, _e) in enumerate(SHELVES):
        x0 = 30 + si * slot + 10
        cnt = counts.get(name, 0)
        books = max(1, round(cnt / 5))
        per_row = 12
        bw = (slot - 20) / per_row
        for b in range(books):
            row, col = divmod(b, per_row)
            if row > 3:
                break
            h = rnd.uniform(26, 38)
            x = x0 + col * bw
            y = base - row * 42 - h
            shade = rnd.choice(["0.95", "0.8", "0.65"])
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 1.5:.1f}" height="{h:.1f}" rx="1.5" '
                       f'fill="{c}" fill-opacity="{shade}" opacity="0">'
                       f'<animate attributeName="opacity" from="0" to="1" begin="{0.2 + si * 0.25 + b * 0.012:.2f}s" '
                       f'dur="0.3s" fill="freeze"/></rect>')
        for row in range(4):
            y = base - row * 42 + 1
            out.append(f'<rect x="{x0 - 4:.0f}" y="{y}" width="{slot - 12:.0f}" height="3" rx="1.5" '
                       f'fill="#334155"/>')
        cx = x0 + (slot - 20) / 2
        out.append(f'<text x="{cx:.0f}" y="{base + 30}" text-anchor="middle" font-family="{MONO}" font-size="22" '
                   f'font-weight="700" fill="{c}">{cnt}</text>'
                   f'<text x="{cx:.0f}" y="{base + 50}" text-anchor="middle" font-family="{KO}" font-size="12" '
                   f'fill="#cbd5e1">{escape(name)}</text>')
    out.append("</svg>")
    return "".join(out)


# ── SVG 5. 성장 곡선 ────────────────────────────────────────────────────
def growth_svg(days, ys):
    W, H, L, R, T, B = 900, 240, 50, 30, 50, 40
    out = [svg_open(W, H, '<linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">'
                          '<stop offset="0" stop-color="#a78bfa" stop-opacity="0.45"/>'
                          '<stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>')]
    out.append(f'<text x="30" y="34" font-family="{KO}" font-size="16" font-weight="700" fill="#e2e8f0">'
               f'Growth</text><text x="100" y="34" font-family="{MONO}" font-size="12" fill="#64748b">'
               f'누적 노트 수 · git 기록 기준</text>')
    if not days:
        out.append("</svg>")
        return "".join(out)
    d0 = datetime.strptime(days[0], "%Y-%m-%d")
    d1 = datetime.strptime(days[-1], "%Y-%m-%d")
    span = max((d1 - d0).days, 1)
    ymax = max(ys) * 1.1
    pts = []
    for d, y in zip(days, ys):
        x = L + (datetime.strptime(d, "%Y-%m-%d") - d0).days / span * (W - L - R)
        pts.append((x, T + (1 - y / ymax) * (H - T - B)))
    step = [pts[0]]
    for p in pts[1:]:
        step += [(p[0], step[-1][1]), p]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in step)
    length = sum(math.hypot(step[i + 1][0] - step[i][0], step[i + 1][1] - step[i][1]) for i in range(len(step) - 1))
    for g in range(5):
        y = T + g * (H - T - B) / 4
        val = int(ymax * (1 - g / 4))
        out.append(f'<line x1="{L}" y1="{y:.0f}" x2="{W - R}" y2="{y:.0f}" stroke="#1e293b"/>'
                   f'<text x="{L - 8}" y="{y + 4:.0f}" text-anchor="end" font-family="{MONO}" font-size="10" '
                   f'fill="#64748b">{val}</text>')
    out.append(f'<polygon points="{L},{H - B} {line} {step[-1][0]:.1f},{H - B}" fill="url(#ga)" opacity="0">'
               f'{fade(1.6, 0.8)}</polygon>')
    out.append(f'<polyline points="{line}" fill="none" stroke="#c4b5fd" stroke-width="2.5" '
               f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
               f'<animate attributeName="stroke-dashoffset" to="0" begin="0.2s" dur="1.8s" fill="freeze"/></polyline>')
    ex, ey = step[-1]
    out.append(f'<g opacity="0">{fade(2.0)}<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="#f0abfc" '
               f'filter="url(#glow)"><animate attributeName="r" values="4.5;7;4.5" dur="1.6s" '
               f'repeatCount="indefinite"/></circle><text x="{ex - 10:.0f}" y="{ey - 12:.0f}" text-anchor="end" '
               f'font-family="{MONO}" font-size="13" font-weight="700" fill="#f0abfc">{ys[-1]} notes</text></g>')
    for d, anchor, x in [(days[0], "start", L), (days[-1], "end", W - R)]:
        out.append(f'<text x="{x}" y="{H - 16}" text-anchor="{anchor}" font-family="{MONO}" font-size="11" '
                   f'fill="#64748b">{d}</text>')
    out.append("</svg>")
    return "".join(out)


# ── README 조립 ─────────────────────────────────────────────────────────
def replace_block(text, name, content):
    pat = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    return pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    notes = collect()
    edges = collect_links(notes)
    days, ys = growth_series(notes)
    since = days[0].replace("-", ".") if days else "2026.08.11"
    now = datetime.now(KST).strftime("%Y-%m-%d")

    write("header.svg", header_svg(len(notes), len(edges), since))
    write("pipeline.svg", pipeline_svg())
    write("graph.svg", graph_svg(notes, edges))
    write("shelves.svg", shelves_svg(notes))
    write("growth.svg", growth_svg(days, ys))

    counts = Counter(shelf_of(r) for r in notes.values())
    shelf_rows = ["| 서가 | 노트 | 들어가기 |", "| --- | ---: | --- |"]
    for name, _en, _c, zones, entry in SHELVES:
        title = os.path.basename(entry)[:-3]
        shelf_rows.append(f"| **{name}** | {counts.get(name, 0)} | [{title}]({gh_link(entry)}) |")

    rec_rows = ["| 날짜 | 노트 | 서가 |", "| --- | --- | --- |"]
    for day, rel in recent(notes):
        rec_rows.append(f"| `{day}` | [{os.path.basename(rel)[:-3]}]({gh_link(rel)}) | {shelf_of(rel)} |")
    rec_rows.append(f"\n<sub>마지막 자동 갱신: {now} (KST)</sub>")

    text = open(README, encoding="utf-8").read()
    text = replace_block(text, "SHELVES", "\n".join(shelf_rows))
    text = replace_block(text, "RECENT", "\n".join(rec_rows))
    open(README, "w", encoding="utf-8").write(text)
    print(f"notes={len(notes)} links={len(edges)} shelves={dict(counts)}")


if __name__ == "__main__":
    main()
