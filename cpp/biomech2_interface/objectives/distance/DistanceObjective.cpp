#include <cmath>
#include <biomech2_interface/objectives/distance/DistanceObjective.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace distance {
      DistanceObjective::DistanceObjective(
          double alphaTOld,
          double alphaBOld) :
          sgpp::optimization::ScalarFunction(2),
          alphaTOld(alphaTOld),
          alphaBOld(alphaBOld) {
      }

      double DistanceObjective::eval(
          const sgpp::base::DataVector& x) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          return INFINITY;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;

        return std::pow(alphaT - alphaTOld, 2.0) +
            std::pow(alphaB - alphaBOld, 2.0);
      }

      void DistanceObjective::clone(
          std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::ScalarFunction>(
            new DistanceObjective(*this));
      }
    }
  }
}
