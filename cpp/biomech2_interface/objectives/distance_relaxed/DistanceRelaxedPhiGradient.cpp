#include <cmath>
#include <biomech2_interface/objectives/distance_relaxed/DistanceRelaxedPhiGradient.hpp>

namespace muscle {
  namespace objectives {
    namespace distance_relaxed {
      DistanceRelaxedPhiGradient::DistanceRelaxedPhiGradient(
          momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient,
          double alphaTOld,
          double alphaBOld,
          double targetThetaOld,
          double c) :
          sgpp::optimization::VectorFunctionGradient(2, 3),
          momentumBalanceThetaGradient(momentumBalanceThetaGradient),
          alphaTOld(alphaTOld),
          alphaBOld(alphaBOld),
          targetThetaOld(targetThetaOld),
          c(c) {
      }

      void DistanceRelaxedPhiGradient::eval(
          const sgpp::base::DataVector& x,
          sgpp::base::DataVector& value,
          sgpp::base::DataMatrix& gradient) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          value.setAll(INFINITY);
          gradient.setAll(NAN);
          return;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;

        sgpp::base::DataVector thetaGradient(2);
        const double theta =
            momentumBalanceThetaGradient.eval(x, thetaGradient);

        value[0] = alphaT - alphaTOld;
        value[1] = alphaB - alphaBOld;
        value[2] = c * (theta - targetThetaOld);

        gradient(0, 0) = ALPHA_MAX - ALPHA_MIN;
        gradient(0, 1) = 0.0;
        gradient(1, 0) = 0.0;
        gradient(1, 1) = ALPHA_MAX - ALPHA_MIN;
        gradient(2, 0) = c * thetaGradient[0];
        gradient(2, 1) = c * thetaGradient[1];
      }

      void DistanceRelaxedPhiGradient::clone(
          std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::VectorFunctionGradient>(
            new DistanceRelaxedPhiGradient(*this));
      }
    }
  }
}
