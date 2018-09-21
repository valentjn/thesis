#include <cmath>
#include <biomech2_interface/momentum/Momentum.hpp>

namespace muscle {
  namespace momentum {
    Momentum::Momentum(double F,
                       sgpp::optimization::VectorFunction& TB) :
      sgpp::optimization::ScalarFunction(3),
      F(F),
      TB(TB),
      tbResult(2) {
    }

    double Momentum::eval(const sgpp::base::DataVector& x) {
      if ((x[0] < 0.0) || (x[0] > 1.0) ||
          (x[1] < 0.0) || (x[1] > 1.0) ||
          (x[2] < 0.0) || (x[2] > 1.0)) {
        return INFINITY;
      }

      TB.eval(x, tbResult);
      const double T = tbResult[0];
      const double B = tbResult[1];

      const double theta = x[0] * (THETA_MAX - THETA_MIN) + THETA_MIN;
      return T * lT(theta) + F * lF(theta) + B * lB(theta);
    }

    void Momentum::clone(
        std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::ScalarFunction>(
          new Momentum(*this));
    }

    double Momentum::lT(double theta) {
      return (-9.399e-4 * theta * theta + 0.1126 * theta + 22.21) / 1000.0;
    }

    double Momentum::lB(double theta) {
      return (-1.482e-3 * theta * theta + 0.1776 * theta + 35.02) / 1000.0;
    }

    double Momentum::lF(double theta) {
      constexpr double L_F = 0.2825;
      return std::sin(theta * M_PI / 180.0) * L_F;
    }
  }
}
