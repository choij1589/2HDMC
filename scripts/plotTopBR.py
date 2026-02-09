import argparse
import csv
import math
import os
from array import array

import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)
CMS.setCMSStyle()

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Plot BR(t -> H+b) vs mHc for multiple tanb")
parser.add_argument("--type", required=True, type=int, help="Yukawa type (1-4)")
args = parser.parse_args()

TYPE_LABEL = {1: "Type-I", 2: "Type-II", 3: "Type-X", 4: "Type-Y"}

TANB_1D = [1, 2, 3, 4, 5]
COLORS = [CMS.p6.kBlue, CMS.p6.kRed, CMS.p6.kGrape, CMS.p6.kYellow, CMS.p6.kViolet]
TANB_ALL = list(range(1, 11))

# ---------------------------------------------------------------------------
# Load CSV data for all tanb values
# ---------------------------------------------------------------------------
def load_csv(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            d = {}
            for k, v in r.items():
                try:
                    d[k] = float(v)
                except ValueError:
                    d[k] = float("nan")
            rows.append(d)
    return rows


def get_br_per_mHc(rows):
    """For each mHc, pick first valid row (any mA) and compute BR(t->H+b)."""
    mHc_vals = sorted(set(int(r["mHc"]) for r in rows))
    result = {}
    for mHc in mHc_vals:
        subset = [r for r in rows if int(r["mHc"]) == mHc
                  and not math.isnan(r["gam_t_tot"]) and r["gam_t_tot"] > 0]
        if not subset:
            continue
        ref = subset[0]
        result[mHc] = ref["gam_t_Hcb"] / ref["gam_t_tot"]
    return result


# Load data for all tanb
br_data = {}  # tanb -> {mHc: BR}
for tanb in TANB_ALL:
    csvpath = f"outputs/scan_type{args.type}_tanb{tanb}.csv"
    if not os.path.exists(csvpath):
        print(f"SKIP: {csvpath} not found")
        continue
    rows = load_csv(csvpath)
    br_map = get_br_per_mHc(rows)
    if br_map:
        br_data[tanb] = br_map

outdir = f"outputs/plots/type{args.type}"
os.makedirs(outdir, exist_ok=True)

# ---------------------------------------------------------------------------
# 1D plot: BR(t -> H+b) vs mHc for selected tanb
# ---------------------------------------------------------------------------
graphs = {}
for tanb in TANB_1D:
    if tanb not in br_data:
        continue
    gr = ROOT.TGraph()
    for mHc in sorted(br_data[tanb]):
        gr.SetPoint(gr.GetN(), mHc, br_data[tanb][mHc])
    if gr.GetN() > 0:
        graphs[tanb] = gr

CMS.SetExtraText("Simulation Preliminary")
CMS.SetEnergy(0, unit="")
CMS.SetLumi(None, run=f"{TYPE_LABEL[args.type]}")

all_y = []
for gr in graphs.values():
    for i in range(gr.GetN()):
        all_y.append(gr.GetPointY(i))

ymin = min(all_y) * 0.5
ymax = 1e1

c = CMS.cmsCanvas("c_TopBR", 80, 160, ymin, ymax,
                   "m_{H^{+}} [GeV]",
                   "BR(t #rightarrow H^{+}b)",
                   square=True, iPos=0, extraSpace=0.)
c.SetLogy()

for tanb, color in zip(TANB_1D, COLORS):
    if tanb not in graphs:
        continue
    CMS.cmsObjectDraw(graphs[tanb], "L",
                      LineColor=color, LineWidth=2, LineStyle=1)

lg = CMS.cmsLeg(0.65, 0.65, 0.92, 0.87, textSize=0.035)
for tanb, color in zip(TANB_1D, COLORS):
    if tanb not in graphs:
        continue
    CMS.addToLegend(lg, (graphs[tanb], f"tan#beta = {tanb}", "l"))
lg.Draw()

c.RedrawAxis()
c.SaveAs(f"{outdir}/TopBR.png")

# ---------------------------------------------------------------------------
# 2D plot: BR(t -> H+b) color map with R_b exclusion contour
# ---------------------------------------------------------------------------
# TH2D: x = mHc (80-160), y = tanb (1-10)
h2 = ROOT.TH2D("h_topbr2d", "",
                81, 79.5, 160.5,
                10, 0.5, 10.5)

min_nonzero = float("inf")
for tanb in TANB_ALL:
    if tanb not in br_data:
        continue
    for mHc, br in br_data[tanb].items():
        if br <= 0:
            continue
        ix = h2.GetXaxis().FindBin(mHc)
        iy = h2.GetYaxis().FindBin(tanb)
        h2.SetBinContent(ix, iy, br)
        if br < min_nonzero:
            min_nonzero = br

if min_nonzero == float("inf"):
    print("WARNING: no valid BR points for 2D plot")
    min_nonzero = 1e-20

h2.SetMinimum(min_nonzero * 0.1)
h2.SetMaximum(h2.GetMaximum())

# Draw color map
CMS.SetCMSPalette()
CMS.SetExtraText("Simulation Preliminary")
CMS.SetEnergy(0, unit="")
CMS.SetLumi(None, run=f"{TYPE_LABEL[args.type]}")

c2 = CMS.cmsCanvas("c_TopBR2D", 80, 160, 1, 10,
                    "m_{H^{+}} [GeV]",
                    "tan#beta",
                    square=True, iPos=0, with_z_axis=True)
c2.SetLogz()

h2.Draw("COLZSAME")
c2.Update()
CMS.UpdatePalettePosition(h2, c2)

# Exclusion contour: R_b > 0.955 => BR(t->H+b) < 0.045
h2_cont = h2.Clone("h_topbr2d_cont")
h2_cont.SetContour(1, array('d', [0.045]))
h2_cont.SetLineColor(ROOT.kBlack)
h2_cont.SetLineWidth(2)
h2_cont.SetLineStyle(1)
h2_cont.Draw("CONT3SAME")

lg2 = CMS.cmsLeg(0.42, 0.82, 0.82, 0.88, textSize=0.035)
lg2.AddEntry(h2_cont, "R_{b} > 0.955 (95% CL)", "l")
lg2.Draw()

c2.Update()
c2.RedrawAxis()
c2.Modified()
c2.Update()
c2.SaveAs(f"{outdir}/TopBR2D.png")
