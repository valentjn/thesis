#ifndef BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDPHI_HPP
#define BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDPHI_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceTheta.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace distance_relaxed {
      class DistanceRelaxedPhi :
          public sgpp::optimization::VectorFunction {
        public:
          DistanceRelaxedPhi(
              momentum::MomentumBalanceTheta& momentumBalanceTheta,
              double alphaTOld,
              double alphaBOld,
              double targetThetaOld,
              double c);

          void eval(const sgpp::base::DataVector& x,
                    sgpp::base::DataVector& value);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const;

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

#endif /* BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_RELAXED_DISTANCERELAXEDPHI_HPP */
