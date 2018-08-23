/**
 * Perform fuzzy optimization with SG++. Call as
 *
 * ./optimizeFuzzy ARG1_NAME=ARG1_VALUE ARG2_NAME=ARG2_VALUE ...
 *
 * The argument order doesn't matter. There are default values for every argument.
 * The possible argument names/values are:
 *
 * NAME     VALUE                                                                       DEFAULT
 * d        number of dimensions                                                        2
 * f        objective function (one of absoluteValue, ackley, alpine02, beale, branin01, branin02, bubbleWrap, easomYang,        branin01
 *          eggHolder, goldsteinPrice, griewank, hartman3, hartman6, himmelblau,
 *          hoelderTable, increasingPower, michalewicz, mladineo, perm, rastrigin, rosenbrock,
 *          schwefel06, schwefel22, schwefel26, shcb, sphere, tremblingParabola)
 * grid     type of the grid (one of bSpline, notAKnotBSpline, modifiedBSpline, modifiedNotAKnotBSpline, fundamentalSpline, fundamentalNotAKnotSpline, weaklyFundamentalSpline, weaklyFundamentalNotAKnotSpline)    modifiedNotAKnotBSpline
 * gridGen  how to generate the grids (regular or ritterNovak)         ritterNovak
 * gamma    if gridGen=ritterNovak: adaptivity of the grid generation                                           0.85
 * N        if gridGen=ritterNovak: maximal number of grid points                                               1000
 * m        if gridGen=ritterNovak: number of alpha segments                                           100
 * n        if gridGen=regular: level of the regular sparse grid                                       5
 * input    index to select one of the fuzzy preset builtins                                           5
 * p        B-spline degree                                                             3
 * seed     unsigned integer RNG seed used for generating all necessary                 0
 *          random numbers, zero seed means "use a time-dependent one"
 *
 * Copyright (C) Julian Valentin, 2014--2018.
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

/// type of the grid generation
enum GridGeneratorType {
  Regular,
  RitterNovak,
};

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
 * @param[out]  m                   number of alpha segments
 * @param[out]  n                   level of the regular sparse grid
 * @param[out]  input               fuzzy input preset index
 * @param[out]  p                   B-spline degree
 * @param[out]  seed                seed for the random number generator
 */
void parseArgs(int argc,
               const char* argv[],
               size_t& d,
               std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>& problem,
               std::string& problem_str,
               GridType& grid_type,
               std::string& grid_type_str,
               GridGeneratorType& grid_gen_type,
               std::string& grid_gen_type_str,
               double& gamma,
               size_t& N,
               size_t& m,
               size_t& n,
               size_t& input,
               size_t& p,
               sgpp::optimization::RandomNumberGenerator::SeedType& seed);

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
 * Create the fuzzy input vector by selecting one of the presets.
 * Delete after use.
 *
 * @param input             fuzzy input preset index
 * @param d                 number of dimensions
 * @return                  fuzzy input vector
 */
void getFuzzyInput(size_t input,
                   size_t d,
                   std::vector<std::unique_ptr<const sgpp::optimization::FuzzyInterval>>& xFuzzy);

/**
 * Create an iterative grid generator for the specified grid.
 * Delete after use.
 *
 * @param grid_gen_type     type of the iterative grid generation
 * @param problem           test problem
 * @param grid              sparse grid
 * @param N                 maximal number of grid points
 * @param gamma             adaptivity \f$\gamma \in [0, 1]
 * @param m                 number of alpha segments
 * @param xFuzzy            fuzzy input vector
 */
std::unique_ptr<sgpp::optimization::IterativeGridGenerator> getGridGenerator(
  GridGeneratorType grid_gen_type,
  sgpp::optimization::test_problems::UnconstrainedTestProblem& problem,
  sgpp::base::Grid& grid,
  size_t N,
  double gamma,
  size_t m,
  const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr);

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
                          sgpp::base::Grid& grid,
                          const sgpp::base::DataVector function_values,
                          std::unique_ptr<sgpp::base::Grid>& grid_linear,
                          std::unique_ptr<sgpp::optimization::InterpolantScalarFunction>& ft_linear);

/**
 * Optimize the smooth interpolant as described in the Master's thesis.
 *
 * @param[in]  ft             smooth interpolant
 * @param[in]  ft_gradient    gradient of smooth interpolant
 * @param[in]  m              number of alpha segments
 * @param[in]  xFuzzyPtr      fuzzy input vector
 * @param[out] yFuzzy         fuzzy output
 */
