#include <cmath>
#include <biomech2_interface/objectives/activation_sum/ActivationSumObjective.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace activation_sum {
      ActivationSumObjective::ActivationSumObjective() :
          sgpp::optimization::ScalarFunction(2) {
      }

      double ActivationSumObjective::eval(
          const sgpp::base::DataVector& x) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          return INFINITY;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;

        return alphaT + alphaB;
      }

      void ActivationSumObjective::clone(
          std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::ScalarFunction>(
            new ActivationSumObjective(*this));
      }
    }
  }
}
