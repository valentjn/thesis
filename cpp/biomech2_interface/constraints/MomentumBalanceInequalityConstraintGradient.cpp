#include <biomech2_interface/constraints/MomentumBalanceInequalityConstraintGradient.hpp>

namespace biomech2_interface {
  namespace constraints {
    MomentumBalanceInequalityConstraintGradient::MomentumBalanceInequalityConstraintGradient(
        sgpp::optimization::VectorFunctionGradient& fGradient) :
            sgpp::optimization::VectorFunctionGradient(
                fGradient.getNumberOfParameters(),
                2 * fGradient.getNumberOfComponents()),
            fGradient(fGradient) {
    }

    void MomentumBalanceInequalityConstraintGradient::eval(
        const sgpp::base::DataVector& x,
        sgpp::base::DataVector& value,
        sgpp::base::DataMatrix& gradient) {
      sgpp::base::DataVector fx(m / 2);
      sgpp::base::DataMatrix fxGradient(m / 2, d);
      fGradient.eval(x, fx, fxGradient);

      for (size_t k = 0; k < m / 2; k++) {
        value[2 * k] = fx[k];
        value[2 * k + 1] = -fx[k];

        for (size_t t = 0; t < d; t++) {
          gradient(2 * k, t) = fxGradient(k, t);
          gradient(2 * k + 1, t) = -fxGradient(k, t);
        }
      }
    }

    void MomentumBalanceInequalityConstraintGradient::clone(
        std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunctionGradient>(
          new MomentumBalanceInequalityConstraintGradient(*this));
    }
  }
}
