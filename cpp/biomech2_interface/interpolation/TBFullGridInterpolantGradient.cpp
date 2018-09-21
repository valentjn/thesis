#include <cmath>
#include <biomech2_interface/interpolation/TBFullGridInterpolantGradient.hpp>

namespace biomech2_interface {
  namespace interpolation {
    TBFullGridInterpolantGradient::TBFullGridInterpolantGradient() :
      sgpp::optimization::VectorFunctionGradient(3, 2),
      intpT(TBFullGridInterpolant::THETA_COUNT,
            TBFullGridInterpolant::ALPHA_COUNT,
            THETA_MIN, TBFullGridInterpolant::THETA_STEP,
            ALPHA_MIN, TBFullGridInterpolant::ALPHA_STEP,
            &TBFullGridInterpolant::T_DATA[0], false),
      intpB(TBFullGridInterpolant::THETA_COUNT,
            TBFullGridInterpolant::ALPHA_COUNT,
            THETA_MIN, TBFullGridInterpolant::THETA_STEP,
            ALPHA_MIN, TBFullGridInterpolant::ALPHA_STEP,
            &TBFullGridInterpolant::B_DATA[0], false),
            evalCounter(0) {
      }

    void TBFullGridInterpolantGradient::eval(const sgpp::base::DataVector& x,
                                           sgpp::base::DataVector& value,
                                           sgpp::base::DataMatrix& gradient) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0) ||
          (x[2] < 0.0) || (x[2] > 1.0)) {
        value.setAll(INFINITY);
        gradient.setAll(NAN);
        return;
      }

      evalCounter++;

      const double thetaRange = THETA_MAX - THETA_MIN;
      const double alphaRange = ALPHA_MAX - ALPHA_MIN;
      const double theta = x[0] * thetaRange + THETA_MIN;
      const double alphaT = x[1] * alphaRange + ALPHA_MIN;
      const double alphaB = x[2] * alphaRange + ALPHA_MIN;

      value[0] = intpT(theta, alphaT);
      value[1] = intpB(theta, alphaB);
      gradient(0, 0) = thetaRange * intpT(1, 0, theta, alphaT);
      gradient(0, 1) = alphaRange * intpT(0, 1, theta, alphaT);
      gradient(0, 2) = alphaRange * 0.0;
      gradient(1, 0) = thetaRange * intpB(1, 0, theta, alphaB);
      gradient(1, 1) = alphaRange * 0.0;
      gradient(1, 2) = alphaRange * intpB(0, 1, theta, alphaB);
    }

    void TBFullGridInterpolantGradient::clone(
        std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunctionGradient>(
          new TBFullGridInterpolantGradient(*this));
    }

    size_t TBFullGridInterpolantGradient::getEvalCounter() const {
      return evalCounter;
    }

    void TBFullGridInterpolantGradient::resetEvalCounter() {
      evalCounter = 0;
    }
  }
}
