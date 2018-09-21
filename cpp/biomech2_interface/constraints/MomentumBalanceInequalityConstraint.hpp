#ifndef MUSCLE_CONSTRAINTS_MOMENTUMBALANCEINEQUALITYCONSTRAINT_HPP
#define MUSCLE_CONSTRAINTS_MOMENTUMBALANCEINEQUALITYCONSTRAINT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

namespace muscle {
  namespace constraints {
    class MomentumBalanceInequalityConstraint :
        public sgpp::optimization::VectorFunction {
      public:
        MomentumBalanceInequalityConstraint(
            sgpp::optimization::VectorFunction& f);

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const;

      protected:
        sgpp::optimization::VectorFunction& f;
    };
  }
}

#endif /* MUSCLE_CONSTRAINTS_MOMENTUMBALANCEINEQUALITYCONSTRAINT_HPP */
