#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include "Constraints.h"
#include "DecayTable.h"
#include "SM.h"
#include "THDM.h"

using namespace std;

int main(int argc, char *argv[]) {
    if (argc < 3) {
        cerr << "Usage: ./ScanBR <type> <tanb> [mH]" << endl;
        return EXIT_FAILURE;
    }

    const unsigned int yukawa_type = stoi(argv[1]);
    const double tanb = stod(argv[2]);
    const double mH = (argc >= 4) ? stod(argv[3]) : 500.;

    // Fixed parameters
    const double mh = 125.;
    const double sba = 0.999;
    const double lambda_6 = 0.;
    const double lambda_7 = 0.;

    // SM setup (same as existing code)
    SM sm;
    sm.set_qmass_pole(6, 172.5);
    sm.set_qmass_pole(5, 4.75);
    sm.set_qmass_pole(4, 1.42);
    sm.set_lmass_pole(3, 1.77684);
    sm.set_alpha(1. / 127.934);
    sm.set_alpha0(1. / 137.0359997);
    sm.set_alpha_s(0.119);
    sm.set_MZ(91.15349);
    sm.set_MW(80.36951);
    sm.set_gamma_Z(2.49581);
    sm.set_gamma_W(2.08856);
    sm.set_GF(1.16637E-5);

    // Output file
    string outdir = "outputs";
    string outpath = outdir + "/scan_type" + to_string(yukawa_type)
                     + "_tanb" + to_string(int(tanb)) + ".csv";
    ofstream fout(outpath);
    if (!fout.is_open()) {
        cerr << "Cannot open " << outpath << endl;
        return EXIT_FAILURE;
    }

    // CSV header
    fout << "type,tanb,mHc,mA,stable,unitary,perturb,"
         << "gam_t_Hcb,gam_t_tot,"
         << "gam_Hc_WA,gam_Hc_taunu,gam_Hc_cs,gam_Hc_tb,gam_Hc_tot,"
         << "gam_A_bb,gam_A_tautau,gam_A_mumu,gam_A_cc,gam_A_gg,gam_A_tot"
         << endl;

    fout << scientific << setprecision(8);

    // 2D scan: mHc = 80..160, mA = 10..155
    for (int imHc = 80; imHc <= 160; imHc++) {
        double mC = static_cast<double>(imHc);
        for (int imA = 10; imA <= 155; imA++) {
            double mA = static_cast<double>(imA);

            // m12^2: MSSM-like Z2 soft-breaking
            double m12_2 = mA * mA * tanb / (1. + tanb * tanb);

            // Create model per point (DecayTable caches internally)
            THDM model;
            model.set_SM(sm);
            bool pset = model.set_param_phys(mh, mH, mA, mC, sba,
                                             lambda_6, lambda_7, m12_2, tanb);

            fout << yukawa_type << "," << int(tanb) << ","
                 << imHc << "," << imA << ",";

            if (!pset) {
                // Invalid parameter point
                fout << "0,0,0,"
                     << "nan,nan,nan,nan,nan,nan,nan,"
                     << "nan,nan,nan,nan,nan,nan" << endl;
                continue;
            }

            model.set_yukawas_type(yukawa_type);

            // Theory constraints
            Constraints constraints(model);
            bool stable = constraints.check_stability();
            bool unitary = constraints.check_unitarity();
            bool perturb = constraints.check_perturbativity();

            fout << stable << "," << unitary << "," << perturb << ",";

            // Compute widths regardless of constraint flags
            DecayTable table(model);

            // Top decays
            double gam_t_Hcb = table.get_gamma_uhd(3, 4, 3);
            double gam_t_tot = table.get_gammatot_top();

            // H+ decays
            double gam_Hc_WA    = table.get_gamma_hvh(4, 3, 3);
            double gam_Hc_taunu = table.get_gamma_hln(4, 3, 3);
            double gam_Hc_cs    = table.get_gamma_hdu(4, 2, 2);
            double gam_Hc_tb    = table.get_gamma_hdu(4, 3, 3);
            double gam_Hc_tot   = table.get_gammatot_h(4);

            // A decays
            double gam_A_bb     = table.get_gamma_hdd(3, 3, 3);
            double gam_A_tautau = table.get_gamma_hll(3, 3, 3);
            double gam_A_mumu   = table.get_gamma_hll(3, 2, 2);
            double gam_A_cc     = table.get_gamma_huu(3, 2, 2);
            double gam_A_gg     = table.get_gamma_hgg(3);
            double gam_A_tot    = table.get_gammatot_h(3);

            fout << gam_t_Hcb << "," << gam_t_tot << ","
                 << gam_Hc_WA << "," << gam_Hc_taunu << ","
                 << gam_Hc_cs << "," << gam_Hc_tb << "," << gam_Hc_tot << ","
                 << gam_A_bb << "," << gam_A_tautau << ","
                 << gam_A_mumu << "," << gam_A_cc << ","
                 << gam_A_gg << "," << gam_A_tot << endl;
        }
    }

    fout.close();
    cerr << "Wrote " << outpath << endl;
    return 0;
}
