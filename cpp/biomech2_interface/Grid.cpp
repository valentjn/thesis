#include <cassert>
#include <limits>

#include <sgpp/optimization/operation/OptimizationOpFactory.hpp>

#include <biomech2_interface/Grid.hpp>
#include <biomech2_interface/Global.hpp>
#include <biomech2_interface/interpolation/TBFullGridInterpolant.hpp>

namespace biomech2_interface {
  Grid::Grid() : X(0, 0) {
  }

  Grid::~Grid() {
  }



  FullGrid::FullGrid() {
    const size_t ALPHA_COUNT =
        interpolation::TBFullGridInterpolant::ALPHA_COUNT;
    const size_t THETA_COUNT =
        interpolation::TBFullGridInterpolant::THETA_COUNT;
    X.resize(THETA_COUNT * ALPHA_COUNT, 2);

    for (size_t i1 = 0; i1 < THETA_COUNT; i1++) {
      for (size_t i2 = 0; i2 < ALPHA_COUNT; i2++) {
        const size_t i = i1 * ALPHA_COUNT + i2;
        X(i, 0) = static_cast<double>(i1) /
            static_cast<double>(THETA_COUNT - 1);
        X(i, 1) = static_cast<double>(i2) /
            static_cast<double>(ALPHA_COUNT - 1);
      }
    }
  }

  std::string FullGrid::toString() const {
    return "FG";
  }

  std::string FullGrid::getID() const {
    return "fg";
  }



  SparseGrid::SparseGrid(Type type, size_t p, size_t n, bool adaptive) :
          type(type), p(p), n(n), adaptive(adaptive), values(0, 0), alpha(0, 0) {
  }

  void SparseGrid::create() {
    switch (type) {
      case Type::MODBSPL:
        sgppGrid.reset(sgpp::base::Grid::createModBsplineGrid(2, p));
        break;
      case Type::MODBSPLCC:
        sgppGrid.reset(sgpp::base::Grid::createModBsplineClenshawCurtisGrid(2, p));
        break;
      default:
        throw std::runtime_error("Grid unsupported.");
    }

    sgppGrid->getGenerator().regular(n);
  }

  void SparseGrid::load(const std::string& filename) {
    if (sgppGrid == nullptr) {
      create();
    }

    sgpp::base::GridStorage& sgppGridStorage = sgppGrid->getStorage();

    std::ifstream file(filename);
    if (!file) {
      throw std::runtime_error("File " + filename + " does not exist.");
    }
    std::string word;
    size_t version;
    // read first word
    file >> word;
    if (word == "sparsegrid") {
      version = 1;
    } else if (word == "sparsegrid_ver2") {
      version = 2;
    } else {
      throw std::runtime_error("Unknown version " + word + ".");
    }

    // new format
    size_t N, d, m;
    file >> N >> d >> m >> word >> word;
    // standard assumptions
    assert(N == sgppGridStorage.getSize());
    assert(d == 2);
    assert(m == 2);
    double dummy;

    if (version >= 2) {
      for (size_t t = 0; t < d; t++) {
        file >> dummy >> dummy;
      }
    }

    // initialize matrices
    X.resize(N, d);
    X.setAll(std::numeric_limits<double>::quiet_NaN());
    values.resize(N, m);
    values.setAll(std::numeric_limits<double>::quiet_NaN());

    std::vector<size_t> level(d, 0);
    std::vector<size_t> index(d, 0);
    sgpp::base::GridPoint gridPoint(d);

    for (size_t i = 0; i < N; i++) {
      for (size_t t = 0; t < d; t++) {
        file >> level[t];
      }
      for (size_t t = 0; t < d; t++) {
        file >> index[t];
        gridPoint.set(t, level[t], index[t]);
      }

      // search grid point
      size_t j = sgppGridStorage.getSequenceNumber(gridPoint);
      assert(j < N);

      for (size_t t = 0; t < d; t++) {
        X(j, t) = sgppGridStorage.getCoordinate(gridPoint, t);
      }

      for (size_t k = 0; k < m; k++) {
        assert(std::isnan(values(j, k)));
        file >> values(j, k);
      }
    }

    file.close();

    for (unsigned int i = 0; i < N; i++) {
      for (size_t k = 0; k < m; k++) {
        assert(!std::isnan(values(i, k)));
      }

      for (size_t t = 0; t < d; t++) {
        assert(!std::isnan(X(i, t)));
      }
    }

    for (size_t i = 0; i < N; i++) {
      X(i, 0) = X(i, 0) * (THETA_MAX - THETA_MIN) + THETA_MIN;
      X(i, 1) = X(i, 1) * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
    }

    std::cout << "X = " << X.toString() << "\n";
    std::cout << "values = " << values.toString() << "\n";
  }

