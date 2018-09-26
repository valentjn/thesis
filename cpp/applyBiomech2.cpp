#include <iostream>
#include <iomanip>

#include <sgpp_base.hpp>
#include <sgpp_optimization.hpp>

#include <biomech2_interface/MetaHeader.hpp>

namespace bm2i = biomech2_interface;

enum class Action {
  EvaluateForces,
  EvaluateEquilibriumElbowAngle,
  SolveScenarioA,
  SolveScenarioB,
  SolveScenarioBComparison,
};

enum class GridType {
  FullGrid,
  SparseGrid,
};

typedef biomech2_interface::SparseGrid::Type BasisType;

void parseArgs(int argc, const char* argv[],
               Action& action, GridType& gridType, BasisType& basisType,
               size_t& p, double& forceLoad);

void evaluateForces(sgpp::optimization::VectorFunction& intpTB);
void evaluateEquilibriumElbowAngle(
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient,
    double forceLoad);
void solveScenarioA(
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient);
void solveScenarioB(
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient);
void solveScenarioBComparison(
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient);

inline void writeNumber(double x);
void writeVector(const sgpp::base::DataVector& xx);
void readMatrix(sgpp::base::DataMatrix& XX);
void writeMatrix(const sgpp::base::DataMatrix& XX);

void printOptimizationResultHeader();
void printOptimizationResults(
    size_t time,
    std::string point,
    double alphaT,
    double alphaB,
    double thetaTilde,
    double theta,
    double M,
    size_t numberOfNewtonCalls,
    size_t numberOfNewtonIterations,
    double runtimeSeconds);
double evaluateMomentum(
    sgpp::optimization::VectorFunction& TB,
    double F,
    const sgpp::base::DataVector& alpha,
    double theta);
sgpp::base::DataVector minimizeActivation(
    size_t time,
    double F,
    double targetTheta,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient);
sgpp::base::DataVector minimizeDistance(
    size_t time,
    double alphaTOld,
    double alphaBOld,
    double F,
    double targetTheta,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient);
sgpp::base::DataVector minimizeDistanceRelaxed(
    size_t time,
    double alphaTOld,
    double alphaBOld,
    double targetThetaOld,
    double F,
    double c,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient);

