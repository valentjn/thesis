#include <cmath>
#include <biomech2_interface/interpolation/TBSparseGridInterpolant.hpp>

namespace muscle {
  namespace interpolation {
    TBSparseGridInterpolant::TBSparseGridInterpolant(
        sgpp::base::Grid& grid,
        const sgpp::base::DataMatrix& alpha) :
          sgpp::optimization::VectorFunction(3, 2),
          grid(grid),
          alpha(alpha),
          f(grid, alpha),
          y(2),
          fy(2),
          evalCounter(0) {
    }

    void TBSparseGridInterpolant::eval(const sgpp::base::DataVector& x,
                                       sgpp::base::DataVector& value) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0) ||
          (x[2] < 0.0) || (x[2] > 1.0)) {
        value.setAll(INFINITY);
        return;
      }

      evalCounter++;

      y[0] = x[0];
      y[1] = x[1];
      f.eval(y, fy);
      value[0] = fy[0];

      y[1] = x[2];
      f.eval(y, fy);
      value[1] = fy[1];
    }

    void TBSparseGridInterpolant::clone(
        std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::VectorFunction>(
          new TBSparseGridInterpolant(grid, alpha));
    }

    size_t TBSparseGridInterpolant::getEvalCounter() const {
      return evalCounter;
    }

    void TBSparseGridInterpolant::resetEvalCounter() {
      evalCounter = 0;
    }
  }
}
