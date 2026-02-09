import argparse
import csv
import math
import os

import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)
CMS.setCMSStyle()

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Plot H+ and A decay from CSV scan")
parser.add_argument("--type", required=True, type=int, help="Yukawa type (1-4)")
parser.add_argument("--tanb", required=True, type=int, help="tan beta (1-10)")
args = parser.parse_args()

TYPE_LABEL = {1: "Type-I", 2: "Type-II", 3: "Type-X", 4: "Type-Y"}

# ---------------------------------------------------------------------------
# Read CSV
# ---------------------------------------------------------------------------
csvpath = f"outputs/scan_type{args.type}_tanb{args.tanb}.csv"
if not os.path.exists(csvpath):
    raise FileNotFoundError(csvpath)

rows = []
with open(csvpath) as f:
    reader = csv.DictReader(f)
    for r in reader:
        d = {}
        for k, v in r.items():
            try:
                d[k] = float(v)
            except ValueError:
                d[k] = float("nan")
        rows.append(d)


def isvalid(row):
    return not math.isnan(row["gam_Hc_tot"])


# ---------------------------------------------------------------------------
# H+ decay plot: partial widths vs mHc (dual y-axes)
# ---------------------------------------------------------------------------
# Collect fermionic partial widths (constant vs mA) at each mHc
# by taking the value from the first valid mA at that mHc.
# Collect WA partial width band (min/max over valid mA) and benchmarks.

mHc_vals = sorted(set(int(r["mHc"]) for r in rows))
mW = 80.36951

# Fermionic channels: pick first valid mA per mHc
gr_taunu = ROOT.TGraph()
gr_cs = ROOT.TGraph()
gr_tb = ROOT.TGraph()

# WA benchmark lines: mA=15, mA=mHc-30, mA=mHc-mW
gr_WA_15 = ROOT.TGraph()
gr_WA_near = ROOT.TGraph()
gr_WA_threshold = ROOT.TGraph()

for mHc in mHc_vals:
    subset = [r for r in rows if int(r["mHc"]) == mHc and isvalid(r)]
    if not subset:
        continue

    # Fermionic widths (first valid point)
    ref = subset[0]
    gr_taunu.SetPoint(gr_taunu.GetN(), mHc, ref["gam_Hc_taunu"])
    gr_cs.SetPoint(gr_cs.GetN(), mHc, ref["gam_Hc_cs"])
    gr_tb.SetPoint(gr_tb.GetN(), mHc, ref["gam_Hc_tb"])

    # Benchmark: mA=15
    bench15 = [r for r in subset if int(r["mA"]) == 15]
    if bench15 and bench15[0]["gam_Hc_WA"] > 0:
        gr_WA_15.SetPoint(gr_WA_15.GetN(), mHc, bench15[0]["gam_Hc_WA"])

    # Benchmark: mA = mHc - 30
    near_mA = mHc - 30
    bench_near = [r for r in subset if int(r["mA"]) == near_mA]
    if bench_near and bench_near[0]["gam_Hc_WA"] > 0:
        gr_WA_near.SetPoint(gr_WA_near.GetN(), mHc, bench_near[0]["gam_Hc_WA"])

    # Benchmark: mA = mHc - mW (on-shell W threshold), start from mHc=100
    if mHc >= 100:
        threshold_mA = int(round(mHc - mW))
        bench_thr = [r for r in subset if int(r["mA"]) == threshold_mA]
        if bench_thr and bench_thr[0]["gam_Hc_WA"] > 0:
            gr_WA_threshold.SetPoint(gr_WA_threshold.GetN(), mHc, bench_thr[0]["gam_Hc_WA"])

# --- Draw H+ plot ---
CMS.SetExtraText("Simulation Preliminary")
CMS.SetEnergy(0, unit="")
CMS.SetLumi(None, run=f"tan#beta = {args.tanb} ({TYPE_LABEL[args.type]})")

c1 = CMS.cmsCanvas("c_Hc", 80, 160, 1e-6, 1e2,
                    "m_{H^{+}} [GeV]",
                    "#Gamma(H^{+} #rightarrow X) [GeV]",
                    square=True, iPos=0, extraSpace=0.)
c1.SetLogy()

# WA benchmark lines (dashed)
if gr_WA_15.GetN() > 0:
    CMS.cmsObjectDraw(gr_WA_15, "L",
                      LineColor=CMS.p6.kBlue, LineWidth=2, LineStyle=7)
if gr_WA_near.GetN() > 0:
    CMS.cmsObjectDraw(gr_WA_near, "L",
                      LineColor=CMS.p6.kYellow, LineWidth=2, LineStyle=7)
if gr_WA_threshold.GetN() > 0:
    CMS.cmsObjectDraw(gr_WA_threshold, "L",
                      LineColor=CMS.p6.kRed, LineWidth=2, LineStyle=7)

