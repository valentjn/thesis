#include <cmath>
#include <biomech2_interface/momentum/NewtonsMethod.hpp>

namespace biomech2_interface {
  namespace momentum {
    NewtonsMethod::NewtonsMethod(
        sgpp::optimization::ScalarFunction& f,
        sgpp::optimization::ScalarFunctionGradient& fGradient,
        size_t t) :
          UnconstrainedOptimizer(f, &fGradient, nullptr, 100),
          t(t),
          x(f.getNumberOfParameters()),
          fxGradient(f.getNumberOfParameters()),
          k(0) {
    }

    void NewtonsMethod::optimize() {
      xOpt.resize(0);
      fOpt = NAN;

      x = x0;
      double fx = fGradient->eval(x, fxGradient);
      k = 0;

      while (k < N) {
        //std::cout << "k = " << k << ": x = " << x.toString() << ", fx = "
        //          << fx << ", fxGradient = " << fxGradient.toString() << "\n";

        x[t] -= fx / fxGradient[t];
        x[t] = std::min(std::max(x[t], 0.0), 1.0);

        fx = fGradient->eval(x, fxGradient);
        k++;

        if ((std::abs(fx) < 1e-9) || (std::abs(fxGradient[t]) < 1e-9)) {
          break;
        }
      }

      xOpt.resize(x.getSize());
      xOpt = x;
      fOpt = fx;
    }

    size_t NewtonsMethod::getNumberOfIterations() const {
      return k;
    }

    void NewtonsMethod::clone(std::unique_ptr<sgpp::optimization::
                              optimizer::UnconstrainedOptimizer>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::optimizer::
          UnconstrainedOptimizer>(new NewtonsMethod(*this));
    }
  }
}
