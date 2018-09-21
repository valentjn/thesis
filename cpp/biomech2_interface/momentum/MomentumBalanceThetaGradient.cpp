#include <cmath>
#include <biomech2_interface/momentum/MomentumBalanceThetaGradient.hpp>

namespace biomech2_interface {
  namespace momentum {
    MomentumBalanceThetaGradient::MomentumBalanceThetaGradient(
        MomentumBalanceTheta& momentumBalanceTheta,
        MomentumGradient& momentumGradient) :
      sgpp::optimization::ScalarFunctionGradient(2),
      momentumBalanceTheta(momentumBalanceTheta),
      momentumGradient(momentumGradient),
      y(3),
      momentumGradientY(3),
      evalCounter(0) {
    }

    double MomentumBalanceThetaGradient::eval(
        const sgpp::base::DataVector& x,
        sgpp::base::DataVector& gradient) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
        gradient.setAll(NAN);
        return INFINITY;
      }

      evalCounter++;

      const double theta = momentumBalanceTheta.eval(x);

      y[0] = (theta - THETA_MIN) / (THETA_MAX - THETA_MIN);
      y[1] = x[0];
      y[2] = x[1];

      momentumGradient.eval(y, momentumGradientY);
      gradient[0] = -momentumGradientY[1] / momentumGradientY[0] *
          (THETA_MAX - THETA_MIN);
      gradient[1] = -momentumGradientY[2] / momentumGradientY[0] *
          (THETA_MAX - THETA_MIN);

      return theta;
    }

    void MomentumBalanceThetaGradient::clone(
        std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>(
          new MomentumBalanceThetaGradient(*this));
    }

    size_t MomentumBalanceThetaGradient::getEvalCounter() const {
      return evalCounter;
    }

    void MomentumBalanceThetaGradient::resetEvalCounter() {
      evalCounter = 0;
    }
  }
}