# Fermionic channels (solid)
CMS.cmsObjectDraw(gr_taunu, "L",
                  LineColor=CMS.p6.kGrape, LineWidth=2, LineStyle=1)
CMS.cmsObjectDraw(gr_cs, "L",
                  LineColor=CMS.p6.kGray, LineWidth=2, LineStyle=1)
CMS.cmsObjectDraw(gr_tb, "L",
                  LineColor=CMS.p6.kViolet, LineWidth=2, LineStyle=1)

# Legend
lg = CMS.cmsLeg(0.17, 0.65, 0.60, 0.87, textSize=0.035)
CMS.addToLegend(lg, (gr_WA_15, "H^{+} #rightarrow W^{+}A, m_{A}=15 GeV", "l"))
CMS.addToLegend(lg, (gr_WA_near, "H^{+} #rightarrow W^{+}A, m_{A}=m_{H^{+}}#minus30 GeV", "l"))
CMS.addToLegend(lg, (gr_WA_threshold, "H^{+} #rightarrow W^{+}A, m_{A}=m_{H^{+}}#minusm_{W}", "l"))
CMS.addToLegend(lg, (gr_taunu, "H^{+} #rightarrow #tau#nu", "l"))
CMS.addToLegend(lg, (gr_cs, "H^{+} #rightarrow c#bar{s}", "l"))
CMS.addToLegend(lg, (gr_tb, "H^{+} #rightarrow t#bar{b}", "l"))
lg.Draw()

c1.RedrawAxis()

outdir = f"outputs/plots/type{args.type}"
os.makedirs(outdir, exist_ok=True)
c1.SaveAs(f"{outdir}/HcDecay_tanb{args.tanb}.png")

# ---------------------------------------------------------------------------
# A decay BR plot: BR vs mA at fixed mHc=160, log scale
# ---------------------------------------------------------------------------
fixed_mHc = 160
a_rows = [r for r in rows if int(r["mHc"]) == fixed_mHc and isvalid(r)
          and r["gam_A_tot"] > 0]

if a_rows:
    gr_A_bb = ROOT.TGraph()
    gr_A_tautau = ROOT.TGraph()
    gr_A_cc = ROOT.TGraph()
    gr_A_gg = ROOT.TGraph()

    for r in sorted(a_rows, key=lambda x: x["mA"]):
        mA = r["mA"]
        tot = r["gam_A_tot"]
        gr_A_bb.SetPoint(gr_A_bb.GetN(), mA, r["gam_A_bb"] / tot)
        gr_A_tautau.SetPoint(gr_A_tautau.GetN(), mA, r["gam_A_tautau"] / tot)
        gr_A_cc.SetPoint(gr_A_cc.GetN(), mA, r["gam_A_cc"] / tot)
        gr_A_gg.SetPoint(gr_A_gg.GetN(), mA, r["gam_A_gg"] / tot)

    CMS.SetExtraText("Simulation Preliminary")
    CMS.SetEnergy(0, unit="")
    CMS.SetLumi(None, run=f"tan#beta = {args.tanb} ({TYPE_LABEL[args.type]})")

    c2 = CMS.cmsCanvas("c_A", 10, 155, 1e-3, 1e2,
                        "m_{A} [GeV]",
                        "BR(A #rightarrow X)",
                        square=True, iPos=0, extraSpace=0.)
    c2.SetLogy()

    CMS.cmsObjectDraw(gr_A_bb, "L",
                      LineColor=CMS.p6.kBlue, LineWidth=2, LineStyle=1)
    CMS.cmsObjectDraw(gr_A_tautau, "L",
                      LineColor=CMS.p6.kRed, LineWidth=2, LineStyle=1)
    CMS.cmsObjectDraw(gr_A_cc, "L",
                      LineColor=CMS.p6.kYellow, LineWidth=2, LineStyle=1)
    CMS.cmsObjectDraw(gr_A_gg, "L",
                      LineColor=CMS.p6.kGray, LineWidth=2, LineStyle=1)

    lg2 = CMS.cmsLeg(0.17, 0.65, 0.60, 0.87, textSize=0.035)
    CMS.addToLegend(lg2, (gr_A_bb, f"A #rightarrow b#bar{{b}}, m_{{H^{{+}}}} = {fixed_mHc} GeV", "l"))
    CMS.addToLegend(lg2, (gr_A_tautau, "A #rightarrow #tau^{+}#tau^{-} (#mu^{+}#mu^{-} #times 3#times10^{2})", "l"))
    CMS.addToLegend(lg2, (gr_A_cc, "A #rightarrow c#bar{c}", "l"))
    CMS.addToLegend(lg2, (gr_A_gg, "A #rightarrow gg", "l"))
    lg2.Draw()

    c2.RedrawAxis()

    c2.SaveAs(f"{outdir}/ADecay_tanb{args.tanb}_mHc{fixed_mHc}.png")
