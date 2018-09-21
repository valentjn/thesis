#ifndef MUSCLE_OBJECTIVES_DISTANCE_DISTANCEOBJECTIVE_HPP
#define MUSCLE_OBJECTIVES_DISTANCE_DISTANCEOBJECTIVE_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunction.hpp>

namespace muscle {
  namespace objectives {
    namespace distance {
      class DistanceObjective :
          public sgpp::optimization::ScalarFunction {
        public:
          DistanceObjective(double alphaTOld, double alphaBOld);

          double eval(const sgpp::base::DataVector& x);

          virtual void clone(
              std::unique_ptr<sgpp::optimization::ScalarFunction>& clone) const;

        protected:
          double alphaTOld;
          double alphaBOld;
      };
    }
  }
}

#endif /* MUSCLE_OBJECTIVES_DISTANCE_DISTANCEOBJECTIVE_HPP */
