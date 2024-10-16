import os, argparse
import pyslha
import numpy as np
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("--type", required=True, type=str, help="Yukawa type")
parser.add_argument("--tanb", required=True, type=str, help="tan beta")
parser.add_argument("--mHc", required=True, type=int, help="mass of charged Higgs")
args = parser.parse_args()

# change mA values and see how Hc -> WA branching ratio changes
mAarr = np.arange(15, args.mHc, 5)
graphs_wa = ROOT.TGraph()
graphs_taunu = ROOT.TGraph()
graphs_tb = ROOT.TGraph()
graphs_cs = ROOT.TGraph()
graphs_others = ROOT.TGraph()
for mA in mAarr:
    d = pyslha.read(f"outputs/type{args.type}/output.tanb{args.tanb}.{args.mHc}.{mA}.lha")
    hc = d.decays[37]
    # get WA decay rate
    br_other = 0.
    for decay in hc.decays:
        if decay.ids == [24, 36]:
            graphs_wa.AddPoint(mA, decay.br)
        elif decay.ids == [-15, 16]:
            graphs_taunu.AddPoint(mA, decay.br)
        elif decay.ids == [6, -5]:
            graphs_tb.AddPoint(mA, decay.br)
        elif decay.ids == [4, -3]:
            graphs_cs.AddPoint(mA, decay.br)
        else:
            br_other += decay.br
    graphs_others.AddPoint(mA, br_other)

graphs_wa.SetTitle("H^{+} decay mode (M(H^{+})"+ f"= {args.mHc} GeV)")
graphs_wa.GetXaxis().SetRangeUser(15, args.mHc-5)
graphs_wa.GetXaxis().SetTitle("M_{A} [GeV]")

graphs_wa.GetYaxis().SetRangeUser(0., 1.)
graphs_wa.GetYaxis().SetTitle("Branching Ratio")
graphs_wa.GetYaxis().SetTitleOffset(1.3)

graphs_wa.SetLineColor(ROOT.kBlack); graphs_wa.SetLineWidth(2)
graphs_taunu.SetLineColor(ROOT.kGreen); graphs_taunu.SetLineWidth(2)
graphs_tb.SetLineColor(ROOT.kBlue); graphs_tb.SetLineWidth(2)
graphs_cs.SetLineColor(ROOT.kRed); graphs_cs.SetLineWidth(2)
graphs_others.SetLineColor(ROOT.kGray); graphs_others.SetLineWidth(2)

lg = ROOT.TLegend(0.2, 0.5, 0.5, 0.75)
lg.SetFillStyle(0)
lg.SetBorderSize(0)
lg.AddEntry(graphs_wa, "H^{+} #rightarrow W^{+}A", "l")
lg.AddEntry(graphs_taunu, "H^{+} #rightarrow #bar{#tau}#nu", "l")
lg.AddEntry(graphs_tb, "H^{+} #rightarrow t#bar{b}", "l")
lg.AddEntry(graphs_cs, "H^{+} #rightarrow c#bar{s}", "l")
lg.AddEntry(graphs_others, "H^{+} #rightarrow others", "l")

c = ROOT.TCanvas("c", f"MHc {args.mHc} GeV", 800, 800)
c.cd()
graphs_wa.Draw()
graphs_taunu.Draw("same")
graphs_tb.Draw("same")
graphs_cs.Draw("same")
graphs_others.Draw("same")
lg.Draw("same")
c.RedrawAxis()

c.SaveAs(f"outputs/plots/type{args.type}/HcDecay.tanb{args.tanb}.mHc{args.mHc}.png")
