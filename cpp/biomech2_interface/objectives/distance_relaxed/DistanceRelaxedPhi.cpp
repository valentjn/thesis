#include <cmath>
#include <biomech2_interface/objectives/distance_relaxed/DistanceRelaxedPhi.hpp>

namespace muscle {
  namespace objectives {
    namespace distance_relaxed {
      DistanceRelaxedPhi::DistanceRelaxedPhi(
          momentum::MomentumBalanceTheta& momentumBalanceTheta,
          double alphaTOld,
          double alphaBOld,
          double targetThetaOld,
          double c) :
          sgpp::optimization::VectorFunction(2, 3),
          momentumBalanceTheta(momentumBalanceTheta),
          alphaTOld(alphaTOld),
          alphaBOld(alphaBOld),
          targetThetaOld(targetThetaOld),
          c(c) {
      }

      void DistanceRelaxedPhi::eval(const sgpp::base::DataVector& x,
                                    sgpp::base::DataVector& value) {
        if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
          value.setAll(INFINITY);
          return;
        }

        const double alphaT = x[0] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double alphaB = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
        const double theta = momentumBalanceTheta.eval(x);

        value[0] = alphaT - alphaTOld;
        value[1] = alphaB - alphaBOld;
        value[2] = c * (theta - targetThetaOld);
      }

      void DistanceRelaxedPhi::clone(
          std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const {
        clone = std::unique_ptr<sgpp::optimization::VectorFunction>(
            new DistanceRelaxedPhi(*this));
      }
    }
  }
}