int main(int argc, const char* argv[]) {
  std::cerr << "applyBiomech2 program started.\n\n";
  sgpp::optimization::Printer::getInstance().setStream(&std::cerr);
  sgpp::optimization::Printer::getInstance().setVerbosity(-1);

  // arguments with default values
  Action action = Action::EvaluateForces;
  GridType gridType = GridType::FullGrid;
  BasisType basisType = BasisType::ModifiedNotAKnotBSpline;
  size_t p = 3;
  double forceLoad = 22.0;

  // other parameters
  const size_t n = 4;
  const bool adaptive = false;
  const double surplusThresPercentT = 0.01;
  const double surplusThresPercentB = 0.01;

  // parse arguments
  parseArgs(argc, argv, action, gridType, basisType, p, forceLoad);

  // full grid interpolants
  bm2i::interpolation::TBFullGridInterpolant fgIntpTB;
  bm2i::interpolation::TBFullGridInterpolantGradient fgIntpTBGradient;
  sgpp::optimization::ComponentScalarFunction
      fgIntpT(fgIntpTB, 0, {NAN, NAN, 0.0});
  sgpp::optimization::ComponentScalarFunction
      fgIntpB(fgIntpTB, 1, {NAN, 0.0, NAN});

  // current interpolants (may be full grid or sparse grid)
  std::unique_ptr<sgpp::optimization::VectorFunction> intpTB;
  std::unique_ptr<sgpp::optimization::VectorFunctionGradient> intpTBGradient;
  std::unique_ptr<sgpp::optimization::ScalarFunction> intpT;
  std::unique_ptr<sgpp::optimization::ScalarFunction> intpB;

  std::unique_ptr<bm2i::SparseGrid> sparseGrid;

  if (gridType == GridType::FullGrid) {
    // use full grid interpolant
    fgIntpTB.clone(intpTB);
    fgIntpTBGradient.clone(intpTBGradient);
    fgIntpT.clone(intpT);
    fgIntpB.clone(intpB);
  } else {
    // use sparse grid interpolant
    sparseGrid.reset(new bm2i::SparseGrid(basisType, p, n, adaptive));
    sparseGrid->create();
    sparseGrid->load(sparseGrid->isClenshawCurtis() ?
                     "data/biomech2/sgRegular4ClenshawCurtis.dat" :
                     "data/biomech2/sgRegular4Uniform.dat");
    sparseGrid->hierarchize();

    if (sparseGrid->isAdaptive()) {
      sparseGrid->coarsen(surplusThresPercentT, surplusThresPercentB);
    }

    intpTB.reset(
        new bm2i::interpolation::TBSparseGridInterpolant(
            *sparseGrid->sgppGrid, sparseGrid->alpha));
    intpTBGradient.reset(
        new bm2i::interpolation::TBSparseGridInterpolantGradient(
            *sparseGrid->sgppGrid, sparseGrid->alpha));
    intpT.reset(new sgpp::optimization::ComponentScalarFunction(
        *intpTB, 0, {NAN, NAN, 0.0}));
    intpB.reset(new sgpp::optimization::ComponentScalarFunction(
        *intpTB, 1, {NAN, 0.0, NAN}));
  }

  // execute action
  if (action == Action::EvaluateForces) {
    evaluateForces(*intpTB);
  } else if (action == Action::EvaluateEquilibriumElbowAngle) {
    evaluateEquilibriumElbowAngle(*intpTB, *intpTBGradient, forceLoad);
  } else if (action == Action::SolveScenarioA) {
    solveScenarioA(fgIntpTB, fgIntpTBGradient, *intpTB, *intpTBGradient);
  } else if (action == Action::SolveScenarioB) {
    solveScenarioB(fgIntpTB, fgIntpTBGradient, *intpTB, *intpTBGradient);
  } else if (action == Action::SolveScenarioBComparison) {
    solveScenarioBComparison(
        fgIntpTB, fgIntpTBGradient, *intpTB, *intpTBGradient);
  } else {
    throw std::invalid_argument("Invalid action.");
  }

  std::cerr << "\napplyBiomech2 program terminated.\n";

  return 0;
}

void parseArgs(int argc, const char* argv[],
               Action& action, GridType& gridType, BasisType& basisType,
               size_t& p, double& forceLoad) {
  for (size_t i = 1; i < static_cast<size_t>(argc); i++) {
    std::string arg(argv[i]);

    if (arg.find("action=") == 0) {
      arg = arg.substr(7, std::string::npos);

      if (arg == "evaluateForces") {
        action = Action::EvaluateForces;
      } else if (arg == "evaluateEquilibriumElbowAngle") {
        action = Action::EvaluateEquilibriumElbowAngle;
      } else if (arg == "solveScenarioA") {
        action = Action::SolveScenarioA;
      } else if (arg == "solveScenarioB") {
        action = Action::SolveScenarioB;
      } else if (arg == "solveScenarioBComparison") {
        action = Action::SolveScenarioBComparison;
      } else {
        throw std::invalid_argument("Invalid action.");
      }
    } else if (arg.find("gridType=") == 0) {
      arg = arg.substr(9, std::string::npos);

      if (arg == "fullGrid") {
        gridType = GridType::FullGrid;
      } else if (arg == "sparseGrid") {
        gridType = GridType::SparseGrid;
      } else {
        throw std::invalid_argument("Invalid grid type.");
      }
    } else if (arg.find("basisType=") == 0) {
      arg = arg.substr(10, std::string::npos);

      if (arg == "modifiedBSpline") {
        basisType = BasisType::ModifiedBSpline;
      } else if (arg == "modifiedNotAKnotBSpline") {
        basisType = BasisType::ModifiedNotAKnotBSpline;
      } else if (arg == "modifiedClenshawCurtisBSpline") {
        basisType = BasisType::ModifiedClenshawCurtisBSpline;
      } else {
        throw std::invalid_argument("Invalid basis type.");
      }
    } else if (arg.find("p=") == 0) {
      arg = arg.substr(2, std::string::npos);
      p = std::stoi(arg);

      if (p < 1) {
        throw std::invalid_argument("Invalid degree (must be positive).");
      } else if (p % 2 == 0) {
        throw std::invalid_argument("Invalid degree (must be odd).");
      }
    } else if (arg.find("forceLoad=") == 0) {
      arg = arg.substr(10, std::string::npos);
      forceLoad = std::stod(arg);
    } else {
      throw std::invalid_argument("Invalid argument.");
    }
  }
}



