#ifndef BIOMECH2_INTERFACE_MOMENTUM_MOMENTUM_HPP
#define BIOMECH2_INTERFACE_MOMENTUM_MOMENTUM_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunction.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

namespace biomech2_interface {
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

#endif /* BIOMECH2_INTERFACE_MOMENTUM_MOMENTUM_HPP */
