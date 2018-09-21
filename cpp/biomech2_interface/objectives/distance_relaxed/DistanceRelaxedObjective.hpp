#ifndef BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDOBJECTIVE_HPP
#define BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDOBJECTIVE_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceTheta.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunction.hpp>

namespace muscle {
  namespace objectives {
    namespace distance_relaxed {
      class DistanceRelaxedObjective :
          public sgpp::optimization::ScalarFunction {
        public:
          DistanceRelaxedObjective(
              momentum::MomentumBalanceTheta& momentumBalanceTheta,
              double alphaTOld,
              double alphaBOld,
              double targetThetaOld,
              double c);

          double eval(const sgpp::base::DataVector& x);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const;

        protected:
          momentum::MomentumBalanceTheta& momentumBalanceTheta;
          double alphaTOld;
          double alphaBOld;
          double targetThetaOld;
          double c;
      };
    }
  }
}

#endif /* BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDOBJECTIVE_HPP */
