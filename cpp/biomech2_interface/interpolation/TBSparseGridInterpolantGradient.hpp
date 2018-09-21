#ifndef BIOMECH2_INTERFACE_INTERPOLATION_TBSPARSEGRIDINTERPOLANTGRADIENT_HPP
#define BIOMECH2_INTERFACE_INTERPOLATION_TBSPARSEGRIDINTERPOLANTGRADIENT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/vector/InterpolantVectorFunctionGradient.hpp>

namespace biomech2_interface {
  namespace interpolation {
    class TBSparseGridInterpolantGradient :
        public sgpp::optimization::VectorFunctionGradient {
      public:
        TBSparseGridInterpolantGradient(
            sgpp::base::Grid& grid,
            const sgpp::base::DataMatrix& alpha);

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value,
                  sgpp::base::DataMatrix& gradient);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunctionGradient>& clone) const;

        size_t getEvalCounter() const;
        void resetEvalCounter();

      protected:
        sgpp::base::Grid& grid;
        sgpp::base::DataMatrix alpha;
        sgpp::optimization::InterpolantVectorFunctionGradient fGradient;
        sgpp::base::DataVector y, fy;
        sgpp::base::DataMatrix fyGradient;

        size_t evalCounter;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_INTERPOLATION_TBSPARSEGRIDINTERPOLANTGRADIENT_HPP */
