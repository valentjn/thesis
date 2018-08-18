/**
 * Example program for using the sgpp::optimization module of SG++.
 * Compile with -std=c++11. Call it as
 *
 * ./optimizeConstrained ARG1_NAME=ARG1_VALUE ARG2_NAME=ARG2_VALUE ...
 *
 * The argument order doesn't matter. There are default values for every argument.
 * The possible argument names/values are:
 *
 * NAME     VALUE                                                                       DEFAULT
 * d        number of dimensions                                                        2
 * problem  constrained optimization problem (one of floudas, g03, g04, g05, g06, g08, g09, g10, g11, g12, g13, simionescu, soland)      g08
 * grid     type of the grid (one of bSpline, notAKnotBSpline, modifiedBSpline, modifiedNotAKnotBSpline, fundamentalSpline, fundamentalNotAKnotSpline, weaklyFundamentalSpline, weaklyFundamentalNotAKnotSpline)    modifiedNotAKnotBSpline
 * gridGen type of the iterative grid generator (linearSurplus or ritterNovak)         ritterNovak
 * gamma    adaptivity of the grid generation                                           0.85
 * N        maximal number of grid points                                               1000
 * p        B-spline degree                                                             3
 * seed     unsigned integer RNG seed used for generating all necessary                 0
 *          random numbers, zero seed means "use a time-dependent one"
 *
 * Copyright (C) Julian Valentin, 2018.
 */

/* ****************************************************************************
 * INCLUDES                                                                   *
 **************************************************************************** */

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <stdexcept>

#include <sgpp_base.hpp>
#include <sgpp_optimization.hpp>

/* ****************************************************************************
 * ENUMERATIONS                                                               *
 **************************************************************************** */

/// type of the sparse grid
enum GridType {
  BSpline,
  NotAKnotBSpline,
  ModifiedBSpline,
  ModifiedNotAKnotBSpline,
  FundamentalSpline,
  FundamentalNotAKnotSpline,
  WeaklyFundamentalSpline,
  WeaklyFundamentalNotAKnotSpline,
};

/// type of the iterative grid generation
enum GridGeneratorType {
  LinearSurplus,
  RitterNovak,
};

/* ****************************************************************************
 * STRUCTURES                                                                 *
 **************************************************************************** */

/**
 * Point in \f$[0, 1]^d\f$ together with the value of the objective function and the value
 * from the (or a) interpolant.
 */
struct EvaluatedPoint {
  /// point
  sgpp::base::DataVector x;
  /// objective function value
  double f_x;
  /// interpolant function value
  double ft_x;
  /// inequality constraint function value
  sgpp::base::DataVector g_x;
  /// equality constraint function value
  sgpp::base::DataVector h_x;

  /// static member indicating invalid points
  static EvaluatedPoint invalid;

  /**
   * @return  whether the point is valid
   */
  bool isValid() const {
    return !x.empty();
  }
};

EvaluatedPoint EvaluatedPoint::invalid = {{}, 0.0, 0.0, {}, {}};

/* ****************************************************************************
 * FORWARD DECLARATIONS                                                       *
 **************************************************************************** */

/**
 * Main routine.
 *
 * @param argc  length of argv
 * @param argv  program arguments
 * @return      exit code
 */
int main(int argc,
         const char* argv[]);

/**
 * Print a long divising line.
 */
void printLine();

/**
 * Print a short divising line.
 */
void printShortLine();

/**
 * Parse program arguments.
 *
 * @param[in]   argc                length of argv
 * @param[in]   argv                program arguments
 * @param[out]  d                   number of dimensions
 * @param[out]  problem             pointer to test problem
 * @param[out]  problem_str         name of problem as string
 * @param[out]  grid_type           type of the sparse grid
 * @param[out]  grid_type_str       name of grid_type as string
 * @param[out]  grid_gen_type       type of the iterative grid generation
 * @param[out]  grid_gen_type_str   name of grid_gen_type as string
 * @param[out]  gamma               adaptivity \f$\gamma \in [0, 1]\f$
 * @param[out]  N                   maximal number of grid points
 * @param[out]  p                   B-spline degree
 * @param[out]  seed                seed for the random number generator
 */
void parseArgs(int argc,
               const char* argv[],
               size_t& d,
               std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>& problem,
               std::string& problem_str,
               GridType& grid_type,
               std::string& grid_type_str,
               GridGeneratorType& grid_gen_type,
               std::string& grid_gen_type_str,
               double& gamma,
               size_t& N,
               size_t& p,
               sgpp::optimization::RandomNumberGenerator::SeedType& seed);

/**
 * Create exact gradients for constraint functions.
 * 
 * @param[in] problem       test problem
 * @param[in] problem_str   name of problem as string
 * @param[out] g_gradient   pointer to inequality constraint gradient function
 * @param[out] h_gradient   pointer to equality constraint gradient function
 */
void createConstraintGradients(sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                               const std::string& problem_str,
                               std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& g_gradient,
                               std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& h_gradient);

/**
 * Create a grid for the specified basis functions.
 * Delete after use.
 *
 * @param grid_type         type of the sparse grid
 * @param d                 number of dimensions
 * @param p                 B-spline degree
 * @return                  pointer to grid
 */
