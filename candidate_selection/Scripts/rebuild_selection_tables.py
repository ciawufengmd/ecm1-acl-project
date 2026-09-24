"""Rebuild descriptive candidate summaries from frozen CSVs; never refit models.
Python >=3.10, standard library only. Run from any working directory.
"""
from pathlib import Path
import csv, json, math, hashlib
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'Source_Data'

def read(name):
    with (SRC/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    assert rows
    with (SRC/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def num(x):
    if x in (None,'','NA'):return None
    return float(x)
def b(x):return str(x).upper()=='TRUE'
def same_dir(v):
    return len(v)==4 and all(x is not None for x in v) and (all(x<0 for x in v) or all(x>0 for x in v))
def tf(v):return 'NE' if v is None else ('TRUE' if v else 'FALSE')

def main():
    family=read('T01a_Candidate_panel.csv')
    eff=read('T01b_Cross_source_expression_effects.csv')
    latest=read('T02b_All_network_gene_ranks.csv')
    topo=read('06_GENE_LEVEL_VGK_ALL_WITH_ROBUSTNESS.csv')
    old=read('POSTHOC_35GENE_STAGE1_STAGE3_STAGE4_MATRIX.csv')
    assert len(family)==35 and len(eff)==175 and len(latest)==len(topo)==1992 and len(old)==35
    td={r['gene']:r for r in topo}; ld={r['gene']:r for r in latest}; od={r['gene']:r for r in old}
    ed={}
    for r in eff:
        k=(r['candidate'],r['comparison']);assert k not in ed;ed[k]=r
    stages=['Mouse CD9','Mouse CX3CR1','Mouse F4_80neg','Mouse Neutrophil']
    short=['CD9','CX3CR1','F4_80neg','Neutrophil']
    qa={}
    qa['n_1992_raw_rank_mismatches']=sum(int(ld[g]['raw_rank'])!=int(td[g]['VGK_rank']) for g in td)
    qa['n_1992_adjusted_rank_mismatches']=sum(int(ld[g]['adjusted_rank'])!=int(td[g]['degree_residual_rank']) for g in td)
    qa['max_absolute_delta_c_difference']=max(abs(float(ld[g]['delta_c'])-float(td[g]['VGK_impact'])) for g in td)
    selected=[]
    for r in topo:
        raw=int(r['VGK_rank'])<=50 and float(r['LOO_top50_frequency'])>=.8 and float(r['threshold_median_rank'])<=50
        residual=int(r['degree_residual_rank'])<=50 and float(r['LOO_top50_frequency'])>=.8
        if raw or residual:selected.append(r['gene'])
    assert set(selected)==set(r['gene'] for r in family)
    qa['union_rule_members']=len(selected)
    cur=[];cs1=[];recon=[]
    for f in family:
        g=f['gene'];t=td[g];o=od[g];l=ld[g];h=ed[g,'Human overlapping']
        qq=[num(ed[g,c]['FDR_primary']) for c in stages];vv=[num(ed[g,c]['logFC']) for c in stages]
        ne=sum(q is not None for q in qq);ns=sum(q is not None and q<.05 for q in qq)
        A=None if ne!=4 else (ns==4 and same_dir(vv));B=None if num(h['FDR_primary']) is None else num(h['FDR_primary'])<.05
        joint=None if A is None or B is None else A and B
        row={'gene':g,'raw_rank':int(l['raw_rank']),'degree_adjusted_rank':int(l['adjusted_rank']),'in_six_candidate_subset':f['in_six_candidate_subset'],'human_log2FC':h['logFC'],'human_FDR_primary':h['FDR_primary'],'human_status':h['status']}
        for s,c in zip(short,stages):
            r=ed[g,c];row[s+'_log2FC']=r['logFC'];row[s+'_FDR_primary']=r['FDR_primary'];row[s+'_status']=r['status']
        row.update({'mouse_evaluable_n':ne,'mouse_significant_n':ns,'mouse_all4_same_direction':tf(None if ne!=4 else same_dir(vv)),'current_rule_A':tf(A),'current_rule_B':tf(B),'current_joint_A_and_B':tf(joint)})
        cur.append(row)
        cs1.append({'gene':g,'raw_rank':int(l['raw_rank']),'degree_adjusted_rank':int(l['adjusted_rank']),'degree':int(l['degree']),'rank_r55':int(t['rank_r55']),'rank_r60':int(t['rank_r60']),'rank_r65':int(t['rank_r65']),'threshold_median_rank':num(t['threshold_median_rank']),'LOO_n':int(t['LOO_n']),'LOO_median_rank':num(t['LOO_median_rank']),'LOO_top10_frequency':num(t['LOO_top10_frequency']),'LOO_top50_frequency':num(t['LOO_top50_frequency']),'stable_raw_topology':t['stable_raw_topology'],'degree_corrected_candidate':t['degree_corrected_candidate'],'in_six_candidate_subset':f['in_six_candidate_subset']})
        oldA=None if o['temporal_rule_A']=='NA' else b(o['temporal_rule_A']);oldB=None if o['human_rule_B']=='NA' else b(o['human_rule_B']);oldJ=None if oldA is None or oldB is None else oldA and oldB
        recon.append({'gene':g,'raw_rank':int(l['raw_rank']),'historical_mouse_sig_n':o['n_temporal_contrasts_FDR_lt_0.05'],'current_mouse_sig_n':ns,'current_mouse_evaluable_n':ne,'historical_rule_A':tf(oldA),'current_rule_A':tf(A),'historical_rule_B':tf(oldB),'current_rule_B':tf(B),'historical_joint':tf(oldJ),'current_joint':tf(joint),'joint_classification_changed':tf(tf(oldJ)!=tf(joint))})
    write('CS1_Candidate35_topology.csv',cs1);write('CS3_Current35_summary.csv',cur);write('CS5_Version_reconciliation.csv',recon)
    qa['current_effect_status_counts']=dict(Counter(r['status'] for r in eff))
    qa['current_evaluable_by_comparison']={c:sum(num(r['FDR_primary']) is not None for r in eff if r['comparison']==c) for c in [*stages,'Human overlapping']}
    qa['current_rule_A_genes']=[r['gene'] for r in cur if r['current_rule_A']=='TRUE']
    qa['current_rule_B_genes']=[r['gene'] for r in cur if r['current_rule_B']=='TRUE']
    qa['current_joint_genes']=[r['gene'] for r in cur if r['current_joint_A_and_B']=='TRUE']
    qa['historical_joint_genes']=[r['gene'] for r in recon if r['historical_joint']=='TRUE']
    qa['joint_classification_changes']=[r for r in recon if r['joint_classification_changed']=='TRUE']
    # Publication table and pre-publication render input must preserve all scientific fields.
    raw=read('candidate_effects.csv');a={(r['candidate'],r['comparison']):r for r in raw}
    qa['T01b_vs_plot_input_numeric_mismatches']=sum(num(r[k])!=num(a[(r['candidate'],r['comparison'])][k]) for r in eff for k in ['logFC','PValue','FDR_primary'])
    # Sentinels are the values printed in the supplied current manuscript Figure 2.
    sentinel={'Human overlapping':(-1.12,.0229),'Mouse CD9':(-1.07,.0181),'Mouse CX3CR1':(-3.85,2.48e-8),'Mouse F4_80neg':(-2.47,2.79e-6),'Mouse Neutrophil':(-4.20,4.97e-6)}
    qa['ECM1_manuscript_display_sentinels']={c:{'source_logFC':num(ed['ECM1',c]['logFC']),'source_FDR':num(ed['ECM1',c]['FDR_primary']),'printed_logFC':v[0],'printed_FDR':v[1]} for c,v in sentinel.items()}
    assert qa['n_1992_raw_rank_mismatches']==qa['n_1992_adjusted_rank_mismatches']==qa['T01b_vs_plot_input_numeric_mismatches']==0
    assert qa['current_joint_genes']==['ECM1','P4HB','SEC61A1']
    qa['models_refitted']=False;qa['FDR_recalculated']=False;qa['scope']='CSV matching, rule application and descriptive version reconciliation only'
    (ROOT/'Audit'/'NUMERIC_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