void evaluateForces(sgpp::optimization::VectorFunction& intpTB) {
  sgpp::base::DataMatrix XX;
  readMatrix(XX);
  const size_t NN = XX.getNrows();
  const size_t d = XX.getNcols();

  if (d != 2) {
    throw std::runtime_error("Invalid dimensionality.");
  }

  sgpp::base::DataMatrix XX2(NN, 3);

  for (size_t j = 0; j < NN; j++) {
    for (size_t t = 0; t < 3; t++) {
      XX2(j, t) = XX(j, ((t < 2) ? t : 1));
    }
  }

  const size_t m = intpTB.getNumberOfComponents();
  sgpp::base::DataMatrix YY(NN, m);
  intpTB.eval(XX2, YY);
  writeMatrix(YY);
  std::cout << "\n";
}

void evaluateEquilibriumElbowAngle(
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient,
    double forceLoad) {
  sgpp::base::DataMatrix XX;
  readMatrix(XX);
  const size_t NN = XX.getNrows();
  const size_t d = XX.getNcols();

  if (d != 2) {
    throw std::runtime_error("Invalid dimensionality.");
  }

  bm2i::momentum::MomentumBalanceTheta momentumBalanceTheta(
      forceLoad, intpTB, intpTBGradient);
  sgpp::base::DataVector yy(NN);
  momentumBalanceTheta.eval(XX, yy);
  writeVector(yy);
  std::cout << "\n";
}

void solveScenarioA(
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient) {

  std::cout << "[\n  []";
  const double FRef = 22.0;

  // optimization 1
  const double F1 = FRef;
  const double targetTheta1 = 75.0;

  const sgpp::base::DataVector xOpt1(minimizeActivation(
      1, F1, targetTheta1,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));

  // optimization 2
  const double alphaTOld2 = xOpt1[0];
  const double alphaBOld2 = xOpt1[1];
  const double F2 = F1;
  const double targetTheta2 = 60.0;

  const sgpp::base::DataVector xOpt2(minimizeDistance(
      2, alphaTOld2, alphaBOld2, F2, targetTheta2,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));

  // optimization with relaxed minimal distance
  /*const double alphaTOld3 = xOpt2[0];
  const double alphaBOld3 = xOpt2[1];
  const double targetThetaOld3 = targetTheta2;
  const double F3 = 40.0;
  const double c3 = 1e-3;

  const sgpp::base::DataVector xOpt3(minimizeDistanceRelaxed(
      alphaTOld3, alphaBOld3, targetThetaOld3, F3, c3,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));*/

  // optimization 3
  const double alphaTOld3 = xOpt2[0];
  const double alphaBOld3 = xOpt2[1];
  const double F3 = 40.0;
  const double targetTheta3 = targetTheta2;

  const sgpp::base::DataVector xOpt3(minimizeDistance(
      3, alphaTOld3, alphaBOld3, F3, targetTheta3,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));

  // optimization 4
  const double alphaTOld4 = xOpt3[0];
  const double alphaBOld4 = xOpt3[1];
  const double F4 = 100.0;
  const double targetTheta4 = 30.0;

  const sgpp::base::DataVector xOpt4(minimizeDistance(
      4, alphaTOld4, alphaBOld4, F4, targetTheta4,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));

  std::cout << "\n]\n";
}

