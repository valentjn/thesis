#ifndef MUSCLE_CONSTRAINTS_MOMENTUMBALANCECONSTRAINT_HPP
#define MUSCLE_CONSTRAINTS_MOMENTUMBALANCECONSTRAINT_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceTheta.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

namespace muscle {
  namespace constraints {
    class MomentumBalanceConstraint :
        public sgpp::optimization::VectorFunction {
      public:
        MomentumBalanceConstraint(
            momentum::MomentumBalanceTheta& momentumBalanceTheta,
            double targetTheta);

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const;

      protected:
        momentum::MomentumBalanceTheta& momentumBalanceTheta;
        double targetTheta;
    };
  }
}

#endif /* MUSCLE_CONSTRAINTS_MOMENTUMBALANCECONSTRAINT_HPP */
