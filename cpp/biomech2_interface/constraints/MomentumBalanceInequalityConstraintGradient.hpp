#ifndef BIOMECH2_INTERFACE_CONSTRAINTS_MOMENTUMBALANCEINEQUALITYCONSTRAINTGRADIENT_HPP
#define BIOMECH2_INTERFACE_CONSTRAINTS_MOMENTUMBALANCEINEQUALITYCONSTRAINTGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/vector/VectorFunctionGradient.hpp>

namespace biomech2_interface {
  namespace constraints {
    class MomentumBalanceInequalityConstraintGradient :
        public sgpp::optimization::VectorFunctionGradient {
      public:
        MomentumBalanceInequalityConstraintGradient(
            sgpp::optimization::VectorFunctionGradient& f);

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value,
                  sgpp::base::DataMatrix& gradient);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const;

      protected:
        sgpp::optimization::VectorFunctionGradient& fGradient;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_CONSTRAINTS_MOMENTUMBALANCEINEQUALITYCONSTRAINTGRADIENT_HPP */
