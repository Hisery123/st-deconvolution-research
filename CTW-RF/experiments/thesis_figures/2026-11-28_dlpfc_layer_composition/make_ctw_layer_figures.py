#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate editable vector scientific figures from the frozen CTW-RF DLPFC layer CSV.

Input: all_slide_layer_celltype_means.csv (required, same directory or --input CSV)
Output: two PDF/SVG pairs and a by-layer/by-method summary CSV.
No imputation and no inferential statistical tests.
"""
from __future__ import annotations
import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import TwoSlopeNorm

LAYERS = ['L1','L2','L3','L4','L5','L6','WM']
TYPES = ['Astro','EndoMural','Excit','Inhib','Micro','OPC','Oligo']
METHODS = ['CTW_SoftOpt','GlobalStacking','NNLS_all']


def configure_font():
    # Register locally available CJK font; fonts are not included in the package.
    ttc=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
    if ttc.exists(): font_manager.fontManager.addfont(str(ttc))
    available = {x.name for x in font_manager.fontManager.ttflist}
    fallback = ['Noto Sans CJK SC', 'Noto Sans CJK JP', 'Microsoft YaHei', 'SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
    selected = next((x for x in fallback if x in available), 'DejaVu Sans')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': [selected, 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'svg.fonttype': 'none',  # text remains editable
        'pdf.fonttype': 42,
        'figure.dpi': 180,
        'savefig.dpi': 300,
    })
    return selected


def validate_and_aggregate(infile):
    with infile.open('r', encoding='utf-8-sig', newline='') as f:
        raw = list(csv.DictReader(f))
    required={'slide','method','layer','cell_type','n_spots','mean_predicted_fraction'}
    assert raw and required == set(raw[0]), f'Columns unexpected: {raw[0].keys() if raw else "empty"}'
    rows=[]
    for r in raw:
        rr=dict(r)
        rr['n_spots']=int(r['n_spots'])
        rr['mean_predicted_fraction']=float(r['mean_predicted_fraction'])
        assert 0<=rr['mean_predicted_fraction']<=1, rr
        assert rr['n_spots']>0, rr
        rows.append(rr)
    assert len(rows)==4256, f'Expected 4256, got {len(rows)}'
    levels = defaultdict(list)
    slices = defaultdict(list)
    for r in rows:
        levels[(r['slide'],r['method'],r['layer'])].append(r)
        slices[(r['method'],r['layer'],r['cell_type'])].append(r)
    assert len(levels)==608
    for key, group in levels.items():
        assert len(group)==7 and {x['cell_type'] for x in group}==set(TYPES), key
        assert len({x['n_spots'] for x in group})==1, key
        assert abs(sum(x['mean_predicted_fraction'] for x in group)-1)<1e-12, key
    all_methods=sorted({r['method'] for r in rows})
    assert len(all_methods)==8
    out=[]
    for method in all_methods:
        for layer in LAYERS:
            for typ in TYPES:
                g=slices[(method,layer,typ)]
                x=[a['mean_predicted_fraction'] for a in g]
                assert len(x)==(8 if layer in ['L1','L2'] else 12)
                out.append({
                    'method':method, 'layer':layer, 'cell_type':typ,
                    'n_slices':len(x),
                    'mean_fraction':statistics.mean(x),
                    'sd_between_slices':statistics.stdev(x) if len(x)>1 else 0,
                })
    return rows, out


def mat_for(summary, method):
    v={(r['method'],r['layer'],r['cell_type']): r for r in summary}
    return np.array([[100*v[(method,layer,typ)]['mean_fraction'] for layer in LAYERS] for typ in TYPES])


def beautify(ax):
    ax.set_yticks(range(len(TYPES)), labels=TYPES, fontsize=9)
    ax.set_xticks(range(len(LAYERS)), labels=[f'{x}\n(n={8 if x in ["L1","L2"] else 12})' for x in LAYERS], fontsize=9)
    ax.set_xticks(np.arange(-.5,7,1),minor=True)
    ax.set_yticks(np.arange(-.5,7,1),minor=True)
    ax.grid(which='minor',color='white',linewidth=1.1)
    ax.tick_params(which='minor',bottom=False,left=False)
    ax.tick_params(axis='both',length=0,pad=7)
    for sp in ax.spines.values(): sp.set_visible(False)


def save(fig, folder, stem):
    fig.savefig(folder/f'{stem}.svg', bbox_inches='tight', pad_inches=.14)
    fig.savefig(folder/f'{stem}.pdf', bbox_inches='tight', pad_inches=.14)
    plt.close(fig)


def make_ctw_fig(summary, folder):
    fig, ax = plt.subplots(figsize=(10,6.25))
    m=mat_for(summary,'CTW_SoftOpt')
    im=ax.imshow(m,cmap='viridis',vmin=0,vmax=80,interpolation='nearest',aspect='auto')
    beautify(ax)
    ax.set_title('CTW-SoftOpt在DLPFC皮层分层中的细胞组成预测', fontsize=14.5, fontweight='bold', pad=17)
    ax.set_xlabel('参考层级及有该层注释的切片数',fontsize=10,labelpad=11)
    ax.set_ylabel('细胞类型',fontsize=10,labelpad=12)
    for i in range(7):
        for j in range(7):
            val=m[i,j]
            rgb=im.cmap(im.norm(val))[:3]
            lum=.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]
            ax.text(j,i,f'{val:.1f}',ha='center',va='center',fontsize=8.8,
                    color='white' if lum<.48 else '#151515')
    cb=fig.colorbar(im,ax=ax,shrink=.88,pad=.028)
    cb.set_label('平均预测比例（%）',rotation=270,labelpad=16,fontsize=10)
    fig.text(.52,.015,'切片等权平均（每张切片先按层汇总）；无细胞组成真值，不能据此评价预测精度。',ha='center',fontsize=8.6)
    fig.subplots_adjust(left=.16,right=.93,top=.88,bottom=.19)
    save(fig,folder,'fig3_ctw_layer_composition')


def make_difference_fig(summary, folder):
    fig, axes=plt.subplots(1,2,figsize=(14.9,6.0),gridspec_kw={'wspace':.44})
    main=mat_for(summary,'CTW_SoftOpt')
    for ax,base,name,title in zip(axes, ['GlobalStacking','NNLS_all'], ['GlobalStacking','NNLS_all'],
                                   ['(a) 相对GlobalStacking','(b) 相对NNLS_all']):
        d=main-mat_for(summary,base)
        lim=max(1.0,np.ceil(np.max(np.abs(d))*2)/2)
        im=ax.imshow(d,cmap='RdBu_r',norm=TwoSlopeNorm(vcenter=0,vmin=-lim,vmax=lim),interpolation='nearest',aspect='auto')
        beautify(ax)
        ax.set_title(f'{title}\n(CTW-SoftOpt − {base})',fontsize=12,pad=13)
        for i in range(7):
            for j in range(7):
                val=d[i,j]
                rgb=im.cmap(im.norm(val))[:3]
                lum=.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]
                disp='0.0' if abs(val)<0.05 else f'{val:+.1f}'
                ax.text(j,i,disp,ha='center',va='center',fontsize=8.3,
                        color='white' if lum<.48 else '#202020')
        cb=fig.colorbar(im,ax=ax,fraction=.045,pad=.02,shrink=.86)
        cb.set_label('预测比例差（百分点）',rotation=270,labelpad=15,fontsize=9)
        ax.set_xlabel('参考层级及切片数',fontsize=9,labelpad=11)
        if ax==axes[0]: ax.set_ylabel('细胞类型',fontsize=9,labelpad=10)
    fig.suptitle('DLPFC分层细胞组成预测：CTW-SoftOpt与基线的差异',fontsize=15,fontweight='bold',y=.98)
    fig.text(.5,.022,'切片内配对比较，再对该层有注释的切片等权平均；不同面板的色标范围不同。差异不代表准确率提升。',ha='center',fontsize=9)
    fig.subplots_adjust(left=.075,right=.94,top=.82,bottom=.19)
    save(fig,folder,'fig3_ctw_vs_baselines_layer_differences')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input', type=Path, default=Path(__file__).with_name('all_slide_layer_celltype_means.csv'))
    p.add_argument('--outdir', type=Path, default=Path(__file__).resolve().parent)
    a=p.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True)
    rows,summary=validate_and_aggregate(a.input)
    configure_font()
    with (a.outdir/'ctw_layer_slice_equal_summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    make_ctw_fig(summary,a.outdir)
    make_difference_fig(summary,a.outdir)
    print('OK:',len(rows),'rows;',len(summary),'aggregated rows; four vector plots')

if __name__=='__main__': main()
