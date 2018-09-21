#include <cmath>
#include <biomech2_interface/objectives/activation_sum/ActivationSumObjectiveGradient.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace activation_sum {
      ActivationSumObjectiveGradient::ActivationSumObjectiveGradient() :
          sgpp::optimization::ScalarFunctionGradient(2) {
      }

      double ActivationSumObjectiveGradient::eval(
          const sgpp::base::DataVector& x,
          sgpp::base::DataVector& gradient) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          gradient.setAll(NAN);
          return INFINITY;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;

        gradient[0] = ALPHA_MAX - ALPHA_MIN;
        gradient[1] = ALPHA_MAX - ALPHA_MIN;

        return alphaT + alphaB;
      }

      void ActivationSumObjectiveGradient::clone(
          std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>(
            new ActivationSumObjectiveGradient(*this));
      }
    }
  }
}
