#ifndef BIOMECH2_INTERFACE_MOMENTUM_MOMENTUMBALANCETHETAGRADIENT_HPP
#define BIOMECH2_INTERFACE_MOMENTUM_MOMENTUMBALANCETHETAGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/momentum/MomentumBalanceTheta.hpp>
#include <biomech2_interface/momentum/MomentumGradient.hpp>
#include <sgpp/optimization/function/scalar/ScalarFunctionGradient.hpp>

namespace biomech2_interface {
  namespace momentum {
    class MomentumBalanceThetaGradient :
        public sgpp::optimization::ScalarFunctionGradient {
      public:
        MomentumBalanceThetaGradient(
            MomentumBalanceTheta& momentumBalanceTheta,
            MomentumGradient& momentumGradient);

        double eval(const sgpp::base::DataVector& x,
                           sgpp::base::DataVector& gradient);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::ScalarFunctionGradient>& clone) const;

        size_t getEvalCounter() const;
        void resetEvalCounter();

      protected:
        //static constexpr double h = 1e-6;
        MomentumBalanceTheta& momentumBalanceTheta;
        MomentumGradient& momentumGradient;
        sgpp::base::DataVector y;
        sgpp::base::DataVector momentumGradientY;

        size_t evalCounter;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_MOMENTUM_MOMENTUMBALANCETHETAGRADIENT_HPP */