std::unique_ptr<sgpp::base::Grid> getGrid(GridType grid_type,
                                        size_t d,
                                        size_t p);

/**
 * Create an iterative grid generator for the specified grid.
 * Delete after use.
 *
 * @param grid_gen_type     type of the iterative grid generation
 * @param problem           test problem
 * @param grid              sparse grid
 * @param N                 maximal number of grid points
 * @param gamma             adaptivity \f$\gamma \in [0, 1]\f$
 */
std::unique_ptr<sgpp::optimization::IterativeGridGenerator> getGridGenerator(
  GridGeneratorType grid_gen_type,
  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
  sgpp::base::Grid& grid,
  size_t N,
  double gamma);

/**
 * Create a grid with piecewise linear basis functions together with a linear interpolant
 * with specified grid points.
 *
 * @param[in]   grid_type   type of the sparse grid
 * @param[in]   d           number of dimensions
 * @param[in]   grid_gen    iterative grid generator
 * @param[out]  grid_linear piecewise linear grid
 * @param[out]  ft_linear   piecewise linear interpolant
 * @return true if no error occurred, otherwise false
 */
bool getLinearInterpolant(GridType grid_type,
                          size_t d,
                          sgpp::optimization::IterativeGridGenerator& grid_gen,
                          std::unique_ptr<sgpp::base::Grid>& grid_linear,
                          std::unique_ptr<sgpp::optimization::InterpolantScalarFunction>& ft_linear);

/**
 * Determine the grid point in the grid of the iterative grid generator with the lowest
 * objective function value.
 *
 * @param grid_gen  iterative grid generator
 * @param problem   test problem
 * @param ft        interpolant (needed because EvaluatedPoint contains objective function and
 *                  interpolant values)
 */
EvaluatedPoint getBestGridPoint(sgpp::optimization::IterativeGridGenerator& grid_gen,
                                sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                                sgpp::optimization::InterpolantScalarFunction& ft);

/**
 * Try out all optimizers in a list.
 *
 * @param problem       test problem
 * @param ft            interpolant
 * @param optimizers    array of pointers to sgpp::optimization::optimizer::ConstrainedOptimizer objects
 * @param optimizer_str vector of descriptive names for each optimizer
 * @param x0            starting point for the optimizers (if necessary)
 */
EvaluatedPoint tryOptimizers(sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                             sgpp::optimization::InterpolantScalarFunction& ft,
                             std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer> optimizers[],
                             std::vector<std::string> optimizer_str,
                             const EvaluatedPoint& x0);

/**
 * Optimize the smooth interpolant as described in the Master's thesis.
 *
 * @param grid_gen      iterative grid generator
 * @param problem       test problem
 * @param ft            smooth interpolant
 * @param ft_gradient   gradient of smooth interpolant
 * @param ft_hessian    gradient and Hessian of smooth interpolant
 * @param g_gradient    gradient of inequality constraint function
 * @param h_gradient    gradient of equality constraint function
 * @return              optimal point found (together with the objective function value and
 *                      the value of the smooth interpolant)
 */
EvaluatedPoint optimizeSmoothIntp(sgpp::optimization::IterativeGridGenerator& grid_gen,
                                  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                                  sgpp::optimization::InterpolantScalarFunction& ft,
                                  sgpp::optimization::InterpolantScalarFunctionGradient& ft_gradient,
                                  sgpp::optimization::InterpolantScalarFunctionHessian& ft_hessian,
                                  sgpp::optimization::VectorFunctionGradient& g_gradient,
                                  sgpp::optimization::VectorFunctionGradient& h_gradient);

/**
 * Optimize the piecewise linear interpolant.
 *
 * @param grid_gen      iterative grid generator
 * @param problem       test problem
 * @param ft            smooth interpolant (used for evaluation in the returned point)
 * @param ft_linear     piecewise linear interpolant
 * @param g_gradient    gradient of inequality constraint function
 * @param h_gradient    gradient of equality constraint function
 * @return              optimal point found (together with the objective function value and
 *                      the value of the smooth interpolant)
 */
EvaluatedPoint optimizeLinearIntp(sgpp::optimization::IterativeGridGenerator& grid_gen,
                                  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                                  sgpp::optimization::InterpolantScalarFunction& ft,
                                  sgpp::optimization::InterpolantScalarFunction& ft_linear);

/**
 * Directly optimize the test function.
 *
 * @param grid_gen      iterative grid generator (used to get the maximal number of objective
 *                      function evaluations)
 * @param problem       test problem
 * @param ft            smooth interpolant (used for evaluation in the returned point)
 * @param g_gradient    gradient of inequality constraint function
 * @param h_gradient    gradient of equality constraint function
 * @return              optimal point found (together with the objective function value and
 *                      the value of the smooth interpolant)
 */
EvaluatedPoint optimizeObjFcn(sgpp::optimization::IterativeGridGenerator& grid_gen,
                              sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                              sgpp::optimization::InterpolantScalarFunction& ft);