void solveScenarioB(
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient) {

  std::cout << "[\n  []";
  const double FRef = 22.0;
  sgpp::base::DataMatrix scenario2Alphas(0, 2);
  sgpp::base::DataMatrix scenario2Thetas(0, 2);
  sgpp::base::DataVector scenario2Theta(2);

  // optimization 1
  const double F1 = FRef;
  const double targetTheta1 = 25.0;
  size_t time = 1;

  const sgpp::base::DataVector xOpt1(minimizeActivation(
      time, F1, targetTheta1,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));
  scenario2Alphas.appendRow(xOpt1);
  time++;

  {
    bm2i::momentum::MomentumBalanceTheta momentumBalanceTheta(
        F1, intpTB, intpTBGradient);
    bm2i::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
        F1, fgIntpTB, fgIntpTBGradient);
    scenario2Theta[0] = momentumBalanceTheta.eval(xOpt1);
    scenario2Theta[1] = fgIntpMomentumBalanceTheta.eval(xOpt1);
  }
  scenario2Thetas.appendRow(scenario2Theta);

  // optimization 2
  const double targetThetaOld2 = targetTheta1;
  sgpp::base::DataVector xOpt2(xOpt1);

  for (double F2 : {40.0, 100.0, 150.0, 170.0}) {
    for (double c2 : {0.01, 0.03, 0.03, 0.05, 0.2}) {
      const double alphaTOld2 = xOpt2[0];
      const double alphaBOld2 = xOpt2[1];

      xOpt2 = minimizeDistanceRelaxed(
          time, alphaTOld2, alphaBOld2, targetThetaOld2, F2, c2,
          fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient);
      scenario2Alphas.appendRow(xOpt2);
      time++;

      {
        bm2i::momentum::MomentumBalanceTheta momentumBalanceTheta(
            F2, intpTB, intpTBGradient);
        bm2i::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
            F2, fgIntpTB, fgIntpTBGradient);
        scenario2Theta[0] = momentumBalanceTheta.eval(xOpt2);
        scenario2Theta[1] = fgIntpMomentumBalanceTheta.eval(xOpt2);
      }
      scenario2Thetas.appendRow(scenario2Theta);
    }
  }

  std::cout << "\n]\n";
}

void solveScenarioBComparison(
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient) {

  std::cout << "[\n  []";
  const double FRef = 22.0;
  const double scenario2targetTheta = 25.0;
  const std::vector<double> scenario2Loads =
      {FRef, 40.0, 100.0, 150.0, 170.0};
  sgpp::base::DataMatrix scenario2ComparisonPoints(0, 2);

  // optimization 1
  size_t time = 1;

  sgpp::base::DataVector xOpt(minimizeActivation(
      time, scenario2Loads[0], scenario2targetTheta,
      fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient));
  scenario2ComparisonPoints.appendRow(xOpt);
  time++;

  // optimization 2
  for (size_t i = 1; i < scenario2Loads.size(); i++) {
    xOpt = minimizeDistance(
        time, xOpt[0], xOpt[1], scenario2Loads[i], scenario2targetTheta,
        fgIntpTB, fgIntpTBGradient, intpTB, intpTBGradient);
    scenario2ComparisonPoints.appendRow(xOpt);
    time++;
  }

  std::cout << "\n]\n";
}



inline void writeNumber(double x) {
  if (std::isinf(x)) {
    if (x < 0) {
      std::cout << "-Infinity";
    } else {
      std::cout << "Infinity";
    }
  } else if (std::isnan(x)) {
    std::cout << "NaN";
  } else {
    std::cout << std::scientific << std::setprecision(17) << x;
  }
}

void writeVector(const sgpp::base::DataVector& xx) {
  const size_t NN = xx.getSize();

  std::cout << "[";

  for (size_t j = 0; j < NN; j++) {
    if (j > 0) std::cout << ", ";
    writeNumber(xx[j]);
  }

  std::cout << "]";
}

void readMatrix(sgpp::base::DataMatrix& XX) {
  size_t NN;
  size_t d;
  std::cin >> NN >> d;

  XX.resize(NN, d);

  for (size_t j = 0; j < NN; j++) {
    for (size_t t = 0; t < d; t++) {
      std::cin >> XX(j, t);
    }
  }
}

void writeMatrix(const sgpp::base::DataMatrix& XX) {
  const size_t NN = XX.getNrows();
  const size_t d = XX.getNcols();

  std::cout << "[";

  for (size_t j = 0; j < NN; j++) {
    if (j > 0) std::cout << ", ";
    std::cout << "[";

    for (size_t t = 0; t < d; t++) {
      if (t > 0) std::cout << ", ";
      writeNumber(XX(j, t));
    }

    std::cout << "]";
  }

  std::cout << "]";
}



