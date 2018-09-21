#include <iostream>
#include <iomanip>

#include <sgpp/optimization/function/scalar/ComponentScalarFunction.hpp>
#include <sgpp/optimization/function/scalar/ComponentScalarFunctionGradient.hpp>
#include <sgpp/optimization/function/scalar/WrapperScalarFunction.hpp>
#include <sgpp/optimization/function/vector/InterpolantVectorFunction.hpp>
#include <sgpp/optimization/function/vector/InterpolantVectorFunctionGradient.hpp>
#include <sgpp/optimization/function/vector/EmptyVectorFunction.hpp>
#include <sgpp/optimization/function/vector/EmptyVectorFunctionGradient.hpp>
#include <sgpp/optimization/optimizer/constrained/AugmentedLagrangian.hpp>
//#include <sgpp/optimization/optimizer/constrained/LogBarrier.hpp>
//#include <sgpp/optimization/optimizer/constrained/SquaredPenalty.hpp>
#include <sgpp/optimization/optimizer/unconstrained/AdaptiveGradientDescent.hpp>
#include <sgpp/optimization/tools/Printer.hpp>

#include <biomech2_interface/Grid.hpp>
#include <biomech2_interface/objectives/activation_sum/ActivationSumObjective.hpp>
#include <biomech2_interface/objectives/activation_sum/ActivationSumObjectiveGradient.hpp>
#include <biomech2_interface/objectives/distance/DistanceObjective.hpp>
#include <biomech2_interface/objectives/distance/DistanceObjectiveGradient.hpp>
#include <biomech2_interface/objectives/distance_relaxed/DistanceRelaxedObjective.hpp>
#include <biomech2_interface/objectives/distance_relaxed/DistanceRelaxedObjectiveGradient.hpp>
#include <biomech2_interface/momentum/MomentumBalanceTheta.hpp>
#include <biomech2_interface/momentum/MomentumBalanceThetaGradient.hpp>
#include <biomech2_interface/momentum/Momentum.hpp>
#include <biomech2_interface/momentum/MomentumGradient.hpp>
#include <biomech2_interface/constraints/MomentumBalanceConstraint.hpp>
#include <biomech2_interface/constraints/MomentumBalanceConstraintGradient.hpp>
#include <biomech2_interface/interpolation/TBFullGridInterpolant.hpp>
#include <biomech2_interface/interpolation/TBFullGridInterpolantGradient.hpp>
#include <biomech2_interface/interpolation/TBSparseGridInterpolant.hpp>
#include <biomech2_interface/interpolation/TBSparseGridInterpolantGradient.hpp>



const size_t MESHGRID_SIZE = 101;
const std::string DATA_PATH = "/home/valentjn/git/collab/muscle/biomech_repo/gfx/data/";

std::stringstream latexTable;



void writeCSV(const sgpp::base::DataVector& vector, const std::string& filename) {
  std::ofstream f(DATA_PATH + filename);
  const size_t n = vector.getSize();

  for (size_t i = 0; i < n; i++) {
    if (i > 0) f << ",";
    f << vector[i];
  }

  f.close();
}

void writeCSV(const sgpp::base::DataMatrix& matrix, const std::string& filename) {
  std::ofstream f(DATA_PATH + filename);
  const size_t n = matrix.getNrows();
  const size_t m = matrix.getNcols();

  for (size_t i = 0; i < n; i++) {
    for (size_t j = 0; j < m; j++) {
      if (j > 0) f << ",";
      f << matrix(i, j);
    }

    f << "\n";
  }

  f.close();
}



void evaluateFunction(
    sgpp::optimization::ScalarFunction& f,
    sgpp::base::DataMatrix& matrix,
    size_t x1Count = MESHGRID_SIZE,
    size_t x2Count = MESHGRID_SIZE) {
  sgpp::base::DataVector x(2);
  matrix.resize(x2Count, x1Count);

  for (size_t i2 = 0; i2 < x2Count; i2++) {
    x[1] = static_cast<double>(i2) /
        static_cast<double>(x2Count - 1);

    for (size_t i1 = 0; i1 < x1Count; i1++) {
      x[0] = static_cast<double>(i1) /
          static_cast<double>(x1Count - 1);

      matrix(i2, i1) = f.eval(x);
    }
  }
}