/* ****************************************************************************
 * FUNCTION BODIES                                                            *
 **************************************************************************** */

int main(int argc, const char* argv[]) {
  // INITIALIZATION

  std::cerr << "optimizeConstrained program started.\n\n";
  sgpp::optimization::Printer::getInstance().setStream(&std::cerr);
  sgpp::optimization::Printer::getInstance().setVerbosity(2);

  // default parameter values
  size_t d = 2;
  std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>
  problem(new sgpp::optimization::test_problems::G08());
  std::string problem_str = "g08";
  GridType grid_type = GridType::ModifiedNotAKnotBSpline;
  std::string grid_type_str = "modifiedNotAKnotBSpline";
  double gamma = 0.85;
  size_t N = 1000;
  GridGeneratorType grid_gen_type = GridGeneratorType::RitterNovak;
  std::string grid_gen_type_str = "ritterNovak";
  size_t p = 3;
  sgpp::optimization::RandomNumberGenerator::SeedType seed = 0;

  // parse program arguments
  parseArgs(argc, argv, d, problem, problem_str, grid_type, grid_type_str, grid_gen_type, grid_gen_type_str,
            gamma, N, p, seed);

  // create grid and iterative grid generator
  std::unique_ptr<sgpp::base::Grid> grid =
    getGrid(grid_type, d, p);
  std::unique_ptr<sgpp::optimization::IterativeGridGenerator> grid_gen =
    getGridGenerator(grid_gen_type, *problem, *grid, N, gamma);

  if (seed == 0) {
    // set time-dependent seed
    sgpp::optimization::RandomNumberGenerator::getInstance().setSeed();
    seed = sgpp::optimization::RandomNumberGenerator::getInstance().getSeed();
  } else {
    // set seed to program argument
    sgpp::optimization::RandomNumberGenerator::getInstance().setSeed(seed);
  }

  // displace test function randomly and calculate optimal point/function value
  sgpp::base::DataVector displacement(d), x_opt(d);
  problem->generateDisplacement();
  displacement = problem->getDisplacement();
  double f_x_opt = problem->getOptimalPoint(x_opt);
  sgpp::optimization::test_problems::TestVectorFunction& g = problem->getInequalityConstraintFunction();
  sgpp::optimization::test_problems::TestVectorFunction& h = problem->getEqualityConstraintFunction();
  const size_t m_g = g.getNumberOfComponents();
  const size_t m_h = h.getNumberOfComponents();
  sgpp::base::DataVector g_x_opt(m_g);
  sgpp::base::DataVector h_x_opt(m_h);
  g.eval(x_opt, g_x_opt);
  h.eval(x_opt, h_x_opt);

  // create gradients of constraint functions
  std::unique_ptr<sgpp::optimization::VectorFunctionGradient> g_gradient;
  std::unique_ptr<sgpp::optimization::VectorFunctionGradient> h_gradient;
  createConstraintGradients(*problem, problem_str, g_gradient, h_gradient);

  // print settings
  std::cerr << "Settings:\n";
  std::cerr << "d = " << d << "\n";
  std::cerr << "problem = " << problem_str << "\n";
  std::cerr << "grid = " << grid_type_str << "\n";
  std::cerr << "gridGen = " << grid_gen_type_str << "\n";
  std::cerr << "gamma = " << gamma << "\n";
  std::cerr << "N = " << N << "\n";
  std::cerr << "p = " << p << "\n";
  std::cerr << "seed = " << std::to_string(seed) << "\n\n";

  sgpp::optimization::operator<<(std::cerr << "displacement = ", displacement) << "\n";
  sgpp::optimization::operator<<(std::cerr << "x_opt = ", x_opt) << "\n";
  std::cerr << "f(x_opt) = " << f_x_opt << "\n\n";

  // GRID GENERATION

  printLine();
  std::cerr << "Generating grid...\n\n";

  if (!grid_gen->generate()) {
    std::cerr << "Grid generation failed, exiting.\n";
    return 1;
  }

  // HIERARCHISATION

  printLine();
  std::cerr << "Hierarchising...\n\n";
  sgpp::base::DataVector function_values(grid_gen->getFunctionValues());
  sgpp::base::DataVector coeffs;
  sgpp::optimization::HierarchisationSLE hier_system(*grid);
  sgpp::optimization::sle_solver::Auto sle_solver;
  //sgpp::optimization::Printer::getInstance().printSLE(hier_system);

  // solve linear system
  if (!sle_solver.solve(hier_system, function_values, coeffs)) {
    std::cerr << "Solving failed, exiting.\n";
    return 1;
  }

  // hierarchisation of linear interpolant
  printLine();

  std::cerr << "Linear Hierarchisation...\n\n";
  std::unique_ptr<sgpp::base::Grid> grid_linear;
  std::unique_ptr<sgpp::optimization::InterpolantScalarFunction> ft_linear;

  if (!getLinearInterpolant(grid_type, d, *grid_gen, grid_linear, ft_linear)) {
    std::cerr << "Couldn't determine linear interpolant, exiting\n";
    return 1;
  }

  // OPTIMIZATION

  printLine();

  std::cerr << "Optimizing...\n\n";
  sgpp::optimization::InterpolantScalarFunction ft(*grid, coeffs);
  sgpp::optimization::InterpolantScalarFunctionGradient ft_gradient(*grid, coeffs);
  sgpp::optimization::InterpolantScalarFunctionHessian ft_hessian(*grid, coeffs);

  std::vector<std::string> optimizer_str =
  {"smoothInterpolant", "linearInterpolant", "objectiveFunction", "realOptimum"};
  std::vector<EvaluatedPoint> optimizer_x_opt;
  std::vector<double> optimizer_times;

  // optimize and measure times
  for (size_t k = 0; k < 3; k++) {
    std::chrono::time_point<std::chrono::system_clock> start_time =
      std::chrono::system_clock::now();

    switch (k) {
    case 0:
      // optimization of smooth interpolant
      optimizer_x_opt.push_back(
        optimizeSmoothIntp(*grid_gen, *problem, ft, ft_gradient, ft_hessian, *g_gradient, *h_gradient));
      break;
    case 1:
      // optimization of linear interpolant
      optimizer_x_opt.push_back(
        optimizeLinearIntp(*grid_gen, *problem, ft, *ft_linear));
      break;
    case 2:
      // optimization of objective function
      optimizer_x_opt.push_back(
        optimizeObjFcn(*grid_gen, *problem, ft));
      break;
    default:
      break;
    }

    std::chrono::duration<double> duration = std::chrono::system_clock::now() - start_time;
    optimizer_times.push_back(duration.count());
  }

  // real optimum
  optimizer_x_opt.push_back({x_opt, f_x_opt, ft.eval(x_opt), g_x_opt, h_x_opt});
  optimizer_times.push_back(0.0);

  // PRINTING RESULTS

  printLine();
  std::cerr << "Results overview (seed = " << seed << "):\n\n";
  printShortLine();

  std::vector<int> colw = {20, 13, 13, 13};
  std::cerr << std::setw(colw[0]) << std::left << "OPTIMIZED FUNCTION";
  std::cerr << std::setw(colw[1]) << std::right << "f(x)";
  std::cerr << std::setw(colw[2]) << std::right << "ft(x)";
  std::cerr << std::setw(colw[3]) << std::right << "DURATION" << "\n";
  printShortLine();

  for (size_t i = 0; i < optimizer_str.size(); i++) {
    if (optimizer_str[i] == "-") {
      printShortLine();
      continue;
    }

    std::cerr << std::setw(colw[0]) << std::left << optimizer_str[i];
    std::cerr << std::setw(colw[1]) << std::right << optimizer_x_opt[i].f_x;
    std::cerr << std::setw(colw[2]) << std::right << optimizer_x_opt[i].ft_x;

    if (optimizer_times[i] > 0.0) {
      std::cerr << std::setw(colw[3]-2) << std::right
                << static_cast<int>(1000.0 * optimizer_times[i]) << "ms";
    } else {
      std::cerr << std::setw(colw[3]) << std::right << "";
    }

    std::cerr << "\n";
  }

  printShortLine();
  std::cerr << "\n";

  // WRITE RESULTS TO STDOUT

  std::cout << std::scientific << std::setprecision(16);
  std::cout << "{\n";

  for (size_t i = 0; i < optimizer_x_opt.size(); i++) {
    std::cout << "  \"" << optimizer_str[i] << "\" : {\n";
    sgpp::optimization::operator<<(std::cout << "    \"xOpt\" : ",
                                   optimizer_x_opt[i].x) << ",\n";
    std::cout << "    \"fxOpt\" : " << optimizer_x_opt[i].f_x << ",\n";
    std::cout << "    \"fsxOpt\" : " << optimizer_x_opt[i].ft_x << ",\n";
    sgpp::optimization::operator<<(std::cout << "    \"gxOpt\" : ",
                                   optimizer_x_opt[i].g_x) << ",\n";
    sgpp::optimization::operator<<(std::cout << "    \"hxOpt\" : ",
                                   optimizer_x_opt[i].h_x) << ",\n";
    std::cout << "    \"runtime\" : " << optimizer_times[i] << "\n";
    std::cout << "  }" << ((i < optimizer_x_opt.size() - 1) ? "," : "") << "\n";
  }

  std::cout << "}\n";

  // TERMINATION

  printLine();
  std::cerr << "\noptimizeConstrained program terminated.\n";

  return 0;
}

