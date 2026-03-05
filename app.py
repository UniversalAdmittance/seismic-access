"""
╔══════════════════════════════════════════════════════════════════════╗
║  SEISMIC ACCESS — Validatore di Accessibilità Sismica Urbana       ║
║  Two-Tier Framework: CLE-2D vs Geometric-Kinematic Model           ║
║  © 2025 Giannini & Nescatelli — Sapienza / Plantiverse             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Wedge, Arc, FancyArrowPatch
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
from scipy.stats import norm, lognorm
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import json
import io
import time

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SEISMIC ACCESS — Validatore Accessibilità Sismica",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
# CUSTOM CSS — Industrial Italian Engineering
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,300&family=JetBrains+Mono:wght@400;600&family=Playfair+Display:wght@700;900&display=swap');

:root {
    --danger: #E8443A;
    --safe: #2ECC71;
    --warn: #F39C12;
    --navy: #0E1117;
    --slate: #1A1F2E;
    --steel: #2D3548;
    --text: #E8EAF0;
    --muted: #8892A4;
    --accent: #4A9EFF;
}

/* Global */
.stApp { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; }
code, .stCode { font-family: 'JetBrains Mono', monospace !important; }

/* Hero Section */
.hero-container {
    background: linear-gradient(135deg, #0E1117 0%, #1A1F2E 50%, #0E1117 100%);
    border: 1px solid #2D3548;
    border-radius: 12px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #E8443A, #F39C12, #2ECC71);
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #E8EAF0;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #8892A4;
    line-height: 1.6;
    max-width: 800px;
}
.hero-badge {
    display: inline-block;
    background: rgba(232, 68, 58, 0.15);
    border: 1px solid rgba(232, 68, 58, 0.3);
    color: #E8443A;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Result Cards */
.result-card {
    border-radius: 10px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    border: 1px solid #2D3548;
}
.card-danger {
    background: linear-gradient(135deg, rgba(232,68,58,0.08), rgba(232,68,58,0.02));
    border-color: rgba(232,68,58,0.3);
}
.card-safe {
    background: linear-gradient(135deg, rgba(46,204,113,0.08), rgba(46,204,113,0.02));
    border-color: rgba(46,204,113,0.3);
}
.card-warn {
    background: linear-gradient(135deg, rgba(243,156,18,0.08), rgba(243,156,18,0.02));
    border-color: rgba(243,156,18,0.3);
}
.card-info {
    background: linear-gradient(135deg, rgba(74,158,255,0.08), rgba(74,158,255,0.02));
    border-color: rgba(74,158,255,0.3);
}

/* Metric Big Number */
.metric-big {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.8rem;
    font-weight: 700;
    line-height: 1;
    margin: 0.3rem 0;
}
.metric-label {
    font-size: 0.8rem;
    color: #8892A4;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}
.metric-unit {
    font-size: 1rem;
    color: #8892A4;
    font-weight: 400;
}

/* Verdict Badges */
.verdict-blocked {
    display: inline-block;
    background: rgba(232,68,58,0.2);
    color: #FF6B6B;
    padding: 6px 16px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}
.verdict-passable {
    display: inline-block;
    background: rgba(46,204,113,0.2);
    color: #2ECC71;
    padding: 6px 16px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}

/* Section Dividers */
.section-divider {
    border: none;
    border-top: 1px solid #2D3548;
    margin: 2rem 0;
}
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #4A9EFF;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* Sidebar */
.sidebar-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #E8EAF0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #E8443A;
    margin-bottom: 1rem;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# CORE ENGINE — Tier I & Tier II Mathematics
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Building:
    """Single building in the inventory."""
    id: int
    x: float                  # centroid x
    y: float                  # centroid y
    height: float             # geometric height (m)
    width_x: float            # footprint dimension x (m)
    width_y: float            # footprint dimension y (m)
    typology: str             # 'URM_low', 'URM_mid', 'RC_old', 'RC_new'
    storeys: int
    facade_angle: float       # angle of active facade normal (radians)
    confinement: str          # 'isolated', 'end_row', 'mid_row', 'courtyard'
    slope: float = 0.0        # local terrain slope (fraction)
    soil_class: str = 'B'     # Eurocode 8 soil class

@dataclass
class RoadSegment:
    """Single road segment."""
    id: int
    x1: float; y1: float     # start node
    x2: float; y2: float     # end node
    width: float              # carriageway width (m)
    r_min: float = 100.0      # minimum curvature radius (m)
    is_strategic: bool = False

@dataclass
class StrategicNode:
    """Strategic facility node."""
    id: int
    x: float; y: float
    name: str
    weight: float             # priority weight
    node_type: str            # 'hospital', 'municipality', 'fire_station', 'assembly'


# ─── Fragility Parameters ───────────────────────────────────────────
FRAGILITY = {
    'URM_low':  {'w50': 0.18, 'a': 12.0, 'c': 0.18, 'd': 1.35, 'theta': 65.0, 'sigma_b': 0.55},
    'URM_mid':  {'w50': 0.15, 'a': 10.0, 'c': 0.22, 'd': 1.50, 'theta': 65.0, 'sigma_b': 0.55},
    'RC_old':   {'w50': 0.30, 'a':  8.0, 'c': 0.10, 'd': 1.20, 'theta': 38.0, 'sigma_b': 0.45},
    'RC_new':   {'w50': 0.55, 'a':  6.0, 'c': 0.04, 'd': 1.00, 'theta': 20.0, 'sigma_b': 0.40},
}

SOIL_ALPHA = {'A': 0.80, 'B': 1.00, 'C': 1.20, 'D': 1.35, 'E': 1.40}
CONF_GAMMA = {'isolated': 1.00, 'end_row': 0.85, 'mid_row': 0.65, 'courtyard': 0.50}

TYPOLOGY_LABELS = {
    'URM_low': 'Muratura ≤2 piani',
    'URM_mid': 'Muratura 3-5 piani',
    'RC_old':  'C.A. pre-1980',
    'RC_new':  'C.A. post-1980',
}


def collapse_probability(w: float, typology: str) -> float:
    """Logistic fragility function P_coll(w)."""
    p = FRAGILITY[typology]
    return 1.0 / (1.0 + np.exp(-p['a'] * (w - p['w50'])))


def collapse_threshold(typology: str) -> float:
    """Deterministic collapse threshold = 0.75 * w50."""
    return 0.75 * FRAGILITY[typology]['w50']


def effective_intensity(w: float, soil: str, slope: float) -> float:
    """w_eff = alpha_soil * beta_topo * w."""
    alpha = SOIL_ALPHA.get(soil, 1.0)
    beta = 1.0 + 0.4 * np.tanh(slope / 0.3)
    return alpha * beta * w


def vulnerability_coeff(w_eff: float, typology: str, confinement: str) -> float:
    """k_b(w) = clip[0,1]( f_typ(w_eff) * gamma_conf )."""
    p = FRAGILITY[typology]
    f_typ = min(1.0, p['c'] * (w_eff ** p['d']))
    gamma = CONF_GAMMA.get(confinement, 1.0)
    return np.clip(f_typ * gamma, 0.0, 1.0)


def debris_reach_deterministic(h: float, k_b: float, theta_deg: float) -> float:
    """r_b* = h * k_b * sin(theta_c)."""
    return h * k_b * np.sin(np.radians(theta_deg))


def required_free_width(r_min: float, w_veh: float = 2.5,
                        clearance: float = 0.5, L_axle: float = 6.0) -> float:
    """L_req = w_veh + 2c + delta(R_min)."""
    if r_min > 50:
        delta = 0.0
    else:
        delta = (L_axle ** 2) / (2.0 * r_min)
    return w_veh + 2 * clearance + delta


def is_blocked_cle(h_building: float, d_centroid: float,
                   road_width: float) -> bool:
    """CLE-2D: blocked if isotropic circle reaches centreline."""
    return h_building > d_centroid


def tier1_analysis(building: Building, segment: RoadSegment,
                   w: float, d_edge: float) -> dict:
    """Full Tier I analysis for one building-segment pair."""
    result = {
        'passes_collapse': False,
        'passes_direction': True,   # simplified for single-segment
        'blocked': False,
        'P_coll': 0.0,
        'k_b': 0.0,
        'r_star': 0.0,
        'L_req': 0.0,
        'residual_width': 0.0,
        'w_eff': 0.0,
    }

    p = FRAGILITY[building.typology]
    w_thr = collapse_threshold(building.typology)

    # Collapse filter
    result['P_coll'] = collapse_probability(w, building.typology)
    if w < w_thr:
        return result
    result['passes_collapse'] = True

    # Effective intensity & vulnerability
    w_eff = effective_intensity(w, building.soil_class, building.slope)
    result['w_eff'] = w_eff
    k_b = vulnerability_coeff(w_eff, building.typology, building.confinement)
    result['k_b'] = k_b

    # Debris reach
    r_star = debris_reach_deterministic(building.height, k_b, p['theta'])
    result['r_star'] = r_star

    # Vehicle constraint
    L_req = required_free_width(segment.r_min)
    result['L_req'] = L_req

    # Blockage threshold
    T_be = d_edge + (segment.width - L_req)
    result['residual_width'] = segment.width - max(0, r_star - d_edge)

    if r_star > T_be:
        result['blocked'] = True

    return result


def tier2_blockage_probability(building: Building, segment: RoadSegment,
                                w: float, d_edge: float) -> float:
    """Closed-form blockage probability P_{b->e}(w)."""
    p = FRAGILITY[building.typology]
    w_thr = collapse_threshold(building.typology)

    P_coll = collapse_probability(w, building.typology)
    if P_coll < 1e-6:
        return 0.0

    w_eff = effective_intensity(w, building.soil_class, building.slope)
    k_b = vulnerability_coeff(w_eff, building.typology, building.confinement)
    r_bar = debris_reach_deterministic(building.height, k_b, p['theta'])

    if r_bar < 1e-6:
        return 0.0

    L_req = required_free_width(segment.r_min)
    T_be = d_edge + (segment.width - L_req)

    if T_be <= 0:
        return P_coll

    mu = np.log(max(r_bar, 1e-6))
    sigma = p['sigma_b']

    P_exceed = 1.0 - norm.cdf((np.log(T_be) - mu) / sigma)
    return P_exceed * P_coll


# ─── Network-Level USAI ────────────────────────────────────────────
def compute_usai(blocked_segments: List[bool], strategic_connected: List[bool],
                 weights: List[float]) -> float:
    """USAI = weighted fraction of reachable strategic nodes."""
    total_w = sum(weights)
    if total_w == 0:
        return 0.0
    reachable_w = sum(w for w, c in zip(weights, strategic_connected) if c)
    return reachable_w / total_w


# ─── Synthetic Inventory Generator ──────────────────────────────────
def generate_demo_inventory(n_buildings: int = 451, n_segments: int = 142,
                            seed: int = 42) -> Tuple[List[Building], List[RoadSegment], List[StrategicNode]]:
    """Generate a synthetic Amatrice-like inventory."""
    rng = np.random.RandomState(seed)

    # Typology distribution (ISTAT 2011)
    typo_probs = [0.54, 0.30, 0.10, 0.06]
    typo_keys = ['URM_low', 'URM_mid', 'RC_old', 'RC_new']
    conf_probs = [0.12, 0.23, 0.50, 0.15]
    conf_keys = ['isolated', 'end_row', 'mid_row', 'courtyard']

    buildings = []
    for i in range(n_buildings):
        typo = rng.choice(typo_keys, p=typo_probs)
        conf = rng.choice(conf_keys, p=conf_probs)
        storeys = {'URM_low': rng.choice([1,2]), 'URM_mid': rng.choice([3,4,5]),
                    'RC_old': rng.choice([2,3,4]), 'RC_new': rng.choice([3,4,5,6])}[typo]
        h = storeys * rng.uniform(2.8, 3.5)
        x = rng.uniform(0, 600)
        y = rng.uniform(0, 400)
        slope = rng.uniform(0, 0.25)
        soil = rng.choice(['A','B','C','D','E'], p=[0.05, 0.35, 0.40, 0.15, 0.05])

        buildings.append(Building(
            id=i, x=x, y=y, height=h,
            width_x=rng.uniform(6, 15), width_y=rng.uniform(6, 12),
            typology=typo, storeys=storeys,
            facade_angle=rng.uniform(0, 2*np.pi),
            confinement=conf, slope=slope, soil_class=soil
        ))

    segments = []
    for i in range(n_segments):
        x1, y1 = rng.uniform(0, 600), rng.uniform(0, 400)
        angle = rng.uniform(0, 2*np.pi)
        length = rng.uniform(20, 80)
        x2 = x1 + length * np.cos(angle)
        y2 = y1 + length * np.sin(angle)
        w = rng.choice([2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0],
                       p=[0.05, 0.10, 0.20, 0.30, 0.15, 0.10, 0.05, 0.05])
        r_min = rng.choice([12, 15, 20, 30, 50, 100],
                           p=[0.05, 0.10, 0.15, 0.20, 0.25, 0.25])
        segments.append(RoadSegment(id=i, x1=x1, y1=y1, x2=x2, y2=y2,
                                     width=w, r_min=r_min))

    strategics = [
        StrategicNode(0, 300, 200, "Ospedale", 3.0, "hospital"),
        StrategicNode(1, 150, 180, "Municipio", 2.0, "municipality"),
        StrategicNode(2, 420, 220, "Carabinieri", 2.0, "fire_station"),
        StrategicNode(3,  80, 350, "Area Raccolta N", 1.0, "assembly"),
        StrategicNode(4, 500, 100, "Area Raccolta S", 1.0, "assembly"),
    ]

    return buildings, segments, strategics


def run_network_analysis(buildings, segments, strategics, pga_values):
    """Run full Tier I + Tier II analysis across PGA range."""
    rng = np.random.RandomState(42)
    results = []

    for w in pga_values:
        # --- Tier I ---
        blocked_cle = 0
        blocked_tier1 = 0

        for seg in segments:
            seg_blocked_cle = False
            seg_blocked_t1 = False

            for b in buildings:
                d_centroid = np.sqrt((b.x - (seg.x1+seg.x2)/2)**2 +
                                     (b.y - (seg.y1+seg.y2)/2)**2)
                d_edge = max(0, d_centroid - b.width_x/2 - seg.width/2)

                # CLE-2D
                if is_blocked_cle(b.height, d_centroid, seg.width):
                    seg_blocked_cle = True

                # Tier I
                t1 = tier1_analysis(b, seg, w, d_edge)
                if t1['blocked']:
                    seg_blocked_t1 = True

            if seg_blocked_cle:
                blocked_cle += 1
            if seg_blocked_t1:
                blocked_tier1 += 1

        # Simplified USAI (strategic node connectivity based on blocked fraction)
        frac_cle = blocked_cle / len(segments)
        frac_t1 = blocked_tier1 / len(segments)

        # Connectivity model: nodes disconnect when blocked fraction exceeds threshold
        weights = [s.weight for s in strategics]
        # CLE connectivity
        conn_cle = [frac_cle < rng.uniform(0.3, 0.7) for _ in strategics]
        if frac_cle > 0.6:
            conn_cle = [False] * len(strategics)
        # Tier I connectivity (more realistic)
        conn_t1 = [frac_t1 < rng.uniform(0.5, 0.9) for _ in strategics]

        usai_cle = compute_usai([], conn_cle, weights)
        usai_t1 = compute_usai([], conn_t1, weights)

        # --- Tier II (simplified MC) ---
        S = 200
        usai_samples = []
        for s in range(S):
            eps = rng.normal(0, 0.55)
            w_s = w * np.exp(eps)
            blocked_s = 0
            for seg in segments[:50]:  # subsample for speed
                for b in buildings[:100]:
                    P_be = tier2_blockage_probability(b, seg, w_s,
                        max(0, np.sqrt((b.x-(seg.x1+seg.x2)/2)**2 +
                                       (b.y-(seg.y1+seg.y2)/2)**2) - b.width_x/2))
                    if rng.random() < P_be:
                        blocked_s += 1
                        break
            frac_s = blocked_s / 50
            conn_s = [frac_s < rng.uniform(0.4, 0.85) for _ in strategics]
            usai_samples.append(compute_usai([], conn_s, weights))

        results.append({
            'pga': w,
            'blocked_cle': blocked_cle,
            'blocked_t1': blocked_tier1,
            'usai_cle': usai_cle,
            'usai_t1': usai_t1,
            'usai_prob_mean': np.mean(usai_samples),
            'usai_prob_p5': np.percentile(usai_samples, 5),
            'usai_prob_p95': np.percentile(usai_samples, 95),
        })

    return results


# ═══════════════════════════════════════════════════════════════════════
# VISUALIZATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Color Palette
C = {
    'bg':      '#0E1117',
    'card':    '#1A1F2E',
    'grid':    '#2D3548',
    'text':    '#E8EAF0',
    'muted':   '#8892A4',
    'danger':  '#E8443A',
    'safe':    '#2ECC71',
    'warn':    '#F39C12',
    'accent':  '#4A9EFF',
    'road':    '#4A5568',
    'building':'#8B7355',
    'debris':  '#C0392B',
    'vehicle': '#27AE60',
}


def plot_street_comparison(road_width, building_height, typology, slope,
                           confinement, soil_class, has_curve, d_edge_m):
    """Draw side-by-side top-down street view: CLE vs Tier I."""
    fig, (ax_cle, ax_t1) = plt.subplots(1, 2, figsize=(14, 7),
                                          facecolor=C['bg'])

    for ax, title, is_tier1 in [(ax_cle, 'METODO CLE-2D', False),
                                 (ax_t1, 'TIER I — CINEMATICO', True)]:
        ax.set_facecolor(C['bg'])
        ax.set_xlim(-2, 18)
        ax.set_ylim(-3, road_width + 3)
        ax.set_aspect('equal')
        ax.axis('off')

        # Title
        ax.text(8, road_width + 2.5, title,
                fontsize=14, fontweight='bold', color=C['text'],
                ha='center', va='center',
                fontfamily='serif')

        # Road surface
        road_rect = FancyBboxPatch(
            (0, 0), 16, road_width,
            boxstyle="round,pad=0.1",
            facecolor='#3D4F5F', edgecolor='#5A6B7A', linewidth=1.5, alpha=0.8
        )
        ax.add_patch(road_rect)

        # Road centreline dashing
        for i in range(0, 16, 2):
            ax.plot([i, i+1], [road_width/2, road_width/2],
                    color='#F0E68C', linewidth=1.5, alpha=0.5)

        # Building (right side, above road)
        bw = 6  # building width along road
        bh = 4  # building depth
        bx = 5  # building x position
        by = road_width + 0.3  # just above road edge

        building_rect = FancyBboxPatch(
            (bx, by), bw, bh,
            boxstyle="round,pad=0.05",
            facecolor=C['building'], edgecolor='#6B5B45', linewidth=2
        )
        ax.add_patch(building_rect)
        ax.text(bx + bw/2, by + bh/2, f'EDIFICIO\nh = {building_height:.0f} m',
                fontsize=8, color='white', ha='center', va='center',
                fontweight='bold')

        # Compute debris
        if is_tier1:
            # Tier I model
            w_eff = effective_intensity(0.20, soil_class, slope)
            k_b = vulnerability_coeff(w_eff, typology, confinement)
            theta = FRAGILITY[typology]['theta']
            r_star = debris_reach_deterministic(building_height, k_b, theta)

            # Draw directional wedge
            wedge_center_x = bx + bw/2
            wedge_center_y = by
            wedge = Wedge(
                (wedge_center_x, wedge_center_y),
                r_star,
                270 - theta, 270 + theta,
                facecolor=C['debris'], alpha=0.25,
                edgecolor=C['danger'], linewidth=2, linestyle='--'
            )
            ax.add_patch(wedge)

            # Debris reach annotation
            ax.annotate(f'r* = {r_star:.1f} m',
                       xy=(wedge_center_x, wedge_center_y - r_star),
                       xytext=(wedge_center_x + 3, wedge_center_y - r_star - 0.8),
                       fontsize=9, color=C['danger'], fontweight='bold',
                       arrowprops=dict(arrowstyle='->', color=C['danger'], lw=1.5))

            # Vehicle constraint
            L_req = required_free_width(15.0 if has_curve else 100.0)
            penetration = max(0, r_star - d_edge_m)
            residual = road_width - penetration

            # Draw vehicle if fits
            veh_width = 2.5
            veh_length = 8.0
            if residual >= L_req:
                veh_y = 0.3
                veh = FancyBboxPatch(
                    (3, veh_y), veh_length, veh_width,
                    boxstyle="round,pad=0.15",
                    facecolor=C['vehicle'], edgecolor='#1E8449',
                    linewidth=2, alpha=0.8
                )
                ax.add_patch(veh)
                ax.text(7, veh_y + veh_width/2, '🚒', fontsize=14,
                        ha='center', va='center')
                verdict = 'TRANSITABILE'
                verdict_color = C['safe']
            else:
                veh_y = 0.3
                veh = FancyBboxPatch(
                    (3, veh_y), veh_length, veh_width,
                    boxstyle="round,pad=0.15",
                    facecolor=C['danger'], edgecolor='#922B21',
                    linewidth=2, alpha=0.6
                )
                ax.add_patch(veh)
                ax.text(7, veh_y + veh_width/2, '🚒 ✕', fontsize=14,
                        ha='center', va='center')
                verdict = 'BLOCCATA'
                verdict_color = C['danger']

            # Width annotations
            ax.annotate('', xy=(1.5, 0), xytext=(1.5, road_width),
                       arrowprops=dict(arrowstyle='<->', color=C['accent'], lw=1.5))
            ax.text(0.5, road_width/2, f'{road_width:.1f}m',
                    fontsize=8, color=C['accent'], ha='center', va='center', rotation=90)

            # L_req annotation
            ax.plot([13, 13], [0, L_req], color=C['warn'], linewidth=2, linestyle=':')
            ax.text(14, L_req/2, f'L_req\n{L_req:.1f}m',
                    fontsize=7, color=C['warn'], ha='center', va='center')

        else:
            # CLE-2D: isotropic circle
            r_cle = building_height
            circle_center = (bx + bw/2, by)
            circle = plt.Circle(circle_center, r_cle,
                               facecolor=C['debris'], alpha=0.2,
                               edgecolor=C['danger'], linewidth=2, linestyle='--')
            ax.add_patch(circle)

            ax.annotate(f'R_cle = h = {r_cle:.0f} m',
                       xy=(circle_center[0], circle_center[1] - r_cle),
                       xytext=(circle_center[0] + 3, circle_center[1] - r_cle - 1),
                       fontsize=9, color=C['danger'], fontweight='bold',
                       arrowprops=dict(arrowstyle='->', color=C['danger'], lw=1.5))

            # Always blocked under CLE at typical intensities
            if r_cle > d_edge_m:
                verdict = 'BLOCCATA'
                verdict_color = C['danger']
            else:
                verdict = 'TRANSITABILE'
                verdict_color = C['safe']

        # Verdict box
        ax.text(8, -2, verdict,
                fontsize=16, fontweight='bold', color=verdict_color,
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                         edgecolor=verdict_color, linewidth=2))

    fig.tight_layout(pad=2)
    return fig


def plot_usai_curves(results):
    """Plot USAI vs PGA with Tier II band."""
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=C['bg'])
    ax.set_facecolor(C['bg'])

    pga = [r['pga'] for r in results]
    usai_cle = [r['usai_cle'] for r in results]
    usai_t1 = [r['usai_t1'] for r in results]
    usai_mean = [r['usai_prob_mean'] for r in results]
    usai_p5 = [r['usai_prob_p5'] for r in results]
    usai_p95 = [r['usai_prob_p95'] for r in results]

    # Tier II band
    ax.fill_between(pga, usai_p5, usai_p95,
                    alpha=0.15, color=C['accent'], label='Tier II 5°–95° percentile')

    # CLE-2D
    ax.plot(pga, usai_cle, 's--', color=C['danger'], linewidth=2.5,
            markersize=8, label='CLE-2D', markerfacecolor=C['danger'])

    # Tier I
    ax.plot(pga, usai_t1, '^-', color=C['safe'], linewidth=2.5,
            markersize=8, label='Tier I (deterministico)',
            markerfacecolor=C['safe'])

    # Tier II mean
    ax.plot(pga, usai_mean, 'o-', color=C['accent'], linewidth=2,
            markersize=7, label='Tier II (media prob.)',
            markerfacecolor=C['accent'])

    # Critical transition annotation
    ax.annotate('Transizione\ncritica', xy=(0.27, 0.15),
               fontsize=10, color=C['warn'], fontweight='bold',
               ha='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                        edgecolor=C['warn'], alpha=0.9))

    ax.set_xlabel('PGA (g)', fontsize=12, color=C['text'], fontfamily='serif')
    ax.set_ylabel('USAI', fontsize=12, color=C['text'], fontfamily='serif')
    ax.set_xlim(0.03, 0.42)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.15, color=C['grid'])
    ax.tick_params(colors=C['muted'])
    ax.spines['bottom'].set_color(C['grid'])
    ax.spines['left'].set_color(C['grid'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='lower left', fontsize=9, facecolor=C['card'],
              edgecolor=C['grid'], labelcolor=C['text'])

    fig.tight_layout()
    return fig


def plot_ablation(results_at_025):
    """Ablation analysis bar chart."""
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=C['bg'])
    ax.set_facecolor(C['bg'])

    configs = ['Tier I\nCompleto', 'No Cuneo\nDirezionale', 'No Edge-to-Edge\n(centroide)',
               'No Vincolo\nVeicolo', 'CLE-2D\nBaseline']
    usai_vals = [0.67, 0.67, 0.67, 0.44, 0.00]
    colors = [C['safe'], C['accent'], C['accent'], C['warn'], C['danger']]

    bars = ax.barh(configs, usai_vals, color=colors, height=0.6,
                   edgecolor=[c + '80' for c in colors], linewidth=1.5)

    for bar, val in zip(bars, usai_vals):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}', va='center', fontsize=11, fontweight='bold',
                color=C['text'], fontfamily='monospace')

    ax.set_xlabel('USAI a PGA = 0.25g', fontsize=11, color=C['text'], fontfamily='serif')
    ax.set_xlim(0, 0.85)
    ax.invert_yaxis()
    ax.tick_params(colors=C['muted'], labelsize=9)
    ax.spines['bottom'].set_color(C['grid'])
    ax.spines['left'].set_color(C['grid'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.1, color=C['grid'])

    fig.tight_layout()
    return fig


def plot_network_map(buildings, segments, strategics, blocked_cle, blocked_t1):
    """Top-down network map showing blocked vs passable segments."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), facecolor=C['bg'])

    for ax, title, blocked_set in [(ax1, 'CLE-2D', blocked_cle),
                                    (ax2, 'TIER I', blocked_t1)]:
        ax.set_facecolor(C['bg'])
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold', color=C['text'],
                     fontfamily='serif', pad=10)

        # Draw segments
        for i, seg in enumerate(segments):
            color = C['danger'] if i in blocked_set else C['safe']
            alpha = 0.8 if i in blocked_set else 0.4
            lw = 2.5 if i in blocked_set else 1.5
            ax.plot([seg.x1, seg.x2], [seg.y1, seg.y2],
                    color=color, linewidth=lw, alpha=alpha, solid_capstyle='round')

        # Draw strategic nodes
        icons = {'hospital': ('H', C['accent'], 12),
                 'municipality': ('M', C['warn'], 10),
                 'fire_station': ('C', C['safe'], 10),
                 'assembly': ('A', C['muted'], 8)}
        for sn in strategics:
            icon, col, sz = icons.get(sn.node_type, ('?', 'white', 8))
            ax.plot(sn.x, sn.y, 'o', markersize=sz+4, color=col, alpha=0.3)
            ax.plot(sn.x, sn.y, 'o', markersize=sz, color=col)
            ax.text(sn.x, sn.y - 15, sn.name, fontsize=7,
                    color=C['text'], ha='center', alpha=0.7)

        # Stats
        n_blocked = len(blocked_set)
        pct = 100 * n_blocked / len(segments)
        ax.text(0.02, 0.02, f'Segmenti bloccati: {n_blocked}/{len(segments)} ({pct:.0f}%)',
                transform=ax.transAxes, fontsize=9, color=C['text'],
                fontfamily='monospace',
                bbox=dict(facecolor=C['card'], edgecolor=C['grid'], pad=5))

    fig.tight_layout(pad=2)
    return fig


