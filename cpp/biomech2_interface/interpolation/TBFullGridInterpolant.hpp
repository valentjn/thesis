#ifndef MUSCLE_INTERPOLATION_TBFULLGRIDINTERPOLANT_HPP
#define MUSCLE_INTERPOLATION_TBFULLGRIDINTERPOLANT_HPP

#include <biomech2_interface/Global.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

#define GTE_NO_LOGGER
#include <gte/GteIntpBicubic2.h>
//#include <gte/GteIntpBilinear2.h>

namespace muscle {
  namespace interpolation {
    class TBFullGridInterpolant : public sgpp::optimization::VectorFunction {
      public:
        static const size_t THETA_COUNT = 141;
        static constexpr double THETA_STEP =
            (THETA_MAX - THETA_MIN) /
            (static_cast<double>(THETA_COUNT) - 1.0);

        static const size_t ALPHA_COUNT = 11;
        static constexpr double ALPHA_STEP =
            (ALPHA_MAX - ALPHA_MIN) /
            (static_cast<double>(ALPHA_COUNT) - 1.0);

        static const std::vector<double> T_DATA;
        static const std::vector<double> B_DATA;

        TBFullGridInterpolant();

        void eval(const sgpp::base::DataVector& x,
                  sgpp::base::DataVector& value);

        virtual void clone(
            std::unique_ptr<sgpp::optimization::VectorFunction>& clone) const;

        size_t getEvalCounter() const;
        void resetEvalCounter();

      protected:
        gte::IntpBicubic2<double> intpT, intpB;
        //gte::IntpBilinear2<double> intpT, intpB;

        size_t evalCounter;
    };
  }
}

#endif /* MUSCLE_INTERPOLATION_TBFULLGRIDINTERPOLANT_HPP */