void printLine() {
  std::cerr << "----------------------------------------"
            << "----------------------------------------\n";
}

void printShortLine() {
  std::cerr << "-----------------------------------------------------------\n";
}

void parseArgs(int argc, const char* argv[],
               size_t& d, std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>& problem,
               std::string& problem_str,
               GridType& grid_type, std::string& grid_type_str,
               GridGeneratorType& grid_gen_type, std::string& grid_gen_type_str,
               double& gamma, size_t& N,
               size_t& p,
               sgpp::optimization::RandomNumberGenerator::SeedType& seed) {
  std::vector<std::string> test_problem_strs = {
    "floudas", "g03", "g04", "g05", "g06", "g08", "g09", "g10",
    "g11", "g12", "g13", "simionescu", "soland",
  };

  for (size_t i = 1; i < static_cast<size_t>(argc); i++) {
    std::string arg(argv[i]);

    // dimension
    if (arg.find("d=") == 0) {
      arg = arg.substr(2, std::string::npos);
      d = std::stoi(arg);
      // objective function
    } else if (arg.find("f=") == 0) {
      arg = arg.substr(2, std::string::npos);

      if (std::find(test_problem_strs.begin(), test_problem_strs.end(), arg)
          != test_problem_strs.end()) {
        problem_str = arg;
      } else {
        throw std::invalid_argument("Invalid objective function.");
      }
      // type of the sparse grid
    } else if (arg.find("grid=") == 0) {
      arg = arg.substr(5, std::string::npos);

      if (arg == "bSpline") {
        grid_type = GridType::BSpline;
      } else if (arg == "notAKnotBSpline") {
        grid_type = GridType::NotAKnotBSpline;
      } else if (arg == "modifiedBSpline") {
        grid_type = GridType::ModifiedBSpline;
      } else if (arg == "modifiedNotAKnotBSpline") {
        grid_type = GridType::ModifiedNotAKnotBSpline;
      } else if (arg == "fundamentalSpline") {
        grid_type = GridType::FundamentalSpline;
      } else if (arg == "fundamentalNotAKnotSpline") {
        grid_type = GridType::FundamentalNotAKnotSpline;
      } else if (arg == "weaklyFundamentalSpline") {
        grid_type = GridType::WeaklyFundamentalSpline;
      } else if (arg == "weaklyFundamentalNotAKnotSpline") {
        grid_type = GridType::WeaklyFundamentalNotAKnotSpline;
      } else {
        continue;
      }

      grid_type_str = arg;
      // type of the iterative grid generator
    } else if (arg.find("gridGen=") == 0) {
      arg = arg.substr(8, std::string::npos);

      if (arg == "linearSurplus") {
        grid_gen_type = GridGeneratorType::LinearSurplus;
      } else if (arg == "ritterNovak") {
        grid_gen_type = GridGeneratorType::RitterNovak;
      } else {
        continue;
      }

      grid_gen_type_str = arg;
      // adaptivity
    } else if (arg.find("gamma=") == 0) {
      arg = arg.substr(6, std::string::npos);
      gamma = std::stod(arg);
      // maximal number of grid points
    } else if (arg.find("N=") == 0) {
      arg = arg.substr(2, std::string::npos);
      N = std::stoi(arg);
      // B-spline degree
    } else if (arg.find("p=") == 0) {
      arg = arg.substr(2, std::string::npos);
      p = std::stoi(arg);
      // RNG seed
    } else if (arg.find("seed=") == 0) {
      arg = arg.substr(5, std::string::npos);
      seed = std::stol(arg);
    }
  }

  // create test function object, overriding d for some functions with fixed dimension
  if (problem_str == "floudas") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::Floudas());
    d = 2;
  } else if (problem_str == "g03") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G03(d));
  } else if (problem_str == "g04") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G04());
    d = 5;
  } else if (problem_str == "g05") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G05());
    d = 4;
  } else if (problem_str == "g06") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G06());
    d = 2;
  } else if (problem_str == "g08") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G08());
    d = 2;
  } else if (problem_str == "g09") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G09());
    d = 7;
  } else if (problem_str == "g10") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G10());
    d = 8;
  } else if (problem_str == "g11") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G11());
    d = 2;
  } else if (problem_str == "g12") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G12());
    d = 3;
  } else if (problem_str == "g13") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::G13());
    d = 5;
  } else if (problem_str == "simionescu") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::Simionescu());
    d = 2;
  } else if (problem_str == "soland") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::ConstrainedTestProblem>(
          new sgpp::optimization::test_problems::Soland());
    d = 2;
  }
}

