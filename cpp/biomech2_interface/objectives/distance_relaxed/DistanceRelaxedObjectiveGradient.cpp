#include <cmath>
#include <biomech2_interface/objectives/distance_relaxed/DistanceRelaxedObjectiveGradient.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace distance_relaxed {
      DistanceRelaxedObjectiveGradient::DistanceRelaxedObjectiveGradient(
          momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient,
          double alphaTOld,
          double alphaBOld,
          double targetThetaOld,
          double c) :
          sgpp::optimization::ScalarFunctionGradient(2),
          momentumBalanceThetaGradient(momentumBalanceThetaGradient),
          alphaTOld(alphaTOld),
          alphaBOld(alphaBOld),
          targetThetaOld(targetThetaOld),
          c(c) {
      }

      double DistanceRelaxedObjectiveGradient::eval(
          const sgpp::base::DataVector& x,
          sgpp::base::DataVector& gradient) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          gradient.setAll(NAN);
          return INFINITY;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;

        sgpp::base::DataVector thetaGradient(2);
        const double theta =
            momentumBalanceThetaGradient.eval(x, thetaGradient);

        gradient[0] = 2.0 * (alphaT - alphaTOld) * (ALPHA_MAX - ALPHA_MIN) +
            2.0 * c * c * (theta - targetThetaOld) * thetaGradient[0];
        gradient[1] = 2.0 * (alphaB - alphaBOld) * (ALPHA_MAX - ALPHA_MIN) +
            2.0 * c * c * (theta - targetThetaOld) * thetaGradient[1];

        return std::pow(alphaT - alphaTOld, 2.0) +
            std::pow(alphaB - alphaBOld, 2.0) +
            std::pow(c * (theta - targetThetaOld), 2.0);
      }

      void DistanceRelaxedObjectiveGradient::clone(
          std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>(
            new DistanceRelaxedObjectiveGradient(*this));
      }
    }
  }
}
