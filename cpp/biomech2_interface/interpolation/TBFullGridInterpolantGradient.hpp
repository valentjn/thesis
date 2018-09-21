#ifndef BIOMECH2_INTERFACE_INTERPOLATION_TBFULLGRIDINTERPOLANTGRADIENT_HPP
#define BIOMECH2_INTERFACE_INTERPOLATION_TBFULLGRIDINTERPOLANTGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/vector/VectorFunctionGradient.hpp>

#define GTE_NO_LOGGER
#include <gte/GteIntpBicubic2.h>
//#include <gte/GteIntpBilinear2.h>

#include <biomech2_interface/interpolation/TBFullGridInterpolant.hpp>

namespace biomech2_interface {
  namespace interpolation {
    class TBFullGridInterpolantGradient :
        public sgpp::optimization::VectorFunctionGradient {
      public:
        TBFullGridInterpolantGradient();

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value,
                  sgpp::base::DataMatrix& gradient);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const;

        size_t getEvalCounter() const;
        void resetEvalCounter();

      protected:
        gte::IntpBicubic2<double> intpT, intpB;
        //gte::IntpBilinear2<double> intpT, intpB;

        size_t evalCounter;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_INTERPOLATION_TBFULLGRIDINTERPOLANTGRADIENT_HPP */
