#include <cmath>
#include <biomech2_interface/constraints/MomentumBalanceConstraint.hpp>

namespace muscle {
  namespace constraints {
    MomentumBalanceConstraint::MomentumBalanceConstraint(
        momentum::MomentumBalanceTheta& momentumBalanceTheta,
        double targetTheta) :
            sgpp::optimization::VectorFunction(2, 1),
            momentumBalanceTheta(momentumBalanceTheta),
            targetTheta(targetTheta) {
    }

    void MomentumBalanceConstraint::eval(
        const sgpp::base::DataVector& x,
        sgpp::base::DataVector& value) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
        value.setAll(INFINITY);
        return;
      }

      value[0] = momentumBalanceTheta.eval(x) - targetTheta;
    }

    void MomentumBalanceConstraint::clone(
        std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunction>(
          new MomentumBalanceConstraint(*this));
    }
  }
}