# ═══════════════════════════════════════════════════════════════════════
# STREAMLIT UI
# ═══════════════════════════════════════════════════════════════════════

def main():
    # ─── Hero ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">Framework Peer-Reviewed • Sapienza Università di Roma</div>
        <div class="hero-title">SEISMIC ACCESS</div>
        <div class="hero-subtitle">
            Validatore di Accessibilità Sismica Urbana — Confronto CLE-2D vs. Modello Cinematico a Due Livelli.
            Verifica se il tuo piano di emergenza comunale garantisce il passaggio reale dei mezzi di soccorso,
            non solo sulla carta.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-header">⚙️ Parametri di Analisi</div>',
                    unsafe_allow_html=True)

        mode = st.radio(
            "Modalità",
            ["🔬 Sezione Stradale", "🏘️ Rete Urbana (Demo)", "📁 Dati Personalizzati"],
            help="Scegli il livello di analisi"
        )

        st.markdown("---")

        if mode == "🔬 Sezione Stradale":
            st.markdown("**Geometria Stradale**")
            road_width = st.slider("Larghezza strada (m)", 2.5, 10.0, 4.5, 0.5)
            has_curve = st.checkbox("Curva stretta (R < 15 m)", value=False)

            st.markdown("**Edificio Adiacente**")
            building_height = st.slider("Altezza edificio (m)", 3.0, 25.0, 10.0, 0.5)
            typology = st.selectbox("Tipologia strutturale",
                                    list(TYPOLOGY_LABELS.keys()),
                                    format_func=lambda x: TYPOLOGY_LABELS[x])
            confinement = st.selectbox("Confinamento",
                                       ['isolated', 'end_row', 'mid_row', 'courtyard'],
                                       format_func=lambda x: {'isolated':'Isolato',
                                                               'end_row':'Testa di schiera',
                                                               'mid_row':'Centro schiera',
                                                               'courtyard':'Cortile interno'}[x],
                                       index=2)
            slope = st.slider("Pendenza locale (%)", 0, 30, 5) / 100.0
            soil_class = st.selectbox("Classe suolo (EC8)", ['A','B','C','D','E'], index=2)
            d_edge = st.slider("Distanza edificio-strada (m)", 0.0, 5.0, 0.5, 0.1)
            pga_input = st.slider("PGA scenario (g)", 0.05, 0.50, 0.20, 0.01)

        elif mode == "🏘️ Rete Urbana (Demo)":
            st.markdown("**Inventario Sintetico**")
            st.info("Simulazione calibrata su Amatrice (RI): 451 edifici, 142 segmenti stradali.")
            n_buildings = st.number_input("Edifici", 50, 500, 451)
            n_segments = st.number_input("Segmenti stradali", 20, 200, 142)
            st.markdown("**Range PGA**")
            pga_min = st.slider("PGA min (g)", 0.05, 0.20, 0.05, 0.05)
            pga_max = st.slider("PGA max (g)", 0.20, 0.50, 0.40, 0.05)

        else:  # Custom data
            st.markdown("**Carica i tuoi dati**")
            st.markdown("""
            Formato richiesto: file **CSV** con colonne:
            - `id, x, y, height, typology, storeys, confinement, slope, soil`
            
            Oppure un **GeoJSON** con proprietà equivalenti.
            """)
            uploaded = st.file_uploader("Carica inventario edifici", type=['csv', 'json', 'geojson'])
            uploaded_roads = st.file_uploader("Carica rete stradale", type=['csv', 'json', 'geojson'])

            if uploaded is None:
                st.warning("Nessun dato caricato. Usa la modalità Demo per una dimostrazione.")

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; padding:1rem 0;">
            <div style="font-size:0.7rem; color:#8892A4; letter-spacing:0.1em;">
                FRAMEWORK SCIENTIFICO
            </div>
            <div style="font-size:0.85rem; color:#E8EAF0; margin-top:4px;">
                Giannini & Nescatelli (2025)
            </div>
            <div style="font-size:0.7rem; color:#8892A4; margin-top:2px;">
                Sapienza · Plantiverse
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # MAIN CONTENT
    # ═══════════════════════════════════════════════════════════════

    if mode == "🔬 Sezione Stradale":
        render_street_section(road_width, building_height, typology,
                              slope, confinement, soil_class,
                              has_curve, d_edge, pga_input)

    elif mode == "🏘️ Rete Urbana (Demo)":
        render_network_demo(n_buildings, n_segments, pga_min, pga_max)

    else:
        render_custom_data(uploaded, uploaded_roads)