double evaluateMomentum(sgpp::optimization::VectorFunction& TB,
                        double F, const sgpp::base::DataVector& alpha, double theta) {
  muscle::momentum::Momentum fgIntpMomentum(F, TB);
  sgpp::base::DataVector x(3);
  x[0] = (theta - muscle::THETA_MIN) / (muscle::THETA_MAX - muscle::THETA_MIN);
  x[1] = alpha[0];
  x[2] = alpha[1];

  return fgIntpMomentum.eval(x);
}



void printOptimizationResultHeader() {
  const std::vector<size_t> colWidths = { 7, 7, 14, 14, 14, 14, 14, 9, 9, 9 };
  std::cout << std::setw(colWidths[0])     << std::left << "t";
  std::cout << std::setw(colWidths[1])     << std::left << "Point";
  std::cout << std::setw(colWidths[2] + 1) << std::left << "α_T";
  std::cout << std::setw(colWidths[3] + 1) << std::left << "α_B";
  std::cout << std::setw(colWidths[4] + 2) << std::left << "θ~ [°]";
  std::cout << std::setw(colWidths[5] + 2) << std::left << "θ [°]";
  std::cout << std::setw(colWidths[6])     << std::left << "M";
  std::cout << std::setw(colWidths[7])     << std::left << "#Newton";
  std::cout << std::setw(colWidths[8])     << std::left << "#N. It.";
  std::cout << std::setw(colWidths[9])     << std::left << "Runtime [ms]";
  std::cout << "\n";
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

  const std::vector<size_t> colWidths = { 7, 7, 14, 14, 14, 14, 14, 9, 9, 14 };

  std::cout << std::scientific << std::setprecision(4);
  std::cout << std::setw(colWidths[0]) << std::left << time;
  std::cout << std::setw(colWidths[1]) << std::left << point;
  std::cout << std::setw(colWidths[2]) << std::left << alphaT;
  std::cout << std::setw(colWidths[3]) << std::left << alphaB;
  std::cout << std::setw(colWidths[4]) << std::left << thetaTilde;
  std::cout << std::setw(colWidths[5]) << std::left << theta;
  std::cout << std::setw(colWidths[6]) << std::left << M;
  std::cout << std::setw(colWidths[7]) << std::left << numberOfNewtonCalls;
  std::cout << std::setw(colWidths[8]) << std::left << numberOfNewtonIterations;
  std::cout << std::setw(colWidths[9]) << std::left << static_cast<size_t>(1000 * runtimeSeconds);
  std::cout << "\n";

  latexTable << "$t_{" << std::fixed << std::setprecision(4) << time << "}$";
  latexTable << "&" << std::fixed << std::setprecision(4) << alphaT;
  latexTable << "&" << std::fixed << std::setprecision(4) << alphaB;
  latexTable << "&" << std::fixed << std::setprecision(3) << thetaTilde;
  latexTable << "&" << std::fixed << std::setprecision(3) << theta;
  latexTable << "&" << std::fixed << std::setprecision(3) << M;
  latexTable << "&" << numberOfNewtonCalls;
  latexTable << "&" << numberOfNewtonIterations;
  latexTable << "&" << static_cast<size_t>(1000 * runtimeSeconds);
  latexTable << "\\\\\n";
}