void createConstraintGradients(sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                               const std::string& problem_str,
                               std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& g_gradient,
                               std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& h_gradient) {
  const sgpp::base::DataVector& displacement(problem.getDisplacement());
  const size_t d = displacement.getSize();
  const size_t m_g = problem.getInequalityConstraintFunction().getNumberOfComponents();
  const size_t m_h =  problem.getEqualityConstraintFunction().getNumberOfComponents();

  if (problem_str == "g08") {
    g_gradient.reset(new sgpp::optimization::WrapperVectorFunctionGradient(
      d, m_g, [&displacement](const sgpp::base::DataVector& x,
                 sgpp::base::DataVector& value,
                 sgpp::base::DataMatrix& gradient) {
        const double x1 = 2.0 * (x[0] + displacement[0]) + 0.5;
        const double x2 = 3.0 * (x[1] + displacement[1]) + 3.0;

        value[0] = x1 * x1 - x2 + 1.0;
        value[1] = 1.0 - x1 + std::pow(x2 - 4.0, 2.0);
        gradient(0, 0) = 4.0 * x1;
        gradient(0, 1) = -3.0;
        gradient(1, 0) = -2.0;
        gradient(1, 1) = 6.0 * (x2 - 4.0);
      }
    ));
    sgpp::optimization::EmptyVectorFunctionGradient::getInstance().clone(h_gradient);
  } else if (problem_str == "g13") {
    sgpp::optimization::EmptyVectorFunctionGradient::getInstance().clone(g_gradient);
    h_gradient.reset(new sgpp::optimization::WrapperVectorFunctionGradient(
      d, m_h, [&displacement](const sgpp::base::DataVector& x,
                 sgpp::base::DataVector& value,
                 sgpp::base::DataMatrix& gradient) {
          const double x1 = 4.6 * (x[0] + displacement[0]) - 2.3;
          const double x2 = 4.6 * (x[1] + displacement[1]) - 2.3;
          const double x3 = 6.4 * (x[2] + displacement[2]) - 3.2;
          const double x4 = 6.4 * (x[3] + displacement[3]) - 3.2;
          const double x5 = 6.4 * (x[4] + displacement[4]) - 3.2;

          value[0] = x1 * x1 + x2 * x2 + x3 * x3 + x4 * x4 + x5 * x5 - 10.0;
          value[1] = x2 * x3 - 5.0 * x4 * x5;
          value[2] = x1 * x1 * x1 + x2 * x2 * x2 + 1.0;
          gradient(0, 0) = 4.6 * (2.0 * x1);
          gradient(0, 1) = 4.6 * (2.0 * x2);
          gradient(0, 2) = 6.4 * (2.0 * x3);
          gradient(0, 3) = 6.4 * (2.0 * x4);
          gradient(0, 4) = 6.4 * (2.0 * x5);
          gradient(1, 0) = 4.6 * (0.0);
          gradient(1, 1) = 4.6 * (x3);
          gradient(1, 2) = 6.4 * (x2);
          gradient(1, 3) = 6.4 * (-5.0 * x5);
          gradient(1, 4) = 6.4 * (-5.0 * x4);
          gradient(2, 0) = 4.6 * (3.0 * x1 * x1);
          gradient(2, 1) = 4.6 * (3.0 * x2 * x2);
          gradient(1, 2) = 6.4 * (0.0);
          gradient(1, 3) = 6.4 * (0.0);
          gradient(1, 4) = 6.4 * (0.0);
      }
    ));
  } else {
      throw std::invalid_argument("Objective function not supported.");
  }
}