void printOptimizationResultHeader() {
  const std::vector<size_t> colWidths = {
    7, 7, 14, 14, 14, 14, 14, 9, 9, 9,
  };
  std::cerr << std::setw(colWidths[0])     << std::left << "t";
  std::cerr << std::setw(colWidths[1])     << std::left << "Point";
  std::cerr << std::setw(colWidths[2] + 1) << std::left << "α_T";
  std::cerr << std::setw(colWidths[3] + 1) << std::left << "α_B";
  std::cerr << std::setw(colWidths[4] + 2) << std::left << "θ~ [°]";
  std::cerr << std::setw(colWidths[5] + 2) << std::left << "θ [°]";
  std::cerr << std::setw(colWidths[6])     << std::left << "M";
  std::cerr << std::setw(colWidths[7])     << std::left << "#Newton";
  std::cerr << std::setw(colWidths[8])     << std::left << "#N. It.";
  std::cerr << std::setw(colWidths[9])     << std::left << "Runtime [ms]";
  std::cerr << "\n";
}

void printOptimizationResults(
    size_t time,
    std::string point,
    double alphaT,
    double alphaB,
    double thetaTilde,
    double theta,
    double M,
    size_t numberOfNewtonCalls,
    size_t numberOfNewtonIterations,
    double runtimeSeconds) {

  const std::vector<size_t> colWidths = {
    7, 7, 14, 14, 14, 14, 14, 9, 9, 14,
  };

  std::cerr << std::scientific << std::setprecision(4);
  std::cerr << std::setw(colWidths[0]) << std::left
            << time;
  std::cerr << std::setw(colWidths[1]) << std::left
            << point;
  std::cerr << std::setw(colWidths[2]) << std::left
            << alphaT;
  std::cerr << std::setw(colWidths[3]) << std::left
            << alphaB;
  std::cerr << std::setw(colWidths[4]) << std::left
            << thetaTilde;
  std::cerr << std::setw(colWidths[5]) << std::left
            << theta;
  std::cerr << std::setw(colWidths[6]) << std::left
            << M;
  std::cerr << std::setw(colWidths[7]) << std::left
            << numberOfNewtonCalls;
  std::cerr << std::setw(colWidths[8]) << std::left
            << numberOfNewtonIterations;
  std::cerr << std::setw(colWidths[9]) << std::left
            << static_cast<size_t>(1000 * runtimeSeconds);
  std::cerr << "\n";

  sgpp::base::DataVector output(9);
  output[0] = time;
  output[1] = alphaT;
  output[2] = alphaB;
  output[3] = thetaTilde;
  output[4] = theta;
  output[5] = M;
  output[6] = numberOfNewtonCalls;
  output[7] = numberOfNewtonIterations;
  output[8] = static_cast<size_t>(1000 * runtimeSeconds);

  std::cout << ",\n  ";
  writeVector(output);

  /*latexTable << "$t_{" << std::fixed << std::setprecision(4) << time << "}$";
  latexTable << "&" << std::fixed << std::setprecision(4) << alphaT;
  latexTable << "&" << std::fixed << std::setprecision(4) << alphaB;
  latexTable << "&" << std::fixed << std::setprecision(3) << thetaTilde;
  latexTable << "&" << std::fixed << std::setprecision(3) << theta;
  latexTable << "&" << std::fixed << std::setprecision(3) << M;
  latexTable << "&" << numberOfNewtonCalls;
  latexTable << "&" << numberOfNewtonIterations;
  latexTable << "&" << static_cast<size_t>(1000 * runtimeSeconds);
  latexTable << "\\\\\n";*/
}

double evaluateMomentum(
    sgpp::optimization::VectorFunction& TB,
    double F,
    const sgpp::base::DataVector& alpha,
    double theta) {

  bm2i::momentum::Momentum fgIntpMomentum(F, TB);
  sgpp::base::DataVector x(3);
  x[0] = (theta - bm2i::THETA_MIN) / (bm2i::THETA_MAX - bm2i::THETA_MIN);
  x[1] = alpha[0];
  x[2] = alpha[1];

  return fgIntpMomentum.eval(x);
}

