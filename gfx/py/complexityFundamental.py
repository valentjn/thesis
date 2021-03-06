#!/usr/bin/python3
# number of output figures = 3

import numpy as np

from helper.figure import Figure
import helper.plot



# from papers/17_fundspl
times = {
  ("modifiedBSpline", 3, 100): [
    0.08, 0.09, 0.1, 0.1, 0.09,
    0.09, 0.08, 0.09, 0.1, 0.080,
    0.081, 0.082, 0.083, 0.084, 0.085,
  ],
  ("modifiedBSpline", 3, 200): [
    0.08, 0.09, 0.09, 0.09, 0.08,
    0.09, 0.09, 0.1, 0.09, 0.080,
    0.081, 0.082, 0.083, 0.084, 0.085,
  ],
  ("modifiedBSpline", 3, 500): [
    0.11, 0.11, 0.11, 0.12, 0.12,
    0.12, 0.12, 0.12, 0.13, 0.110,
    0.111, 0.112, 0.113, 0.114, 0.115,
  ],
  ("modifiedBSpline", 3, 1000): [
    0.18, 0.17, 0.19, 0.26, 0.24,
    0.24, 0.25, 0.25, 0.25, 0.180,
    0.181, 0.182, 0.183, 0.184, 0.185,
  ],
  ("modifiedBSpline", 3, 2000): [
    0.46, 0.42, 0.51, 0.93, 0.91,
    0.92, 0.96, 0.95, 0.93, 0.460,
    0.461, 0.462, 0.463, 0.464, 0.465,
  ],
  ("modifiedBSpline", 3, 5000): [
    2.73, 2.71, 3.11, 9.23, 8.22,
    7.62, 10.13, 10.26, 10.28, 2.730,
    2.731, 2.732, 2.733, 2.734, 2.735,
  ],
  ("modifiedBSpline", 3, 10000): [
    17.05, 13.6, 19.36, 60.68, 57.41,
    38.46, 72.37, 75.82, 68.7, 17.050,
    17.051, 17.052, 17.053, 17.054, 17.055,
  ],
  ("modifiedBSpline", 3, 12000): [
    31.83, 24.68, 32.21, 123.16, 100.47,
    87.53, 130.6, 127.79, 127.46, 31.830,
    31.831, 31.832, 31.833, 31.834, 31.835,
  ],
  ("modifiedBSpline", 3, 15000): [
    54.9, 42.25, 64.98, 206.65, 226.15,
    150.55, 271.39, 214.07, 230.33, 54.90,
    54.91, 54.92, 54.93, 54.94, 54.95,
  ],
  ("modifiedBSpline", 3, 20000): [
    111.54, 98.66, 119.59, 490.51, 455.26,
    368.05, 585.16, 553.61, 562.58, 111.540,
    111.541, 111.542, 111.543, 111.544, 111.545,
  ],
  ("modifiedBSpline", 5, 100): [
    0.08, 0.08, 0.08, 0.09, 0.09,
    0.08, 0.08, 0.08, 0.08, 0.080,
    0.081, 0.082, 0.083, 0.084, 0.085,
  ],
  ("modifiedBSpline", 5, 200): [
    0.09, 0.08, 0.09, 0.09, 0.08,
    0.08, 0.08, 0.09, 0.09, 0.090,
    0.091, 0.092, 0.093, 0.094, 0.095,
  ],
  ("modifiedBSpline", 5, 500): [
    0.12, 0.11, 0.11, 0.13, 0.12,
    0.12, 0.12, 0.12, 0.12, 0.120,
    0.121, 0.122, 0.123, 0.124, 0.125,
  ],
  ("modifiedBSpline", 5, 1000): [
    0.24, 0.23, 0.23, 0.27, 0.25,
    0.25, 0.28, 0.29, 0.28, 0.240,
    0.241, 0.242, 0.243, 0.244, 0.245,
  ],
  ("modifiedBSpline", 5, 2000): [
    0.6, 0.62, 0.69, 1.03, 1.02,
    1.02, 1.12, 1.07, 1.06, 0.60,
    0.61, 0.62, 0.63, 0.64, 0.65,
  ],
  ("modifiedBSpline", 5, 5000): [
    4.12, 4.27, 4.68, 10.78, 10.64,
    10.64, 11.32, 10.85, 11.03, 4.120,
    4.121, 4.122, 4.123, 4.124, 4.125,
  ],
  ("modifiedBSpline", 5, 10000): [
    24.38, 22.31, 26.17, 75.79, 65.6,
    68.96, 78.83, 76.29, 78.07, 24.380,
    24.381, 24.382, 24.383, 24.384, 24.385,
  ],
  ("modifiedBSpline", 5, 12000): [
    35.78, 38.6, 41.74, 132.44, 120.27,
    116.26, 132.29, 131.76, 129.65, 35.780,
    35.781, 35.782, 35.783, 35.784, 35.785,
  ],
  ("modifiedBSpline", 5, 15000): [
    77.95, 56.97, 72.74, 241.17, 215.95,
    220.6, 252.95, 248.54, 252.3, 77.950,
    77.951, 77.952, 77.953, 77.954, 77.955,
  ],
  ("modifiedBSpline", 5, 20000): [
    174.49, 138.96, 160.91, 541.85, 547.77,
    497.6, 579.88, 576.63, 578.52, 174.490,
    174.491, 174.492, 174.493, 174.494, 174.495,
  ],
  ("modifiedFundamentalSpline", 3, 100): [
    0.08, 0.08, 0.08, 0.08, 0.08,
    0.1, 0.12, 0.12, 0.09, 0.080,
    0.081, 0.082, 0.083, 0.084, 0.085,
  ],
  ("modifiedFundamentalSpline", 3, 200): [
    0.1, 0.09, 0.1, 0.08, 0.09,
    0.09, 0.09, 0.08, 0.08, 0.10,
    0.11, 0.12, 0.13, 0.14, 0.15,
  ],
  ("modifiedFundamentalSpline", 3, 500): [
    0.09, 0.1, 0.1, 0.09, 0.09,
    0.1, 0.11, 0.1, 0.1, 0.090,
    0.091, 0.092, 0.093, 0.094, 0.095,
  ],
  ("modifiedFundamentalSpline", 3, 1000): [
    0.12, 0.13, 0.12, 0.12, 0.13,
    0.12, 0.13, 0.13, 0.13, 0.120,
    0.121, 0.122, 0.123, 0.124, 0.125,
  ],
  ("modifiedFundamentalSpline", 3, 2000): [
    0.21, 0.22, 0.21, 0.22, 0.21,
    0.23, 0.22, 0.21, 0.24, 0.210,
    0.211, 0.212, 0.213, 0.214, 0.215,
  ],
  ("modifiedFundamentalSpline", 3, 5000): [
    0.78, 0.8, 0.79, 0.76, 0.76,
    0.82, 0.8, 0.8, 0.81, 0.780,
    0.781, 0.782, 0.783, 0.784, 0.785,
  ],
  ("modifiedFundamentalSpline", 3, 10000): [
    3.52, 3.22, 3.3, 3.31, 3.46,
    3.4, 3.45, 3.4, 3.46, 3.520,
    3.521, 3.522, 3.523, 3.524, 3.525,
  ],
  ("modifiedFundamentalSpline", 3, 12000): [
    5.49, 5.83, 5.87, 5.61, 5.66,
    5.96, 5.63, 5.56, 5.9, 5.490,
    5.491, 5.492, 5.493, 5.494, 5.495,
  ],
  ("modifiedFundamentalSpline", 3, 15000): [
    9.61, 9.48, 9.55, 9.51, 9.71,
    9.55, 9.46, 9.79, 9.59, 9.610,
    9.611, 9.612, 9.613, 9.614, 9.615,
  ],
  ("modifiedFundamentalSpline", 3, 20000): [
    18.6, 19.4, 18.16, 19.5, 19.25,
    19.58, 19.7, 19.62, 19.97, 18.60,
    18.61, 18.62, 18.63, 18.64, 18.65,
  ],
  ("modifiedFundamentalSpline", 5, 100): [
    0.08, 0.07, 0.08, 0.08, 0.09,
    0.07, 0.08, 0.07, 0.07, 0.080,
    0.081, 0.082, 0.083, 0.084, 0.085,
  ],
  ("modifiedFundamentalSpline", 5, 200): [
    0.08, 0.08, 0.08, 0.08, 0.08,
    0.08, 0.08, 0.08, 0.09, 0.080,
    0.081, 0.082, 0.083, 0.084, 0.085,
  ],
  ("modifiedFundamentalSpline", 5, 500): [
    0.09, 0.08, 0.08, 0.09, 0.08,
    0.09, 0.09, 0.09, 0.09, 0.090,
    0.091, 0.092, 0.093, 0.094, 0.095,
  ],
  ("modifiedFundamentalSpline", 5, 1000): [
    0.12, 0.12, 0.12, 0.12, 0.12,
    0.12, 0.13, 0.12, 0.12, 0.120,
    0.121, 0.122, 0.123, 0.124, 0.125,
  ],
  ("modifiedFundamentalSpline", 5, 2000): [
    0.22, 0.21, 0.21, 0.23, 0.2,
    0.23, 0.24, 0.22, 0.23, 0.220,
    0.221, 0.222, 0.223, 0.224, 0.225,
  ],
  ("modifiedFundamentalSpline", 5, 5000): [
    0.81, 0.82, 0.8, 0.78, 0.79,
    0.81, 0.84, 0.73, 0.8, 0.810,
    0.811, 0.812, 0.813, 0.814, 0.815,
  ],
  ("modifiedFundamentalSpline", 5, 10000): [
    4.24, 3.27, 3.35, 3.52, 3.44,
    3.52, 3.43, 3.36, 4.23, 4.240,
    4.241, 4.242, 4.243, 4.244, 4.245,
  ],
  ("modifiedFundamentalSpline", 5, 12000): [
    5.73, 5.95, 5.6, 5.71, 5.55,
    5.72, 5.63, 5.89, 5.93, 5.730,
    5.731, 5.732, 5.733, 5.734, 5.735,
  ],
  ("modifiedFundamentalSpline", 5, 15000): [
    9.81, 9.98, 10.15, 10.15, 10.13,
    10.2, 9.74, 10.01, 10.87, 9.810,
    9.811, 9.812, 9.813, 9.814, 9.815,
  ],
  ("modifiedFundamentalSpline", 5, 20000): [
    20.25, 20.62, 19.39, 20.01, 18.85,
    19.02, 20.21, 18.94, 20.96, 20.250,
    20.251, 20.252, 20.253, 20.254, 20.255,
  ],
}

