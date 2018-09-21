#ifndef MUSCLE_MOMENTUM_MOMENTUM_HPP
#define MUSCLE_MOMENTUM_MOMENTUM_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunction.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

namespace muscle {
  namespace momentum {
    class Momentum : public sgpp::optimization::ScalarFunction {
      public:
        Momentum(
            double F,
            sgpp::optimization::VectorFunction& TB);

        double eval(const sgpp::base::DataVector& x);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const;

        static double lT(double theta);
        static double lB(double theta);
        static double lF(double theta);

      protected:
        double F;
        sgpp::optimization::VectorFunction& TB;
        sgpp::base::DataVector tbResult;
    };
  }
}

#endif /* MUSCLE_MOMENTUM_MOMENTUM_HPP */
