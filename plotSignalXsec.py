import os, argparse
import pyslha
import numpy as np
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("--type", required=True, type=str, help="Yukawa Type")
parser.add_argument("--tanb", required=True, type=str, help="tanb")
args = parser.parse_args()

## top pair production cross section
## ref: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO
sigma = 833.9 * 1000 # fb

def get_br_top(mHc, mA):
    d = pyslha.read(f"outputs/type{args.type}/output.tanb{args.tanb}.{mHc}.{mA}.lha")
    top = d.decays[6]
    for decay in top.decays:
        if decay.ids == [37, 5]:
            return decay.br
        else:
            continue
    raise ValueError("No decay found")

def get_br_Hc(mHc, mA):
    d = pyslha.read(f"outputs/type{args.type}/output.tanb{args.tanb}.{mHc}.{mA}.lha")
    Hc = d.decays[37]
    for decay in Hc.decays:
        if decay.ids == [24, 36]:
            return decay.br
        else:
            continue
    raise ValueError("No decay found")

def get_br_A(mHc, mA):
    d = pyslha.read(f"outputs/type{args.type}/output.tanb{args.tanb}.{mHc}.{mA}.lha")
    A = d.decays[36]
    for decay in A.decays:
        if decay.ids == [13, -13]:
            return decay.br
        else:
            continue
    raise ValueError("No decay found")

def main():
    h = ROOT.TH2D("h", f"[2HDM - TYPE {args.type}] tanb = {args.tanb}", 91, 70-0.5, 160+0.5, 141, 15-0.5, 155+0.5)
    print("# mHc, mA, xsec")
    for mHc in range(70, 161):
        for mA in range(15, mHc-4):
            br_top = get_br_top(mHc, mA)
            br_Hc = get_br_Hc(mHc, mA)
            br_A = get_br_A(mHc, mA)
            xsec = sigma * br_top * br_Hc * br_A * 2 # charge conjugate
            print(f"{mHc}, {mA}, {xsec}")
            h.Fill(mHc, mA, xsec)
    
    h.SetStats(0)
    h.GetXaxis().SetTitle("m_{H^{#pm}} [GeV]")
    h.GetYaxis().SetTitle("m_{A} [GeV]")
    h.GetZaxis().SetTitle("[fb]")

    info = ROOT.TLatex()
    info.SetTextSize(0.035)
    info.SetTextFont(42)
    logo = ROOT.TLatex()
    logo.SetTextSize(0.04)
    logo.SetTextFont(61)
    extra_logo = ROOT.TLatex()
    extra_logo.SetTextSize(0.035)
    extra_logo.SetTextFont(52)

    c = ROOT.TCanvas("c", "", 1000, 900)
    # Set Margins
    c.SetRightMargin(0.15)
    c.SetLeftMargin(0.12)
    c.cd()
    h.Draw("colz")
    info.DrawLatexNDC(0.75, 0.91, "(13TeV)")
    logo.DrawLatexNDC(0.12, 0.91, "CMS")
    extra_logo.DrawLatexNDC(0.2, 0.91, "Simulation")
    c.RedrawAxis()
    c.SaveAs(f"outputs/type{args.type}/signal.tanb{args.tanb}.png")
    c.SaveAs(f"outputs/type{args.type}/signal.tanb{args.tanb}.pdf")

if __name__ == "__main__":
    main()
