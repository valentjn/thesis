#ifndef BIOMECH2_INTERFACE_OBJECTIVES_ACTIVATION_SUM_ACTIVATIONSUMOBJECTIVEGRADIENT_HPP
#define BIOMECH2_INTERFACE_OBJECTIVES_ACTIVATION_SUM_ACTIVATIONSUMOBJECTIVEGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace activation_sum {
      class ActivationSumObjectiveGradient :
          public sgpp::optimization::ScalarFunctionGradient {
        public:
          ActivationSumObjectiveGradient();

          double eval(const sgpp::base::DataVector& x,
                             sgpp::base::DataVector& gradient);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const;
      };
    }
  }
}

#endif /* BIOMECH2_INTERFACE_OBJECTIVES_ACTIVATION_SUM_ACTIVATIONSUMOBJECTIVEGRADIENT_HPP */
