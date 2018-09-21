#include <cmath>
#include <biomech2_interface/interpolation/TBSparseGridInterpolantGradient.hpp>

namespace muscle {
  namespace interpolation {
    TBSparseGridInterpolantGradient::TBSparseGridInterpolantGradient(
        sgpp::base::Grid& grid,
        const sgpp::base::DataMatrix& alpha) :
          sgpp::optimization::VectorFunctionGradient(3, 2),
          grid(grid),
          alpha(alpha),
          fGradient(grid, alpha),
          y(2),
          fy(2),
          fyGradient(2, 2),
          evalCounter(0) {
    }

    void TBSparseGridInterpolantGradient::eval(const sgpp::base::DataVector& x,
              sgpp::base::DataVector& value,
              sgpp::base::DataMatrix& gradient) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0) ||
          (x[2] < 0.0) || (x[2] > 1.0)) {
        value.setAll(INFINITY);
        gradient.setAll(NAN);
        return;
      }

      evalCounter++;

      y[0] = x[0];
      y[1] = x[1];
      fGradient.eval(y, fy, fyGradient);
      value[0] = fy[0];
      gradient(0, 0) = fyGradient(0, 0);
      gradient(0, 1) = fyGradient(0, 1);
      gradient(0, 2) = 0.0;

      y[1] = x[2];
      fGradient.eval(y, fy, fyGradient);
      value[1] = fy[1];
      gradient(1, 0) = fyGradient(1, 0);
      gradient(1, 1) = 0.0;
      gradient(1, 2) = fyGradient(1, 1);
    }

    void TBSparseGridInterpolantGradient::clone(
        std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunctionGradient>(
          new TBSparseGridInterpolantGradient(grid, alpha));
    }

    size_t TBSparseGridInterpolantGradient::getEvalCounter() const {
      return evalCounter;
    }

    void TBSparseGridInterpolantGradient::resetEvalCounter() {
      evalCounter = 0;
    }
  }
}