sgpp::base::DataVector minimizeActivation(
    size_t time,
    double F,
    double targetTheta,
    sgpp::optimization::VectorFunction& fgIntpTB,
    sgpp::optimization::VectorFunctionGradient& fgIntpTBGradient,
    sgpp::optimization::VectorFunction& TB,
    sgpp::optimization::VectorFunctionGradient& TBGradient) {

  const size_t maxItCount = 10000;
  sgpp::base::SGppStopwatch timer;

  std::cout << "Minimizing activation with F = " << std::to_string(F)
            << "N, θ* = " << std::to_string(targetTheta) << "°\n";
  printOptimizationResultHeader();

  muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
      F, TB, TBGradient);
  muscle::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
      F, fgIntpTB, fgIntpTBGradient);
  muscle::momentum::MomentumGradient momentumGradient(
      F, TBGradient);
  muscle::momentum::MomentumBalanceThetaGradient
      momentumBalanceThetaGradient(
          momentumBalanceTheta, momentumGradient);

  muscle::objectives::activation_sum::ActivationSumObjective
      activationSumObjective;
  muscle::objectives::activation_sum::ActivationSumObjectiveGradient
      activationSumObjectiveGradient;
  muscle::constraints::MomentumBalanceConstraint
      momentumBalanceConstraint(
          momentumBalanceTheta, targetTheta);
  muscle::constraints::MomentumBalanceConstraintGradient
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
  std::cout << "Finding a feasible starting point (α_{T,0}, α_{B,0}) with "
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

  /*std::cout << "Result: (α_{T,0}, α_{B,0}) = " << x0.toString() << " "
            << "with θ(α_{T,0}, α_{B,0}) = "
            << momentumBalanceTheta.eval(x0) << "° "
            << "(and θ_real(α_{T,0}, α_{B,0}) = "
            << fgIntpMomentumBalanceTheta.eval(x0) << "°)\n";
  std::cout << "Optimizing...\n";*/

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  activationMinimizer.setStartingPoint(x0);
  activationMinimizer.setPenaltyStartValue(30.0);
  //activationMinimizer.setPenaltyIncreaseFactor(2.0);
  timer.start();
  activationMinimizer.optimize();

  const sgpp::base::DataVector xOpt = activationMinimizer.getOptimalPoint();
  //const double fOpt = activationMinimizer.getOptimalValue();

  /*std::cout << "Result: (α_{T,*}, α_{B,*}) = " << xOpt.toString() << " with "
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
  std::cout << "\n";
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
    sgpp::optimization::VectorFunction& TB,
    sgpp::optimization::VectorFunctionGradient& TBGradient) {

  const size_t maxItCount = 10000;
  sgpp::base::SGppStopwatch timer;

  std::cout << "Minimizing distance with F_{new} = " << std::to_string(F)
            << "N, θ*_{new} = " << std::to_string(targetTheta)
            << "°, alpha_{T,old} = " << alphaTOld
            << ", alpha_{B,old} = " << alphaBOld << "\n";
  printOptimizationResultHeader();

  muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
      F, TB, TBGradient);
  muscle::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
      F, fgIntpTB, fgIntpTBGradient);
  muscle::momentum::MomentumGradient momentumGradient(
      F, TBGradient);
  muscle::momentum::MomentumBalanceThetaGradient
      momentumBalanceThetaGradient(
          momentumBalanceTheta, momentumGradient);

  muscle::objectives::distance::DistanceObjective
      distanceObjective(alphaTOld, alphaBOld);
  muscle::objectives::distance::DistanceObjectiveGradient
      distanceObjectiveGradient(alphaTOld, alphaBOld);
  muscle::constraints::MomentumBalanceConstraint
      momentumBalanceConstraint(
          momentumBalanceTheta, targetTheta);
  muscle::constraints::MomentumBalanceConstraintGradient
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

  /*std::cout << "Finding a feasible starting point (α_{T,0}, α_{B,0}) with "
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

  /*std::cout << "Result: (α_{T,0}, α_{B,0}) = " << x0.toString() << " "
            << "with θ(α_{T,0}, α_{B,0}) = "
            << momentumBalanceTheta.eval(x0) << "° "
            << "(and θ_real(α_{T,0}, α_{B,0}) = "
            << fgIntpMomentumBalanceTheta.eval(x0) << "°)\n";
  std::cout << "Optimizing...\n";*/

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  //distanceMinimizer.setStartingPoint(x0);
  distanceMinimizer.setPenaltyStartValue(1e-3);
  //distanceMinimizer.setPenaltyIncreaseFactor(1.5);
  timer.start();
  distanceMinimizer.optimize();

  //sgpp::optimization::operator<<(std::cout, distanceMinimizer.getHistoryOfInnerIterations()) << "\n";
  //std::cout << distanceMinimizer.getHistoryOfOptimalPoints().toString() << "\n";

  const sgpp::base::DataVector xOpt(distanceMinimizer.getOptimalPoint());
  //const double fOpt = distanceMinimizer.getOptimalValue();

  /*std::cout << "Result: (α_{T,new}, α_{B,new}) = " << xOpt.toString() << " with "
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
  std::cout << "\n";
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
    sgpp::optimization::VectorFunction& TB,
    sgpp::optimization::VectorFunctionGradient& TBGradient) {

  const size_t maxItCount = 10000;
  sgpp::base::SGppStopwatch timer;

  std::cout << "Minimizing relaxed distance with F_{new} = "
            << std::to_string(F)
            << "N, θ*_{old} = " << std::to_string(targetThetaOld)
            << "°, c = " << std::to_string(c)
            << ", alpha_{T,old} = " << alphaTOld
            << ", alpha_{B,old} = " << alphaBOld << "\n";
  printOptimizationResultHeader();

  muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
      F, TB, TBGradient);
  muscle::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
      F, fgIntpTB, fgIntpTBGradient);
  muscle::momentum::MomentumGradient momentumGradient(
      F, TBGradient);
  muscle::momentum::MomentumBalanceThetaGradient
      momentumBalanceThetaGradient(
          momentumBalanceTheta, momentumGradient);

  muscle::objectives::distance_relaxed::DistanceRelaxedObjective
      distanceRelaxedObjective(
          momentumBalanceTheta,
          alphaTOld,
          alphaBOld,
          targetThetaOld,
          c);
  muscle::objectives::distance_relaxed::DistanceRelaxedObjectiveGradient
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

  //std::cout << "Optimizing...\n";

  momentumBalanceTheta.resetNumberOfNewtonCalls();
  momentumBalanceTheta.resetNumberOfNewtonIterations();

  //relaxedDistanceMinimizer3.setStartingPoint(x0);
  timer.start();
  relaxedDistanceMinimizer.optimize();

  const sgpp::base::DataVector xOpt(relaxedDistanceMinimizer.getOptimalPoint());
  //const double fOpt = relaxedDistanceMinimizer.getOptimalValue();

  /*std::cout << "Result: (α_{T,new}, α_{B,new}) = " << xOpt.toString() << " with "
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
  std::cout << "\n";
  sgpp::optimization::Printer::getInstance().setVerbosity(-1);

  return xOpt;
}



/*void plotMomentumBalanceTheta(
    sgpp::optimization::VectorFunction& TB,
    sgpp::optimization::VectorFunctionGradient& TBGradient,
    double F,
    std::string title) {

  sgpp::base::DataMatrix YY(0, 0);
  muscle::momentum::MomentumBalanceTheta fgMomentumBalanceTheta(F, TB, TBGradient);
  MatlabRemote::evaluateFunction(fgMomentumBalanceTheta, YY);

  matlabRemote.sendCommand(
MatlabRemote::meshGrid(ALPHA_MIN, ALPHA_MAX, ALPHA_MIN, ALPHA_MAX) + R"(
tmp = load(')" + MatlabRemote::saveMatrix(YY) + R"('); YY = tmp.data;
YY(isinf(YY)) = nan;
figure(); hold('on');
surf(XX1, XX2, YY);
v = )" + std::to_string(THETA_MIN) + ":2.5:" + std::to_string(THETA_MAX) + R"(;
contour3(XX1, XX2, YY, v, 'k-', 'LineWidth', 1.5);
xlabel('$\alpha_\mathrm{T}$', 'Interpreter', 'latex');
ylabel('$\alpha_\mathrm{B}$', 'Interpreter', 'latex');
zlabel('$\tilde{\theta}_F(\alpha_\mathrm{T}, )" +
    R"(\alpha_\mathrm{B})$ [$^{\circ}$]', 'Interpreter', 'latex');
title(')" + title + " Momentum Balance Angle and Isolines for $F = " +
    std::to_string(F) + R"($N');
grid('on'); axis('square'); view(3); rotate3d(); maximize(); pause(0.5);
ha{7} = [ha{7}, gca()];
hf = [hf, gcf()];
)");
}



void program2() {
  //const double targetTheta = 40.0;
  const double FOld = -52.0;
  //const double FNew = 22.00392;

  **const size_t p = 3;
  const size_t l = 4;
  RegularSparseGrid regularSparseGrid(RegularSparseGrid::Type::MODBSPL, p, l);
  regularSparseGrid.create();
  regularSparseGrid.load((regularSparseGrid.type ==
      RegularSparseGrid::MODBSPL) ? "sg_reg4_unif.dat" : "sg_reg4_cc.dat");
  //regularSparseGrid.generateValues(fgIntpTB);
  regularSparseGrid.hierarchize();

  muscle::interpolation::TBSparseGridInterpolant sgIntpTB(
      *regularSparseGrid.sgppGrid, regularSparseGrid.alpha);
  muscle::interpolation::TBSparseGridInterpolantGradient sgIntpTBGradient(
          *regularSparseGrid.sgppGrid, regularSparseGrid.alpha);**

  muscle::interpolation::TBFullGridInterpolant fgIntpTB;
  muscle::interpolation::TBFullGridInterpolantGradient fgIntpTBGradient;
  sgpp::optimization::VectorFunction* TB = &fgIntpTB;
  sgpp::optimization::VectorFunctionGradient* TBGradient = &fgIntpTBGradient;
  const std::string title = "FG";

  plotMomentumBalanceTheta(*TB, *TBGradient, FOld, title);

  **sgpp::base::DataVector xOld(minimizeActivation(
      FOld, targetTheta, fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));
  const double alphaTOld = xOld[0];
  const double alphaBOld = xOld[1];

  plotMomentumBalanceTheta(*TB, *TBGradient, FNew, title);

  std::cout << "\n";
  minimizeDistance(alphaTOld, alphaBOld, FNew, targetTheta,
                   fgIntpTB, fgIntpTBGradient, *TB, *TBGradient);**

  // ------------------------------------------------------------------------
  // Optimization 1
  // ------------------------------------------------------------------------

  const double F = 22.0;
  const double targetTheta = 30.0;

  sgpp::base::DataVector xOpt(minimizeActivation(
      F, targetTheta,
      fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));
  sgpp::base::DataVector xOptStart(xOpt);

  // ------------------------------------------------------------------------
  // Optimization 2
  // ------------------------------------------------------------------------

  const double FNew = 50.0;

  for (double c : {0.0, 1e-3, 1e-2, 1e-1, 1.0}) {
    const double alphaTOld = xOpt[0];
    const double alphaBOld = xOpt[1];

    xOpt = minimizeDistanceRelaxed(
        alphaTOld, alphaBOld, targetTheta, FNew, c,
        fgIntpTB, fgIntpTBGradient, *TB, *TBGradient);
  }

  // ------------------------------------------------------------------------
  // Optimization 3
  // ------------------------------------------------------------------------

  const double alphaTOld = xOptStart[0];
  const double alphaBOld = xOptStart[1];

  xOpt = minimizeDistance(
      alphaTOld, alphaBOld, FNew, targetTheta,
      fgIntpTB, fgIntpTBGradient, *TB, *TBGradient);
}*/



