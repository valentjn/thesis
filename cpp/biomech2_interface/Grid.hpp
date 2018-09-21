#pragma once

#include <sgpp/base/datatypes/DataMatrix.hpp>
#include <sgpp/base/grid/Grid.hpp>
#include <sgpp/optimization/function/vector/VectorFunction.hpp>

struct Grid {
  sgpp::base::DataMatrix X;

  Grid();
  virtual ~Grid();
  virtual std::string toString() const = 0;
  virtual std::string getID() const = 0;
};

struct FullGrid : public Grid {
  FullGrid();
  std::string toString() const;
  std::string getID() const;
};

struct SparseGrid : public Grid {
  enum Type {
    MODBSPL,
    MODBSPLCC
  } type;
  size_t p;
  size_t l;
  bool adaptive;
  std::unique_ptr<sgpp::base::Grid> sgppGrid;
  sgpp::base::DataMatrix values;
  sgpp::base::DataMatrix alpha;

  SparseGrid(Type type, size_t p, size_t l, bool adaptive);

  void create();

  void load(const std::string& filename);
  void generateValues(sgpp::optimization::VectorFunction& fgIntpTB);
  void hierarchize();

  void coarsen(double surplusThresPercentT, double surplusThresPercentB);

  std::string basisString() const;
  std::string toString() const;
  std::string getID() const;
  bool isAdaptive() const;
};
