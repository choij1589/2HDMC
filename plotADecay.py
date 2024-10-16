import os, argparse
import pyslha
import numpy as np
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("--type", required=True, type=str, help="Yukawa type")
parser.add_argument("--tanb", required=True, type=str, help="tan beta")
parser.add_argument("--mHc", required=True, type=int, help="mass of charged Higgs")
args = parser.parse_args()

# change MA and see how A -> mumu branching ratio changes
mAarr = np.arange(15, args.mHc-4, 5)
graphs_bb = ROOT.TGraph()
graphs_cc = ROOT.TGraph()
graphs_ss = ROOT.TGraph()
graphs_gg = ROOT.TGraph()
graphs_tautau = ROOT.TGraph()
graphs_mumu = ROOT.TGraph()
graphs_others = ROOT.TGraph()

for mA in mAarr:
    d = pyslha.read(f"outputs/type{args.type}/output.tanb{args.tanb}.{args.mHc}.{mA}.lha")
    A = d.decays[36]
    br_others = 0.
    for decay in A.decays:
        if decay.ids == [5, -5]:
            graphs_bb.AddPoint(mA, decay.br)
        elif decay.ids == [4, -4]:
            graphs_cc.AddPoint(mA, decay.br)
        #elif decay.ids == [3, -3]:
        #    graphs_ss.AddPoint(mA, decay.br)
        elif decay.ids == [21, 21]:
            graphs_gg.AddPoint(mA, decay.br)
        elif decay.ids == [15, -15]:
            graphs_tautau.AddPoint(mA, decay.br)
        elif decay.ids == [13, -13]:
            graphs_mumu.AddPoint(mA, decay.br)
        else:
            br_others += decay.br
    graphs_others.AddPoint(mA, br_others)

graphs_bb.SetTitle("A decay mode (M(H^{+}) = "+f"{args.mHc} GeV)")
graphs_bb.GetXaxis().SetRangeUser(15., args.mHc-5.)
graphs_bb.GetXaxis().SetTitle("M_{A} [GeV]")

graphs_bb.GetYaxis().SetRangeUser(1e-4, 10)
graphs_bb.GetYaxis().SetTitle("Branching Ratio")
graphs_bb.GetYaxis().SetTitleOffset(1.3)

graphs_bb.SetLineColor(ROOT.kViolet); graphs_bb.SetLineWidth(2)
graphs_tautau.SetLineColor(ROOT.kGreen); graphs_tautau.SetLineWidth(2)
graphs_mumu.SetLineColor(ROOT.kBlack); graphs_mumu.SetLineWidth(2)
graphs_gg.SetLineColor(ROOT.kBlue); graphs_gg.SetLineWidth(2)
graphs_cc.SetLineColor(ROOT.kRed); graphs_cc.SetLineWidth(2)
graphs_others.SetLineColor(ROOT.kGray); graphs_others.SetLineWidth(2)

lg = ROOT.TLegend(0.6, 0.25, 0.9, 0.45)
lg.SetFillStyle(0)
lg.SetBorderSize(0)
lg.AddEntry(graphs_bb, "A #rightarrow #bar{b}b", "l")
lg.AddEntry(graphs_tautau, "A #rightarrow #tau^{+}#tau^{-}", "l")
lg.AddEntry(graphs_mumu, "A #rightarrow #mu^{+}#mu^{-}", "l")
lg.AddEntry(graphs_gg, "A #rightarrow gg", "l")
lg.AddEntry(graphs_cc, "A #rightarrow c#bar{c}", "l")
lg.AddEntry(graphs_others, "A #rightarrow others", "l")

c = ROOT.TCanvas("c", f"MHc {args.mHc} GeV", 800, 800)
c.cd()
c.SetLogy()
graphs_bb.Draw()
graphs_tautau.Draw("same")
graphs_mumu.Draw("same")
graphs_gg.Draw("same")
graphs_cc.Draw("same")
graphs_others.Draw("same")
lg.Draw("same")
c.RedrawAxis()
c.Draw()
c.SaveAs(f"outputs/plots/type{args.type}/Adecay.tanb{args.tanb}.mHc{args.mHc} .png")