  void SparseGrid::generateValues(
      sgpp::optimization::VectorFunction& fgIntpTB) {
    sgpp::base::GridStorage& gridStorage = sgppGrid->getStorage();
    const size_t N = sgppGrid->getSize();
    X.resize(N, 2);
    values.resize(N, 2);
    sgpp::base::DataVector x(3), y(2);
    sgpp::base::DataVector fx(2);

    for (size_t i = 0; i < N; i++) {
      sgpp::base::GridPoint& gridPoint = gridStorage[i];

      x[0] = gridStorage.getCoordinate(gridPoint, 0);
      x[1] = gridStorage.getCoordinate(gridPoint, 1);
      x[2] = x[1];

      y[0] = x[0] * (THETA_MAX - THETA_MIN) + THETA_MIN;
      y[1] = x[1] * (ALPHA_MAX - ALPHA_MIN) + ALPHA_MIN;
      X.setRow(i, y);

      fgIntpTB.eval(x, fx);
      values.setRow(i, fx);
    }

    std::cout << "X = " << X.toString() << "\n";
    std::cout << "values = " << values.toString() << "\n";
  }

  void SparseGrid::hierarchize() {
    alpha.resize(values.getNrows(), values.getNcols());
    alpha = values;
    std::unique_ptr<sgpp::optimization::OperationMultipleHierarchisation> opHier(
        sgpp::op_factory::createOperationMultipleHierarchisation(*sgppGrid));
    opHier->doHierarchisation(alpha);
    std::cout << "alpha = " << alpha.toString() << "\n";
  }

  void SparseGrid::coarsen(double surplusThresPercentT,
                          double surplusThresPercentB) {
    if (!adaptive) {
      std::cerr << "Error: Trying to coarsen non-adaptive SparseGrid!\n";
      return;
    }

    double minT, maxT, minB, maxB;

    alpha.minmax(0, &minT, &maxT);
    alpha.minmax(1, &minB, &maxB);

    const double maxAbsAlphaT = std::max(maxT, std::abs(minT));
    const double maxAbsAlphaB = std::max(maxB, std::abs(minB));

    const size_t Nold = sgppGrid->getSize();
    std::list<size_t> indicesToDelete;

    for (size_t k = 0; k < Nold; k++) {
      if ((std::abs(alpha(k, 0)) / maxAbsAlphaT < surplusThresPercentT) &&
          (std::abs(alpha(k, 1)) / maxAbsAlphaB < surplusThresPercentB)) {
        indicesToDelete.push_back(k);
      }
    }

    std::vector<size_t> indicesRemaining =
        sgppGrid->getStorage().deletePoints(indicesToDelete);

    const size_t Nnew = sgppGrid->getSize();

    sgpp::base::DataMatrix Xold(X);
    sgpp::base::DataMatrix valuesOld(values);
    sgpp::base::DataMatrix alphaOld(alpha);

    X.resize(Nnew, 2);
    X.setAll(std::numeric_limits<double>::quiet_NaN());
    values.resize(Nnew, 2);
    values.setAll(std::numeric_limits<double>::quiet_NaN());
    alpha.resize(Nnew, 2);
    alpha.setAll(std::numeric_limits<double>::quiet_NaN());

    for (size_t k = 0; k < Nnew; k++) {
      const size_t kOld = indicesRemaining[k];
      X(k, 0) = Xold(kOld, 0);
      X(k, 1) = Xold(kOld, 1);
      values(k, 0) = valuesOld(kOld, 0);
      values(k, 1) = valuesOld(kOld, 1);
      alpha(k, 0) = alphaOld(kOld, 0);
      alpha(k, 1) = alphaOld(kOld, 1);
    }

    std::cout << "After coarsening:\n";
    std::cout << "X = " << X.toString() << "\n";
    std::cout << "values = " << values.toString() << "\n";
    hierarchize();
  }

  std::string SparseGrid::basisString() const {
    switch (type) {
      case Type::MODBSPL:
        return "modbspl";
      case Type::MODBSPLCC:
        return "modbsplcc";
      default:
        return "";
    }
  }

  std::string SparseGrid::toString() const {
    /*return "Regular SG (" + basisString() + ", $p = " + std::to_string(p) +
          "$, $\\ell = " + std::to_string(l) + "$)";*/
    return std::string(adaptive ? "Adaptive SG" : "Regular SG") +
        " (" + basisString() + ", p=" + std::to_string(p) +
        ", n=" + std::to_string(n) + ")";
  }

  std::string SparseGrid::getID() const {
    return "sg_" + basisString() + std::to_string(p) +
        std::string(adaptive ? "_adap" : "_reg") + std::to_string(n);
  }

  bool SparseGrid::isAdaptive() const {
    return adaptive;
  }
}
