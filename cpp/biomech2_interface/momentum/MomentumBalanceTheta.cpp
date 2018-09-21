#include <cmath>
#include <biomech2_interface/momentum/Momentum.hpp>
#include <biomech2_interface/momentum/MomentumGradient.hpp>
#include <biomech2_interface/momentum/MomentumBalanceTheta.hpp>
#include <biomech2_interface/momentum/NewtonsMethod.hpp>

namespace muscle {
  namespace momentum {
    MomentumBalanceTheta::MomentumBalanceTheta(
        double F,
        sgpp::optimization::VectorFunction& TB,
        sgpp::optimization::VectorFunctionGradient& TBGradient) :
      sgpp::optimization::ScalarFunction(2),
      F(F),
      TB(TB),
      TBGradient(TBGradient),
      evalCounter(0),
      numberOfNewtonCalls(0),
      numberOfNewtonIterations(0) {
    }

    double MomentumBalanceTheta::eval(const sgpp::base::DataVector& x) {
      if ((x[0] < 0.0) || (x[0] > 1.0) || (x[1] < 0.0) || (x[1] > 1.0)) {
        return INFINITY;
      }

      evalCounter++;

      Momentum momentum(F, TB);
      MomentumGradient momentumGradient(F, TBGradient);

      const std::vector<double> theta0s = {0.5, 0.21428, 0.78572};

      /*SquaredFunction squaredMomentum(momentum);
      SquaredFunctionGradient squaredMomentumGradient(momentumGradient);
      sgpp::optimization::optimizer::AdaptiveGradientDescent
          optimizer(squaredMomentum, squaredMomentumGradient);*/

      NewtonsMethod optimizer(momentum, momentumGradient, 0);
      sgpp::base::DataVector x0DataVector(3);
      x0DataVector[1] = x[0];
      x0DataVector[2] = x[1];

      for (double theta0 : theta0s) {
        x0DataVector[0] = theta0;
        optimizer.setStartingPoint(x0DataVector);
        //std::cout << "x0 = " << x0DataVector.toString() << "\n";

        optimizer.optimize();
        const sgpp::base::DataVector& xOpt = optimizer.getOptimalPoint();
        const double fOpt = optimizer.getOptimalValue();

        numberOfNewtonCalls++;
        numberOfNewtonIterations += optimizer.getNumberOfIterations();

        //std::cout << "xOpt = " << xOpt[0] << ", fOpt = " << fOpt << "\n";

        //if ((xOpt[0] > 1e-3) && (xOpt[0] < 1.0 - 1e-3) &&
        //    (std::abs(fOpt) < 1e-2)) {
        if (std::abs(fOpt) < 1e-2) {
          return xOpt[0] * (THETA_MAX - THETA_MIN) + THETA_MIN;
        }

        // TODO
        //std::cout << "F = " << F << ", x = " << x.toString() << ": didn't accept theta0 = " << theta0 << "\n";
        //std::cout << "xOpt = " << xOpt[0] << ", fOpt = " << fOpt << ", f(xOpt) = " << momentum.eval(xOpt) << "\n";
      }

      return INFINITY;
    }

    void MomentumBalanceTheta::clone(
        std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const {
      clone = std::unique_ptr<sgpp::optimization::ScalarFunction>(
          new MomentumBalanceTheta(*this));
    }

    size_t MomentumBalanceTheta::getEvalCounter() const {
      return evalCounter;
    }

    void MomentumBalanceTheta::resetEvalCounter() {
      evalCounter = 0;
    }

    size_t MomentumBalanceTheta::getNumberOfNewtonCalls() const {
      return numberOfNewtonCalls;
    }

    void MomentumBalanceTheta::resetNumberOfNewtonCalls() {
      numberOfNewtonCalls = 0;
    }

    size_t MomentumBalanceTheta::getNumberOfNewtonIterations() const {
      return numberOfNewtonIterations;
    }

    void MomentumBalanceTheta::resetNumberOfNewtonIterations() {
      numberOfNewtonIterations = 0;
    }
  }
}