void programGenerateGraphics() {
  // --------------------------------------------------------------------------
  // Initialization
  // --------------------------------------------------------------------------

  const size_t p = 3;
  const size_t l = 4;
  const double surplusThresPercentT = 0.01;
  const double surplusThresPercentB = 0.01;
  const double FRef = 22.0;

  std::vector<std::unique_ptr<Grid>> grids;
  grids.push_back(std::move(std::unique_ptr<Grid>(new FullGrid())));
  grids.push_back(std::move(std::unique_ptr<Grid>(
      new SparseGrid(SparseGrid::Type::MODBSPL, p, l, false))));
  grids.push_back(std::move(std::unique_ptr<Grid>(
      new SparseGrid(SparseGrid::Type::MODBSPL, p, l, true))));
  /*grids.push_back(std::move(std::unique_ptr<Grid>(
      new RegularSparseGrid(RegularSparseGrid::Type::MODBSPLCC, p, l))));*/
  sgpp::base::DataMatrix YY(0, 0);

  muscle::interpolation::TBFullGridInterpolant fgIntpTB;
  muscle::interpolation::TBFullGridInterpolantGradient fgIntpTBGradient;
  sgpp::optimization::ComponentScalarFunction fgIntpT(
      fgIntpTB, 0, {NAN, NAN, 0.0});
  sgpp::optimization::ComponentScalarFunction fgIntpB(
      fgIntpTB, 1, {NAN, 0.0, NAN});

  std::unique_ptr<sgpp::optimization::VectorFunction> sgIntpTB;
  std::unique_ptr<sgpp::optimization::VectorFunctionGradient> sgIntpTBGradient;
  std::unique_ptr<sgpp::optimization::ScalarFunction> sgIntpT;
  std::unique_ptr<sgpp::optimization::ScalarFunction> sgIntpB;

  for (std::unique_ptr<Grid>& grid : grids) {
    // ------------------------------------------------------------------------
    // Creation of Interpolants
    // ------------------------------------------------------------------------

    std::cout << "Grid: " << grid->toString() << "\n";
    std::cout << std::string(80, '-')  << "\n";

    sgpp::optimization::VectorFunction* TB;
    sgpp::optimization::ScalarFunction* T;
    sgpp::optimization::ScalarFunction* B;
    sgpp::optimization::VectorFunctionGradient* TBGradient;

    if (grid->getID() == "fg") {
      TB = &fgIntpTB;
      T = &fgIntpT;
      B = &fgIntpB;
      TBGradient = &fgIntpTBGradient;
    } else {
      SparseGrid& sparseGrid =
          dynamic_cast<SparseGrid&>(*grid.get());
      sparseGrid.create();
      //regularSparseGrid.generateValues(fgIntpTB);
      //regularSparseGrid.hierarchize();
      sparseGrid.load((sparseGrid.type ==
          SparseGrid::MODBSPL) ? "sg_reg4_unif.dat" : "sg_reg4_cc.dat");
      sparseGrid.hierarchize();

      if (sparseGrid.isAdaptive()) {
      	sparseGrid.coarsen(surplusThresPercentT, surplusThresPercentB);
      }

      sgIntpTB.reset(
          new muscle::interpolation::TBSparseGridInterpolant(
              *sparseGrid.sgppGrid, sparseGrid.alpha));
      sgIntpT.reset(new sgpp::optimization::ComponentScalarFunction(
          *sgIntpTB, 0, {NAN, NAN, 0.0}));
      sgIntpB.reset(new sgpp::optimization::ComponentScalarFunction(
          *sgIntpTB, 1, {NAN, 0.0, NAN}));
      sgIntpTBGradient.reset(
          new muscle::interpolation::TBSparseGridInterpolantGradient(
              *sparseGrid.sgppGrid, sparseGrid.alpha));

      TB = sgIntpTB.get();
      T = sgIntpT.get();
      B = sgIntpB.get();
      TBGradient = sgIntpTBGradient.get();

      {
        sgpp::base::DataVector x(2), value(2);
        double l2ErrorT = 0.0;
        double l2ErrorB = 0.0;
        double lInfErrorT = 0.0;
        double lInfErrorB = 0.0;

        for (size_t i = 0; i < sparseGrid.X.getNrows(); i++) {
          sparseGrid.X.getRow(i, x);
          x[0] = (x[0] - muscle::THETA_MIN) / (muscle::THETA_MAX - muscle::THETA_MIN);
          const double errorT = (fgIntpT.eval(x) - sparseGrid.values(i,0)) /
              sparseGrid.values(i,0);
          const double errorB = (fgIntpB.eval(x) - sparseGrid.values(i,1)) /
              sparseGrid.values(i,1);
          //errorT += std::pow(TValue - regularSparseGrid.values(i,0), 2.0);
          //errorB += std::pow(BValue - regularSparseGrid.values(i,1), 2.0);
          l2ErrorT += std::pow(errorT, 2.0);
          l2ErrorB += std::pow(errorB, 2.0);
          lInfErrorT = std::max(errorT, lInfErrorT);
          lInfErrorB = std::max(errorB, lInfErrorB);
        }

        l2ErrorT = std::sqrt(l2ErrorT);
        l2ErrorB = std::sqrt(l2ErrorB);
        std::cout << "l2ErrorT = " << l2ErrorT << "\n";
        std::cout << "l2ErrorB = " << l2ErrorB << "\n\n";
        std::cout << "lInfErrorT = " << lInfErrorT << "\n";
        std::cout << "lInfErrorB = " << lInfErrorB << "\n\n";
      }
    }

    // ------------------------------------------------------------------------
    // Optimization Scenario 1
    // ------------------------------------------------------------------------

    std::cout << "Optimization Scenario 1\n";
    std::cout << std::string(50, '-')  << "\n";
    latexTable.str(std::string());
    latexTable.clear();

    {
      // ----------------------------------------------------------------------
      // Optimization 1
      // ----------------------------------------------------------------------

      const double F1 = FRef;
      const double targetTheta1 = 75.0;

      const sgpp::base::DataVector xOpt1(minimizeActivation(
          1, F1, targetTheta1,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));

      // ----------------------------------------------------------------------
      // Optimization 2
      // ----------------------------------------------------------------------

      const double alphaTOld2 = xOpt1[0];
      const double alphaBOld2 = xOpt1[1];
      const double F2 = F1;
      const double targetTheta2 = 60.0;

      const sgpp::base::DataVector xOpt2(minimizeDistance(
          2, alphaTOld2, alphaBOld2, F2, targetTheta2,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));

      // ----------------------------------------------------------------------
      // Optimization with Relaxed Minimal Distance
      // ----------------------------------------------------------------------

      /*const double alphaTOld3 = xOpt2[0];
      const double alphaBOld3 = xOpt2[1];
      const double targetThetaOld3 = targetTheta2;
      const double F3 = 40.0;
      const double c3 = 1e-3;

      const sgpp::base::DataVector xOpt3(minimizeDistanceRelaxed(
          alphaTOld3, alphaBOld3, targetThetaOld3, F3, c3,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));*/

      // ----------------------------------------------------------------------
      // Optimization 3
      // ----------------------------------------------------------------------

      const double alphaTOld3 = xOpt2[0];
      const double alphaBOld3 = xOpt2[1];
      const double F3 = 40.0;
      const double targetTheta3 = targetTheta2;

      const sgpp::base::DataVector xOpt3(minimizeDistance(
          3, alphaTOld3, alphaBOld3, F3, targetTheta3,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));

      // ----------------------------------------------------------------------
      // Optimization 4
      // ----------------------------------------------------------------------

      const double alphaTOld4 = xOpt3[0];
      const double alphaBOld4 = xOpt3[1];
      const double F4 = 100.0;
      const double targetTheta4 = 30.0;

      const sgpp::base::DataVector xOpt4(minimizeDistance(
          4, alphaTOld4, alphaBOld4, F4, targetTheta4,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));
    }

    std::cout << latexTable.str() << "\n";

    // ------------------------------------------------------------------------
    // Optimization Scenario 2
    // ------------------------------------------------------------------------

    std::cout << "Optimization Scenario 2\n";
    std::cout << std::string(50, '-')  << "\n";
    latexTable.str(std::string());
    latexTable.clear();

    sgpp::base::DataMatrix scenario2Alphas(0, 2);
    sgpp::base::DataMatrix scenario2Thetas(0, 2);
    sgpp::base::DataVector scenario2Theta(2);

    {
      // ----------------------------------------------------------------------
      // Optimization 1
      // ----------------------------------------------------------------------

      const double F1 = 22.0;
      const double targetTheta1 = 25.0;
      size_t time = 1;

      const sgpp::base::DataVector xOpt1(minimizeActivation(
          time, F1, targetTheta1,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));
      scenario2Alphas.appendRow(xOpt1);
      time++;

      {
        muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
            F1, *TB, *TBGradient);
        muscle::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
            F1, fgIntpTB, fgIntpTBGradient);
        scenario2Theta[0] = momentumBalanceTheta.eval(xOpt1);
        scenario2Theta[1] = fgIntpMomentumBalanceTheta.eval(xOpt1);
      }
      scenario2Thetas.appendRow(scenario2Theta);

      // ----------------------------------------------------------------------
      // Optimization 2
      // ----------------------------------------------------------------------

      const double targetThetaOld2 = targetTheta1;
      sgpp::base::DataVector xOpt2(xOpt1);

      for (double F2 : {40.0, 100.0, 150.0, 170.0}) {
        for (double c2 : {0.01, 0.03, 0.03, 0.05, 0.2}) {
          const double alphaTOld2 = xOpt2[0];
          const double alphaBOld2 = xOpt2[1];

          xOpt2 = minimizeDistanceRelaxed(
              time, alphaTOld2, alphaBOld2, targetThetaOld2, F2, c2,
              fgIntpTB, fgIntpTBGradient, *TB, *TBGradient);
          scenario2Alphas.appendRow(xOpt2);
          time++;

          {
            muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
                F2, *TB, *TBGradient);
            muscle::momentum::MomentumBalanceTheta fgIntpMomentumBalanceTheta(
                F2, fgIntpTB, fgIntpTBGradient);
            scenario2Theta[0] = momentumBalanceTheta.eval(xOpt2);
            scenario2Theta[1] = fgIntpMomentumBalanceTheta.eval(xOpt2);
          }
          scenario2Thetas.appendRow(scenario2Theta);
        }
      }
    }

    std::cout << latexTable.str() << "\n";

    // ------------------------------------------------------------------------
    // Optimization Scenario 2 (Comparison)
    // ------------------------------------------------------------------------

    std::cout << "Optimization Scenario 2 (Comparison)\n";
    std::cout << std::string(50, '-')  << "\n";
    latexTable.str(std::string());
    latexTable.clear();

    const double scenario2targetTheta = 25.0;
    const std::vector<double> scenario2Loads =
        {FRef, 40.0, 100.0, 150.0, 170.0};
    sgpp::base::DataMatrix scenario2ComparisonPoints(0, 2);

    {
      // ----------------------------------------------------------------------
      // Optimization 1
      // ----------------------------------------------------------------------

      size_t time = 1;

      sgpp::base::DataVector xOpt(minimizeActivation(
          time, scenario2Loads[0], scenario2targetTheta,
          fgIntpTB, fgIntpTBGradient, *TB, *TBGradient));
      scenario2ComparisonPoints.appendRow(xOpt);
      time++;

      // ----------------------------------------------------------------------
      // Optimization 2
      // ----------------------------------------------------------------------

      for (size_t i = 1; i < scenario2Loads.size(); i++) {
        xOpt = minimizeDistance(
            time, xOpt[0], xOpt[1], scenario2Loads[i], scenario2targetTheta,
            fgIntpTB, fgIntpTBGradient, *TB, *TBGradient);
        scenario2ComparisonPoints.appendRow(xOpt);
        time++;
      }
    }

    std::cout << latexTable.str() << "\n";

    // ------------------------------------------------------------------------
    // Plot of Interpolation of T and B
    // ------------------------------------------------------------------------

    for (std::string component : {"T", "B"}) {
      if (component == "T") {
        evaluateFunction(*T, YY);
      } else {
        evaluateFunction(*B, YY);
      }

      writeCSV(YY, "intp_" + grid->getID() + "_" + component + ".csv");
    }

    // ------------------------------------------------------------------------
    // Plot of Interpolation Error of T and B
    // ------------------------------------------------------------------------

    writeCSV(grid->X, "grid_" + grid->getID() + ".csv");

    for (std::string component : {"T", "B"}) {
      sgpp::optimization::ScalarFunction* fgIntp;
      sgpp::optimization::ScalarFunction* sgIntp;

      if (component == "T") {
        fgIntp = &fgIntpT;
        sgIntp = T;
      } else {
        fgIntp = &fgIntpB;
        sgIntp = B;
      }

      sgpp::optimization::WrapperScalarFunction errorFcn(
          2, [&](const sgpp::base::DataVector& x) {
        return std::abs(fgIntp->eval(x) - sgIntp->eval(x));
        //return std::abs((fgIntp->eval(x) - sgIntp->eval(x)) / fgIntp->eval(x));
      });

      evaluateFunction(errorFcn, YY);
      writeCSV(YY, "intp_error_" + grid->getID() + "_" + component + ".csv");
    }

    // ------------------------------------------------------------------------
    // Plot of theta for Reference Load and "Infeasible" Loads
    // ------------------------------------------------------------------------

    for (double F : {FRef, -60.0, 180.0}) {
      muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
          F, *TB, *TBGradient);
      evaluateFunction(momentumBalanceTheta, YY, 50, 50);
      writeCSV(YY, "theta_F=" + std::to_string(static_cast<int>(F)) +
                   "_" + grid->getID() + ".csv");
    }

    // ------------------------------------------------------------------------
    // Plot of Interpolation Error of theta for Reference Load
    // ------------------------------------------------------------------------

    {
      muscle::momentum::MomentumBalanceTheta fgMomentumBalanceTheta(
          FRef, fgIntpTB, fgIntpTBGradient);
      muscle::momentum::MomentumBalanceTheta sgMomentumBalanceTheta(
          FRef, *TB, *TBGradient);

      sgpp::optimization::WrapperScalarFunction errorFcn(
          2, [&](const sgpp::base::DataVector& x) {
        return std::abs(fgMomentumBalanceTheta.eval(x) - sgMomentumBalanceTheta.eval(x));
      });

      evaluateFunction(errorFcn, YY, 50, 50);
      writeCSV(YY, "theta_error_" + grid->getID() + ".csv");
    }

    // ------------------------------------------------------------------------
    // Plot of Scenario 2 Point Trace
    // ------------------------------------------------------------------------

    writeCSV(scenario2Alphas, "scen2_alphas_" + grid->getID() + ".csv");
    writeCSV(scenario2Thetas, "scen2_thetas_" + grid->getID() + ".csv");
    writeCSV(scenario2ComparisonPoints, "scen2_comparison_points_" + grid->getID() + ".csv");

    if (grid->getID() == "fg") {
      for (double F : {40.0, 100.0, 150.0, 170.0}) {
        muscle::momentum::MomentumBalanceTheta momentumBalanceTheta(
            F, fgIntpTB, fgIntpTBGradient);
        evaluateFunction(momentumBalanceTheta, YY, 50, 50);
        writeCSV(YY, "theta_F=" + std::to_string(static_cast<int>(F)) +
                     "_" + grid->getID() + ".csv");
      }
    }
  }
}



int main() {
  sgpp::optimization::Printer::getInstance().setVerbosity(-1);

  //program1();
  //program2();
  programGenerateGraphics();

  return 0;
}
