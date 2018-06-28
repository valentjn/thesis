#!/usr/bin/python3
# number of helper figures = 12

import matplotlib as mpl
import numpy as np
import scipy.optimize

from helper.figure import Figure
import helper.grid
import helper.plot



def createFigure():
  fig = Figure.create(figsize=(3, 3), preamble=r"""
\usepackage{contour}
\contourlength{1.5pt}
""")
  ax = fig.gca()
  ax.set_position((0, 0, 1, 1))
  ax.set_xlim(0, 10)
  ax.set_ylim(0, 10)
  ax.set_aspect("equal")
  ax.set_axis_off()
  return fig, ax



def plotTitle(ax, x, y, title, normal=False, **kwargs):
  if not normal: kwargs["weight"] = "bold"
  ax.text(x, y, r"\contour{{mittelblau!10}}{{{}}}".format(title), **kwargs)



def createBranin(left, right, bottom, top, order=0):
  f = lambda X: ((X[:,1]-5.1*X[:,0]**2/(4*np.pi**2)+5*X[:,0]/np.pi-6)**2 +
                 10*(1-1/(8*np.pi))*np.cos(X[:,0]) + 10)
  fdx0 = lambda X: (2*(X[:,1]-5.1*X[:,0]**2/(4*np.pi**2)+5*X[:,0]/np.pi-6)*
                    (-2*5.1*X[:,0]/(4*np.pi**2)+5/np.pi) -
                    10*(1-1/(8*np.pi))*np.sin(X[:,0]))
  fdx1 = lambda X: 2*(X[:,1]-5.1*X[:,0]**2/(4*np.pi**2)+5*X[:,0]/np.pi-6)
  fdx0dx0 = lambda X: (2*(X[:,1]-5.1*X[:,0]**2/(4*np.pi**2)+5*X[:,0]/np.pi-6)*
                       (-2*5.1/(4*np.pi**2)) +
                       2*(-2*5.1*X[:,0]/(4*np.pi**2)+5/np.pi)**2 -
                       10*(1-1/(8*np.pi))*np.cos(X[:,0]))
  fdx1dx1 = lambda X: 2*np.ones((X.shape[0],))
  fdx0dx1 = lambda X: 2*(-2*5.1*X[:,0]/(4*np.pi**2)+5/np.pi)
  
  g = lambda X: np.column_stack([X[:,0]*(right-left)*0.1+left,
                                 X[:,1]*(top-bottom)*0.1+bottom])
  gdx0 = lambda X: (right-left)*0.1*np.ones((X.shape[0],))
  gdx1 = lambda X: (top-bottom)*0.1*np.ones((X.shape[0],))
  gInv = lambda X: np.column_stack([(X[:,0]-left)/((right-left)*0.1),
                                    (X[:,1]-bottom)/((top-bottom)*0.1)])
  
  fg = lambda X: f(g(X))
  fgdx0 = lambda X: fdx0(g(X)) * gdx0(X)
  fgdx1 = lambda X: fdx1(g(X)) * gdx1(X)
  fgdx0dx0 = lambda X: fdx0dx0(g(X)) * gdx0(X)**2
  fgdx0dx1 = lambda X: fdx0dx1(g(X)) * gdx0(X) * gdx1(X)
  fgdx1dx1 = lambda X: fdx1dx1(g(X)) * gdx1(X)**2
  # d/dx f(g(x)) = f'(g(x)) * g'(x)
  # d^2/dx^2 f(g(x)) = f'(g(x)) * g''(x) + f''(g(x)) * (g'(x))^2
  # = f''(g(x)) * (g'(x))^2
  
  fgGradient = lambda x: np.array([fgdx0(np.array([x]))[0],
                                   fgdx1(np.array([x]))[0]])
  fgHessian = lambda x: np.array(
      [[fgdx0dx0(np.array([x]))[0], fgdx0dx1(np.array([x]))[0]],
       [fgdx0dx1(np.array([x]))[0], fgdx1dx1(np.array([x]))[0]]])
  
  if order == 0:
    return fg, gInv
  elif order == 1:
    return fg, fgGradient, gInv
  else:
    return fg, fgGradient, fgHessian, gInv