std::unique_ptr<sgpp::base::Grid> getGrid(GridType grid_type,
                                        size_t d, size_t p) {
  std::unique_ptr<sgpp::base::Grid> grid;

  switch (grid_type) {
    case GridType::BSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::BsplineBoundaryGrid(d, p));
      break;
    case GridType::NotAKnotBSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::NotAKnotBsplineBoundaryGrid(d, p));
      break;
    case GridType::ModifiedBSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::ModBsplineGrid(d, p));
      break;
    case GridType::ModifiedNotAKnotBSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::ModNotAKnotBsplineGrid(d, p));
      break;
    case GridType::FundamentalSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::FundamentalSplineBoundaryGrid(d, p));
      break;
    case GridType::FundamentalNotAKnotSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::FundamentalNotAKnotSplineBoundaryGrid(d, p));
      break;
    case GridType::WeaklyFundamentalSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::LagrangeSplineBoundaryGrid(d, p));
      break;
    case GridType::WeaklyFundamentalNotAKnotSpline:
      grid = std::unique_ptr<sgpp::base::Grid>(
                new sgpp::base::LagrangeNotAKnotSplineBoundaryGrid(d, p));
      break;
    default:
      throw std::invalid_argument("Grid type not supported.");
  }

  return grid;
}

std::unique_ptr<sgpp::optimization::IterativeGridGenerator> getGridGenerator(
  GridGeneratorType grid_gen_type,
  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
  sgpp::base::Grid& grid,
  size_t N,
  double gamma) {
  sgpp::optimization::test_problems::TestScalarFunction& f = problem.getObjectiveFunction();
  std::unique_ptr<sgpp::optimization::IterativeGridGenerator> grid_gen;

  if (grid_gen_type == GridGeneratorType::LinearSurplus) {
    grid_gen = std::unique_ptr<sgpp::optimization::IterativeGridGenerator>(
                 new sgpp::optimization::IterativeGridGeneratorLinearSurplus(f, grid, N, gamma));
  } else if (grid_gen_type == GridGeneratorType::RitterNovak) {
    grid_gen = std::unique_ptr<sgpp::optimization::IterativeGridGenerator>(
                 new sgpp::optimization::IterativeGridGeneratorRitterNovak(f, grid, N, gamma));
  } else {
    throw std::invalid_argument("Grid generator type not supported.");
  }

  return grid_gen;
}