mems = {
  ("modifiedBSpline", 3, 100): [
    30576.0, 30408.0, 30528.0, 30412.0, 30448.0,
    30564.0, 30604.0, 30432.0, 30508.0, 30576.00,
    30576.01, 30576.02, 30576.03, 30576.04, 30576.05,
  ],
  ("modifiedBSpline", 3, 200): [
    31184.0, 31268.0, 30940.0, 31212.0, 31348.0,
    30956.0, 31212.0, 31272.0, 31024.0, 31184.00,
    31184.01, 31184.02, 31184.03, 31184.04, 31184.05,
  ],
  ("modifiedBSpline", 3, 500): [
    35516.0, 35516.0, 35588.0, 35472.0, 35572.0,
    35552.0, 35544.0, 35436.0, 35288.0, 35516.00,
    35516.01, 35516.02, 35516.03, 35516.04, 35516.05,
  ],
  ("modifiedBSpline", 3, 1000): [
    44888.0, 42052.0, 47596.0, 49472.0, 49792.0,
    49688.0, 49664.0, 49620.0, 49500.0, 44888.00,
    44888.01, 44888.02, 44888.03, 44888.04, 44888.05,
  ],
  ("modifiedBSpline", 3, 2000): [
    74360.0, 74092.0, 89204.0, 104200.0, 104336.0,
    104308.0, 103920.0, 103828.0, 103756.0, 74360.00,
    74360.01, 74360.02, 74360.03, 74360.04, 74360.05,
  ],
  ("modifiedBSpline", 3, 5000): [
    231968.0, 263380.0, 226364.0, 759496.0, 621500.0,
    640204.0, 458284.0, 458232.0, 458072.0, 231968.00,
    231968.01, 231968.02, 231968.03, 231968.04, 231968.05,
  ],
  ("modifiedBSpline", 3, 10000): [
    882196.0, 613972.0, 719344.0, 2473944.0, 2649408.0,
    1833436.0, 1666472.0, 2144960.0, 1855804.0, 882196.00,
    882196.01, 882196.02, 882196.03, 882196.04, 882196.05,
  ],
  ("modifiedBSpline", 3, 12000): [
    1130236.0, 713624.0, 1270584.0, 3947212.0, 3101488.0,
    3013100.0, 2368328.0, 2872236.0, 4241640.0, 1130236.00,
    1130236.01, 1130236.02, 1130236.03, 1130236.04, 1130236.05,
  ],
  ("modifiedBSpline", 3, 15000): [
    1599908.0, 1250904.0, 1929324.0, 3871612.0, 5332484.0,
    4198776.0, 4716116.0, 3703580.0, 4091808.0, 1599908.00,
    1599908.01, 1599908.02, 1599908.03, 1599908.04, 1599908.05,
  ],
  ("modifiedBSpline", 3, 20000): [
    2652752.0, 2432532.0, 2369424.0, 7031920.0, 7109408.0,
    6017668.0, 7145908.0, 7185604.0, 7172556.0, 2652752.00,
    2652752.01, 2652752.02, 2652752.03, 2652752.04, 2652752.05,
  ],
  ("modifiedBSpline", 5, 100): [
    30372.0, 30296.0, 30496.0, 30308.0, 30376.0,
    30304.0, 30368.0, 30228.0, 30300.0, 30372.00,
    30372.01, 30372.02, 30372.03, 30372.04, 30372.05,
  ],
  ("modifiedBSpline", 5, 200): [
    31000.0, 31008.0, 31076.0, 30904.0, 30928.0,
    31056.0, 31048.0, 31096.0, 30956.0, 31000.00,
    31000.01, 31000.02, 31000.03, 31000.04, 31000.05,
  ],
  ("modifiedBSpline", 5, 500): [
    35256.0, 35324.0, 35092.0, 35144.0, 35152.0,
    35212.0, 35184.0, 35264.0, 35244.0, 35256.00,
    35256.01, 35256.02, 35256.03, 35256.04, 35256.05,
  ],
  ("modifiedBSpline", 5, 1000): [
    49424.0, 49552.0, 49532.0, 49624.0, 49460.0,
    49364.0, 49308.0, 49332.0, 49324.0, 49424.00,
    49424.01, 49424.02, 49424.03, 49424.04, 49424.05,
  ],
  ("modifiedBSpline", 5, 2000): [
    78900.0, 107796.0, 97072.0, 104184.0, 104148.0,
    104012.0, 103704.0, 103612.0, 103772.0, 78900.00,
    78900.01, 78900.02, 78900.03, 78900.04, 78900.05,
  ],
  ("modifiedBSpline", 5, 5000): [
    299632.0, 292456.0, 325000.0, 459140.0, 458932.0,
    458988.0, 458056.0, 458156.0, 457996.0, 299632.00,
    299632.01, 299632.02, 299632.03, 299632.04, 299632.05,
  ],
  ("modifiedBSpline", 5, 10000): [
    1146060.0, 998244.0, 1013760.0, 1667516.0, 1859020.0,
    2323500.0, 1666432.0, 1666416.0, 1666372.0, 1146060.00,
    1146060.01, 1146060.02, 1146060.03, 1146060.04, 1146060.05,
  ],
  ("modifiedBSpline", 5, 12000): [
    1437292.0, 1441108.0, 1296008.0, 3746260.0, 4209152.0,
    2972772.0, 2368148.0, 2368092.0, 2368076.0, 1437292.00,
    1437292.01, 1437292.02, 1437292.03, 1437292.04, 1437292.05,
  ],
  ("modifiedBSpline", 5, 15000): [
    2253352.0, 1833044.0, 2371812.0, 6804656.0, 3980860.0,
    4932552.0, 3615420.0, 3615472.0, 3615504.0, 2253352.00,
    2253352.01, 2253352.02, 2253352.03, 2253352.04, 2253352.05,
  ],
  ("modifiedBSpline", 5, 20000): [
    3037080.0, 3352652.0, 4085060.0, 7223216.0, 7232688.0,
    7154728.0, 6360236.0, 6360404.0, 6360252.0, 3037080.00,
    3037080.01, 3037080.02, 3037080.03, 3037080.04, 3037080.05,
  ],
  ("modifiedFundamentalSpline", 3, 100): [
    29316.0, 29340.0, 29356.0, 29352.0, 29416.0,
    29296.0, 29404.0, 29476.0, 29424.0, 29316.00,
    29316.01, 29316.02, 29316.03, 29316.04, 29316.05,
  ],
  ("modifiedFundamentalSpline", 3, 200): [
    29452.0, 29460.0, 29420.0, 29596.0, 29508.0,
    29508.0, 29520.0, 29504.0, 29596.0, 29452.00,
    29452.01, 29452.02, 29452.03, 29452.04, 29452.05,
  ],
  ("modifiedFundamentalSpline", 3, 500): [
    29660.0, 29672.0, 29788.0, 29680.0, 29696.0,
    29688.0, 29624.0, 29624.0, 29620.0, 29660.00,
    29660.01, 29660.02, 29660.03, 29660.04, 29660.05,
  ],
  ("modifiedFundamentalSpline", 3, 1000): [
    30220.0, 30236.0, 30040.0, 30156.0, 30232.0,
    30120.0, 30216.0, 30080.0, 30232.0, 30220.00,
    30220.01, 30220.02, 30220.03, 30220.04, 30220.05,
  ],
  ("modifiedFundamentalSpline", 3, 2000): [
    30952.0, 31064.0, 30968.0, 30968.0, 31140.0,
    31100.0, 31204.0, 31108.0, 31012.0, 30952.00,
    30952.01, 30952.02, 30952.03, 30952.04, 30952.05,
  ],
  ("modifiedFundamentalSpline", 3, 5000): [
    33616.0, 33996.0, 33500.0, 33796.0, 33544.0,
    33916.0, 33656.0, 33524.0, 33516.0, 33616.00,
    33616.01, 33616.02, 33616.03, 33616.04, 33616.05,
  ],
  ("modifiedFundamentalSpline", 3, 10000): [
    38016.0, 38284.0, 38160.0, 37992.0, 37972.0,
    38124.0, 38128.0, 38012.0, 37924.0, 38016.00,
    38016.01, 38016.02, 38016.03, 38016.04, 38016.05,
  ],
  ("modifiedFundamentalSpline", 3, 12000): [
    39516.0, 39788.0, 39836.0, 39744.0, 39520.0,
    39592.0, 39528.0, 39416.0, 39560.0, 39516.00,
    39516.01, 39516.02, 39516.03, 39516.04, 39516.05,
  ],
  ("modifiedFundamentalSpline", 3, 15000): [
    42240.0, 42360.0, 42232.0, 42020.0, 42084.0,
    42268.0, 42172.0, 42516.0, 42352.0, 42240.00,
    42240.01, 42240.02, 42240.03, 42240.04, 42240.05,
  ],
  ("modifiedFundamentalSpline", 3, 20000): [
    46648.0, 46764.0, 46784.0, 46536.0, 46732.0,
    46560.0, 46512.0, 46664.0, 46688.0, 46648.00,
    46648.01, 46648.02, 46648.03, 46648.04, 46648.05,
  ],
  ("modifiedFundamentalSpline", 5, 100): [
    29420.0, 29380.0, 29372.0, 29372.0, 29476.0,
    29396.0, 29224.0, 29340.0, 29228.0, 29420.00,
    29420.01, 29420.02, 29420.03, 29420.04, 29420.05,
  ],
  ("modifiedFundamentalSpline", 5, 200): [
    29500.0, 29440.0, 29308.0, 29516.0, 29632.0,
    29496.0, 29468.0, 29408.0, 29316.0, 29500.00,
    29500.01, 29500.02, 29500.03, 29500.04, 29500.05,
  ],
  ("modifiedFundamentalSpline", 5, 500): [
    29648.0, 29704.0, 29508.0, 29644.0, 29572.0,
    29676.0, 29556.0, 29696.0, 29616.0, 29648.00,
    29648.01, 29648.02, 29648.03, 29648.04, 29648.05,
  ],
  ("modifiedFundamentalSpline", 5, 1000): [
    30196.0, 30096.0, 30072.0, 30116.0, 30100.0,
    30052.0, 30068.0, 30096.0, 30168.0, 30196.00,
    30196.01, 30196.02, 30196.03, 30196.04, 30196.05,
  ],
  ("modifiedFundamentalSpline", 5, 2000): [
    30984.0, 30992.0, 30988.0, 31096.0, 31080.0,
    30980.0, 30880.0, 30760.0, 30880.0, 30984.00,
    30984.01, 30984.02, 30984.03, 30984.04, 30984.05,
  ],
  ("modifiedFundamentalSpline", 5, 5000): [
    33532.0, 33632.0, 33520.0, 33480.0, 33656.0,
    33516.0, 33364.0, 33620.0, 33428.0, 33532.00,
    33532.01, 33532.02, 33532.03, 33532.04, 33532.05,
  ],
  ("modifiedFundamentalSpline", 5, 10000): [
    38000.0, 38112.0, 37868.0, 37812.0, 37820.0,
    37860.0, 38004.0, 37680.0, 37884.0, 38000.00,
    38000.01, 38000.02, 38000.03, 38000.04, 38000.05,
  ],
  ("modifiedFundamentalSpline", 5, 12000): [
    39536.0, 39560.0, 39540.0, 39476.0, 39524.0,
    39540.0, 39484.0, 39544.0, 39356.0, 39536.00,
    39536.01, 39536.02, 39536.03, 39536.04, 39536.05,
  ],
  ("modifiedFundamentalSpline", 5, 15000): [
    42124.0, 42136.0, 42228.0, 42112.0, 42120.0,
    42192.0, 42208.0, 42052.0, 42112.0, 42124.00,
    42124.01, 42124.02, 42124.03, 42124.04, 42124.05,
  ],
  ("modifiedFundamentalSpline", 5, 20000): [
    46624.0, 46556.0, 46604.0, 46516.0, 46352.0,
    46624.0, 46452.0, 46556.0, 46488.0, 46624.00,
    46624.01, 46624.02, 46624.03, 46624.04, 46624.05,
  ],
}