sgpp::base::DataVector minimizeActivation(
    size_t time,
    double F,
    double targetTheta,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient) {

  const size_t maxItCount = 10000;
  sgpp::base::SGppStopwatch timer;

  std::cerr << "Minimizing activation with F = " << std::to_string(F)
            << "N, θ* = " << std::to_string(targetTheta) << "°\n";
  printOptimizationResultHeader();

  bm2i::momentum::MomentumBalanceTheta momentumBalanceTheta(
      F, intpTB, intpTBGradient);
  bm2i::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
      F, fgIntpTB, fgIntpTBGradient);
  bm2i::momentum::MomentumGradient momentumGradient(
      F, intpTBGradient);
  bm2i::momentum::MomentumBalanceThetaGradient
      momentumBalanceThetaGradient(
          momentumBalanceTheta, momentumGradient);

  bm2i::objectives::activation_sum::ActivationSumObjective
      activationSumObjective;
  bm2i::objectives::activation_sum::ActivationSumObjectiveGradient
      activationSumObjectiveGradient;
  bm2i::constraints::MomentumBalanceConstraint
      momentumBalanceConstraint(
          momentumBalanceTheta, targetTheta);
  bm2i::constraints::MomentumBalanceConstraintGradient
      momentumBalanceConstraintGradient(
          momentumBalanceThetaGradient, targetTheta);

  sgpp::optimization::optimizer::AugmentedLagrangian activationMinimizer(
      activationSumObjective,
      activationSumObjectiveGradient,
      sgpp::optimization::EmptyVectorFunction::getInstance(),
      sgpp::optimization::EmptyVectorFunctionGradient::getInstance(),
      momentumBalanceConstraint,
      momentumBalanceConstraintGradient,
      maxItCount);
  std::cerr << "Finding a feasible starting point (α_{T,0}, α_{B,0}) with "
            << "θ(α_{T,0}, α_{B,0}) = θ*...\n";

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  timer.start();
  const sgpp::base::DataVector x0(activationMinimizer.findFeasiblePoint());

  printOptimizationResults(
      time - 1,
      "x0",
      x0[0],
      x0[1],
      momentumBalanceTheta.eval(x0),
      fgIntpMomentumBalanceTheta.eval(x0),
      std::abs(evaluateMomentum(fgIntpTB, F, x0, momentumBalanceTheta.eval(x0))),
      momentumBalanceTheta.getNumberOfNewtonCalls(),
      momentumBalanceTheta.getNumberOfNewtonIterations(),
      timer.stop());

  /*std::cerr << "Result: (α_{T,0}, α_{B,0}) = " << x0.toString() << " "
            << "with θ(α_{T,0}, α_{B,0}) = "
            << momentumBalanceTheta.eval(x0) << "° "
            << "(and θ_real(α_{T,0}, α_{B,0}) = "
            << fgIntpMomentumBalanceTheta.eval(x0) << "°)\n";
  std::cerr << "Optimizing...\n";*/

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  activationMinimizer.setStartingPoint(x0);
  activationMinimizer.setPenaltyStartValue(30.0);
  //activationMinimizer.setPenaltyIncreaseFactor(2.0);
  timer.start();
  activationMinimizer.optimize();

  const sgpp::base::DataVector xOpt = activationMinimizer.getOptimalPoint();
  //const double fOpt = activationMinimizer.getOptimalValue();

  /*std::cerr << "Result: (α_{T,*}, α_{B,*}) = " << xOpt.toString() << " with "
            << "α_{T,*} + α_{B,*} = " << std::to_string(fOpt) << " and "
            << "θ(α_{T,*}, α_{B,*}) = "
            << momentumBalanceTheta.eval(xOpt) << "° "
            << "(and θ_real(α_{T,*}, α_{B,*}) = "
            << fgIntpMomentumBalanceTheta.eval(xOpt) << "°)\n";*/
  printOptimizationResults(
      time,
      "xOpt",
      xOpt[0],
      xOpt[1],
      momentumBalanceTheta.eval(xOpt),
      fgIntpMomentumBalanceTheta.eval(xOpt),
      std::abs(evaluateMomentum(fgIntpTB, F, xOpt, momentumBalanceTheta.eval(xOpt))),
      momentumBalanceTheta.getNumberOfNewtonCalls(),
      momentumBalanceTheta.getNumberOfNewtonIterations(),
      timer.stop());
  std::cerr << "\n";
  sgpp::optimization::Printer::getInstance().setVerbosity(-1);

  return xOpt;
}