bool getLinearInterpolant(GridType grid_type, size_t d,
                          sgpp::optimization::IterativeGridGenerator& grid_gen,
                          std::unique_ptr<sgpp::base::Grid>& grid_linear,
                          std::unique_ptr<sgpp::optimization::InterpolantScalarFunction>& ft_linear) {
  sgpp::base::GridStorage& grid_storage = grid_gen.getGrid().getStorage();
  sgpp::base::DataVector function_values(grid_gen.getFunctionValues());

  // generate linear grid
  switch (grid_type) {
    case GridType::BSpline:
    case GridType::NotAKnotBSpline:
    case GridType::FundamentalSpline:
    case GridType::FundamentalNotAKnotSpline:
    case GridType::WeaklyFundamentalSpline:
    case GridType::WeaklyFundamentalNotAKnotSpline:
      grid_linear = std::unique_ptr<sgpp::base::Grid>(
                      new sgpp::base::LinearBoundaryGrid(d));
      break;
    case GridType::ModifiedBSpline:
    case GridType::ModifiedNotAKnotBSpline:
      grid_linear = std::unique_ptr<sgpp::base::Grid>(
                      new sgpp::base::ModLinearGrid(d));
      break;
    default:
      throw std::invalid_argument("Grid type not supported.");
  }

  // insert all grid points
  for (size_t i = 0; i < grid_storage.getSize(); i++) {
    grid_linear->getStorage().insert(grid_storage[i]);
  }

  sgpp::base::DataVector coeffs;
  sgpp::optimization::HierarchisationSLE hier_system(*grid_linear);
  sgpp::optimization::sle_solver::Auto sle_solver;
  //sgpp::optimization::Printer::getInstance().printSLE(hier_system);

  // solve linear system
  if (!sle_solver.solve(hier_system, function_values, coeffs)) {
    return false;
  }

  ft_linear = std::unique_ptr<sgpp::optimization::InterpolantScalarFunction>(
                new sgpp::optimization::InterpolantScalarFunction(*grid_linear, coeffs));

  return true;
}

EvaluatedPoint getBestGridPoint(
  sgpp::optimization::IterativeGridGenerator& grid_gen,
  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
  sgpp::optimization::InterpolantScalarFunction& ft) {
  sgpp::optimization::test_problems::TestScalarFunction& f = problem.getObjectiveFunction();
  const size_t d = f.getNumberOfParameters();
  const sgpp::base::DataVector& function_values = grid_gen.getFunctionValues();
  sgpp::base::GridStorage& grid_storage = grid_gen.getGrid().getStorage();
  EvaluatedPoint x0;

  // index of grid point with minimal function value
  size_t x0_index = std::distance(function_values.begin(),
                                  std::min_element(function_values.begin(), function_values.end()));
  x0.x = sgpp::base::DataVector(d, 0.0);

  for (size_t t = 0; t < d; t++) {
    x0.x[t] = grid_storage[x0_index].getStandardCoordinate(t);
  }

  // evaluate objective function and interpolant
  x0.f_x = function_values[x0_index];
  x0.ft_x = ft.eval(x0.x);

  return x0;
}

EvaluatedPoint tryOptimizers(sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
                             sgpp::optimization::InterpolantScalarFunction& ft,
                             std::vector<std::string> optimizer_str,
                             std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer> optimizers[],
                             const EvaluatedPoint& x0) {
  sgpp::optimization::test_problems::TestScalarFunction& f = problem.getObjectiveFunction();
  sgpp::optimization::test_problems::TestVectorFunction& g = problem.getInequalityConstraintFunction();
  sgpp::optimization::test_problems::TestVectorFunction& h = problem.getEqualityConstraintFunction();
  const size_t m_g = g.getNumberOfComponents();
  const size_t m_h = h.getNumberOfComponents();
  sgpp::base::DataVector x_opt;
  sgpp::base::DataVector g_x_opt(m_g);
  sgpp::base::DataVector h_x_opt(m_h);
  // best result of all optimizers
  EvaluatedPoint x_opt_min = {{}, INFINITY, INFINITY, {}, {}};

  if (x0.isValid()) {
    // optimal point should be no worse than the starting point (if supplied)
    x_opt_min = x0;
  }

  for (size_t i = 0; i < optimizer_str.size(); i++) {
    if (x0.isValid()) {
      optimizers[i]->setStartingPoint(x0.x);
    }

    // optimize and evaluate at optimum
    optimizers[i]->optimize();
    x_opt = optimizers[i]->getOptimalPoint();
    double f_x_opt = f.eval(x_opt);
    double ft_x_opt = ft.eval(x_opt);
    g.eval(x_opt, g_x_opt);
    h.eval(x_opt, h_x_opt);

    if (f_x_opt < x_opt_min.f_x) {
      // should be executed for i == 0 (because x_opt_min.f_x == INFINITY)
      x_opt_min = {x_opt, f_x_opt, ft_x_opt, g_x_opt, h_x_opt};
    }

    std::cerr << "Result with " << optimizer_str[i] << ": ";
    sgpp::optimization::operator<<(std::cerr << "x_opt = ", x_opt) << "\n";
    std::cerr << "f(x_opt) = " << f_x_opt << ", ft(x_opt) = " << ft_x_opt << "\n";
    sgpp::optimization::operator<<(std::cerr << "g(x_opt) = ", g_x_opt) << "\n";
    sgpp::optimization::operator<<(std::cerr << "h(x_opt) = ", h_x_opt) << "\n\n";
  }

  return x_opt_min;
}

