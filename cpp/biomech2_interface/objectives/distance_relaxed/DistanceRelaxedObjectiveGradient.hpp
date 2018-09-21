#ifndef BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDOBJECTIVEGRADIENT_HPP
#define BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDOBJECTIVEGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceThetaGradient.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>

namespace muscle {
  namespace objectives {
    namespace distance_relaxed {
      class DistanceRelaxedObjectiveGradient :
          public sgpp::optimization::ScalarFunctionGradient {
        public:
          DistanceRelaxedObjectiveGradient(
              momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient,
              double alphaTOld,
              double alphaBOld,
              double targetThetaOld,
              double c);

          double eval(const sgpp::base::DataVector& x,
                             sgpp::base::DataVector& gradient);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const;

        protected:
          momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient;
          double alphaTOld;
          double alphaBOld;
          double targetThetaOld;
          double c;
      };
    }
  }
}

#endif /* BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDOBJECTIVEGRADIENT_HPP */
