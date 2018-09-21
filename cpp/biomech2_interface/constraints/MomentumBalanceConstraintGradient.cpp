#include <cmath>
#include <biomech2_interface/constraints/MomentumBalanceConstraintGradient.hpp>

namespace biomech2_interface {
  namespace constraints {
    MomentumBalanceConstraintGradient::MomentumBalanceConstraintGradient(
        momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient,
        double targetTheta) :
            sgpp::optimization::VectorFunctionGradient(2, 1),
            momentumBalanceThetaGradient(momentumBalanceThetaGradient),
            targetTheta(targetTheta) {
    }

    void MomentumBalanceConstraintGradient::eval(
        const sgpp::base::DataVector& x,
        sgpp::base::DataVector& value,
        sgpp::base::DataMatrix& gradient) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
        value.setAll(INFINITY);
        gradient.setAll(NAN);
        return;
      }

      sgpp::base::DataVector fxGradient(2);
      const double fx = momentumBalanceThetaGradient.eval(x, fxGradient);
      value[0] = fx - targetTheta;
      gradient.setRow(0, fxGradient);
    }

    void MomentumBalanceConstraintGradient::clone(
        std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunctionGradient>(
          new MomentumBalanceConstraintGradient(*this));
    }
  }
}
