#include <cmath>
#include <biomech2_interface/objectives/distance/DistanceObjectiveGradient.hpp>

namespace muscle {
  namespace objectives {
    namespace distance {
      DistanceObjectiveGradient::DistanceObjectiveGradient(
          double alphaTOld,
          double alphaBOld) :
          sgpp::optimization::ScalarFunctionGradient(2),
          alphaTOld(alphaTOld),
          alphaBOld(alphaBOld) {
      }

      double DistanceObjectiveGradient::eval(
          const sgpp::base::DataVector& x,
          sgpp::base::DataVector& gradient) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          gradient.setAll(NAN);
          return INFINITY;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;

        gradient[0] = 2.0 * (alphaT - alphaTOld) * (ALPHA_MAX - ALPHA_MIN);
        gradient[1] = 2.0 * (alphaB - alphaBOld) * (ALPHA_MAX - ALPHA_MIN);

        return std::pow(alphaT - alphaTOld, 2.0) +
            std::pow(alphaB - alphaBOld, 2.0);
      }

      void DistanceObjectiveGradient::clone(
          std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>(
            new DistanceObjectiveGradient(*this));
      }
    }
  }
}
