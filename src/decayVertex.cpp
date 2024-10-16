#include <iostream>
#include <fstream>
#include <cstring>
#include "Constraints.h"
#include "DecayTable.h"
#include "HBHS.h"
#include "SM.h"
#include "THDM.h"

using namespace std;

int main(int argc, char *argv[]) {
    // Reference SM Higggs mass for EW precision observables
    const double mh_ref = 125.;

    unsigned int yukawa_type;
    double mC, tan_beta;
    if (argc < 4) {
        cerr << "Insufficient command-line arguments provided" << endl;
        exit(EXIT_FAILURE);
    }
    else {
        yukawa_type = stoi(argv[1]);
        mC = stod(argv[2]);
        tan_beta = stod(argv[3]);
    }
    cout << "@@@@ Running 2HDMC with..." << endl;
    cout << "@@@@ Yukawa Type: " << yukawa_type << endl;
    cout << "@@@@ mC: " << mC << endl;
    cout << "@@@@ tan_beta: " << tan_beta << endl;
    cout << "@@@@ Start running..." << endl;


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

    // Create 2HDM and set SM parameters
    THDM model;
    model.set_SM(sm);

    // Set parameters of the 2HDM in the "physical" basis [GeV]
    const double mh = 125.;
    const double mH = 3000.;
    //const double mA = 85.;
    //const double mC = 70.;
    const double sin_beta_m_alpha = 0.999;
    const double lambda_6 = 0.;
    const double lambda_7 = 0.;
    const double m12_2 = 40000.;
    //const double tan_beta = 50.;

    double mA;
    for (mA = 15.; mA <= mC-5.; mA += 1) {
        bool pset = model.set_param_phys(mh, mH, mA, mC, sin_beta_m_alpha, lambda_6, lambda_7, m12_2, tan_beta);
        if (!pset) {
            cerr << "The specified parameters are not valid" << endl;
            exit(EXIT_FAILURE);
        }

        // Set Yukawa couplings to type II
        model.set_yukawas_type(yukawa_type);

        model.print_param_gen();
        // Prepare to calculate the observables
        Constraints constraints(model);

        double S, T, U, V, W, X;
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
        string filePath = "outputs/type"+to_string(yukawa_type)+"/output.tanb" + to_string(int(tan_beta)) + "." + to_string(int(mC)) + "." + to_string(int(mA)) + ".lha";
        char c_filePath[filePath.length()+1];
        strcpy(c_filePath, filePath.c_str());

        // prepare hbhs results
        //const HBHSResult *p_hbhsres = nullptr;
        //HBHS hbhs{};

        //const HBHSResult hbhs_result = hbhs.check(model);
        //hbhs_result.hb.print();
        //hbhs_result.hs.print();
        //p_hbhsres = &hbhs_result;

        model.write_LesHouches(c_filePath, 1, 0, 1, nullptr);
    }

    return 0;
}
