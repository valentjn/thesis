#ifndef MUSCLE_OBJECTIVES_ACTIVATION_SUM_ACTIVATIONSUMOBJECTIVE_HPP
#define MUSCLE_OBJECTIVES_ACTIVATION_SUM_ACTIVATIONSUMOBJECTIVE_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunction.hpp>

namespace muscle {
  namespace objectives {
    namespace activation_sum {
      class ActivationSumObjective :
          public sgpp::optimization::ScalarFunction {
        public:
          ActivationSumObjective();

          double eval(const sgpp::base::DataVector& x);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const;
      };
    }
  }
}

#endif /* MUSCLE_OBJECTIVES_ACTIVATION_SUM_ACTIVATIONSUMOBJECTIVE_HPP */
