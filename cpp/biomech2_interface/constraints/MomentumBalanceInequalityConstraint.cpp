#include <biomech2_interface/constraints/MomentumBalanceInequalityConstraint.hpp>

namespace biomech2_interface {
  namespace constraints {
    MomentumBalanceInequalityConstraint::MomentumBalanceInequalityConstraint(
        sgpp::optimization::VectorFunction& f) :
            sgpp::optimization::VectorFunction(
                f.getNumberOfParameters(), 2 * f.getNumberOfComponents()),
            f(f) {
    }

    void MomentumBalanceInequalityConstraint::eval(
        const sgpp::base::DataVector& x,
        sgpp::base::DataVector& value) {
      sgpp::base::DataVector fx(m / 2);
      f.eval(x, fx);

      for (size_t k = 0; k < m / 2; k++) {
        value[2 * k] = fx[k];
        value[2 * k + 1] = -fx[k];
      }
    }

    void MomentumBalanceInequalityConstraint::clone(
        std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunction>(
          new MomentumBalanceInequalityConstraint(*this));
    }
  }
}