sgpp::base::DataVector minimizeDistance(
    size_t time,
    double alphaTOld,
    double alphaBOld,
    double F,
    double targetTheta,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient) {

  const size_t maxItCount = 10000;
  sgpp::base::SGppStopwatch timer;

  std::cerr << "Minimizing distance with F_{new} = " << std::to_string(F)
            << "N, θ*_{new} = " << std::to_string(targetTheta)
            << "°, alpha_{T,old} = " << alphaTOld
            << ", alpha_{B,old} = " << alphaBOld << "\n";
  printOptimizationResultHeader();

  bm2i::momentum::MomentumBalanceTheta momentumBalanceTheta(
      F, intpTB, intpTBGradient);
  bm2i::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
      F, fgIntpTB, fgIntpTBGradient);
  bm2i::momentum::MomentumGradient momentumGradient(
      F, intpTBGradient);
  bm2i::momentum::MomentumBalanceThetaGradient
      momentumBalanceThetaGradient(
          momentumBalanceTheta, momentumGradient);

  bm2i::objectives::distance::DistanceObjective
      distanceObjective(alphaTOld, alphaBOld);
  bm2i::objectives::distance::DistanceObjectiveGradient
      distanceObjectiveGradient(alphaTOld, alphaBOld);
  bm2i::constraints::MomentumBalanceConstraint
      momentumBalanceConstraint(
          momentumBalanceTheta, targetTheta);
  bm2i::constraints::MomentumBalanceConstraintGradient
      momentumBalanceConstraintGradient(
          momentumBalanceThetaGradient, targetTheta);

  sgpp::optimization::optimizer::AugmentedLagrangian distanceMinimizer(
      distanceObjective,
      distanceObjectiveGradient,
      sgpp::optimization::EmptyVectorFunction::getInstance(),
      sgpp::optimization::EmptyVectorFunctionGradient::getInstance(),
      momentumBalanceConstraint,
      momentumBalanceConstraintGradient,
      maxItCount);

  /*std::cerr << "Finding a feasible starting point (α_{T,0}, α_{B,0}) with "
            << "θ(α_{T,0}, α_{B,0}) = θ*...\n";*/

  /*momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  sgpp::base::DataVector x0(distanceMinimizer.findFeasiblePoint());

  printOptimizationResults(
      time,
      "x0",
      x0[0],
      x0[1],
      distanceMinimizationObjective.eval(x0),
      momentumBalanceTheta.eval(x0),
      fgIntpMomentumBalanceTheta.eval(x0),
      std::abs(evaluateMomentum(fgIntpTB, F, x0, momentumBalanceTheta.eval(x0))),
      momentumBalanceTheta.getNumberOfNewtonCalls(),
      momentumBalanceTheta.getNumberOfNewtonIterations());*/

  /*std::cerr << "Result: (α_{T,0}, α_{B,0}) = " << x0.toString() << " "
            << "with θ(α_{T,0}, α_{B,0}) = "
            << momentumBalanceTheta.eval(x0) << "° "
            << "(and θ_real(α_{T,0}, α_{B,0}) = "
            << fgIntpMomentumBalanceTheta.eval(x0) << "°)\n";
  std::cerr << "Optimizing...\n";*/

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  //distanceMinimizer.setStartingPoint(x0);
  distanceMinimizer.setPenaltyStartValue(1e-3);
  //distanceMinimizer.setPenaltyIncreaseFactor(1.5);
  timer.start();
  distanceMinimizer.optimize();

  //sgpp::optimization::operator<<(std::cerr, distanceMinimizer.getHistoryOfInnerIterations()) << "\n";
  //std::cerr << distanceMinimizer.getHistoryOfOptimalPoints().toString() << "\n";

  const sgpp::base::DataVector xOpt(distanceMinimizer.getOptimalPoint());
  //const double fOpt = distanceMinimizer.getOptimalValue();

  /*std::cerr << "Result: (α_{T,new}, α_{B,new}) = " << xOpt.toString() << " with "
            << "distance^2 = " << std::to_string(fOpt) << " and "
            << "θ(α_{T,new}, α_{B,new}) = "
            << momentumBalanceTheta.eval(xOpt) << "° "
            << "(and θ_real(α_{T,new}, α_{B,new}) = "
            << fgIntpMomentumBalanceTheta.eval(xOpt) << "°)\n";*/
  printOptimizationResults(
      time,
      "xOpt",
      xOpt[0],
      xOpt[1],
      momentumBalanceTheta.eval(xOpt),
      fgIntpMomentumBalanceTheta.eval(xOpt),
      std::abs(evaluateMomentum(fgIntpTB, F, xOpt, momentumBalanceTheta.eval(xOpt))),
      momentumBalanceTheta.getNumberOfNewtonCalls(),
      momentumBalanceTheta.getNumberOfNewtonIterations(),
      timer.stop());
  std::cerr << "\n";
  sgpp::optimization::Printer::getInstance().setVerbosity(-1);

  return xOpt;
}