EvaluatedPoint optimizeSmoothIntp(
  sgpp::optimization::IterativeGridGenerator& grid_gen,
  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
  sgpp::optimization::InterpolantScalarFunction& ft,
  sgpp::optimization::InterpolantScalarFunctionGradient& ft_gradient,
  sgpp::optimization::InterpolantScalarFunctionHessian& ft_hessian,
  sgpp::optimization::VectorFunctionGradient& g_gradient,
  sgpp::optimization::VectorFunctionGradient& h_gradient) {
  EvaluatedPoint x0 = getBestGridPoint(grid_gen, problem, ft);
  sgpp::optimization::VectorFunction& g = problem.getInequalityConstraintFunction();
  sgpp::optimization::VectorFunction& h = problem.getEqualityConstraintFunction();
  // results of the optimizers
  std::vector<EvaluatedPoint> x_opt_candidates = {x0};

  // optimize smooth interpolant
  std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer> optimizers[] = {
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::LogBarrier(ft, ft_gradient, g, g_gradient)),
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::SquaredPenalty(ft, ft_gradient, g, g_gradient, h, h_gradient)),
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::AugmentedLagrangian(ft, ft_gradient, g, g_gradient, h, h_gradient)),
  };
  x_opt_candidates.push_back(tryOptimizers(problem, ft,
  {"LB", "SP", "AL"},
  optimizers, x0));

  // best point so far
  EvaluatedPoint x_opt_min = x_opt_candidates[0];

  for (size_t i = 0; i < x_opt_candidates.size(); i++) {
    if (x_opt_candidates[i].f_x < x_opt_min.f_x) {
      x_opt_min = x_opt_candidates[i];
    }
  }

  return x_opt_min;
}

EvaluatedPoint optimizeLinearIntp(
  sgpp::optimization::IterativeGridGenerator& grid_gen,
  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
  sgpp::optimization::InterpolantScalarFunction& ft,
  sgpp::optimization::InterpolantScalarFunction& ft_linear) {
  EvaluatedPoint x0 = getBestGridPoint(grid_gen, problem, ft);
  EvaluatedPoint x_opt_min;
  sgpp::optimization::ScalarFunction& f = problem.getObjectiveFunction();
  sgpp::optimization::VectorFunction& g = problem.getInequalityConstraintFunction();
  sgpp::optimization::VectorFunction& h = problem.getEqualityConstraintFunction();
  // results of the optimizers
  std::vector<EvaluatedPoint> x_opt_candidates = {x0};

  // optimize linear interpolant
  std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer> optimizers[] = {
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::LogBarrier(ft_linear, g)),
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::SquaredPenalty(ft_linear, g, h)),
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::AugmentedLagrangian(ft, g, h)),
  };
  x_opt_candidates.push_back(tryOptimizers(problem, ft,
  {"LB on linintp", "SP on linintp", "AL on linintp"},
  optimizers, x0));

  // best point so far
  EvaluatedPoint x_opt_min = x_opt_candidates[0];

  for (size_t i = 0; i < x_opt_candidates.size(); i++) {
    if (x_opt_candidates[i].f_x < x_opt_min.f_x) {
      x_opt_min = x_opt_candidates[i];
    }
  }

  return x_opt_min;
}

EvaluatedPoint optimizeObjFcn(
  sgpp::optimization::IterativeGridGenerator& grid_gen,
  sgpp::optimization::test_problems::ConstrainedTestProblem& problem,
  sgpp::optimization::InterpolantScalarFunction& ft) {
  sgpp::optimization::test_problems::TestScalarFunction& f = problem.getObjectiveFunction();
  const size_t N = grid_gen.getFunctionValues().size();
  EvaluatedPoint x_opt_min;
  sgpp::optimization::VectorFunction& g = problem.getInequalityConstraintFunction();
  sgpp::optimization::VectorFunction& h = problem.getEqualityConstraintFunction();
  // results of the optimizers
  std::vector<EvaluatedPoint> x_opt_candidates = {x0};

  // optimize objective function (split N up evenly for all three optimizers)
  std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer> optimizers[] = {
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::LogBarrier(f, g,
    static_cast<size_t>(static_cast<double>(N) / 3.0 + 1.0))),
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::SquaredPenalty(f, g, h,
    static_cast<size_t>(static_cast<double>(N) / 3.0 + 1.0))),
    std::unique_ptr<sgpp::optimization::optimizer::ConstrainedOptimizer>(
      new sgpp::optimization::optimizer::AugmentedLagrangian(f, g, h,
    static_cast<size_t>(static_cast<double>(N) / 3.0 + 1.0))),
  };
  x_opt_candidates.push_back(tryOptimizers(problem, ft,
  {"LB on objfun", "SP on objfun", "AL on objfun"},
  optimizers, x0));

  // best point so far
  EvaluatedPoint x_opt_min = x_opt_candidates[0];

  for (size_t i = 0; i < x_opt_candidates.size(); i++) {
    if (x_opt_candidates[i].f_x < x_opt_min.f_x) {
      x_opt_min = x_opt_candidates[i];
    }
  }

  return x_opt_min;
}
