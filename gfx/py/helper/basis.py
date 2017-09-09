import scipy.signal

class Basis(object):
  def coord_to_mother_fcn(l, i, xx):
    return 2**l * xx - i

class CardinalBSpline(object):
  def __init__(self, p):
    self.p = p
  
  def evaluate(self, xx):
    return scipy.signal.bspline(xx - (self.p+1)/2, self.p)

class BSpline(object):
  def __init__(self, p):
    self.p = p
    self.cardinal_bspline = CardinalBSpline(p)
  
  def evaluate(self, l, i, xx):
    t = Basis.coord_to_mother_fcn(l, i, xx)
    return self.cardinal_bspline.evaluate(t + (self.p+1)/2)
