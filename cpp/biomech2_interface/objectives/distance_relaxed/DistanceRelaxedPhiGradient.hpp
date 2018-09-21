#ifndef BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDPHIGRADIENT_HPP
#define BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDPHIGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceThetaGradient.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace distance_relaxed {
      class DistanceRelaxedPhiGradient :
          public sgpp::optimization::VectorFunctionGradient {
        public:
          DistanceRelaxedPhiGradient(
              momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient,
              double alphaTOld,
              double alphaBOld,
              double targetThetaOld,
              double c);

          void eval(const sgpp::base::DataVector& x,
                    sgpp::base::DataVector& value,
                    sgpp::base::DataMatrix& gradient);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const;

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

#endif /* BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDPHIGRADIENT_HPP */
