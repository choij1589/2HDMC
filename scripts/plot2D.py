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
parser = argparse.ArgumentParser(description="2D color map plots for B_sig and sigma_sig")
parser.add_argument("--type", required=True, type=int, help="Yukawa type (1-4)")
parser.add_argument("--tanb", required=True, type=int, help="tan beta (1-10)")
args = parser.parse_args()

TYPE_LABEL = {1: "Type-I", 2: "Type-II", 3: "Type-X", 4: "Type-Y"}

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SIGMA_TTBAR_13 = 833.9e3    # fb, NNLO+NNLL at 13 TeV
SIGMA_TTBAR_13p6 = 923.6e3  # fb, NNLO+NNLL at 13.6 TeV

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
# Fill TH2D for B_sig
# ---------------------------------------------------------------------------
# Grid: mHc 80-160 (step 1) → 81 bins, mA 10-155 (step 1) → 146 bins
# Bin edges shifted by 0.5 so bin centers land on integer mass values
h_bsig = ROOT.TH2D("h_bsig", "",
                    81, 79.5, 160.5,
                    146, 9.5, 155.5)

min_nonzero_bsig = float("inf")

for r in rows:
    if not isvalid(r):
        continue
    if r["gam_t_tot"] <= 0 or r["gam_Hc_tot"] <= 0 or r["gam_A_tot"] <= 0:
        continue

    br_t_Hcb = r["gam_t_Hcb"] / r["gam_t_tot"]
    br_Hc_WA = r["gam_Hc_WA"] / r["gam_Hc_tot"]
    br_A_mumu = r["gam_A_mumu"] / r["gam_A_tot"]

    bsig = br_t_Hcb * br_Hc_WA * br_A_mumu

    if bsig <= 0:
        continue

    mHc = int(r["mHc"])
    mA = int(r["mA"])
    ix = h_bsig.GetXaxis().FindBin(mHc)
    iy = h_bsig.GetYaxis().FindBin(mA)
    h_bsig.SetBinContent(ix, iy, bsig)

    if bsig < min_nonzero_bsig:
        min_nonzero_bsig = bsig

if min_nonzero_bsig == float("inf"):
    print(f"WARNING: no valid B_sig points for type={args.type} tanb={args.tanb}")
    min_nonzero_bsig = 1e-20

# Set z-axis range: floor at 0.1× minimum nonzero, ceiling at maximum
z_max_bsig = h_bsig.GetMaximum()
z_min_bsig = min_nonzero_bsig * 0.1
h_bsig.SetMinimum(z_min_bsig)
h_bsig.SetMaximum(z_max_bsig)

outdir = f"outputs/plots/type{args.type}"
os.makedirs(outdir, exist_ok=True)

# ---------------------------------------------------------------------------
# Draw B_sig plot
# ---------------------------------------------------------------------------
CMS.SetCMSPalette()
CMS.SetExtraText("Simulation Preliminary")
CMS.SetEnergy(0, unit="")
CMS.SetLumi(None, run=f"tan#beta = {args.tanb} ({TYPE_LABEL[args.type]})")

c1 = CMS.cmsCanvas("c_bsig", 80, 160, 10, 155,
                    "m_{H^{+}} [GeV]",
                    "m_{A} [GeV]",
                    square=True, iPos=11, with_z_axis=True,
                    scaleLumi=0.9)
c1.SetLogz()

h_bsig.Draw("COLZSAME")
c1.Update()
CMS.UpdatePalettePosition(h_bsig, c1)
c1.RedrawAxis()

c1.SaveAs(f"{outdir}/Bsig_tanb{args.tanb}.png")

# ---------------------------------------------------------------------------
# Draw sigma_sig plots (13 TeV and 13.6 TeV)
# ---------------------------------------------------------------------------
for energy, sigma_tt, suffix in [
    (13, SIGMA_TTBAR_13, "13TeV"),
    (13.6, SIGMA_TTBAR_13p6, "13p6TeV"),
]:
    h_xsec = h_bsig.Clone(f"h_xsec_{suffix}")
    h_xsec.Scale(2 * sigma_tt)

    z_min_xsec = z_min_bsig * 2 * sigma_tt
    z_max_xsec = z_max_bsig * 2 * sigma_tt
    h_xsec.SetMinimum(z_min_xsec)
    h_xsec.SetMaximum(z_max_xsec)

    CMS.SetCMSPalette()
    CMS.SetExtraText("Simulation Preliminary")
    CMS.SetEnergy(energy)
    CMS.SetLumi(None, run=f"tan#beta = {args.tanb} ({TYPE_LABEL[args.type]})")

    cx = CMS.cmsCanvas(f"c_xsec_{suffix}", 80, 160, 10, 155,
                       "m_{H^{+}} [GeV]",
                       "m_{A} [GeV]",
                       square=True, iPos=11, with_z_axis=True,
                       scaleLumi=0.9)
    cx.SetLogz()

    h_xsec.Draw("COLZSAME")
    cx.Update()
    CMS.UpdatePalettePosition(h_xsec, cx)
    cx.RedrawAxis()

    cx.SaveAs(f"{outdir}/Xsec_{suffix}_tanb{args.tanb}.png")
