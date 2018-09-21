#include <cmath>
#include <biomech2_interface/momentum/Momentum.hpp>
#include <biomech2_interface/momentum/MomentumGradient.hpp>

namespace biomech2_interface {
  namespace momentum {
    MomentumGradient::MomentumGradient(
        double F,
        sgpp::optimization::VectorFunctionGradient& TBGradient) :
      sgpp::optimization::ScalarFunctionGradient(3),
      F(F),
      TBGradient(TBGradient),
      tbResult(2),
      tbGradientResult(2, 3) {
    }

    double MomentumGradient::eval(const sgpp::base::DataVector& x,
                                         sgpp::base::DataVector& gradient) {
      if ((x[0] < 0.0) || (x[0] > 1.0) ||
          (x[1] < 0.0) || (x[1] > 1.0) ||
          (x[2] < 0.0) || (x[2] > 1.0)) {
        gradient.setAll(NAN);
        return INFINITY;
      }

      TBGradient.eval(x, tbResult, tbGradientResult);

      const double& T = tbResult[0];
      const double& B = tbResult[1];

      const double& TGradientTheta = tbGradientResult(0, 0);
      const double& TGradientAlphaT = tbGradientResult(0, 1);
      const double& TGradientAlphaB = tbGradientResult(0, 2);

      const double& BGradientTheta = tbGradientResult(1, 0);
      const double& BGradientAlphaT = tbGradientResult(1, 1);
      const double& BGradientAlphaB = tbGradientResult(1, 2);

      const double thetaRange = THETA_MAX - THETA_MIN;
      const double theta = x[0] * thetaRange + THETA_MIN;

      const double lT = Momentum::lT(theta);
      const double lB = Momentum::lB(theta);
      const double lF = Momentum::lF(theta);

      const double lTGrad = thetaRange * lTGradient(theta);
      const double lBGrad = thetaRange * lBGradient(theta);
      const double lFGrad = thetaRange * lFGradient(theta);

      const double M = T * lT + F * lF + B * lB;

      gradient[0] =
          (TGradientTheta * lT + T * lTGrad) +
          F * lFGrad +
          (BGradientTheta * lB + B * lBGrad);
      gradient[1] = TGradientAlphaT * lT + BGradientAlphaT * lB;
      gradient[2] = TGradientAlphaB * lT + BGradientAlphaB * lB;

      return M;
    }

    void MomentumGradient::clone(
        std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>(
          new MomentumGradient(*this));
    }

    double MomentumGradient::lTGradient(double theta) {
      return (-1.8798e-3 * theta + 0.1126) / 1000.0;
    }

    double MomentumGradient::lBGradient(double theta) {
      return (-2.964e-3 * theta + 0.1776) / 1000.0;
    }

    double MomentumGradient::lFGradient(double theta) {
      constexpr double L_F = 0.2825;
      return std::cos(theta * M_PI / 180.0) * L_F * M_PI / 180.0;
    }
  }
}
