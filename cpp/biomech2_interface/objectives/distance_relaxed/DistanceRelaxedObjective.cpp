#include <cmath>
#include <biomech2_interface/objectives/distance_relaxed/DistanceRelaxedObjective.hpp>

namespace muscle {
  namespace objectives {
    namespace distance_relaxed {
      DistanceRelaxedObjective::DistanceRelaxedObjective(
          momentum::MomentumBalanceTheta& momentumBalanceTheta,
          double alphaTOld,
          double alphaBOld,
          double targetThetaOld,
          double c) :
          sgpp::optimization::ScalarFunction(2),
          momentumBalanceTheta(momentumBalanceTheta),
          alphaTOld(alphaTOld),
          alphaBOld(alphaBOld),
          targetThetaOld(targetThetaOld),
          c(c) {
      }

      double DistanceRelaxedObjective::eval(
          const sgpp::base::DataVector& x) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          return INFINITY;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double theta = momentumBalanceTheta.eval(x);

        return std::pow(alphaT - alphaTOld, 2.0) +
            std::pow(alphaB - alphaBOld, 2.0) +
            std::pow(c * (theta - targetThetaOld), 2.0);
      }

      void DistanceRelaxedObjective::clone(
          std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::ScalarFunction>(
            new DistanceRelaxedObjective(*this));
      }
    }
  }
}