void optimizeSmoothIntp(
    sgpp::optimization::InterpolantScalarFunction& ft,
    sgpp::optimization::InterpolantScalarFunctionGradient& ft_gradient,
    size_t m,
    const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr,
    std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>& yFuzzy);

/**
 * Optimize the piecewise linear interpolant.
 *
 * @param[in]  ft_linear      piecewise linear interpolant
 * @param[in]  m              number of alpha segments
 * @param[in]  xFuzzyPtr      fuzzy input vector
 * @param[out] yFuzzy         fuzzy output
 */
void optimizeLinearIntp(
    sgpp::optimization::InterpolantScalarFunction& ft_linear,
    size_t m,
    const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr,
    std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>& yFuzzy);

/**
 * Directly optimize the test function.
 *
 * @param[in]  f              objective function
 * @param[in]  m              number of alpha segments
 * @param[in]  xFuzzyPtr      fuzzy input vector
 * @param[out] yFuzzy         fuzzy output
 */
void optimizeObjFcn(
    sgpp::optimization::ScalarFunction& f,
    size_t m,
    const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr,
    std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>& yFuzzy);

/* ****************************************************************************
 * FUNCTION BODIES                                                            *
 **************************************************************************** */

int main(int argc, const char* argv[]) {
  // INITIALIZATION

  std::cerr << "optimizeFuzzy program started.\n\n";
  sgpp::optimization::Printer::getInstance().setStream(&std::cerr);
  sgpp::optimization::Printer::getInstance().setVerbosity(2);

  // default parameter values
  size_t d = 2;
  std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>
  problem(new sgpp::optimization::test_problems::Branin01());
  std::string problem_str = "branin01";
  GridType grid_type = GridType::ModifiedNotAKnotBSpline;
  std::string grid_type_str = "modifiedNotAKnotBSpline";
  double gamma = 0.85;
  size_t N = 1000;
  size_t m = 100;
  size_t n = 5;
  size_t input = 0;
  GridGeneratorType grid_gen_type = GridGeneratorType::RitterNovak;
  std::string grid_gen_type_str = "ritterNovak";
  size_t p = 3;
  sgpp::optimization::RandomNumberGenerator::SeedType seed = 0;

  // parse program arguments
  parseArgs(argc, argv, d, problem, problem_str, grid_type, grid_type_str, grid_gen_type, grid_gen_type_str,
            gamma, N, m, n, input, p, seed);

  // create grid, fuzzy input, and iterative grid generator
  std::unique_ptr<sgpp::base::Grid> grid =
    getGrid(grid_type, d, p);
  std::vector<std::unique_ptr<const sgpp::optimization::FuzzyInterval>> xFuzzy;
  getFuzzyInput(input, d, xFuzzy);
  std::vector<const sgpp::optimization::FuzzyInterval*> xFuzzyPtr;

  for (size_t t = 0; t < xFuzzy.size(); t++) {
    xFuzzyPtr.push_back(xFuzzy[t].get());
  }

  std::unique_ptr<sgpp::optimization::IterativeGridGenerator> grid_gen;

  if (grid_gen_type != GridGeneratorType::Regular) {
    grid_gen =
      getGridGenerator(grid_gen_type, *problem, *grid, N, gamma, m, xFuzzyPtr);
  }

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
  sgpp::optimization::ScalarFunction& f = problem->getObjectiveFunction();

  // print settings
  std::cerr << "Settings:\n";
  std::cerr << "d = " << d << "\n";
  std::cerr << "problem = " << problem_str << "\n";
  std::cerr << "grid = " << grid_type_str << "\n";
  std::cerr << "gridGen = " << grid_gen_type_str << "\n";
  std::cerr << "gamma = " << gamma << "\n";
  std::cerr << "N = " << N << "\n";
  std::cerr << "m = " << m << "\n";
  std::cerr << "n = " << n << "\n";
  std::cerr << "p = " << p << "\n";
  std::cerr << "seed = " << std::to_string(seed) << "\n\n";

  sgpp::optimization::operator<<(std::cerr << "displacement = ", displacement) << "\n";
  sgpp::optimization::operator<<(std::cerr << "x_opt = ", x_opt) << "\n";
  std::cerr << "f(x_opt) = " << f_x_opt << "\n\n";

  // GRID GENERATION

  printLine();
  std::cerr << "Generating grid...\n\n";

  sgpp::base::DataVector function_values;

  if (grid_gen_type == GridGeneratorType::Regular) {
    grid->getGenerator().regular(n);
    sgpp::base::DataVector x(d);
    function_values.resize(grid->getSize());

    for (size_t k = 0; k < grid->getSize(); k++) {
      grid->getStorage()[k].getStandardCoordinates(x);
      function_values[k] = f.eval(x);
    }
  } else if (grid_gen_type == GridGeneratorType::RitterNovak) {
    if (!grid_gen->generate()) {
      std::cerr << "Grid generation failed, exiting.\n";
      return 1;
    }

    function_values = grid_gen->getFunctionValues();
  } else {
    throw std::invalid_argument("Grid generator type not supported.");
  }

  // HIERARCHISATION

  printLine();
  std::cerr << "Hierarchising...\n\n";
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

  std::cerr << "Linear hierarchisation...\n\n";
  std::unique_ptr<sgpp::base::Grid> grid_linear;
  std::unique_ptr<sgpp::optimization::InterpolantScalarFunction> ft_linear;

  if (!getLinearInterpolant(grid_type, d, *grid, function_values, grid_linear, ft_linear)) {
    std::cerr << "Couldn't determine linear interpolant, exiting\n";
    return 1;
  }

  // OPTIMIZATION

  printLine();

  std::cerr << "Optimizing...\n\n";
  sgpp::optimization::InterpolantScalarFunction ft(*grid, coeffs);
  sgpp::optimization::InterpolantScalarFunctionGradient ft_gradient(*grid, coeffs);

  std::vector<std::string> optimizer_str =
  {"smoothInterpolant", "linearInterpolant", "objectiveFunction"};
  std::vector<std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>> optimizer_y_fuzzy;
  std::vector<double> optimizer_times;

  // optimize and measure times
  for (size_t k = 0; k < 3; k++) {
    std::chrono::time_point<std::chrono::system_clock> start_time =
      std::chrono::system_clock::now();

    switch (k) {
    case 0:
      // optimization of smooth interpolant
      optimizer_y_fuzzy.emplace_back();
      optimizeSmoothIntp(ft, ft_gradient, m, xFuzzyPtr, optimizer_y_fuzzy[k]);
      break;
    case 1:
      // optimization of linear interpolant
      optimizer_y_fuzzy.emplace_back();
      optimizeLinearIntp(*ft_linear, m, xFuzzyPtr, optimizer_y_fuzzy[k]);
      break;
    case 2:
      // optimization of objective function
      optimizer_y_fuzzy.emplace_back();
      optimizeObjFcn(f, m, xFuzzyPtr, optimizer_y_fuzzy[k]);
      break;
    default:
      break;
    }

    std::chrono::duration<double> duration = std::chrono::system_clock::now() - start_time;
    optimizer_times.push_back(duration.count());
  }

  // CALCULATION OF ERRORS

  std::vector<double> optimizer_fuzzy_errors;

  for (size_t i = 0; i < optimizer_y_fuzzy.size(); i++) {
    optimizer_fuzzy_errors.push_back(
        optimizer_y_fuzzy[2]->approximateRelativeL2Error(
          *optimizer_y_fuzzy[i]));
  }

  /*printLine();
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
  std::cerr << "\n";*/

  // WRITE RESULTS TO STDOUT

  std::cout << std::scientific << std::setprecision(16);
  std::cout << "{\n";

  for (size_t i = 0; i < optimizer_y_fuzzy.size(); i++) {
    std::cout << "  \"" << optimizer_str[i] << "\" : {\n";
    sgpp::optimization::operator<<(std::cout << "    \"yFuzzyXData\" : ",
                                   optimizer_y_fuzzy[i]->getXData()) << ",\n";
    sgpp::optimization::operator<<(std::cout << "    \"yFuzzyAlphaData\" : ",
                                   optimizer_y_fuzzy[i]->getAlphaData()) << ",\n";
    std::cout << "    \"fuzzyError\" : " << optimizer_fuzzy_errors[i] << ",\n";
    std::cout << "    \"runtime\" : " << optimizer_times[i] << "\n";
    std::cout << "  }" << ((i < optimizer_y_fuzzy.size() - 1) ? "," : "") << "\n";
  }

  std::cout << "}\n";

  // TERMINATION

  printLine();
  std::cerr << "\noptimizeFuzzy program terminated.\n";

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
               size_t& d, std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>& problem,
               std::string& problem_str,
               GridType& grid_type, std::string& grid_type_str,
               GridGeneratorType& grid_gen_type, std::string& grid_gen_type_str,
               double& gamma, size_t& N, size_t& m, size_t& n, size_t& input,
               size_t& p,
               sgpp::optimization::RandomNumberGenerator::SeedType& seed) {
  std::vector<std::string> test_problem_strs = {
    "absoluteValue", "ackley", "alpine02", "beale", "branin01", "branin02", "bubbleWrap", "easomYang", "eggHolder", "goldsteinPrice",
    "griewank", "hartman3", "hartman6", "himmelblau", "hoelderTable", "increasingPower",
    "michalewicz", "mladineo", "perm", "rastrigin", "rosenbrock",
    "schwefel06", "schwefel22", "schwefel26", "shcb", "sphere", "tremblingParabola",
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

      if (arg == "regular") {
        grid_gen_type = GridGeneratorType::Regular;
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
      // number of alpha segments
    } else if (arg.find("m=") == 0) {
      arg = arg.substr(2, std::string::npos);
      m = std::stoi(arg);
      // level of the regular sparse grid
    } else if (arg.find("n=") == 0) {
      arg = arg.substr(2, std::string::npos);
      n = std::stoi(arg);
      // B-spline degree
    } else if (arg.find("p=") == 0) {
      arg = arg.substr(2, std::string::npos);
      p = std::stoi(arg);
      // fuzzy input preset index
    } else if (arg.find("input=") == 0) {
      arg = arg.substr(6, std::string::npos);
      input = std::stoi(arg);
      // RNG seed
    } else if (arg.find("seed=") == 0) {
      arg = arg.substr(5, std::string::npos);
      seed = std::stol(arg);
    }
  }

  // create test function object, overriding d for some functions with fixed dimension
  if (problem_str == "absoluteValue") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::AbsoluteValue(d));
  } else if (problem_str == "ackley") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Ackley(d));
  } else if (problem_str == "alpine02") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Alpine02(d));
  } else if (problem_str == "beale") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Beale());
    d = 2;
  } else if (problem_str == "branin01") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Branin01());
    d = 2;
  } else if (problem_str == "branin02") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Branin02());
    d = 2;
  } else if (problem_str == "bubbleWrap") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::BubbleWrap(d));
  } else if (problem_str == "easomYang") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::EasomYang(d));
  } else if (problem_str == "eggHolder") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Eggholder());
    d = 2;
  } else if (problem_str == "goldsteinPrice") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::GoldsteinPrice());
    d = 2;
  } else if (problem_str == "griewank") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Griewank(d));
  } else if (problem_str == "hartman3") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Hartman3());
    d = 3;
  } else if (problem_str == "hartman6") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Hartman6());
    d = 6;
  } else if (problem_str == "himmelblau") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Himmelblau());
    d = 2;
  } else if (problem_str == "hoelderTable") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::HoelderTable());
    d = 2;
  } else if (problem_str == "increasingPower") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::IncreasingPower(d));
  } else if (problem_str == "michalewicz") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Michalewicz());
    d = 2;
  } else if (problem_str == "mladineo") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Mladineo());
    d = 2;
  } else if (problem_str == "perm") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Perm(d));
  } else if (problem_str == "rastrigin") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Rastrigin(d));
  } else if (problem_str == "rosenbrock") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Rosenbrock(d));
  } else if (problem_str == "schwefel06") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Schwefel06());
    d = 2;
  } else if (problem_str == "schwefel22") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Schwefel22(d));
  } else if (problem_str == "schwefel26") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Schwefel26(d));
  } else if (problem_str == "shcb") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::SHCB());
    d = 2;
  } else if (problem_str == "sphere") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::Sphere(d));
  } else if (problem_str == "tremblingParabola") {
    problem = std::unique_ptr<sgpp::optimization::test_problems::UnconstrainedTestProblem>(
          new sgpp::optimization::test_problems::TremblingParabola(d, 3));
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


void getFuzzyInput(size_t input,
                   size_t d,
                   std::vector<std::unique_ptr<const sgpp::optimization::FuzzyInterval>>& xFuzzy) {
  xFuzzy.clear();

  switch (input) {
    case 0:
      for (size_t t = 0; t < d; t++) {
        if (t % 2 == 0) {
          xFuzzy.emplace_back(new sgpp::optimization::TriangularFuzzyInterval(
              0.25, 0.375, 0.125, 0.25));
        } else {
          xFuzzy.emplace_back(new sgpp::optimization::QuasiGaussianFuzzyNumber(
              0.5, 0.125, 3.0));
        }
      }

      break;
    default:
      throw std::invalid_argument("Fuzzy input index not supported.");
  }
}

std::unique_ptr<sgpp::optimization::IterativeGridGenerator> getGridGenerator(
  GridGeneratorType grid_gen_type,
  sgpp::optimization::test_problems::UnconstrainedTestProblem& problem,
  sgpp::base::Grid& grid,
  size_t N,
  double gamma,
  size_t m,
  const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr) {
  sgpp::optimization::test_problems::TestScalarFunction& f = problem.getObjectiveFunction();
  std::unique_ptr<sgpp::optimization::IterativeGridGenerator> grid_gen;

  if (grid_gen_type == GridGeneratorType::RitterNovak) {
    grid_gen = std::unique_ptr<sgpp::optimization::IterativeGridGenerator>(
                 new sgpp::optimization::IterativeGridGeneratorFuzzyRitterNovak(f, grid, N, xFuzzyPtr, m, gamma));
  } else {
    throw std::invalid_argument("Grid generator type not supported.");
  }

  return grid_gen;
}

bool getLinearInterpolant(GridType grid_type, size_t d,
                          sgpp::base::Grid& grid,
                          sgpp::base::DataVector function_values,
                          std::unique_ptr<sgpp::base::Grid>& grid_linear,
                          std::unique_ptr<sgpp::optimization::InterpolantScalarFunction>& ft_linear) {
  sgpp::base::GridStorage& grid_storage = grid.getStorage();

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

void optimizeSmoothIntp(
    sgpp::optimization::InterpolantScalarFunction& ft,
    sgpp::optimization::InterpolantScalarFunctionGradient& ft_gradient,
    size_t m,
    const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr,
    std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>& yFuzzy) {
  const size_t numberOfMultiStartPoints      = 100;
  const size_t numberOfMultiStartEvaluations = 500 * numberOfMultiStartPoints;
  sgpp::optimization::optimizer::AdaptiveGradientDescent optimizerLocal(
      ft, ft_gradient);
  sgpp::optimization::optimizer::MultiStart optimizer(
      optimizerLocal,
      numberOfMultiStartEvaluations, numberOfMultiStartPoints);
  sgpp::optimization::FuzzyExtensionPrincipleViaOptimization extensionPrinciple(optimizer, m);
  yFuzzy.reset(dynamic_cast<sgpp::optimization::InterpolatedFuzzyInterval*>(
      extensionPrinciple.apply(xFuzzyPtr)));
}

void optimizeLinearIntp(
    sgpp::optimization::InterpolantScalarFunction& ft_linear,
    size_t m,
    const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr,
    std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>& yFuzzy) {
  const size_t numberOfMultiStartPoints      = 100;
  const size_t numberOfMultiStartEvaluations = 500 * numberOfMultiStartPoints;
  sgpp::optimization::optimizer::MultiStart optimizer(
      ft_linear, numberOfMultiStartEvaluations, numberOfMultiStartPoints);
  sgpp::optimization::FuzzyExtensionPrincipleViaOptimization extensionPrinciple(optimizer, m);
  yFuzzy.reset(dynamic_cast<sgpp::optimization::InterpolatedFuzzyInterval*>(
      extensionPrinciple.apply(xFuzzyPtr)));
}

void optimizeObjFcn(
    sgpp::optimization::ScalarFunction& f,
    size_t m,
    const std::vector<const sgpp::optimization::FuzzyInterval*>& xFuzzyPtr,
    std::unique_ptr<sgpp::optimization::InterpolatedFuzzyInterval>& yFuzzy) {
  const size_t numberOfMultiStartPoints      = 1000;
  const size_t numberOfMultiStartEvaluations = 2000 * numberOfMultiStartPoints;
  sgpp::optimization::optimizer::MultiStart optimizer(
      f, numberOfMultiStartEvaluations, numberOfMultiStartPoints);
  sgpp::optimization::FuzzyExtensionPrincipleViaOptimization extensionPrinciple(optimizer, m);
  yFuzzy.reset(dynamic_cast<sgpp::optimization::InterpolatedFuzzyInterval*>(
      extensionPrinciple.apply(xFuzzyPtr)));
}
