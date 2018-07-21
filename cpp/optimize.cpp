#include <iostream>

#include <omp.h>

#include <sgpp_base.hpp>
#include <sgpp_optimization.hpp>

int main() {
  sgpp::optimization::test_problems::Branin02Objective f;
  std::cout << "Hello World!\n";
  std::cout << f.getNumberOfParameters() << "\n";
  
  sgpp::optimization::Printer::getInstance().setVerbosity(2);
  omp_set_num_threads(4);
  
  std::unique_ptr<sgpp::base::Grid> grid(
      sgpp::base::Grid::createBsplineBoundaryGrid(2, 1, 0));
  grid->getGenerator().regular(5);
  sgpp::base::DataVector fX(grid->getSize(), 2.0);
  sgpp::optimization::HierarchisationSLE hierarchisationSLE(*grid);
  sgpp::optimization::sle_solver::UMFPACK sleSolver;
  sgpp::base::DataVector aX(grid->getSize(), 3.0);
  sleSolver.solve(hierarchisationSLE, fX, aX);
  
  return 0;
}
