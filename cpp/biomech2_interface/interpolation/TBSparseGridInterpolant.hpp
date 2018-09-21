#ifndef BIOMECH2_INTERFACE_INTERPOLATION_TBSPARSEGRIDINTERPOLANT_HPP
#define BIOMECH2_INTERFACE_INTERPOLATION_TBSPARSEGRIDINTERPOLANT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/vector/InterpolantVectorFunction.hpp>

namespace biomech2_interface {
  namespace interpolation {
    class TBSparseGridInterpolant : public sgpp::optimization::VectorFunction {
      public:
        TBSparseGridInterpolant(
            sgpp::base::Grid& grid,
            const sgpp::base::DataMatrix& alpha);

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const;

        size_t getEvalCounter() const;
        void resetEvalCounter();

      protected:
        sgpp::base::Grid& grid;
        sgpp::base::DataMatrix alpha;
        sgpp::optimization::InterpolantVectorFunction f;
        sgpp::base::DataVector y, fy;

        size_t evalCounter;
    };
  }
}

#endif /* BIOMECH2_INTERFACE_INTERPOLATION_TBSPARSEGRIDINTERPOLANT_HPP */
