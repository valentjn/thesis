#include <iostream>

#include <sgpp_base.hpp>
#include <sgpp_optimization.hpp>

#include <biomech2_interface/MetaHeader.hpp>

namespace bm2i = biomech2_interface;

enum class Action {
  EvaluateForces,
  EvaluateEquilibriumElbowAngle,
  SolveScenario1,
  SolveScenario2,
  SolveScenario3,
};

enum class GridType {
  FullGrid,
  SparseGrid,
};

typedef biomech2_interface::SparseGrid::Type BasisType;

void parseArgs(int argc, const char* argv[],
               Action& action, GridType& gridType, BasisType& basisType,
               size_t& p, double& forceLoad);

inline void writeNumber(double x);

void writeVector(const sgpp::base::DataVector& xx);

void readMatrix(sgpp::base::DataMatrix& XX);
void writeMatrix(const sgpp::base::DataMatrix& XX);

void evaluateForces(sgpp::optimization::VectorFunction& intpTB);

void evaluateEquilibriumElbowAngle(
    sgpp::optimization::VectorFunction& intpTB,
    sgpp::optimization::VectorFunctionGradient& intpTBGradient,
    double forceLoad);

int main(int argc, const char* argv[]) {
  std::cerr << "applyBiomech2 program started.\n\n";
  sgpp::optimization::Printer::getInstance().setStream(&std::cerr);
  sgpp::optimization::Printer::getInstance().setVerbosity(2);
  
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
      } else if (arg == "solveScenario1") {
        action = Action::SolveScenario1;
      } else if (arg == "solveScenario2") {
        action = Action::SolveScenario2;
      } else if (arg == "solveScenario3") {
        action = Action::SolveScenario3;
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
    std::cout << x;
  }
}

void writeVector(const sgpp::base::DataVector& xx) {
  const size_t NN = xx.getSize();
  
  std::cout << "[";
  
  for (size_t j = 0; j < NN; j++) {
    if (j > 0) std::cout << ", ";
    writeNumber(xx[j]);
  }
  
  std::cout << "]\n";
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
  
  std::cout << "]\n";
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
}
