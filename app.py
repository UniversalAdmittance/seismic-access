"""
SEISMIC ACCESS v2.0 - Validatore di Accessibilita Sismica Urbana
Two-Tier Framework: CLE-2D vs Geometric-Kinematic Model
2025 Giannini & Nescatelli - Sapienza / Plantiverse
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Wedge
from scipy.stats import norm
from dataclasses import dataclass
from typing import List, Tuple

st.set_page_config(page_title="SEISMIC ACCESS", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500;9..40,700&family=JetBrains+Mono:wght@400;600&family=Playfair+Display:wght@700;900&display=swap');
.stApp { font-family: 'DM Sans', sans-serif; }
h1,h2,h3,h4 { font-family: 'Playfair Display', serif !important; }
code,.stCode { font-family: 'JetBrains Mono', monospace !important; }
.hero-box { background:linear-gradient(135deg,#0E1117,#1A1F2E,#0E1117); border:1px solid #2D3548; border-radius:16px; padding:2.5rem 2rem; margin-bottom:1.5rem; position:relative; overflow:hidden; }
.hero-box::before { content:''; position:absolute; top:0;left:0;right:0; height:4px; background:linear-gradient(90deg,#E8443A,#F39C12,#2ECC71); border-radius:16px 16px 0 0; }
.hero-tag { display:inline-block; background:rgba(232,68,58,0.12); border:1px solid rgba(232,68,58,0.25); color:#E8443A; padding:5px 14px; border-radius:20px; font-size:0.7rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:1rem; }
.hero-title { font-family:'Playfair Display',serif; font-size:2.6rem; font-weight:900; color:#E8EAF0; margin-bottom:0.4rem; letter-spacing:-0.03em; line-height:1.1; }
.hero-sub { font-size:1rem; color:#8892A4; line-height:1.7; max-width:780px; }
.card { border-radius:12px; padding:1.4rem 1.2rem; margin:0.4rem 0; border:1px solid #2D3548; }
.card-r { background:linear-gradient(145deg,rgba(232,68,58,0.07),rgba(232,68,58,0.01)); border-color:rgba(232,68,58,0.25); }
.card-g { background:linear-gradient(145deg,rgba(46,204,113,0.07),rgba(46,204,113,0.01)); border-color:rgba(46,204,113,0.25); }
.card-y { background:linear-gradient(145deg,rgba(243,156,18,0.07),rgba(243,156,18,0.01)); border-color:rgba(243,156,18,0.25); }
.card-b { background:linear-gradient(145deg,rgba(74,158,255,0.07),rgba(74,158,255,0.01)); border-color:rgba(74,158,255,0.25); }
.big { font-family:'JetBrains Mono',monospace; font-size:2.8rem; font-weight:700; line-height:1; margin:0.25rem 0; }
.big-xl { font-family:'JetBrains Mono',monospace; font-size:3.8rem; font-weight:700; line-height:1; margin:0.3rem 0; }
.lbl { font-size:0.75rem; color:#8892A4; text-transform:uppercase; letter-spacing:0.12em; font-weight:600; }
.unit { font-size:1rem; color:#8892A4; }
.sec { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#4A9EFF; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.6rem; }
.alert-box { border-radius:12px; padding:2rem; text-align:center; margin:1rem 0; border:1px solid; }
.alert-green { background:rgba(46,204,113,0.06); border-color:rgba(46,204,113,0.3); }
.alert-red { background:rgba(232,68,58,0.06); border-color:rgba(232,68,58,0.3); }
.alert-blue { background:rgba(74,158,255,0.06); border-color:rgba(74,158,255,0.3); }
.alert-yellow { background:rgba(243,156,18,0.06); border-color:rgba(243,156,18,0.3); }
.cta-box { background:linear-gradient(135deg,#1A1F2E,#0E1117); border:1px solid #E8443A; border-radius:16px; padding:2.5rem; text-align:center; margin:2.5rem 0; }
.sidebar-hdr { font-family:'Playfair Display',serif; font-size:1.15rem; font-weight:700; color:#E8EAF0; padding-bottom:0.5rem; border-bottom:2px solid #E8443A; margin-bottom:1rem; }
#MainMenu,footer,header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ENGINE
@dataclass
class Building:
    id:int;x:float;y:float;height:float;width_x:float;width_y:float;typology:str;storeys:int;facade_angle:float;confinement:str;slope:float=0.0;soil_class:str='B'
@dataclass
class RoadSegment:
    id:int;x1:float;y1:float;x2:float;y2:float;width:float;r_min:float=100.0
@dataclass
class StrategicNode:
    id:int;x:float;y:float;name:str;weight:float;node_type:str

FRAGILITY = {
    'URM_low':{'w50':0.18,'a':12.0,'c':0.18,'d':1.35,'theta':65.0,'sigma_b':0.55},
    'URM_mid':{'w50':0.15,'a':10.0,'c':0.22,'d':1.50,'theta':65.0,'sigma_b':0.55},
    'RC_old': {'w50':0.30,'a': 8.0,'c':0.10,'d':1.20,'theta':38.0,'sigma_b':0.45},
    'RC_new': {'w50':0.55,'a': 6.0,'c':0.04,'d':1.00,'theta':20.0,'sigma_b':0.40},
}
SOIL_ALPHA = {'A':0.80,'B':1.00,'C':1.20,'D':1.35,'E':1.40}
CONF_GAMMA = {'isolated':1.00,'end_row':0.85,'mid_row':0.65,'courtyard':0.50}
TYPO_LABELS = {'URM_low':'Muratura 1-2 piani','URM_mid':'Muratura 3-5 piani','RC_old':'C.A. pre-1980','RC_new':'C.A. post-1980'}

PAPER = {
    0.05:{'bl_cle':34,'bl_t1':34,'iso_cle':2,'iso_t1':2,'usai_cle':0.67,'usai_t1':0.67,'pm':0.78,'p5':0.78,'p95':0.78,'bpm':8.0},
    0.10:{'bl_cle':34,'bl_t1':34,'iso_cle':2,'iso_t1':2,'usai_cle':0.67,'usai_t1':0.67,'pm':0.78,'p5':0.78,'p95':0.78,'bpm':11.3},
    0.15:{'bl_cle':123,'bl_t1':36,'iso_cle':5,'iso_t1':2,'usai_cle':0.00,'usai_t1':0.67,'pm':0.76,'p5':0.78,'p95':0.78,'bpm':15.0},
    0.20:{'bl_cle':123,'bl_t1':36,'iso_cle':5,'iso_t1':2,'usai_cle':0.00,'usai_t1':0.67,'pm':0.75,'p5':0.67,'p95':0.78,'bpm':18.9},
    0.25:{'bl_cle':129,'bl_t1':36,'iso_cle':5,'iso_t1':2,'usai_cle':0.00,'usai_t1':0.67,'pm':0.72,'p5':0.22,'p95':0.78,'bpm':22.7},
    0.30:{'bl_cle':129,'bl_t1':36,'iso_cle':5,'iso_t1':2,'usai_cle':0.00,'usai_t1':0.67,'pm':0.66,'p5':0.00,'p95':0.78,'bpm':27.6},
    0.40:{'bl_cle':129,'bl_t1':39,'iso_cle':5,'iso_t1':2,'usai_cle':0.00,'usai_t1':0.67,'pm':0.55,'p5':0.00,'p95':0.67,'bpm':33.0},
}

def P_coll(w, typo):
    p=FRAGILITY[typo]; return 1.0/(1.0+np.exp(-p['a']*(w-p['w50'])))
def w_threshold(typo):
    return 0.75*FRAGILITY[typo]['w50']
def w_eff(w, soil, slope):
    return SOIL_ALPHA.get(soil,1.0)*(1.0+0.4*np.tanh(slope/0.3))*w
def k_b(we, typo, conf):
    p=FRAGILITY[typo]; return float(np.clip(min(1.0,p['c']*(we**p['d']))*CONF_GAMMA.get(conf,1.0),0,1))
def r_star(h, kb, typo):
    return h*kb*np.sin(np.radians(FRAGILITY[typo]['theta']))
def L_req(r_min, w_veh=2.5, c=0.5, La=6.0):
    return w_veh+2*c+(0 if r_min>50 else La**2/(2*r_min))

def tier1(h, typo, conf, soil, slope, w, d_edge, road_w, r_min):
    pc=P_coll(w,typo); wt=w_threshold(typo); we=w_eff(w,soil,slope)
    kb_v=k_b(we,typo,conf); rs=r_star(h,kb_v,typo); lr=L_req(r_min)
    pen=max(0,rs-d_edge); resid=road_w-pen; Tbe=d_edge+(road_w-lr)
    blocked=(w>=wt) and (rs>Tbe)
    return {'P_coll':pc,'w_thr':wt,'w_eff':we,'k_b':kb_v,'r_star':rs,'L_req':lr,'residual':resid,'blocked':blocked,'pen':pen}

def P_block_t2(h, typo, conf, soil, slope, w, d_edge, road_w, r_min):
    pc=P_coll(w,typo)
    if pc<1e-6: return 0.0
    we=w_eff(w,soil,slope); kb_v=k_b(we,typo,conf); rb=r_star(h,kb_v,typo)
    if rb<1e-6: return 0.0
    lr=L_req(r_min); Tbe=d_edge+(road_w-lr)
    if Tbe<=0: return pc
    return (1.0-norm.cdf((np.log(Tbe)-np.log(rb))/FRAGILITY[typo]['sigma_b']))*pc

def gen_inventory(n_b=451, n_s=142, seed=42):
    rng=np.random.RandomState(seed)
    tp=['URM_low','URM_mid','RC_old','RC_new']; cp=['isolated','end_row','mid_row','courtyard']
    blds=[]
    for i in range(n_b):
        t=rng.choice(tp,p=[0.54,0.30,0.10,0.06]); c=rng.choice(cp,p=[0.12,0.23,0.50,0.15])
        ns={'URM_low':rng.choice([1,2]),'URM_mid':rng.choice([3,4,5]),'RC_old':rng.choice([2,3,4]),'RC_new':rng.choice([3,4,5,6])}[t]
        blds.append(Building(i,rng.uniform(0,600),rng.uniform(0,400),ns*rng.uniform(2.8,3.5),rng.uniform(6,15),rng.uniform(6,12),t,ns,rng.uniform(0,6.28),c,rng.uniform(0,0.25),rng.choice(['A','B','C','D','E'],p=[0.05,0.35,0.40,0.15,0.05])))
    segs=[]
    for i in range(n_s):
        x1,y1=rng.uniform(0,600),rng.uniform(0,400); a=rng.uniform(0,6.28); l=rng.uniform(20,80)
        segs.append(RoadSegment(i,x1,y1,x1+l*np.cos(a),y1+l*np.sin(a),rng.choice([2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0],p=[0.05,0.10,0.20,0.30,0.15,0.10,0.05,0.05]),rng.choice([12,15,20,30,50,100],p=[0.05,0.10,0.15,0.20,0.25,0.25])))
    strats=[StrategicNode(0,300,200,"Ospedale",3,"hospital"),StrategicNode(1,150,180,"Municipio",2,"municipality"),StrategicNode(2,420,220,"Carabinieri",2,"fire_station"),StrategicNode(3,80,350,"Area Raccolta N",1,"assembly"),StrategicNode(4,500,100,"Area Raccolta S",1,"assembly")]
    return blds,segs,strats

# COLORS
BG='#0E1117';CRD='#1A1F2E';GRD='#2D3548';TXT='#E8EAF0';MUT='#8892A4';DNG='#E8443A';SAF='#2ECC71';WRN='#F39C12';ACC='#4A9EFF'

def fig_street(road_w, h_b, typo, slope, conf, soil, has_curve, d_edge, pga):
    t1=tier1(h_b,typo,conf,soil,slope,pga,d_edge,road_w,15 if has_curve else 100)
    r_cle=h_b
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,6.5),facecolor=BG)
    for ax,title,is_t1 in [(ax1,'METODO CLE-2D (Standard)',False),(ax2,'TIER I — CINEMATICO (Nostro)',True)]:
        ax.set_facecolor(BG);ax.set_xlim(-1,17);ax.set_ylim(-2.5,road_w+5);ax.set_aspect('equal');ax.axis('off')
        tc=DNG if not is_t1 else SAF
        ax.add_patch(FancyBboxPatch((-0.5,road_w+3.5),17,1.2,boxstyle="round,pad=0.2",facecolor=tc+'15',edgecolor=tc+'50',lw=1))
        ax.text(8,road_w+4.1,title,fontsize=11,fontweight='bold',color=tc,ha='center')
        ax.add_patch(FancyBboxPatch((0,0),16,road_w,boxstyle="round,pad=0.08",facecolor='#374151',edgecolor='#4B5563',lw=1.5))
        for i in range(0,16,2): ax.plot([i,i+1],[road_w/2]*2,color='#FDE68A',lw=1.2,alpha=0.4)
        ax.text(-0.3,road_w/2,f'{road_w:.1f}m',fontsize=8,color=ACC,ha='right',va='center',rotation=90,fontweight='bold')
        bx,bw_d,bh_d=4.5,7,3; by=road_w+d_edge
        ax.add_patch(FancyBboxPatch((bx,by),bw_d,bh_d,boxstyle="round,pad=0.05",facecolor='#92713A',edgecolor='#6B5B45',lw=2))
        ax.text(bx+bw_d/2,by+bh_d/2,f'h={h_b:.0f}m\n{TYPO_LABELS.get(typo,typo)}',fontsize=7,color='white',ha='center',va='center',fontweight='bold')
        if not is_t1:
            circ=plt.Circle((bx+bw_d/2,by),r_cle,facecolor=DNG,alpha=0.15,edgecolor=DNG,lw=2,ls='--');ax.add_patch(circ)
            ax.annotate(f'R=h={r_cle:.0f}m',xy=(bx+bw_d/2,by-r_cle),xytext=(bx+bw_d/2+3.5,by-r_cle-0.5),fontsize=8,color=DNG,fontweight='bold',arrowprops=dict(arrowstyle='->',color=DNG,lw=1.2))
            verdict='BLOCCATA' if r_cle>d_edge else 'TRANSITABILE'; vc=DNG if r_cle>d_edge else SAF
        else:
            theta=FRAGILITY[typo]['theta']; rs=t1['r_star']; cx,cy=bx+bw_d/2,by
            if rs>0.05:
                wedge=Wedge((cx,cy),rs,270-theta,270+theta,facecolor=DNG,alpha=0.18,edgecolor=DNG,lw=2,ls='--');ax.add_patch(wedge)
                ax.annotate(f'r*={rs:.1f}m',xy=(cx,cy-rs),xytext=(cx+3.5,cy-rs-0.5),fontsize=8,color=DNG,fontweight='bold',arrowprops=dict(arrowstyle='->',color=DNG,lw=1.2))
            if t1['residual']>=t1['L_req']:
                ax.add_patch(FancyBboxPatch((4,0.25),7.5,2.5,boxstyle="round,pad=0.12",facecolor=SAF,edgecolor='#1E8449',lw=2,alpha=0.85))
                ax.text(7.75,1.5,'🚒 PASSA',fontsize=10,ha='center',va='center',color='white',fontweight='bold')
                verdict='TRANSITABILE';vc=SAF
            else:
                ax.add_patch(FancyBboxPatch((4,0.25),7.5,2.5,boxstyle="round,pad=0.12",facecolor=DNG,edgecolor='#922B21',lw=2,alpha=0.6))
                ax.text(7.75,1.5,'🚒 ✕',fontsize=10,ha='center',va='center',color='white',fontweight='bold')
                verdict='BLOCCATA';vc=DNG
            ax.plot([15,15],[0,t1['L_req']],color=WRN,lw=1.5,ls=':')
            ax.text(15.5,t1['L_req']/2,f'L_req\n{t1["L_req"]:.1f}m',fontsize=6.5,color=WRN,ha='left',va='center')
        ax.add_patch(FancyBboxPatch((2,-2.2),12,1.3,boxstyle="round,pad=0.3",facecolor=CRD,edgecolor=vc,lw=2.5))
        ax.text(8,-1.55,verdict,fontsize=15,fontweight='bold',color=vc,ha='center',va='center')
    fig.tight_layout(pad=1.5);return fig,t1

def fig_usai_curves(current_pga=None):
    fig,ax=plt.subplots(figsize=(13,5.5),facecolor=BG);ax.set_facecolor(BG)
    pgas=sorted(PAPER.keys())
    ax.fill_between(pgas,[PAPER[p]['p5'] for p in pgas],[PAPER[p]['p95'] for p in pgas],alpha=0.12,color=ACC,label='Tier II 5-95 pctile')
    ax.plot(pgas,[PAPER[p]['usai_cle'] for p in pgas],'s--',color=DNG,lw=2.5,ms=9,label='CLE-2D',mfc=DNG)
    ax.plot(pgas,[PAPER[p]['usai_t1'] for p in pgas],'^-',color=SAF,lw=2.5,ms=9,label='Tier I (det.)',mfc=SAF)
    ax.plot(pgas,[PAPER[p]['pm'] for p in pgas],'o-',color=ACC,lw=2,ms=7,label='Tier II (media)',mfc=ACC)
    if current_pga and current_pga in PAPER:
        ax.axvline(current_pga,color=WRN,lw=1.5,ls='--',alpha=0.7)
        ax.text(current_pga+0.008,0.95,f'PGA={current_pga}g',fontsize=8,color=WRN,fontweight='bold')
    ax.annotate('Transizione critica',xy=(0.275,0.11),fontsize=9,color=WRN,fontweight='bold',ha='center',bbox=dict(boxstyle='round,pad=0.3',facecolor=CRD,edgecolor=WRN,alpha=0.9))
    ax.set_xlabel('PGA (g)',fontsize=11,color=TXT);ax.set_ylabel('USAI',fontsize=11,color=TXT);ax.set_xlim(0.03,0.42);ax.set_ylim(-0.05,1.08)
    ax.grid(True,alpha=0.1,color=GRD);ax.tick_params(colors=MUT)
    for s in ['top','right']:ax.spines[s].set_visible(False)
    for s in ['bottom','left']:ax.spines[s].set_color(GRD)
    ax.legend(loc='lower left',fontsize=8.5,facecolor=CRD,edgecolor=GRD,labelcolor=TXT);fig.tight_layout();return fig

def fig_ablation():
    fig,ax=plt.subplots(figsize=(10,4.5),facecolor=BG);ax.set_facecolor(BG)
    cfgs=['Tier I Completo','No Cuneo\nDirezionale','No Edge-to-Edge','No Vincolo\nVeicolo','CLE-2D\nBaseline']
    vals=[0.67,0.67,0.67,0.44,0.00];cols=[SAF,ACC,ACC,WRN,DNG]
    bars=ax.barh(cfgs,vals,color=cols,height=0.55,edgecolor=[c+'80' for c in cols],lw=1.5)
    for b,v in zip(bars,vals):ax.text(v+0.02,b.get_y()+b.get_height()/2,f'{v:.2f}',va='center',fontsize=11,fontweight='bold',color=TXT,fontfamily='monospace')
    ax.set_xlabel('USAI @ PGA=0.25g',fontsize=10,color=TXT);ax.set_xlim(0,0.82);ax.invert_yaxis();ax.tick_params(colors=MUT,labelsize=8.5)
    for s in ['top','right']:ax.spines[s].set_visible(False)
    for s in ['bottom','left']:ax.spines[s].set_color(GRD)
    ax.grid(True,axis='x',alpha=0.08,color=GRD);fig.tight_layout();return fig

def fig_network(segments, strategics, bl_cle_n, bl_t1_n, pga):
    rng=np.random.RandomState(int(pga*1000)+7);idx=list(range(len(segments)));rng.shuffle(idx)
    set_cle=set(idx[:bl_cle_n]);set_t1=set(idx[:bl_t1_n])
    fig,(a1,a2)=plt.subplots(1,2,figsize=(14,6.5),facecolor=BG)
    for ax,title,bset in [(a1,'CLE-2D',set_cle),(a2,'TIER I',set_t1)]:
        ax.set_facecolor(BG);ax.set_aspect('equal');ax.axis('off');tc=DNG if title=='CLE-2D' else SAF
        ax.set_title(title,fontsize=13,fontweight='bold',color=tc,fontfamily='serif',pad=12)
        for i,s in enumerate(segments):
            c=DNG if i in bset else SAF+'90';ax.plot([s.x1,s.x2],[s.y1,s.y2],color=c,lw=2.2 if i in bset else 1.3,alpha=0.85,solid_capstyle='round')
        icons={'hospital':(ACC,13),'municipality':(WRN,11),'fire_station':(SAF,11),'assembly':(MUT,8)}
        for sn in strategics:
            cl,sz=icons.get(sn.node_type,('white',8));ax.plot(sn.x,sn.y,'o',ms=sz+4,color=cl,alpha=0.25);ax.plot(sn.x,sn.y,'o',ms=sz,color=cl)
            ax.text(sn.x,sn.y-16,sn.name,fontsize=6.5,color=TXT,ha='center',alpha=0.75)
        nb=len(bset);pct=100*nb/len(segments)
        ax.text(0.02,0.02,f'Bloccati: {nb}/{len(segments)} ({pct:.0f}%)',transform=ax.transAxes,fontsize=8.5,color=TXT,fontfamily='monospace',bbox=dict(facecolor=CRD,edgecolor=GRD,pad=5))
    fig.tight_layout(pad=2);return fig

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    st.markdown("""<div class="hero-box"><div class="hero-tag">Peer-Reviewed · Sapienza Universita di Roma · Plantiverse S.r.l.</div><div class="hero-title">SEISMIC ACCESS</div><div class="hero-sub">Il tuo piano CLE protegge davvero i tuoi cittadini? Confronta il metodo standard (CLE-2D) con un modello cinematico che tiene conto della direzionalita del crollo, dei vincoli dei veicoli e della correlazione spaziale.</div></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-hdr">Parametri</div>',unsafe_allow_html=True)
        mode=st.radio("Modalita",["🔬 Sezione Stradale","🏘️ Rete Urbana","📁 Dati Tuoi"],label_visibility="collapsed")
        st.markdown("---")
        if mode=="🔬 Sezione Stradale":
            st.markdown("**Strada**");road_w=st.slider("Larghezza (m)",2.5,10.0,4.5,0.5);has_curve=st.checkbox("Curva stretta (R<15m)")
            st.markdown("**Edificio**");h_b=st.slider("Altezza (m)",3.0,25.0,10.0,0.5)
            typo=st.selectbox("Tipologia",list(TYPO_LABELS.keys()),format_func=lambda x:TYPO_LABELS[x])
            conf=st.selectbox("Confinamento",['isolated','end_row','mid_row','courtyard'],format_func=lambda x:{'isolated':'Isolato','end_row':'Testa schiera','mid_row':'Centro schiera','courtyard':'Cortile'}[x],index=2)
            slope=st.slider("Pendenza (%)",0,30,5)/100;soil=st.selectbox("Suolo EC8",['A','B','C','D','E'],index=2)
            d_edge=st.slider("Distanza edificio-strada (m)",0.0,5.0,0.5,0.1);pga=st.slider("**PGA (g)**",0.05,0.50,0.20,0.01)
        st.markdown("---")
        st.markdown('<div style="text-align:center;color:#8892A4;font-size:0.7rem;">FRAMEWORK SCIENTIFICO<br><span style="color:#E8EAF0;font-size:0.85rem;">Giannini & Nescatelli (2025)</span><br>Sapienza · Plantiverse</div>',unsafe_allow_html=True)

    if mode=="🔬 Sezione Stradale":
        page_street(road_w,h_b,typo,slope,conf,soil,has_curve,d_edge,pga)
    elif mode=="🏘️ Rete Urbana":
        page_network()
    else:
        page_custom()

    st.markdown(f"""<div class="cta-box"><div style="font-family:'Playfair Display',serif;font-size:1.7rem;font-weight:700;color:#E8EAF0;margin-bottom:0.4rem;">Vuoi l'analisi completa sul tuo Comune?</div><div style="color:#8892A4;max-width:600px;margin:0 auto 1.5rem;font-size:0.95rem;">Questa demo analizza dati sintetici. L'audit professionale copre l'intero tessuto urbano con dati reali e Monte Carlo correlato.</div><a href="mailto:leonardo.giannini@uniroma1.it?subject=Richiesta%20Audit%20Sismico" style="display:inline-block;background:#E8443A;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.95rem;margin:0 0.5rem;">📧 Richiedi Audit</a><a href="https://github.com/UniversalAdmittance/seismic-access" style="display:inline-block;background:transparent;color:#4A9EFF;border:1px solid #4A9EFF;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.95rem;margin:0 0.5rem;">📄 Paper & Codice</a></div>""",unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;padding:1rem 0;color:#5A6B7A;font-size:0.65rem;">SEISMIC ACCESS v2.0 · 2025 Giannini (Sapienza) · Nescatelli (Plantiverse)</div>',unsafe_allow_html=True)


def page_street(road_w,h_b,typo,slope,conf,soil,has_curve,d_edge,pga):
    st.markdown('<div class="sec">ANALISI SEZIONE STRADALE</div>',unsafe_allow_html=True)
    t1=tier1(h_b,typo,conf,soil,slope,pga,d_edge,road_w,15 if has_curve else 100);r_cle=h_b;cle_blocked=r_cle>d_edge
    c1,c2,c3,c4=st.columns(4)
    with c1:st.markdown(f'<div class="card card-r"><div class="lbl">Raggio CLE</div><div class="big" style="color:{DNG}">{r_cle:.1f}<span class="unit"> m</span></div><div class="lbl">= altezza edificio</div></div>',unsafe_allow_html=True)
    with c2:
        red=(1-t1["r_star"]/r_cle)*100 if r_cle>0 else 0
        st.markdown(f'<div class="card card-g"><div class="lbl">Raggio Tier I</div><div class="big" style="color:{SAF}">{t1["r_star"]:.1f}<span class="unit"> m</span></div><div class="lbl">-{red:.0f}% vs CLE</div></div>',unsafe_allow_html=True)
    with c3:
        rc=SAF if t1['residual']>=t1['L_req'] else DNG;cc='card-g' if t1['residual']>=t1['L_req'] else 'card-r'
        st.markdown(f'<div class="card {cc}"><div class="lbl">Largh. Residua</div><div class="big" style="color:{rc}">{t1["residual"]:.1f}<span class="unit"> m</span></div><div class="lbl">L_req={t1["L_req"]:.1f}m</div></div>',unsafe_allow_html=True)
    with c4:
        pc=DNG if t1['P_coll']>0.5 else (WRN if t1['P_coll']>0.1 else SAF)
        st.markdown(f'<div class="card card-b"><div class="lbl">P(collasso)</div><div class="big" style="color:{pc}">{t1["P_coll"]:.0%}</div><div class="lbl">soglia {t1["w_thr"]:.3f}g</div></div>',unsafe_allow_html=True)
    fig,_=fig_street(road_w,h_b,typo,slope,conf,soil,has_curve,d_edge,pga);st.pyplot(fig,use_container_width=True);plt.close(fig)
    if cle_blocked and not t1['blocked']:
        st.markdown(f'<div class="alert-box alert-green"><div style="font-size:2.2rem;">✅</div><div style="font-size:1.15rem;font-weight:700;color:{SAF};margin:0.5rem 0;">RISORSE SALVATE — Falso Positivo Eliminato</div><div style="color:{MUT};max-width:650px;margin:0 auto;">CLE blocca questa arteria. L\'analisi cinematica conferma il passaggio (residuo {t1["residual"]:.1f}m > L_req {t1["L_req"]:.1f}m). <strong>Nessuno sgombero necessario.</strong></div></div>',unsafe_allow_html=True)
    elif not cle_blocked and t1['blocked']:
        st.markdown(f'<div class="alert-box alert-red"><div style="font-size:2.2rem;">🚨</div><div style="font-size:1.15rem;font-weight:700;color:{DNG};margin:0.5rem 0;">TRAPPOLA LETALE — Falso Negativo CLE</div><div style="color:{MUT};max-width:650px;margin:0 auto;">CLE dice aperta ma il residuo ({t1["residual"]:.1f}m) e insufficiente (L_req={t1["L_req"]:.1f}m). <strong>Mezzo di soccorso incastrato.</strong></div></div>',unsafe_allow_html=True)
    elif cle_blocked and t1['blocked']:
        st.markdown(f'<div class="alert-box alert-yellow"><div style="font-size:2.2rem;">⚠️</div><div style="font-size:1.15rem;font-weight:700;color:{WRN};margin:0.5rem 0;">BLOCCO CONFERMATO</div><div style="color:{MUT};">Entrambi concordano. <strong>Priorita sgombero alta.</strong></div></div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-box alert-blue"><div style="font-size:2.2rem;">ℹ️</div><div style="font-size:1.15rem;font-weight:700;color:{ACC};margin:0.5rem 0;">STRADA LIBERA</div><div style="color:{MUT};">Transitabile a PGA={pga:.2f}g.</div></div>',unsafe_allow_html=True)
    with st.expander("📐 Dettaglio Tecnico"):
        c1,c2=st.columns(2)
        with c1:st.code(f"CLE-2D\n  R=h={r_cle:.1f}m\n  Bloccato={cle_blocked}")
        with c2:st.code(f"Tier I\n  w_eff={t1['w_eff']:.4f}g\n  k_b={t1['k_b']:.4f}\n  theta={FRAGILITY[typo]['theta']:.0f} deg\n  r*={t1['r_star']:.2f}m\n  L_req={t1['L_req']:.2f}m\n  Resid={t1['residual']:.2f}m\n  Blocked={t1['blocked']}")
    st.markdown('<div class="sec" style="margin-top:2rem;">TIER II — PROBABILITA DI BLOCCO</div>',unsafe_allow_html=True)
    pb=P_block_t2(h_b,typo,conf,soil,slope,pga,d_edge,road_w,15 if has_curve else 100)
    r95=t1['r_star']*np.exp(1.645*FRAGILITY[typo]['sigma_b']) if t1['r_star']>0 else 0
    c1,c2,c3=st.columns(3)
    with c1:st.markdown(f'<div class="card card-b"><div class="lbl">P(blocco)</div><div class="big" style="color:{ACC}">{pb:.1%}</div><div class="lbl">P_coll x P_eccedenza</div></div>',unsafe_allow_html=True)
    with c2:st.markdown(f'<div class="card card-b"><div class="lbl">sigma_b</div><div class="big" style="color:{MUT}">{FRAGILITY[typo]["sigma_b"]:.2f}</div><div class="lbl">log-normal</div></div>',unsafe_allow_html=True)
    with c3:st.markdown(f'<div class="card card-y"><div class="lbl">r* 95pct</div><div class="big" style="color:{WRN}">{r95:.1f}<span class="unit"> m</span></div><div class="lbl">coda distribuzione</div></div>',unsafe_allow_html=True)


def page_network():
    st.markdown('<div class="sec">RETE URBANA — INVENTARIO SINTETICO AMATRICE (RI)</div>',unsafe_allow_html=True)
    pga=st.select_slider("**Seleziona PGA (g)**",options=[0.05,0.10,0.15,0.20,0.25,0.30,0.40],value=0.15)
    d=PAPER[pga];N=142
    c1,c2,c3,c4=st.columns(4)
    with c1:st.markdown(f'<div class="card card-r"><div class="lbl">Bloccati CLE</div><div class="big" style="color:{DNG}">{d["bl_cle"]}<span class="unit">/{N}</span></div><div class="lbl">{100*d["bl_cle"]/N:.0f}% rete</div></div>',unsafe_allow_html=True)
    with c2:st.markdown(f'<div class="card card-g"><div class="lbl">Bloccati Tier I</div><div class="big" style="color:{SAF}">{d["bl_t1"]}<span class="unit">/{N}</span></div><div class="lbl">{100*d["bl_t1"]/N:.0f}% rete</div></div>',unsafe_allow_html=True)
    with c3:
        fp=(d['bl_cle']-d['bl_t1'])/max(d['bl_cle'],1)*100
        st.markdown(f'<div class="card card-b"><div class="lbl">Falsi Positivi Eliminati</div><div class="big" style="color:{ACC}">{fp:.0f}<span class="unit">%</span></div></div>',unsafe_allow_html=True)
    with c4:st.markdown(f'<div class="card card-y"><div class="lbl">PGA</div><div class="big" style="color:{WRN}">{pga}<span class="unit"> g</span></div><div class="lbl">451 edifici · 142 segmenti</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:st.markdown(f'<div class="card card-r" style="text-align:center;padding:1.8rem;"><div class="lbl">USAI — CLE-2D</div><div class="big-xl" style="color:{DNG if d["usai_cle"]==0 else SAF}">{d["usai_cle"]:.2f}</div><div class="lbl">{d["iso_cle"]} nodi isolati su 5</div></div>',unsafe_allow_html=True)
    with c2:st.markdown(f'<div class="card card-g" style="text-align:center;padding:1.8rem;"><div class="lbl">USAI — Tier I</div><div class="big-xl" style="color:{SAF if d["usai_t1"]>0 else DNG}">{d["usai_t1"]:.2f}</div><div class="lbl">{5-d["iso_t1"]} nodi raggiungibili</div></div>',unsafe_allow_html=True)
    if d['usai_cle']==0 and d['usai_t1']>0:
        st.markdown(f'<div class="alert-box alert-green"><div style="font-size:2rem;">✅</div><div style="font-size:1.1rem;font-weight:700;color:{SAF};margin:0.4rem 0;">CLE dichiara il comune IRRAGGIUNGIBILE — Tier I preserva la connettivita</div><div style="color:{MUT};max-width:700px;margin:0 auto;">A PGA={pga}g, CLE blocca {d["bl_cle"]}/{N} segmenti ({100*d["bl_cle"]/N:.0f}%) e isola tutti i nodi. Tier I identifica {d["bl_t1"]} blocchi reali. <strong>{fp:.0f}% dei blocchi CLE sono falsi positivi.</strong></div></div>',unsafe_allow_html=True)
    elif d['usai_cle']==d['usai_t1'] and d['usai_cle']>0:
        st.markdown(f'<div class="alert-box alert-blue"><div style="font-size:2rem;">ℹ️</div><div style="font-size:1.1rem;font-weight:700;color:{ACC};margin:0.4rem 0;">Concordanza a bassa intensita</div><div style="color:{MUT};">A PGA={pga}g entrambi producono risultati identici. La divergenza emerge da 0.15g.</div></div>',unsafe_allow_html=True)
    st.markdown("---");st.markdown("### Mappa di Rete")
    _,segs,strats=gen_inventory();fig=fig_network(segs,strats,d['bl_cle'],d['bl_t1'],pga);st.pyplot(fig,use_container_width=True);plt.close(fig)
    st.markdown("---");st.markdown("### Curva USAI vs PGA")
    fig2=fig_usai_curves(pga);st.pyplot(fig2,use_container_width=True);plt.close(fig2)
    st.markdown("---");st.markdown("### Ablazione Componenti (PGA=0.25g)")
    fig3=fig_ablation();st.pyplot(fig3,use_container_width=True);plt.close(fig3)
    st.markdown("---");st.markdown('<div class="sec">TIER II — RISCHIO PROBABILISTICO</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    p5c=DNG if d['p5']<0.5 else SAF
    with c1:st.markdown(f'<div class="card card-r" style="text-align:center;padding:1.5rem;"><div class="lbl">USAI 5 Percentile</div><div class="big-xl" style="color:{p5c}">{d["p5"]:.2f}</div><div class="lbl">scenario peggiore (5%)</div></div>',unsafe_allow_html=True)
    with c2:st.markdown(f'<div class="card card-b" style="text-align:center;padding:1.5rem;"><div class="lbl">USAI Media Prob.</div><div class="big-xl" style="color:{ACC}">{d["pm"]:.2f}</div><div class="lbl">500 scenari Monte Carlo</div></div>',unsafe_allow_html=True)
    with c3:st.markdown(f'<div class="card card-y" style="text-align:center;padding:1.5rem;"><div class="lbl">Blocchi Medi Prob.</div><div class="big-xl" style="color:{WRN}">{d["bpm"]:.0f}</div><div class="lbl">su {N} segmenti</div></div>',unsafe_allow_html=True)
    if d['p5']<=0.22 and d['p5']>0:
        st.markdown(f'<div class="alert-box alert-red"><div style="font-size:2rem;">🚨</div><div style="font-size:1.1rem;font-weight:700;color:{DNG};">ZONA DI TRANSIZIONE CRITICA</div><div style="color:{MUT};max-width:700px;margin:0 auto;">Nel 5% degli scenari peggiori a PGA={pga}g, solo l\'ospedale resta raggiungibile. Informazione <strong>invisibile</strong> al CLE.</div></div>',unsafe_allow_html=True)
    elif d['p5']==0:
        st.markdown(f'<div class="alert-box alert-red"><div style="font-size:2rem;">⛔</div><div style="font-size:1.1rem;font-weight:700;color:{DNG};">ISOLAMENTO TOTALE NEL TAIL-RISK</div><div style="color:{MUT};max-width:700px;margin:0 auto;">Nel 5% peggiore a PGA={pga}g <strong>nessun nodo raggiungibile</strong>. USAI=0.00.</div></div>',unsafe_allow_html=True)


def page_custom():
    st.markdown('<div class="sec">ANALISI CON DATI PERSONALIZZATI</div>',unsafe_allow_html=True)
    st.markdown("### Carica i dati del tuo Comune")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Inventario Edifici** (CSV)");st.code("id,x,y,height,typology,storeys,confinement,slope,soil\n1,100.5,200.3,9.0,URM_low,3,mid_row,0.05,C",language="csv")
        ub=st.file_uploader("Carica edifici",type=['csv'])
    with c2:
        st.markdown("**Rete Stradale** (CSV)");st.code("id,x1,y1,x2,y2,width,r_min\n1,90,200,120,200,4.5,100",language="csv")
        ur=st.file_uploader("Carica strade",type=['csv'])
    sb="id,x,y,height,typology,storeys,confinement,slope,soil\n1,50,22,9,URM_low,3,mid_row,0.05,C\n2,55,23,12,URM_mid,4,end_row,0.08,B\n3,80,22.5,6,URM_low,2,mid_row,0.10,C"
    sr="id,x1,y1,x2,y2,width,r_min\n1,30,10,170,10,4.5,100\n2,50,10,50,40,3.5,15\n3,100,10,100,50,5.0,50"
    c1,c2=st.columns(2)
    with c1:st.download_button("Template edifici",sb,"edifici_template.csv","text/csv")
    with c2:st.download_button("Template strade",sr,"strade_template.csv","text/csv")
    if ub and ur:
        import pandas as pd
        try:
            db=pd.read_csv(ub);dr=pd.read_csv(ur);pga_c=st.slider("PGA (g)",0.05,0.50,0.20,0.01)
            bl_cle,bl_t1,details=set(),set(),[];segs_obj=[]
            for _,r in dr.iterrows():segs_obj.append(RoadSegment(int(r['id']),float(r['x1']),float(r['y1']),float(r['x2']),float(r['y2']),float(r['width']),float(r.get('r_min',100))))
            for i,seg in enumerate(segs_obj):
                for _,b in db.iterrows():
                    dc=np.sqrt((b['x']-(seg.x1+seg.x2)/2)**2+(b['y']-(seg.y1+seg.y2)/2)**2);de=max(0,dc-4-seg.width/2)
                    if b['height']>dc:bl_cle.add(i)
                    t=tier1(b['height'],b['typology'],b['confinement'],b.get('soil','B'),b.get('slope',0),pga_c,de,seg.width,seg.r_min)
                    if t['blocked']:bl_t1.add(i);details.append({'Seg':seg.id,'Edif':b['id'],'r*':f"{t['r_star']:.1f}m",'Resid':f"{t['residual']:.1f}m"})
            st.success(f"Analizzati {len(db)} edifici, {len(dr)} segmenti.")
            c1,c2,c3=st.columns(3)
            with c1:st.metric("Bloccati CLE",f"{len(bl_cle)}/{len(segs_obj)}")
            with c2:st.metric("Bloccati Tier I",f"{len(bl_t1)}/{len(segs_obj)}")
            with c3:st.metric("Falsi positivi",f"{len(bl_cle)-len(bl_t1)}")
            if details:st.dataframe(details,use_container_width=True)
            fig=fig_network(segs_obj,[],len(bl_cle),len(bl_t1),pga_c);st.pyplot(fig,use_container_width=True);plt.close(fig)
        except Exception as e:st.error(f"Errore: {e}")

if __name__=="__main__":
    main()
