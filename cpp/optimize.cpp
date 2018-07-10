#include <iostream>

#include <sgpp_base.hpp>
#include <sgpp_optimization.hpp>

int main() {
  sgpp::optimization::test_problems::Branin02Objective f;
  std::cout << "Hello World!\n";
  std::cout << f.getNumberOfParameters() << "\n";
  return 0;
}
