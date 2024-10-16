import os, argparse
import pyslha
import numpy as np
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("--type", required=True, type=str, help="Yukawa type")
parser.add_argument("--tanb", required=True, type=str, help="tan beta")
parser.add_argument("--mHc", required=True, type=int, help="mass of charged Higgs")
args = parser.parse_args()


# change MA and see how Hc -> WA branching ratio changes
mAarr = np.arange(15, args.mHc-4)
graphs_wa = ROOT.TGraph()
graphs_taunu = ROOT.TGraph()
graphs_tb = ROOT.TGraph()
graphs_cs = ROOT.TGraph()
graphs_others = ROOT.TGraph()
for mA in mAarr:
    d = pyslha.read(f"type{args.type}/output.tanb{args.tanb}.{args.mHc}.{mA}.lha")
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
graphs_wa.GetXaxis().SetTitle("M_{A}")

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

c.SaveAs(f"plots/type{args.type}/tanb{args.tanb}.mHc{args.mHc}.Hcdecay.png")

# change MA and see how A -> mumu branching ratio changes
mAarr = np.arange(15, args.mHc-4)
graphs_bb = ROOT.TGraph()
graphs_cc = ROOT.TGraph()
graphs_ss = ROOT.TGraph()
graphs_gg = ROOT.TGraph()
graphs_tautau = ROOT.TGraph()
graphs_mumu = ROOT.TGraph()
graphs_others = ROOT.TGraph()

for mA in mAarr:
    d = pyslha.read(f"type{args.type}/output.tanb{args.tanb}.{args.mHc}.{mA}.lha")
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
graphs_bb.GetXaxis().SetTitle("M_{A}")

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
c.SaveAs(f"plots/type{args.type}/tanb{args.tanb}.mHc{args.mHc}.Adecay.png")