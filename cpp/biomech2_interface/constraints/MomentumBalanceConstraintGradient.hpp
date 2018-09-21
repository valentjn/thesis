#ifndef BIOMECH2_INTERFACE_CONSTRAINTS_MOMENTUMBALANCECONSTRAINTGRADIENT_HPP
#define BIOMECH2_INTERFACE_CONSTRAINTS_MOMENTUMBALANCECONSTRAINTGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceThetaGradient.hpp>
#include <sgpp/optimization/function/vector/VectorFunctionGradient.hpp>

namespace muscle {
  namespace constraints {
    class MomentumBalanceConstraintGradient :
        public sgpp::optimization::VectorFunctionGradient {
      public:
        MomentumBalanceConstraintGradient(
            momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient,
            double targetTheta);

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value,
                  sgpp::base::DataMatrix& gradient);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const;

      protected:
        momentum::MomentumBalanceThetaGradient& momentumBalanceThetaGradient;
        double targetTheta;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_CONSTRAINTS_MOMENTUMBALANCECONSTRAINTGRADIENT_HPP */
