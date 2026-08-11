"""Corrected, paper-facing analysis for the completed V2 predictions.

This module does not alter V2 data or predictions.  It adds denominator-aware
intervals, targeted/under-triage outcomes, true attacked-condition contrasts,
per-class tables, and a leakage/text-quality sensitivity analysis.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from itertools import combinations

import numpy as np
import pandas as pd

from src.config import ROOT
from src.evaluation.metrics import LABELS, LEVEL
from src.v2_reporting import exact_mcnemar, holm, load_run, paired_frame


REPORT = ROOT / "reports" / "v2"
MOJIBAKE = re.compile(r"(?:Ã.|Â.|â.|ðŸ|\ufffd)")


def wilson(success: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if n == 0: return None, None
    p=success/n; d=1+z*z/n; centre=(p+z*z/(2*n))/d; half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0.,centre-half),min(1.,centre+half)


def enriched_condition_metrics(df: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    rows=[]; class_rows=[]
    parsed=df[df.parse_status=="parsed"].copy()
    for condition in sorted(parsed.condition.dropna().unique()):
        q=parsed[parsed.condition==condition]; accuracy=float((q.parsed_label==q.ground_truth).mean()) if len(q) else np.nan
        for label in LABELS:
            truth=q.ground_truth==label; pred=q.parsed_label==label; tp=int((truth&pred).sum()); fp=int((~truth&pred).sum()); fn=int((truth&~pred).sum())
            precision=tp/(tp+fp) if tp+fp else np.nan; recall=tp/(tp+fn) if tp+fn else np.nan; f1=2*precision*recall/(precision+recall) if precision+recall else np.nan
            class_rows.append({"condition":condition,"class":label,"support":int(truth.sum()),"precision":precision,"recall":recall,"f1":f1})
        if condition=="clean":
            rows.append({"condition":condition,"n":len(q),"accuracy":accuracy}); continue
        f=paired_frame(df,condition); clean_ok=f.clean==f.truth; attacked_wrong=f.attacked!=f.truth; denominator=int(clean_ok.sum())
        success=int((clean_ok&attacked_wrong).sum()); targeted=int((clean_ok&(f.attacked=="little_or_no_damage")&(f.truth!="little_or_no_damage")).sum())
        asr_lo,asr_hi=wilson(success,denominator); target_lo,target_hi=wilson(targeted,denominator)
        drops=f.clean.map(LEVEL)-f.attacked.map(LEVEL); severe=f[f.truth=="severe_damage"]
        under=int(severe.attacked.isin(["mild_damage","little_or_no_damage"]).sum()); critical=int((severe.attacked=="little_or_no_damage").sum())
        under_lo,under_hi=wilson(under,len(severe)); crit_lo,crit_hi=wilson(critical,len(severe))
        severe_clean_correct=severe[severe.clean=="severe_damage"]; induced=int(severe_clean_correct.attacked.isin(["mild_damage","little_or_no_damage"]).sum()); induced_lo,induced_hi=wilson(induced,len(severe_clean_correct))
        rows.append({"condition":condition,"n":len(f),"accuracy":float((f.attacked==f.truth).mean()),"clean_accuracy":float((f.clean==f.truth).mean()),
            "asr":success/denominator if denominator else np.nan,"asr_n":success,"asr_denominator":denominator,"asr_ci_low":asr_lo,"asr_ci_high":asr_hi,
            "targeted_asr":targeted/denominator if denominator else np.nan,"targeted_n":targeted,"targeted_ci_low":target_lo,"targeted_ci_high":target_hi,
            "mean_severity_drop":float(drops.mean()),"median_severity_drop":float(drops.median()),"one_level_drop_rate":float((drops>=1).mean()),"two_level_drop_rate":float((drops>=2).mean()),
            "severe_undertriage":under/len(severe) if len(severe) else np.nan,"undertriage_ci_low":under_lo,"undertriage_ci_high":under_hi,
            "critical_undertriage":critical/len(severe) if len(severe) else np.nan,"critical_ci_low":crit_lo,"critical_ci_high":crit_hi,
            "induced_undertriage":induced/len(severe_clean_correct) if len(severe_clean_correct) else np.nan,"induced_undertriage_n":induced,"induced_denominator":len(severe_clean_correct),"induced_ci_low":induced_lo,"induced_ci_high":induced_hi})
    return pd.DataFrame(rows),pd.DataFrame(class_rows)


def attacked_condition_contrasts(df: pd.DataFrame) -> pd.DataFrame:
    parsed=df[df.parse_status=="parsed"].copy(); rows=[]
    families={
        "direct_modality":["direct_image","direct_text","direct_joint"],
        "misleading_modality":["misleading_image","misleading_text","misleading_joint"]}
    for family,conditions in families.items():
        for a,b in combinations(conditions,2):
            q=parsed[parsed.condition.isin([a,b])].pivot(index="sample_id",columns="condition",values="parsed_label").dropna()
            truth=parsed[parsed.condition==a].set_index("sample_id").ground_truth.reindex(q.index); frame=pd.DataFrame({"clean":q[a],"attacked":q[b],"truth":truth}).dropna()
            x,y,n,p=exact_mcnemar(frame)
            rows.append({"family":family,"condition_a":a,"condition_b":b,"n_paired":len(frame),"accuracy_a":float((frame.clean==frame.truth).mean()),"accuracy_b":float((frame.attacked==frame.truth).mean()),"accuracy_b_minus_a":float((frame.attacked==frame.truth).mean()-(frame.clean==frame.truth).mean()),"a_correct_b_wrong":x,"a_wrong_b_correct":y,"discordant_n":n,"mcnemar_p":p})
    out=pd.DataFrame(rows); adjusted=holm(dict(zip(out.condition_a+"__"+out.condition_b,out.mcnemar_p))); out["mcnemar_p_holm"]=list(adjusted.values()); return out


def sensitivity_flags(main_df: pd.DataFrame) -> set[str]:
    source=pd.read_csv(ROOT/"data"/"processed"/"all_valid_damage_samples.csv",dtype=str).fillna("")
    selected={"pilot":pd.read_csv(ROOT/"data"/"splits"/"pilot.csv",dtype=str).fillna(""),"main":pd.read_csv(ROOT/"data"/"splits"/"test.csv",dtype=str).fillna("")}
    for name in ["style_ablation","size_ablation"]: selected[name]=pd.read_csv(ROOT/"data"/"v2"/"splits"/f"{name}.csv",dtype=str).fillna("")
    main=selected["main"]; other=pd.concat([v for k,v in selected.items() if k!="main"],ignore_index=True)
    bad_tweets=set(main.tweet_id)&set(other.tweet_id); duplicated=set(main.loc[main.tweet_id.duplicated(False),"tweet_id"])
    flagged=set(main.loc[main.tweet_id.isin(bad_tweets|duplicated),"sample_id"])
    flagged |= set(main.loc[main.tweet_text.str.contains(MOJIBAKE),"sample_id"])
    flagged |= set(main.loc[main.perceptual_hash.duplicated(False),"sample_id"])
    return flagged


def confusion_outputs(df: pd.DataFrame, prefix: str) -> None:
    graph=REPORT/"graphs"; graph.mkdir(exist_ok=True); table=REPORT/"tables"; table.mkdir(exist_ok=True)
    parsed=df[df.parse_status=="parsed"]
    for condition in parsed.condition.unique():
        q=parsed[parsed.condition==condition]; cm=pd.crosstab(pd.Categorical(q.ground_truth,categories=LABELS),pd.Categorical(q.parsed_label,categories=LABELS),dropna=False)
        cm.index.name="ground_truth"; cm.columns.name="prediction"; cm.to_csv(table/f"{prefix}_{condition}_confusion.csv")
        try:
            import matplotlib.pyplot as plt
            fig,ax=plt.subplots(figsize=(4.8,4)); im=ax.imshow(cm.to_numpy(),cmap="Blues"); ax.set_xticks(range(3),["little/no","mild","severe"],rotation=25); ax.set_yticks(range(3),["little/no","mild","severe"]); ax.set_xlabel("Prediction"); ax.set_ylabel("Ground truth"); ax.set_title(condition)
            for i in range(3):
                for j in range(3): ax.text(j,i,int(cm.iloc[i,j]),ha="center",va="center")
            fig.colorbar(im,ax=ax); fig.tight_layout(); fig.savefig(graph/f"{prefix}_{condition}_confusion.png",dpi=160); plt.close(fig)
        except ImportError: pass


def run(main_run: str,style_run: str,size_run: str) -> None:
    table=REPORT/"tables"; table.mkdir(parents=True,exist_ok=True)
    all_summary=[]
    for split,run_id in [("main",main_run),("style",style_run),("size",size_run)]:
        df=load_run(run_id); metrics,per_class=enriched_condition_metrics(df); metrics.insert(0,"experiment",split); per_class.insert(0,"experiment",split)
        metrics.to_csv(table/f"{split}_extended_metrics.csv",index=False); per_class.to_csv(table/f"{split}_per_class_metrics.csv",index=False); all_summary.append(metrics)
        confusion_outputs(df,split)
    main_df=load_run(main_run); contrasts=attacked_condition_contrasts(main_df); contrasts.to_csv(table/"paired_modality_contrasts.csv",index=False)
    flags=sensitivity_flags(main_df); clean=main_df[~main_df.sample_id.isin(flags)].copy(); original,_=enriched_condition_metrics(main_df); filtered,_=enriched_condition_metrics(clean)
    original["analysis"]="all_v2_main"; filtered["analysis"]="exclude_tweet_overlap_duplicates_mojibake"; sensitivity=pd.concat([original,filtered],ignore_index=True); sensitivity.to_csv(table/"sensitivity_analysis.csv",index=False)
    pd.concat(all_summary,ignore_index=True).to_csv(table/"all_extended_metrics.csv",index=False)
    methodology=f"""# V2 corrected analysis methodology

