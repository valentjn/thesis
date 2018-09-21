#ifndef BIOMECH2_INTERFACE_MOMENTUM_MOMENTUMBALANCETHETA_HPP
#define BIOMECH2_INTERFACE_MOMENTUM_MOMENTUMBALANCETHETA_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunction.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>
#include <sgpp/optimization/function/vector/VectorFunctionGradient.hpp>

namespace muscle {
  namespace momentum {
    class MomentumBalanceTheta : public sgpp::optimization::ScalarFunction {
      public:
        MomentumBalanceTheta(
            double F,
            sgpp::optimization::VectorFunction& TB,
            sgpp::optimization::VectorFunctionGradient& TBGradient);

        double eval(const sgpp::base::DataVector& x);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const;

        size_t getEvalCounter() const;
        void resetEvalCounter();

        size_t getNumberOfNewtonCalls() const;
        void resetNumberOfNewtonCalls();

        size_t getNumberOfNewtonIterations() const;
        void resetNumberOfNewtonIterations();

      protected:
        double F;
        sgpp::optimization::VectorFunction& TB;
        sgpp::optimization::VectorFunctionGradient& TBGradient;

        size_t evalCounter;
        size_t numberOfNewtonCalls;
        size_t numberOfNewtonIterations;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_MOMENTUM_MOMENTUMBALANCETHETA_HPP */
