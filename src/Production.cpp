#include <iostream>
#include <fstream>
#include <cstring>
#include <vector>
#include <omp.h>
#include "Constraints.h"
#include "DecayTable.h"
#include "SM.h"
#include "THDM.h"
using namespace std;

void write_lha(SM &sm, const double mHc, const double mA, const unsigned int yukawa_type, const double tanb);

int main(int argc, char *argv[]) {
    // Reference SM Higgs mass for EW precision observables
    unsigned int yukawa_type;
    double tanb;
    if (argc == 3) {
        yukawa_type = stoi(argv[1]);
        tanb = stod(argv[2]);
    }
    else {
        cerr << "Usage: " << argv[0] << " <yukawa_type> <tanb>" << endl;
        exit(EXIT_FAILURE);
    }
    cout << "@@@@ Running 2HDMC with yukawa_type = " << yukawa_type << " and tanb = " << tanb << endl;
    
    // Create SM and set parameters
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

    #pragma omp parallel for collapse(2)
    for (int iHc = 70; iHc <= 160; iHc++) {
        for (int iA = 15; iA <= iHc-5; iA++) {
            double mHc = iHc;
            double mA = iA;
            write_lha(sm, mHc, mA, yukawa_type, tanb);
        }
    }

    return 0;
}

void write_lha(SM &sm, const double mHc, const double mA, const unsigned int yukawa_type, const double tanb) {
    // Create 2HDM and set SM parameters
    THDM model;
    model.set_SM(sm);

    // Set 2HDM parameters in the physical basis
    const double mh = 125.;
    const double mH = 500.;

    const double sin_beta_m_alpha = 0.999; // alignment limit
    const double lambda_6 = 0.;
    const double lambda_7 = 0.;
    const double m12_2 = mA*mA*(tanb / (1+tanb*tanb));

    bool pset = model.set_param_phys(mh, mH, mA, mHc, sin_beta_m_alpha, lambda_6, lambda_7, m12_2, tanb);
    if (!pset) return;
    model.set_yukawas_type(yukawa_type);
    model.print_param_gen();

    // Prepare to calculate the observables
    Constraints constraints(model);
    double S, T, U, V, W, X;
    const double mh_ref = 125.;
    constraints.oblique_param(mh_ref, S, T, U, V, W, X);

    cout << "[Constraints] Potential stability: " << (constraints.check_stability() ? "OK": "Not OK") << endl;
    cout << "[Constraints] Tree-level unitarity: " << (constraints.check_unitarity() ? "OK": "Not OK") << endl;
    cout << "[Constraints] Perturbativity: " << (constraints.check_perturbativity() ? "OK": "Not OK") << endl;

    // Prepare to calculate decay width
    DecayTable table(model);

    // Print total widths of Higgs bosons
    table.print_width(1);
    table.print_width(2);
    table.print_width(3);
    table.print_width(4);

    table.print_decays(1);
    table.print_decays(2);
    table.print_decays(3);
    table.print_decays(4);

    // Write output to LesHouches file
    string filePath = "outputs/type"+to_string(yukawa_type)+"/output.tanb" + to_string(int(tanb)) + "." + to_string(int(mHc)) + "." + to_string(int(mA)) + ".lha";
    char c_filePath[filePath.length()+1];
    strcpy(c_filePath, filePath.c_str());

    model.write_LesHouches(c_filePath, 1, 0, 1, nullptr);
}