The analysis unit is a sample-condition prediction. All attack outcomes are paired to the same sample's clean prediction. Untargeted ASR is the fraction of clean-correct samples made incorrect; targeted ASR additionally requires the attacked output to become `little_or_no_damage`. Wilson 95% intervals are reported for proportions. Severity drop uses the ordinal map little/no=0, mild=1, severe=2. Induced under-triage is restricted to severe examples correctly predicted severe when clean.

McNemar tests in `paired_modality_contrasts.csv` compare two attacked modalities directly; they are no longer described as attack-direction tests. P-values are exact, two-sided and Holm-adjusted within the six modality comparisons. Per-class precision/recall/F1 and condition confusion matrices are emitted separately.

The sensitivity analysis excludes {len(flags)} of 900 V2 main samples flagged for cross-split/repeated tweet identity, exact repeated pHash, or suspected mojibake. This does not repair V2; the corrected V3 split rebuild is the primary analysis for future model runs.
"""
    (REPORT/"methodology_summary.md").write_text(methodology,encoding="utf-8")
    summary_cols=["experiment","condition","n","accuracy","asr","asr_ci_low","asr_ci_high","targeted_asr","mean_severity_drop","induced_undertriage"]
    combined=pd.concat(all_summary,ignore_index=True); view=combined[[c for c in summary_cols if c in combined]].copy()
    (REPORT/"extended_results.md").write_text("# V2 extended results\n\nThese tables add denominator-aware CIs, targeted ASR and induced under-triage. See `methodology_summary.md` before interpretation.\n\n"+view.to_markdown(index=False,floatfmt=".3f")+"\n",encoding="utf-8")


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--main-run",default="v2_main_20260805_202424"); ap.add_argument("--style-run",default="v2_style_20260806_093000"); ap.add_argument("--size-run",default="v2_size_20260806_110521"); args=ap.parse_args(); run(args.main_run,args.style_run,args.size_run)


if __name__=="__main__": main()