sgpp::base::DataVector minimizeDistanceRelaxed(
    size_t time,
    double alphaTOld,
    double alphaBOld,
    double targetThetaOld,
    double F,
    double c,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient) {

  const size_t maxItCount = 10000;
  sgpp::base::SGppStopwatch timer;

  std::cerr << "Minimizing relaxed distance with F_{new} = "
            << std::to_string(F)
            << "N, θ*_{old} = " << std::to_string(targetThetaOld)
            << "°, c = " << std::to_string(c)
            << ", alpha_{T,old} = " << alphaTOld
            << ", alpha_{B,old} = " << alphaBOld << "\n";
  printOptimizationResultHeader();

  bm2i::momentum::MomentumBalanceTheta momentumBalanceTheta(
      F, intpTB, intpTBGradient);
  bm2i::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
      F, fgIntpTB, fgIntpTBGradient);
  bm2i::momentum::MomentumGradient momentumGradient(
      F, intpTBGradient);
  bm2i::momentum::MomentumBalanceThetaGradient
      momentumBalanceThetaGradient(
          momentumBalanceTheta, momentumGradient);

  bm2i::objectives::distance_relaxed::DistanceRelaxedObjective
      distanceRelaxedObjective(
          momentumBalanceTheta,
          alphaTOld,
          alphaBOld,
          targetThetaOld,
          c);
  bm2i::objectives::distance_relaxed::DistanceRelaxedObjectiveGradient
      distanceRelaxedObjectiveGradient(
          momentumBalanceThetaGradient,
          alphaTOld,
          alphaBOld,
          targetThetaOld,
          c);

  sgpp::optimization::optimizer::AdaptiveGradientDescent
      relaxedDistanceMinimizer(
          distanceRelaxedObjective,
          distanceRelaxedObjectiveGradient,
          maxItCount);

  //std::cerr << "Optimizing...\n";

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  //relaxedDistanceMinimizer3.setStartingPoint(x0);
  timer.start();
  relaxedDistanceMinimizer.optimize();

  const sgpp::base::DataVector xOpt(relaxedDistanceMinimizer.getOptimalPoint());
  //const double fOpt = relaxedDistanceMinimizer.getOptimalValue();

  /*std::cerr << "Result: (α_{T,new}, α_{B,new}) = " << xOpt.toString() << " with "
            << "relaxed distance^2 = " << std::to_string(fOpt) << " and "
            << "θ(α_{T,new}, α_{B,new}) = "
            << momentumBalanceTheta.eval(xOpt) << "° "
            << "(and θ_real(α_{T,new}, α_{B,new}) = "
            << fgIntpMomentumBalanceTheta.eval(xOpt) << "°)\n";*/
  printOptimizationResults(
      time,
      "xOpt",
      xOpt[0],
      xOpt[1],
      momentumBalanceTheta.eval(xOpt),
      fgIntpMomentumBalanceTheta.eval(xOpt),
      std::abs(evaluateMomentum(fgIntpTB, F, xOpt, momentumBalanceTheta.eval(xOpt))),
      momentumBalanceTheta.getNumberOfNewtonCalls(),
      momentumBalanceTheta.getNumberOfNewtonIterations(),
      timer.stop());
  std::cerr << "\n";
  sgpp::optimization::Printer::getInstance().setVerbosity(-1);

  return xOpt;
}
