#ifndef BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_DISTANCEOBJECTIVEGRADIENT_HPP
#define BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_DISTANCEOBJECTIVEGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>

namespace biomech2_interface {
  namespace objectives {
    namespace distance {
      class DistanceObjectiveGradient :
          public sgpp::optimization::ScalarFunctionGradient {
        public:
          DistanceObjectiveGradient(double alphaTOld,
                                    double alphaBOld);

          double eval(const sgpp::base::DataVector& x,
                             sgpp::base::DataVector& gradient);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const;

        protected:
          double alphaTOld;
          double alphaBOld;
      };
    }
  }
}

#endif /* BIOMECH2_INTERFACE_OBJECTIVES_DISTANCE_DISTANCEOBJECTIVEGRADIENT_HPP */