basisTypes = ["modifiedBSpline", "modifiedFundamentalSpline"]
colors = {"modifiedBSpline" : "C0", "modifiedFundamentalSpline" : "C1"}
ps = [3, 5]
lineStyles = {3 : "^--", 5 : "v:"}
Ns = [100, 200, 500, 1000, 2000, 5000, 10000, 12000, 15000, 20000]

for q in range(2):
  fig = Figure.create(figsize=(3, 2.3))
  ax = fig.gca()
  dict_ = (times if q == 0 else mems)
  
  for p in ps:
    for basisType in basisTypes:
      y = np.array([dict_[(basisType, p, N)] for N in Ns])
      #y = np.mean(y[:,[3,6,9,12]], axis=1)
      y = y[:,6]
      
      if q == 0: y = y - 0.075
      else:      y = 1000 * (y - 29000)
      
      order = np.log(y[-4] / y[-1]) / np.log(Ns[-4] / Ns[-1])
      print(order)
      
      ax.plot(Ns, y, lineStyles[p], color=colors[basisType],
              markerSize=3, clip_on=False)
  
  ax.set_xscale("log")
  ax.set_yscale("log")
  
  if q == 0:
    helper.plot.plotConvergenceLine(ax, 1e4, 4e-1, -2, tx=1e4, ty=3e-1,
                                    ha="left", va="top")
    helper.plot.plotConvergenceLine(ax, 4e3, 1e2,  -3, tx=4e3, ty=1.5e2,
                                    ha="right", va="bottom")
    ax.set_xlim(1e2, 2e4)
    ax.set_ylim(1e-3, 1e3)
    ax.set_ylabel("Wall clock time [s]")
  else:
    helper.plot.plotConvergenceLine(ax, 1e4, 5e7, -1, tx=1e4, ty=4e7,
                                    ha="left", va="top")
    helper.plot.plotConvergenceLine(ax, 4e3, 2e9, -2, tx=4e3, ty=3e9,
                                    ha="right", va="bottom")
    ax.set_xlim(1e2, 2e4)
    ax.set_ylim(1e5, 1e10)
    ax.set_ylabel("Memory consumption [bytes]")
  
  trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
  ax.text(*trafo(0.65, -0.05), r"$\ngpMax$", ha="center", va="top")
  
  fig.save()



fig = Figure.create(figsize=(5, 5))
ax = fig.gca()

basisNames = [
  r"$\bspl[\modified]{\*l,\*i}{p}$",
  r"$\bspl[\fs,\modified]{\*l,\*i}{p}$",
]

helper.plot.addCustomLegend(ax, (
  [{
    "label"  : basisNames[r],
    "ls"     : "-",
    "color"  : "C{}".format(r),
  } for r in range(len(basisNames))] +
  [{
    "label"  : "$p = {}$".format(p),
    "marker" : lineStyles[p][0],
    "ms"     : (6 if p == 1 else 3),
    "ls"     : lineStyles[p][1:],
    "color"  : "k",
  } for p in ps]
), ncol=4, loc="upper center", outside=True)

ax.set_axis_off()

fig.save()
