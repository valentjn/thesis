#ifndef BIOMECH2_INTERFACE_MOMENTUM_NEWTONSMETHOD_HPP
#define BIOMECH2_INTERFACE_MOMENTUM_NEWTONSMETHOD_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>
#include <sgpp/optimization/optimizer/unconstrained/UnconstrainedOptimizer.hpp>

namespace biomech2_interface {
  namespace momentum {
    class NewtonsMethod :
        public sgpp::optimization::optimizer::UnconstrainedOptimizer {
      public:
        NewtonsMethod(sgpp::optimization::ScalarFunction& f,
                      sgpp::optimization::ScalarFunctionGradient& fGradient,
                      size_t t);

        void optimize();

        size_t getNumberOfIterations() const;

        void clone(std::unique_ptr<sgpp::optimization::optimizer::
                   UnconstrainedOptimizer>& clone) const;

      protected:
        size_t t;

        sgpp::base::DataVector x;
        sgpp::base::DataVector fxGradient;
        size_t k;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_MOMENTUM_NEWTONSMETHOD_HPP */