def plotNelderMead():
  fig, ax = createFigure()
  alpha, beta, gamma, delta = 1, 2, 0.5, 0.5
  X = np.array([[5, 1], [9, 8], [4, 5]])
  y0 = np.mean(X[:-1], axis=0)
  scale = (0.48, 0.6)
  
  for i in range(6):
    offset = [(i%3) * 10/3, 5 * (1 - (i//3))]
    if i >= 3: offset[1] += 1
    helper.plot.transform(ax, offset, scale,
        ax.fill(*list(zip(X[0], X[1], X[2], X[0])), "-",
                ec="C0", fc=helper.plot.mixColors("C0", 0.3), clip_on=False))
    
    if i == 1:
      y1 = y0 + alpha * (y0 - X[2])
      helper.plot.transform(ax, offset, scale,
          ax.plot(*list(zip(X[0], X[1], y1, X[0])), "k--", clip_on=False))
    elif i == 2:
      y2 = y0 + beta * (y1 - y0)
      helper.plot.transform(ax, offset, scale,
          ax.plot(*list(zip(X[0], X[1], y2, X[0])), "k--", clip_on=False))
    elif i == 3:
      y3 = y0 + gamma * (y1 - y0)
      helper.plot.transform(ax, offset, scale,
          ax.plot(*list(zip(X[0], X[1], y3, X[0])), "k--", clip_on=False))
    elif i == 4:
      y4 = y0 - gamma * (y0 - X[2])
      helper.plot.transform(ax, offset, scale,
          ax.plot(*list(zip(X[0], X[1], y4, X[0])), "k--", clip_on=False))
    elif i == 5:
      Y = X[0] + delta * (X - X[0])
      helper.plot.transform(ax, offset, scale,
          ax.plot(*list(zip(Y[0], Y[1], Y[2], Y[0])), "k--", clip_on=False))
  
  plotTitle(ax, 7, 10.7, "Nelder--Mead", ha="center", va="top")
  fig.save()



def plotDifferentialEvolution():
  fig, ax = createFigure()
  
  squareCount = 6
  squareSize = 1.2
  squareOffset = [0.5, 1]
  squareMargin = 2.7
  x, y = squareOffset
  mutationDimensions = [0, 3, 5]
  
  for i in range(3):
    ax.plot(x + squareSize * np.array([0, 1, 1, 0, 0]),
            y + squareCount * squareSize * np.array([0, 0, 1, 1, 0]), "k-",
            clip_on=False)
    
    for t in range(squareCount):
      if t >= 1: ax.plot([x, x + squareSize], [y, y], "k-", clip_on=False)
      if i == 1:
        xStart = (x+squareSize if t in mutationDimensions else x-squareMargin)
        helper.plot.plotArrow(
            ax, [xStart + 0.15, y + squareSize/2],
            [x + squareSize + squareMargin - 0.2, y + squareSize/2],
            scaleHead=5)
      if i == 0:   color = "C0"
      elif i == 1: color = "C1"
      else:        color = ("C1" if t in mutationDimensions else "C0")
      ax.fill(x + squareSize * np.array([0, 1, 1, 0, 0]),
              y + squareSize * np.array([0, 0, 1, 1, 0]),
              fc=color, clip_on=False)
      y += squareSize
    
    x += squareSize + squareMargin
    y = squareOffset[1]
  
  plotTitle(ax, 5, 9.5, "Differential evolution", ha="center", va="top")
  ax.text(squareOffset[0] + squareSize/2, -0.5,
          r"\textcolor{C0}{Original}", ha="center", va="bottom")
  ax.text(squareOffset[0] + squareMargin + 3*squareSize/2, -0.5,
          r"\vphantom{g}\textcolor{C1}{Mutation}",
          ha="center", va="bottom")
  ax.text(squareOffset[0] + 2*squareMargin + 5*squareSize/2, -0.5,
          r"\vphantom{g}" + "".join(
      [r"\textcolor{{{}}}{{{}}}".format(("C0" if i % 2 == 0 else "C1"), x)
       for i, x in enumerate("Crossover")]),
      ha="center", va="bottom")
  ax.text(squareOffset[0] + squareSize, squareOffset[1] + squareSize/2,
          "\;$t = 1$", ha="left", va="center", size=9)
  ax.text(squareOffset[0] + squareSize,
          squareOffset[1] + (squareCount-1)*squareSize + squareSize/2,
          "\;$t = d$", ha="left", va="center", size=9)
  fig.save()



def plotCMAES():
  fig, ax = createFigure()
  
  left, right, bottom, top = 0, 6, -2, 8
  fg, gInv = createBranin(left, right, bottom, top, order=0)
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((201, 201))
  XX0 *= 10; XX1 *= 10; XX *= 10
  YY = np.reshape(fg(XX), XX0.shape)
  v = 5/(4*np.pi) + np.arange(0, 20, 0.8)**2
  ax.contour(XX0, XX1, YY, v, colors="k")
  
  np.random.seed(342)
  
  for mu, d, v1, color in [((2,6), (2,2), (1,0), "C0"),
                           ((5,4), (1.0,0.5), (1, -1), "C1")]:
    mu = np.array(mu)
    d = np.array(d)
    v1 = np.array(v1)
    v1 = v1 / np.linalg.norm(v1)
    v2 = np.array([-v1[1], v1[0]])
    V = np.column_stack((v1, v2))
    C = np.linalg.multi_dot((V, np.diag(d), np.linalg.inv(V)))
    X = np.random.multivariate_normal(mu, C, 100)
    ax.plot(*list(zip(*X)), ".", color=color)
    
    A = np.linalg.multi_dot((V, np.diag(np.sqrt(d)), np.linalg.inv(V)))
    radius = 3
    tt = np.linspace(0, 2*np.pi, 201)
    xx0, xx1 = radius*np.cos(tt), radius*np.sin(tt)
    XX = np.column_stack((xx0, xx1))
    XX = mu + np.dot(A, XX.T).T
    ax.plot(*list(zip(*XX)), "--", color=color, zorder=100)
  
  plotTitle(ax, 0.5, 0.2,
            r"\textcolor{C0}{Old}/\textcolor{C1}{new} distribution",
            ha="left", va="bottom", normal=True)
  plotTitle(ax, 8, 9.5, "CMA-ES", ha="center", va="top")
  fig.save()



def plotSimulatedAnnealing():
  fig, ax = createFigure()
  left, right, bottom, top = 200, 300, -0.5, 9
  f = lambda x: (2 + np.sin(0.1*x)) * (2 + np.sin(0.02*(15+np.sin(0.1*x))*x))
  g = lambda X: np.column_stack([(X[:,0]-left)/((right-left)*0.1),
                                 (X[:,1]-bottom)/((top-bottom)*0.1)])
  xx = np.linspace(left, right, 401)
  yy = f(xx)
  ax.plot(*g(np.column_stack((xx, yy))).T, "k-", clip_on=False)
  
  np.random.seed(343)
  x0 = np.random.uniform(left, right)
  fx0 = f(x0)
  kMax = 10000
  T0 = 100
  psi = lambda k: T0 * 0.95**k
  X = []
  
  for k in range(kMax):
    T = psi(k)
    x = np.random.uniform(left, right)
    fx = f(x)
    delta = fx - fx0
    accept = False
    
    if delta <= 0: accept = True
    else:          accept = (np.random.uniform() < np.exp(-delta / T))
    
    if accept:
      x0, fx0 = x, fx
      X.append(x)
  
  normalize = mpl.colors.Normalize(0, 1)
  colormap = helper.plot.createLinearColormap("myCoolWarm", "C1", "C0")
  scalarMappable = mpl.cm.ScalarMappable(norm=normalize, cmap=colormap)
  
  for k, x in enumerate(X):
    fx = f(x)
    ax.plot(*g(np.array([[x, fx]]))[0], ".",
            color=scalarMappable.to_rgba((k/len(X))**1.8), clip_on=False)
  
  ax.text(1, 7, "High tem-\nperature", color="C1",
          ha="left", va="center", size=9)
  ax.text(4.5, 1.8, "Low temperature", color="C0",
          ha="left", va="center", size=9)
  
  plotTitle(ax, 5, 10, "Simulated annealing", ha="center", va="bottom")
  fig.save()



def plotPSO():
  fig, ax = createFigure()
  np.random.seed(345)
  N = 5
  X = np.random.normal([3, 7], [1, 1], (N, 2))
  Y = np.random.normal([7, 3], [1, 1], (N, 2))[[3,1,4,2,0]]
  ax.plot(X[:,0], X[:,1], ".", color="C0", clip_on=False)
  ax.plot(Y[:,0], Y[:,1], ".", color="C1", clip_on=False)
  
  for x, y in zip(X, Y):
    direction = y - x
    direction = 0.3 * direction / np.linalg.norm(direction)
    arrowStart, arrowEnd = x + direction, y - direction
    helper.plot.plotArrow(ax, arrowStart, arrowEnd, scaleHead=5,
                          color="C0")
  
  ax.text(4.5, 7.2, r"$\vec{x}_k$", ha="left", va="bottom", color="C0")
  ax.text(5, 2, r"$\vec{x}_{k+1}$", ha="left", va="bottom", color="C1")
  ax.text(6.5, 5, r"$\vec{v}_k$", ha="left", va="bottom", color="C0")
  
  plotTitle(ax, 5.2, 10, "PSO", ha="center", va="top")
  fig.save()



def plotGPLCB():
  fig, ax = createFigure()
  left, right, bottom, top = 20, 100, -0.5, 9
  f = lambda x: (2 + np.sin(0.1*x)) * (2 + np.sin(0.02*(15+np.sin(0.1*x))*x))
  g = lambda X: np.column_stack([(X[:,0]-left)/((right-left)*0.1),
                                 (X[:,1]-bottom)/((top-bottom)*0.1)])
  xx = np.linspace(left, right, 201)
  yy = f(xx)
  ax.plot(*g(np.column_stack((xx, yy))).T, "k-")
  
  exponentialCov = lambda x, y, params: (
    params[0] * np.exp(-0.5 * params[1] * np.subtract.outer(x, y)**2))
  
  def conditional(xNew, x, y, params):
    B = exponentialCov(xNew, x, params)
    C = exponentialCov(x, x, params)
    A = exponentialCov(xNew, xNew, params)
    CInvBT = np.linalg.solve(C, B.T)
    mu = CInvBT.T.dot(y)
    sigma = A - B.dot(CInvBT)
    return mu.squeeze(), sigma.squeeze()
  
  params = [1, 0.01]
  xx = np.linspace(left, right, 1000)
  xData = np.array([25, 67, 80, 90])
  yData = f(xData)
  mu, sigma = conditional(xx, xData, yData, params)
  sigma = np.sqrt(np.diag(sigma))
  
  factor = 2
  yyMin, yyMax = mu-factor*sigma, mu+factor*sigma
  
  ax.fill_between(
      (xx-left)/((right-left)*0.1),
      (yyMin-bottom)/((top-bottom)*0.1),
      (yyMax-bottom)/((top-bottom)*0.1),
      color=helper.plot.mixColors("C0", 0.3), clip_on=False)
  ax.plot(*g(np.column_stack((xx, mu))).T, "-",
          color="C0", clip_on=False)
  ax.plot(*g(np.column_stack((xx, yyMin))).T, "--",
          color="C0", clip_on=False)
  ax.plot(*g(np.column_stack((xx, yyMax))).T, "--",
          color="C0", clip_on=False)
  ax.plot(*g(np.column_stack((xData, yData))).T, ".",
          color="C0", clip_on=False)
  k = np.argmin(yyMin)
  ax.plot(*g(np.array([[xx[k], yyMin[k]]])).T, "x",
          color="C0", ms=5, mew=2, clip_on=False)
  
  plotTitle(ax, 3.5, 9.5, "GP-LCB", ha="center", va="top")
  fig.save()



def plotGradientDescentNLCG():
  fig, ax = createFigure()
  f = lambda X: (X[:,0] - 3)**2 + 10 * (X[:,1] - 5)**2
  fGradient = lambda X: np.hstack([2*(X[:,0] - 3), 20*(X[:,1] - 5)])
  XX0, XX1, XX = helper.grid.generateMeshGrid((201, 201))
  XX0 *= 10; XX1 *= 10; XX *= 10
  YY = np.reshape(f(XX), XX0.shape)
  v = np.arange(0.5, 100, 1)**2
  ax.contour(XX0, XX1, YY, v)
  x = np.array([9.5, 7])
  X = [x.tolist()]
  
  for i in range(5):
    fx = f(np.array([x]))[0]
    fgx = fGradient(np.array([x]))
    fgx = fgx / np.linalg.norm(fgx)
    fLine = lambda alpha: f(np.array([x - alpha * fgx]))
    alphaOpt = scipy.optimize.minimize_scalar(fLine).x
    x = x - alphaOpt * fgx
    X.append(x.tolist())
  
  ax.plot(*list(zip(*X)), ".-", color="C0")
  ax.plot(*list(zip(*X[:2], [3, 5])), "o--", color="C1",
          ms=4, fillstyle="none")
  plotTitle(ax, 5, 6.2, r"\textcolor{C0}{Gradient descent}",
            ha="center", va="bottom")
  plotTitle(ax, 7, 4.5, r"\textcolor{C1}{NLCG}",
            ha="center", va="top")
  fig.save()



def plotNewton():
  fig, ax = createFigure()
  
  left, right, bottom, top = 0, 6, -2, 8
  fg, fgGradient, fgHessian, gInv = createBranin(
      left, right, bottom, top, order=2)
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((201, 201))
  XX0 *= 10; XX1 *= 10; XX *= 10
  YY = np.reshape(fg(XX), XX0.shape)
  v = 5/(4*np.pi) + np.arange(0, 20, 0.8)**2
  ax.contour(XX0, XX1, YY, v, colors="k")
  
  x = gInv(np.array([[4, 6]]))[0]
  ax.plot(*x, "k.")
  X = [x]
  
  for i in range(2):
    fgx = fg(np.array([x]))[0]
    fgxGradient = fgGradient(x)
    fgxHessian = fgHessian(x)
    fgQuadratic = lambda X: (
        fgx + np.dot(X-x, fgxGradient) +
        0.5 * np.sum(np.dot(X-x, fgxHessian) * (X-x), axis=1))
    
    YY = np.reshape(fgQuadratic(XX), XX0.shape)
    v = np.min(YY) + np.arange(0, 20, 1.5)**2
    ax.contour(XX0, XX1, YY, v, colors="C{}".format(i), linestyles="dashed")
    xNew = x + np.linalg.solve(fgxHessian, -fgxGradient)
    ax.plot(*xNew, ".", color="C{}".format(i))
    
    direction = xNew - x
    direction = 0.3 * direction / np.linalg.norm(direction)
    arrowStart, arrowEnd = x + direction, xNew - direction
    helper.plot.plotArrow(ax, arrowStart, arrowEnd, zorder=100, scaleHead=5)
    
    X.append(xNew)
    x = xNew
  
  plotTitle(ax, 5, 9.8, "Newton", ha="center", va="top")
  fig.save()



def plotBFGS():
  fig, ax = createFigure()
  left, right, bottom, top = 20, 60, 0, 9
  f = lambda x: (2 + np.sin(0.1*x)) * (2 + np.sin(0.02*(15+np.sin(0.1*x))*x))
  fdx = lambda x: (
      (2 + np.sin(0.1*x)) * np.cos(0.02*(15+np.sin(0.1*x))*x) *
      (0.02*(15+np.sin(0.1*x)) + 0.02*(np.cos(0.1*x)*0.1)*x) +
      (np.cos(0.1*x)*0.1) * (2 + np.sin(0.02*(15+np.sin(0.1*x))*x)))
  g = lambda X: np.column_stack([(X[:,0]-left)/((right-left)*0.1),
                                 (X[:,1]-bottom)/((top-bottom)*0.1)])
  
  xx = np.linspace(left, right, 201)
  yy = f(xx)
  ax.plot(*g(np.column_stack((xx, yy))).T, "k-")
  
  x1, x2 = 27, 47
  fx1, fx2 = f(x1), f(x2)
  fdx1, fdx2 = fdx(x1), fdx(x2)
  fdxdx2 = (fdx2 - fdx1) / (x2 - x1)
  h = lambda x: fx2 + fdx2*(x-x2) + fdxdx2/2*(x-x2)**2
  yy = h(xx)
  ax.plot(*g(np.column_stack((xx, yy))).T, "--", color="C0")
  x3 = x2 - fdx2 / fdxdx2
  hx3 = h(x3)
  ax.plot(*g(np.array([[x3, hx3]])).T, "x", color="C0", ms=5, mew=2)
  ax.plot(*g(np.array([[x1, fx1]])).T, "k.")
  ax.plot(*g(np.array([[x2, fx2]])).T, ".", color="C1")
  
  h1 = 1.7
  ax.plot(*g(np.array([[x1-h1, fx1-h1*fdx1], [x1+h1, fx1+h1*fdx1]])).T, "-",
          color="C1")
  hx1 = h(x1)
  ax.plot(*g(np.array([[x1-h1, hx1-h1*fdx1], [x1+h1, hx1+h1*fdx1]])).T, "-",
          color="C1")
  h2 = 3
  ax.plot(*g(np.array([[x2-h2, fx2-h2*fdx2], [x2+h2, fx2+h2*fdx2]])).T, "-",
          color="C1")
  
  plotTitle(ax, 5, 9.8, "BFGS", ha="center", va="top",)
  fig.save()



#def plotRprop():
#  fig, ax = createFigure()
#  
#  left, right, bottom, top = 0, 6, -2, 8
#  fg, fgGradient, gInv = createBranin(left, right, bottom, top, order=1)
#  
#  XX0, XX1, XX = helper.grid.generateMeshGrid((201, 201))
#  XX0 *= 10; XX1 *= 10; XX *= 10
#  YY = np.reshape(fg(XX), XX0.shape)
#  v = 5/(4*np.pi) + np.arange(0, 20, 0.8)**2
#  ax.contour(XX0, XX1, YY, v, colors="k")
#  
#  x = gInv(np.array([[5.5, 1.5]]))[0]
#  ax.plot(*x, "k.")
#  X = [x]
#  alpha = 3.5 * np.ones((2,))
#  fgxGradientLast = np.zeros((2,))
#  
#  for i in range(6):
#    fgx = fg(np.array([x]))[0]
#    fgxGradient = fgGradient(x)
#    print(fgx, fgxGradient)
#    
#    for t in range(2):
#      if fgxGradient[t] * fgxGradientLast[t] > 0:
#        alpha[t] = 1.2 * alpha[t]
#        fgxGradientLast[t] = fgxGradient[t]
#      elif fgxGradient[t] * fgxGradientLast[t] < 0:
#        alpha[t] = 0.5 * alpha[t]
#        fgxGradientLast[t] = 0
#      else:
#        fgxGradientLast[t] = fgxGradient[t]
#      
#      x[t] = x[t] - alpha[t] * np.sign(fgxGradient[t])
#    
#    ax.plot(*x, "k.")
#  
#  fig.save()



def plotLogBarrier():
  fig, ax = createFigure()
  ax.set_axis_on()
  ax.set_xlim(-3, 0.5)
  ax.set_ylim(-3, 3)
  ax.set_aspect(0.62)
  ax.spines["left"].set_position("zero")
  ax.spines["bottom"].set_position("zero")
  ax.set_xticklabels([])
  ax.set_yticklabels([])
  
  ax.text(0.1, 0.1, "$0$", ha="left", va="bottom")
  ax.text(-0.1, -0.1, "$g(x)$", ha="right", va="top")
  ax.text(-1.6, -1.7, r"$-\mu_k \log(-g(x))$", ha="center", va="center",
          rotation=40, color="mittelblau")
  
  xx = np.linspace(-3, 0, 501)[:-1]
  
  for i in range(5):
    mu = 2.5 * 0.5**i
    yy = -mu * np.log(-xx)
    ax.plot(xx, yy, "-",
            color=helper.plot.mixColors("hellblau", i/4, "mittelblau"))
  
  plotTitle(ax, -1.5, 2.8, "Log-barrier", ha="center", va="top")
  fig.save()



def plotSquaredPenalty():
  fig, ax = createFigure()
  ax.set_axis_on()
  ax.set_xlim(-0.5, 3)
  ax.set_ylim(-0.7, 6)
  ax.set_aspect(0.55)
  ax.spines["left"].set_position("zero")
  ax.spines["bottom"].set_position("zero")
  ax.set_xticklabels([])
  ax.set_yticklabels([])
  
  ax.text(-0.1, -0.1, "$0$", ha="right", va="top")
  ax.text(2.9, -0.1, "$g(x)$", ha="right", va="top")
  ax.text(1.9, 2.6, r"$\mu_k \cdot ((g(x))_{+})^2$",
          ha="center", va="center", rotation=57, color="mittelblau")
  
  xx = np.linspace(0, 3, 501)
  
  for i in range(5):
    mu = 1 * 2**i
    yy = mu * xx**2
    ax.plot(xx, yy, "-",
            color=helper.plot.mixColors("hellblau", i/4, "mittelblau"))
  
  plotTitle(ax, 1.5, 5.8, "Squared penalty", ha="center", va="top")
  fig.save()



def plotSQP():
  fig, ax = createFigure()
  f = lambda X: np.sin(0.5*X[:,0] + 2) * np.sin(0.5*X[:,1] - 1)
  fdx0 = lambda X: 0.5 * (
      np.cos(0.5*X[:,0] + 2) * np.sin(0.5*X[:,1] - 1))
  fdx1 = lambda X: 0.5 * (
      np.sin(0.5*X[:,0] + 2) * np.cos(0.5*X[:,1] - 1))
  fdx0dx0 = lambda X: 0.5**2 * (
      -np.sin(0.5*X[:,0] + 2) * np.sin(0.5*X[:,1] - 1))
  fdx0dx1 = lambda X: 0.5**2 * (
      np.cos(0.5*X[:,0] + 2) * np.cos(0.5*X[:,1] - 1))
  fdx1dx1 = lambda X: 0.5**2 * (
      -np.sin(0.5*X[:,0] + 2) * np.sin(0.5*X[:,1] - 1))
  g1 = lambda X: ((0.35*X[:,0])**2 - X[:,1] + 0.5)
  g2 = lambda X: (1 - X[:,0] + (0.5*X[:,1]-2)**2)
  g1dx0 = lambda X: 0.35*X[:,0]*2
  g1dx1 = lambda X: -np.ones((X.shape[0],))
  g2dx0 = lambda X: -np.ones((X.shape[0],))
  g2dx1 = lambda X: (0.5*X[:,1]-2)*2*0.5
  g1dx0dx0 = lambda X: 0.35*2*np.ones((X.shape[0],))
  g1dx0dx1 = lambda X: np.zeros((X.shape[0],))
  g1dx1dx1 = lambda X: np.zeros((X.shape[0],))
  g2dx0dx0 = lambda X: np.zeros((X.shape[0],))
  g2dx0dx1 = lambda X: np.zeros((X.shape[0],))
  g2dx1dx1 = lambda X: 0.5*2*0.5*np.ones((X.shape[0],))
  
  fGradient = lambda x: np.array([fdx0(np.array([x]))[0],
                                  fdx1(np.array([x]))[0]])
  fHessian = lambda x: np.array(
      [[fdx0dx0(np.array([x]))[0], fdx0dx1(np.array([x]))[0]],
       [fdx0dx1(np.array([x]))[0], fdx1dx1(np.array([x]))[0]]])
  g1Gradient = lambda x: np.array([g1dx0(np.array([x]))[0],
                                   g1dx1(np.array([x]))[0]])
  g2Gradient = lambda x: np.array([g2dx0(np.array([x]))[0],
                                   g2dx1(np.array([x]))[0]])
  g1Hessian = lambda x: np.array(
      [[g1dx0dx0(np.array([x]))[0], g1dx0dx1(np.array([x]))[0]],
       [g1dx0dx1(np.array([x]))[0], g1dx1dx1(np.array([x]))[0]]])
  g2Hessian = lambda x: np.array(
      [[g2dx0dx0(np.array([x]))[0], g2dx0dx1(np.array([x]))[0]],
       [g2dx0dx1(np.array([x]))[0], g2dx1dx1(np.array([x]))[0]]])
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((201, 201))
  XX0 *= 10; XX1 *= 10; XX *= 10
  
  #YY = np.reshape(f(XX), XX0.shape)
  #ax.contour(XX0, XX1, YY, np.arange(-1.05, 1.05, 0.1))
  
  K = np.logical_and(g1(XX) <= 0, g2(XX) <= 0)
  triangulation = mpl.tri.Triangulation(XX[K,0], XX[K,1])
  YY = f(XX[K,:])
  colormap = helper.plot.createLinearColormap(
      "myBlue", "C0", helper.plot.mixColors("C0", 0.3))
  ax.tricontour(triangulation, YY, np.arange(-1.05, 1.05, 0.1),
                cmap=colormap)
  
  YY = np.reshape(g1(XX), XX0.shape)
  ax.contour(XX0, XX1, YY, [0], colors="C0")
  YY = np.reshape(g2(XX), XX0.shape)
  ax.contour(XX0, XX1, YY, [0], colors="C0")
  
  x0 = np.array([4, 7])
  fx0 = f(np.array([x0]))[0]
  fx0Gradient = fGradient(x0)
  fx0Hessian = fHessian(x0)
  g1x0 = g1(np.array([x0]))[0]
  g2x0 = g2(np.array([x0]))[0]
  g1x0Gradient = g1Gradient(x0)
  g2x0Gradient = g2Gradient(x0)
  g1x0Hessian = g1Hessian(x0)
  g2x0Hessian = g2Hessian(x0)
  
  # L(x, u) = f(x) + G(x)^T * u
  u = np.array([1, 2])
  Lx0dx0dx0 = fx0Hessian[0,0] + np.dot(u, [g1x0Hessian[0,0],g2x0Hessian[0,0]])
  Lx0dx0dx1 = fx0Hessian[0,1] + np.dot(u, [g1x0Hessian[0,1],g2x0Hessian[0,1]])
  Lx0dx1dx1 = fx0Hessian[1,1] + np.dot(u, [g1x0Hessian[1,1],g2x0Hessian[1,1]])
  Lx0Hessian = np.array([[Lx0dx0dx0, Lx0dx0dx1], [Lx0dx0dx1, Lx0dx1dx1]])
  
  fQuadratic = lambda X: (
      np.dot(X-x0, fx0Gradient) +
      0.5 * np.sum(np.dot(X-x0, Lx0Hessian) * (X-x0), axis=1))
  g1Quadratic = lambda X: (g1x0 + np.dot(X-x0, g1x0Gradient))
  g2Quadratic = lambda X: (g2x0 + np.dot(X-x0, g2x0Gradient))
  
  #YY = np.reshape(fQuadratic(XX), XX0.shape)
  #ax.contour(XX0, XX1, YY, np.arange(0, np.max(YY), 0.5)**2)
  
  K = np.logical_and(g1Quadratic(XX) <= 0, g2Quadratic(XX) <= 0)
  triangulation = mpl.tri.Triangulation(XX[K,0], XX[K,1])
  YY = fQuadratic(XX[K,:])
  colormap = helper.plot.createLinearColormap(
      "myRed", "C1", helper.plot.mixColors("C1", 0.3))
  ax.tricontour(triangulation, YY, np.arange(0, np.max(YY), 0.5)**2,
                cmap=colormap)
  
  YY = np.reshape(g1Quadratic(XX), XX0.shape)
  ax.contour(XX0, XX1, YY, [0], colors="C1")
  YY = np.reshape(g2Quadratic(XX), XX0.shape)
  ax.contour(XX0, XX1, YY, [0], colors="C1")
  
  ax.plot(*x0, "k.")
  
  ax.text(6.8, 5, "Original\nproblem", color="C0",
          ha="left", va="center", size=9)
  ax.text(4.2, 1.5, "Quadratic\nsub-problem", color="C1",
          ha="left", va="center", size=9)
  plotTitle(ax, 3, 9.8, "SQP", ha="center", va="top")
  fig.save()



plotFunctions = [
  plotNelderMead,
  plotDifferentialEvolution,
  plotCMAES,
  plotSimulatedAnnealing,
  plotPSO,
  plotGPLCB,
  plotGradientDescentNLCG,
  plotNewton,
  plotBFGS,
  plotLogBarrier,
  plotSquaredPenalty,
  plotSQP,
]

for plotFunction in plotFunctions:
  plotFunction()