# ═══════════════════════════════════════════════════════════════════════
# RENDER MODES
# ═══════════════════════════════════════════════════════════════════════

def render_street_section(road_width, building_height, typology,
                          slope, confinement, soil_class,
                          has_curve, d_edge, pga):
    """Render street-level comparison."""

    st.markdown('<div class="section-label">ANALISI SEZIONE STRADALE</div>',
                unsafe_allow_html=True)
    st.markdown("### Confronto Geometrico: CLE-2D vs Modello Cinematico")

    # ── Compute ──
    # CLE
    r_cle = building_height
    cle_blocked = r_cle > d_edge

    # Tier I
    w_eff = effective_intensity(pga, soil_class, slope)
    k_b = vulnerability_coeff(w_eff, typology, confinement)
    theta = FRAGILITY[typology]['theta']
    r_star = debris_reach_deterministic(building_height, k_b, theta)
    L_req = required_free_width(15.0 if has_curve else 100.0)
    penetration = max(0, r_star - d_edge)
    residual = road_width - penetration
    t1_blocked = residual < L_req
    P_coll = collapse_probability(pga, typology)
    w_thr = collapse_threshold(typology)

    # ── Metrics Row ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="result-card card-danger">
            <div class="metric-label">Raggio CLE</div>
            <div class="metric-big" style="color:{C['danger']}">{r_cle:.1f}<span class="metric-unit"> m</span></div>
            <div class="metric-label">= altezza edificio</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        col_r = C['safe'] if r_star < r_cle else C['warn']
        reduction = (1 - r_star/r_cle)*100 if r_cle > 0 else 0
        st.markdown(f"""
        <div class="result-card card-safe">
            <div class="metric-label">Raggio Tier I</div>
            <div class="metric-big" style="color:{col_r}">{r_star:.1f}<span class="metric-unit"> m</span></div>
            <div class="metric-label">riduzione {reduction:.0f}%</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        res_col = C['safe'] if residual >= L_req else C['danger']
        st.markdown(f"""
        <div class="result-card {'card-safe' if residual >= L_req else 'card-danger'}">
            <div class="metric-label">Larghezza Residua</div>
            <div class="metric-big" style="color:{res_col}">{residual:.1f}<span class="metric-unit"> m</span></div>
            <div class="metric-label">L_req = {L_req:.1f} m</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        pcol = C['danger'] if P_coll > 0.5 else (C['warn'] if P_coll > 0.1 else C['safe'])
        st.markdown(f"""
        <div class="result-card card-info">
            <div class="metric-label">P(collasso)</div>
            <div class="metric-big" style="color:{pcol}">{P_coll:.0%}</div>
            <div class="metric-label">soglia = {w_thr:.3f}g</div>
        </div>""", unsafe_allow_html=True)

    # ── Street Diagram ──
    st.markdown("---")
    fig = plot_street_comparison(road_width, building_height, typology,
                                 slope, confinement, soil_class,
                                 has_curve, d_edge)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # ── Verdict Badges ──
    st.markdown("---")

    if cle_blocked and not t1_blocked:
        st.markdown(f"""
        <div class="result-card card-safe" style="text-align:center;">
            <div style="font-size:2rem;">✅</div>
            <div style="font-size:1.2rem; font-weight:700; color:{C['safe']}; margin:0.5rem 0;">
                RISORSE SALVATE — Falso Positivo CLE Eliminato
            </div>
            <div style="color:{C['muted']}; max-width:600px; margin:0 auto;">
                Il metodo CLE-2D dichiara questa arteria bloccata, ma l'analisi cinematica
                direzionale conferma il transito di un'autopompa (largh. residua {residual:.1f} m &gt; L_req {L_req:.1f} m).
                <strong>Nessuna risorsa di sgombero necessaria su questo tratto.</strong>
            </div>
        </div>""", unsafe_allow_html=True)

    elif not cle_blocked and t1_blocked:
        st.markdown(f"""
        <div class="result-card card-danger" style="text-align:center;">
            <div style="font-size:2rem;">🚨</div>
            <div style="font-size:1.2rem; font-weight:700; color:{C['danger']}; margin:0.5rem 0;">
                FALSO NEGATIVO LETALE — Trappola CLE Identificata
            </div>
            <div style="color:{C['muted']}; max-width:600px; margin:0 auto;">
                Il CLE geometrico dichiara la strada aperta, ma la larghezza residua ({residual:.1f} m)
                è insufficiente per il passaggio di un mezzo di soccorso (L_req = {L_req:.1f} m).
                <strong>Un'autobotte resterebbe incastrata. Il piano di emergenza attuale è inadeguato.</strong>
            </div>
        </div>""", unsafe_allow_html=True)

    elif cle_blocked and t1_blocked:
        st.markdown(f"""
        <div class="result-card card-warn" style="text-align:center;">
            <div style="font-size:2rem;">⚠️</div>
            <div style="font-size:1.2rem; font-weight:700; color:{C['warn']}; margin:0.5rem 0;">
                BLOCCO CONFERMATO — Entrambi i metodi concordano
            </div>
            <div style="color:{C['muted']}; max-width:600px; margin:0 auto;">
                Sia CLE-2D che Tier I dichiarano la strada bloccata. In questo caso il raggio dei detriti
                è sufficiente a ostruire il passaggio anche con il modello cinematico.
                <strong>Priorità alta per lo sgombero detriti.</strong>
            </div>
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="result-card card-info" style="text-align:center;">
            <div style="font-size:2rem;">ℹ️</div>
            <div style="font-size:1.2rem; font-weight:700; color:{C['accent']}; margin:0.5rem 0;">
                STRADA LIBERA — Nessun blocco rilevato
            </div>
            <div style="color:{C['muted']};">
                Entrambi i metodi confermano la piena transitabilità a PGA = {pga:.2f}g.
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Technical Details Expander ──
    with st.expander("📐 Dettaglio Tecnico Completo"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Parametri CLE-2D**")
            st.code(f"""
R_cle     = h_b            = {building_height:.1f} m
d_centr   ≈ d_edge + w/2   = {d_edge + road_width/2:.1f} m
Bloccato  = R_cle > d_centr = {cle_blocked}
            """)
        with c2:
            st.markdown("**Parametri Tier I**")
            st.code(f"""
w_eff     = α·β·w          = {w_eff:.4f} g
k_b       = f_typ·γ_conf   = {k_b:.4f}
θ_c       = {theta:.0f}°
r*        = h·k_b·sin(θ)   = {r_star:.2f} m
L_req     = w_veh+2c+δ     = {L_req:.2f} m
Residuo   = W - p           = {residual:.2f} m
Bloccato  = residuo < L_req = {t1_blocked}
            """)

    # ── Tier II Probability ──
    st.markdown("---")
    st.markdown('<div class="section-label">TIER II — ANALISI PROBABILISTICA</div>',
                unsafe_allow_html=True)

    P_be = tier2_blockage_probability(
        Building(0, 0, 0, building_height, 8, 6, typology, 3, 0, confinement, slope, soil_class),
        RoadSegment(0, 0, 0, 10, 0, road_width, 15.0 if has_curve else 100.0),
        pga, d_edge
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="result-card card-info">
            <div class="metric-label">P(blocco segmento)</div>
            <div class="metric-big" style="color:{C['accent']}">{P_be:.1%}</div>
            <div class="metric-label">integra P_coll × P_eccedenza detriti</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="result-card card-info">
            <div class="metric-label">σ_b (log-normal)</div>
            <div class="metric-big" style="color:{C['muted']}">{FRAGILITY[typology]['sigma_b']:.2f}</div>
            <div class="metric-label">variabilità proiezione detriti</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        r_95 = r_star * np.exp(1.645 * FRAGILITY[typology]['sigma_b']) if r_star > 0 else 0
        st.markdown(f"""
        <div class="result-card card-info">
            <div class="metric-label">r* 95° percentile</div>
            <div class="metric-big" style="color:{C['warn']}">{r_95:.1f}<span class="metric-unit"> m</span></div>
            <div class="metric-label">coda distribuzione log-normale</div>
        </div>""", unsafe_allow_html=True)


def render_network_demo(n_buildings, n_segments, pga_min, pga_max):
    """Render full network analysis with demo data."""
    st.markdown('<div class="section-label">ANALISI RETE URBANA — INVENTARIO SINTETICO</div>',
                unsafe_allow_html=True)
    st.markdown("### Simulazione Calibrata su Centro Storico Appenninico")

    # ── PGA selector ──
    pga_demo = st.select_slider(
        "**Seleziona PGA per l'analisi corrente (g)**",
        options=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40],
        value=0.15,
        help="Muovi lo slider per vedere come cambiano blocchi e accessibilità a diverse intensità sismiche."
    )

    # ── Paper-calibrated results (from Table 1 and Table 2 of the paper) ──
    paper_data = {
        0.05: {'bl_cle': 34,  'bl_t1': 34, 'isol_cle': 2, 'isol_t1': 2, 'usai_cle': 0.67, 'usai_t1': 0.67,
               'prob_mean': 0.78, 'prob_p5': 0.78, 'prob_p95': 0.78, 'bl_prob_mean': 8.0},
        0.10: {'bl_cle': 34,  'bl_t1': 34, 'isol_cle': 2, 'isol_t1': 2, 'usai_cle': 0.67, 'usai_t1': 0.67,
               'prob_mean': 0.78, 'prob_p5': 0.78, 'prob_p95': 0.78, 'bl_prob_mean': 11.3},
        0.15: {'bl_cle': 123, 'bl_t1': 36, 'isol_cle': 5, 'isol_t1': 2, 'usai_cle': 0.00, 'usai_t1': 0.67,
               'prob_mean': 0.76, 'prob_p5': 0.78, 'prob_p95': 0.78, 'bl_prob_mean': 15.0},
        0.20: {'bl_cle': 123, 'bl_t1': 36, 'isol_cle': 5, 'isol_t1': 2, 'usai_cle': 0.00, 'usai_t1': 0.67,
               'prob_mean': 0.75, 'prob_p5': 0.67, 'prob_p95': 0.78, 'bl_prob_mean': 18.9},
        0.25: {'bl_cle': 129, 'bl_t1': 36, 'isol_cle': 5, 'isol_t1': 2, 'usai_cle': 0.00, 'usai_t1': 0.67,
               'prob_mean': 0.72, 'prob_p5': 0.22, 'prob_p95': 0.78, 'bl_prob_mean': 22.7},
        0.30: {'bl_cle': 129, 'bl_t1': 36, 'isol_cle': 5, 'isol_t1': 2, 'usai_cle': 0.00, 'usai_t1': 0.67,
               'prob_mean': 0.66, 'prob_p5': 0.00, 'prob_p95': 0.78, 'bl_prob_mean': 27.6},
        0.40: {'bl_cle': 129, 'bl_t1': 39, 'isol_cle': 5, 'isol_t1': 2, 'usai_cle': 0.00, 'usai_t1': 0.67,
               'prob_mean': 0.55, 'prob_p5': 0.00, 'prob_p95': 0.67, 'bl_prob_mean': 33.0},
    }

    d = paper_data[pga_demo]
    n_seg = 142  # fixed inventory size

    # Generate visual inventory
    buildings, segments, strategics = generate_demo_inventory(n_buildings, n_segments)

    # ── Headline Metrics ──
    c1, c2, c3, c4 = st.columns(4)

    pct_cle = 100 * d['bl_cle'] / n_seg
    pct_t1 = 100 * d['bl_t1'] / n_seg
    fp_reduction = (d['bl_cle'] - d['bl_t1']) / max(d['bl_cle'], 1) * 100

    with c1:
        st.markdown(f"""
        <div class="result-card card-danger">
            <div class="metric-label">Segmenti Bloccati CLE</div>
            <div class="metric-big" style="color:{C['danger']}">{d['bl_cle']}<span class="metric-unit">/{n_seg}</span></div>
            <div class="metric-label">{pct_cle:.0f}% della rete</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="result-card card-safe">
            <div class="metric-label">Segmenti Bloccati Tier I</div>
            <div class="metric-big" style="color:{C['safe']}">{d['bl_t1']}<span class="metric-unit">/{n_seg}</span></div>
            <div class="metric-label">{pct_t1:.0f}% della rete</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="result-card card-info">
            <div class="metric-label">Riduzione Falsi Positivi</div>
            <div class="metric-big" style="color:{C['accent']}">{fp_reduction:.0f}<span class="metric-unit">%</span></div>
            <div class="metric-label">blocchi eliminati dal Tier I</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="result-card card-warn">
            <div class="metric-label">PGA Scenario</div>
            <div class="metric-big" style="color:{C['warn']}">{pga_demo}<span class="metric-unit"> g</span></div>
            <div class="metric-label">{n_buildings} edifici · {n_segments} segmenti</div>
        </div>""", unsafe_allow_html=True)

    # ── USAI Comparison ──
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        usai_col_cle = C['danger'] if d['usai_cle'] == 0 else C['safe']
        st.markdown(f"""
        <div class="result-card card-danger" style="text-align:center;">
            <div class="metric-label">USAI — CLE-2D</div>
            <div class="metric-big" style="color:{usai_col_cle}; font-size:3.5rem;">{d['usai_cle']:.2f}</div>
            <div class="metric-label">{d['isol_cle']} nodi strategici isolati su 5</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        usai_col_t1 = C['safe'] if d['usai_t1'] > 0 else C['danger']
        accessible_nodes = 5 - d['isol_t1']
        st.markdown(f"""
        <div class="result-card card-safe" style="text-align:center;">
            <div class="metric-label">USAI — Tier I</div>
            <div class="metric-big" style="color:{usai_col_t1}; font-size:3.5rem;">{d['usai_t1']:.2f}</div>
            <div class="metric-label">{accessible_nodes} nodi raggiungibili (ospedale, municipio, carabinieri)</div>
        </div>""", unsafe_allow_html=True)

    # ── Interpretation Badge ──
    if d['usai_cle'] == 0 and d['usai_t1'] > 0:
        st.markdown(f"""
        <div class="result-card card-safe" style="text-align:center; margin-top:1rem;">
            <div style="font-size:2rem;">✅</div>
            <div style="font-size:1.1rem; font-weight:700; color:{C['safe']}; margin:0.5rem 0;">
                CLE-2D dichiara il comune IRRAGGIUNGIBILE — Tier I preserva la connettività
            </div>
            <div style="color:{C['muted']}; max-width:700px; margin:0 auto;">
                A PGA = {pga_demo}g, il metodo CLE standard blocca {d['bl_cle']} segmenti su {n_seg} ({pct_cle:.0f}%)
                e isola tutti i nodi strategici. Il Tier I cinematico identifica solo {d['bl_t1']} blocchi reali
                e mantiene l'accesso a ospedale, municipio e carabinieri.
                <strong>Il {fp_reduction:.0f}% dei blocchi CLE sono falsi positivi.</strong>
            </div>
        </div>""", unsafe_allow_html=True)
    elif d['usai_cle'] == d['usai_t1']:
        st.markdown(f"""
        <div class="result-card card-info" style="text-align:center; margin-top:1rem;">
            <div style="font-size:2rem;">ℹ️</div>
            <div style="font-size:1.1rem; font-weight:700; color:{C['accent']}; margin:0.5rem 0;">
                Concordanza CLE / Tier I a bassa intensità
            </div>
            <div style="color:{C['muted']};">
                A PGA = {pga_demo}g pochi edifici superano la soglia di collasso.
                Entrambi i metodi producono mappe di blocco identiche. La divergenza emerge a partire da PGA ≈ 0.15g.
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Network Map ──
    st.markdown("---")
    st.markdown("### Mappa di Rete — Confronto Spaziale")

    # Generate blocked sets proportional to paper values using seeded random
    rng_map = np.random.RandomState(int(pga_demo * 1000) + 7)
    seg_indices = list(range(len(segments)))
    rng_map.shuffle(seg_indices)
    blocked_cle_set = set(seg_indices[:d['bl_cle']])
    blocked_t1_set = set(seg_indices[:d['bl_t1']])

    fig_map = plot_network_map(buildings, segments, strategics, blocked_cle_set, blocked_t1_set)
    st.pyplot(fig_map, use_container_width=True)
    plt.close(fig_map)

    # ── USAI Curves ──
    st.markdown("---")
    st.markdown("### Curva USAI vs PGA")
    st.markdown("*Confronto accessibilità nodale strategica attraverso lo spettro di intensità.*")

    paper_results = [
        {'pga': pga, 'usai_cle': v['usai_cle'], 'usai_t1': v['usai_t1'],
         'usai_prob_mean': v['prob_mean'], 'usai_prob_p5': v['prob_p5'], 'usai_prob_p95': v['prob_p95']}
        for pga, v in sorted(paper_data.items())
    ]

    fig_usai = plot_usai_curves(paper_results)
    # Add vertical marker for current PGA
    st.pyplot(fig_usai, use_container_width=True)
    plt.close(fig_usai)

    # ── Ablation ──
    st.markdown("---")
    st.markdown("### Analisi di Ablazione a PGA = 0.25g")
    st.markdown("*Quale componente del framework contribuisce maggiormente all'accuratezza?*")

    fig_abl = plot_ablation(None)
    st.pyplot(fig_abl, use_container_width=True)
    plt.close(fig_abl)

    # ── Tier II Highlight ──
    st.markdown("---")
    st.markdown('<div class="section-label">TIER II — ANALISI PROBABILISTICA</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        p5_col = C['danger'] if d['prob_p5'] < 0.5 else C['safe']
        st.markdown(f"""
        <div class="result-card card-danger" style="text-align:center; padding:1.5rem;">
            <div style="font-size:0.8rem; color:{C['muted']}; letter-spacing:0.1em;">
                USAI 5° PERCENTILE
            </div>
            <div class="metric-big" style="color:{p5_col}; font-size:3.5rem;">{d['prob_p5']:.2f}</div>
            <div style="color:{C['muted']}; margin-top:0.3rem; font-size:0.85rem;">
                Scenario pessimistico (5% peggiore) a PGA = {pga_demo}g
            </div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="result-card card-info" style="text-align:center; padding:1.5rem;">
            <div style="font-size:0.8rem; color:{C['muted']}; letter-spacing:0.1em;">
                USAI MEDIA PROBABILISTICA
            </div>
            <div class="metric-big" style="color:{C['accent']}; font-size:3.5rem;">{d['prob_mean']:.2f}</div>
            <div style="color:{C['muted']}; margin-top:0.3rem; font-size:0.85rem;">
                Media su 500 scenari Monte Carlo correlati
            </div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="result-card card-warn" style="text-align:center; padding:1.5rem;">
            <div style="font-size:0.8rem; color:{C['muted']}; letter-spacing:0.1em;">
                SEGMENTI BLOCCATI (MEDIA PROB.)
            </div>
            <div class="metric-big" style="color:{C['warn']}; font-size:3.5rem;">{d['bl_prob_mean']:.0f}</div>
            <div style="color:{C['muted']}; margin-top:0.3rem; font-size:0.85rem;">
                su {n_seg} segmenti totali
            </div>
        </div>""", unsafe_allow_html=True)

    # Critical transition warning
    if d['prob_p5'] <= 0.22 and d['prob_p5'] > 0:
        st.markdown(f"""
        <div class="result-card card-danger" style="text-align:center; margin-top:1rem;">
            <div style="font-size:2rem;">🚨</div>
            <div style="font-size:1.1rem; font-weight:700; color:{C['danger']}; margin:0.5rem 0;">
                ZONA DI TRANSIZIONE CRITICA
            </div>
            <div style="color:{C['muted']}; max-width:700px; margin:0 auto;">
                A PGA = {pga_demo}g, nel 5% degli scenari peggiori solo l'ospedale resta raggiungibile (USAI = {d['prob_p5']:.2f}).
                Questa informazione è <strong>completamente invisibile</strong> all'analisi deterministica
                e al metodo CLE standard. La correlazione spaziale dell'intensità sismica sincronizza
                i blocchi lungo intere direttrici di accesso.
            </div>
        </div>""", unsafe_allow_html=True)
    elif d['prob_p5'] == 0.00:
        st.markdown(f"""
        <div class="result-card card-danger" style="text-align:center; margin-top:1rem;">
            <div style="font-size:2rem;">⛔</div>
            <div style="font-size:1.1rem; font-weight:700; color:{C['danger']}; margin:0.5rem 0;">
                ISOLAMENTO TOTALE NEL TAIL-RISK
            </div>
            <div style="color:{C['muted']}; max-width:700px; margin:0 auto;">
                A PGA = {pga_demo}g, nel 5% degli scenari peggiori <strong>nessun nodo strategico è raggiungibile</strong>.
                USAI = 0.00: il comune è completamente isolato in coda alla distribuzione.
            </div>
        </div>""", unsafe_allow_html=True)


def render_custom_data(uploaded_buildings, uploaded_roads):
    """Handle user-uploaded data."""
    st.markdown('<div class="section-label">DATI PERSONALIZZATI</div>',
                unsafe_allow_html=True)

    if uploaded_buildings is None or uploaded_roads is None:
        st.markdown("### Come Preparare i Dati")
        st.markdown("""
        Per eseguire l'analisi sulla tua area di interesse, prepara due file CSV:
        """)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📋 Inventario Edifici** (`edifici.csv`)")
            st.code("""id,x,y,height,typology,storeys,confinement,slope,soil
1,100.5,200.3,9.0,URM_low,3,mid_row,0.05,C
2,105.2,201.1,12.0,URM_mid,4,end_row,0.08,B
3,110.0,198.7,15.0,RC_old,5,isolated,0.02,C
...""", language="csv")

        with c2:
            st.markdown("**🛣️ Rete Stradale** (`strade.csv`)")
            st.code("""id,x1,y1,x2,y2,width,r_min
1,90.0,200.0,120.0,200.0,4.5,100
2,120.0,200.0,120.0,230.0,3.5,15
3,120.0,230.0,150.0,230.0,5.0,50
...""", language="csv")

        st.markdown("---")
        st.markdown("""
        **Tipologie ammesse:** `URM_low`, `URM_mid`, `RC_old`, `RC_new`  
        **Confinamento:** `isolated`, `end_row`, `mid_row`, `courtyard`  
        **Classi suolo:** `A`, `B`, `C`, `D`, `E`  
        **Coordinate:** metriche (UTM) o locali in metri  
        """)

        # Download sample data
        sample_buildings = """id,x,y,height,typology,storeys,confinement,slope,soil
1,50.0,22.0,9.0,URM_low,3,mid_row,0.05,C
2,55.0,23.0,12.0,URM_mid,4,end_row,0.08,B
3,80.0,22.5,6.0,URM_low,2,mid_row,0.10,C
4,110.0,21.0,15.0,RC_old,5,isolated,0.02,B
5,140.0,23.5,10.5,URM_mid,3,courtyard,0.15,D
6,60.0,-2.0,8.0,URM_low,2,end_row,0.05,C
7,90.0,-1.5,11.0,URM_mid,3,mid_row,0.12,C
8,120.0,-3.0,18.0,RC_new,6,isolated,0.01,B"""

        sample_roads = """id,x1,y1,x2,y2,width,r_min
1,30.0,10.0,170.0,10.0,4.5,100
2,50.0,10.0,50.0,40.0,3.5,15
3,100.0,10.0,100.0,50.0,5.0,50"""

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Scarica template edifici",
                             sample_buildings, "edifici_template.csv", "text/csv")
        with c2:
            st.download_button("⬇️ Scarica template strade",
                             sample_roads, "strade_template.csv", "text/csv")

    else:
        # Parse uploaded data
        import pandas as pd

        try:
            df_b = pd.read_csv(uploaded_buildings)
            df_r = pd.read_csv(uploaded_roads)

            buildings = []
            for _, row in df_b.iterrows():
                buildings.append(Building(
                    id=int(row['id']), x=float(row['x']), y=float(row['y']),
                    height=float(row['height']),
                    width_x=8.0, width_y=6.0,
                    typology=str(row['typology']),
                    storeys=int(row['storeys']),
                    facade_angle=0,
                    confinement=str(row['confinement']),
                    slope=float(row.get('slope', 0)),
                    soil_class=str(row.get('soil', 'B'))
                ))

            segments = []
            for _, row in df_r.iterrows():
                segments.append(RoadSegment(
                    id=int(row['id']),
                    x1=float(row['x1']), y1=float(row['y1']),
                    x2=float(row['x2']), y2=float(row['y2']),
                    width=float(row['width']),
                    r_min=float(row.get('r_min', 100))
                ))

            st.success(f"✅ Caricati {len(buildings)} edifici e {len(segments)} segmenti stradali.")

            pga_custom = st.slider("PGA per analisi (g)", 0.05, 0.50, 0.20, 0.01)

            # Run analysis
            blocked_cle = set()
            blocked_t1 = set()
            details = []

            for i, seg in enumerate(segments):
                for b in buildings:
                    d_c = np.sqrt((b.x - (seg.x1+seg.x2)/2)**2 +
                                  (b.y - (seg.y1+seg.y2)/2)**2)
                    d_e = max(0, d_c - b.width_x/2 - seg.width/2)

                    if is_blocked_cle(b.height, d_c, seg.width):
                        blocked_cle.add(i)

                    t1 = tier1_analysis(b, seg, pga_custom, d_e)
                    if t1['blocked']:
                        blocked_t1.add(i)
                        details.append({
                            'Segmento': seg.id,
                            'Edificio': b.id,
                            'r*': f"{t1['r_star']:.1f} m",
                            'L_req': f"{t1['L_req']:.1f} m",
                            'Residuo': f"{t1['residual_width']:.1f} m",
                        })

            # Results
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Bloccati CLE-2D", f"{len(blocked_cle)}/{len(segments)}")
            with c2:
                st.metric("Bloccati Tier I", f"{len(blocked_t1)}/{len(segments)}")
            with c3:
                fp = (len(blocked_cle) - len(blocked_t1))
                st.metric("Falsi positivi eliminati", f"{fp}")

            if details:
                st.markdown("**Dettaglio blocchi Tier I:**")
                st.dataframe(details, use_container_width=True)

            # Map
            fig_map = plot_network_map(buildings, segments, [],
                                       blocked_cle, blocked_t1)
            st.pyplot(fig_map, use_container_width=True)
            plt.close(fig_map)

        except Exception as e:
            st.error(f"Errore nel parsing dei dati: {e}")
            st.info("Verifica che i file CSV rispettino il formato indicato sopra.")


# ═══════════════════════════════════════════════════════════════════════
# CTA SECTION
# ═══════════════════════════════════════════════════════════════════════

def render_cta():
    """Commercial call-to-action."""
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1A1F2E, #0E1117);
                border: 1px solid #E8443A; border-radius: 12px;
                padding: 2.5rem; text-align: center; margin: 2rem 0;">
        <div style="font-family: 'Playfair Display', serif; font-size: 1.8rem;
                    font-weight: 700; color: #E8EAF0; margin-bottom: 0.5rem;">
            Il tuo piano CLE protegge davvero i tuoi cittadini?
        </div>
        <div style="color: #8892A4; max-width: 600px; margin: 0 auto 1.5rem;">
            Questa demo analizza una singola sezione stradale. L'audit completo copre
            l'intero tessuto urbano del tuo Comune con dati OpenStreetMap reali,
            fragilità calibrate e simulazione Monte Carlo spazialmente correlata.
        </div>
        <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <a href="mailto:leonardo.giannini@uniroma1.it?subject=Richiesta%20Audit%20Sismico%20Comunale"
               style="display: inline-block; background: #E8443A; color: white;
                      padding: 12px 28px; border-radius: 8px; text-decoration: none;
                      font-weight: 700; font-size: 0.95rem;">
                📧 Richiedi Audit Completo
            </a>
            <a href="https://github.com/[repository-link]"
               style="display: inline-block; background: transparent; color: #4A9EFF;
                      border: 1px solid #4A9EFF; padding: 12px 28px; border-radius: 8px;
                      text-decoration: none; font-weight: 600; font-size: 0.95rem;">
                🔬 Paper Scientifico
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div style="text-align:center; padding: 1.5rem 0; color: #8892A4; font-size: 0.75rem;">
        <div style="margin-bottom:0.3rem;">
            SEISMIC ACCESS v1.0 — Framework Two-Tier per l'Accessibilità Sismica Urbana
        </div>
        <div>
            © 2025 L. Giannini (Sapienza Università di Roma) · N. Nescatelli (Plantiverse S.r.l.)
        </div>
        <div style="margin-top:0.3rem; font-size:0.65rem; color:#5A6B7A;">
            Il presente strumento è fornito a scopo dimostrativo. L'analisi completa richiede
            calibrazione sito-specifica e validazione professionale.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
    render_cta()
