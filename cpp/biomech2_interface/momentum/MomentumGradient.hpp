#ifndef MUSCLE_MOMENTUM_MOMENTUMGRADIENT_HPP
#define MUSCLE_MOMENTUM_MOMENTUMGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>
#include <sgpp/optimization/function/vector/VectorFunctionGradient.hpp>

namespace muscle {
  namespace momentum {
    class MomentumGradient : public sgpp::optimization::ScalarFunctionGradient {
      public:
        MomentumGradient(
            double F,
            sgpp::optimization::VectorFunctionGradient& TBGradient);

        double eval(const sgpp::base::DataVector& x,
                           sgpp::base::DataVector& gradient);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const;

        static double lTGradient(double theta);
        static double lBGradient(double theta);
        static double lFGradient(double theta);

      protected:
        double F;
        sgpp::optimization::VectorFunctionGradient& TBGradient;
        sgpp::base::DataVector tbResult;
        sgpp::base::DataMatrix tbGradientResult;
    };
  }
}

#endif /* MUSCLE_MOMENTUM_MOMENTUMGRADIENT_HPP */
