#!/usr/bin/python3
# number of output figures = 1

import base64
import gzip

import numpy as np

import helper.basis
import helper.figure
import helper.grid

d = 2
n = 3
p = 3
l = (1, 1)
i = (1, 1)

# s = '''code'''
# a = base64.b64encode(gzip.compress(s.encode())).decode()
# print("\n".join(a[i:i+80] for i in range(0, len(a), 80)))
g = """
H4sIAA+XGloC/31WzY7bNhC+8ykmuTQBtEZ2k03S3LIp2qToT4AE7SUXSqIs1jRpkNQqQlEgD9K+XJ6k
34wkS/Zue1l4bXL4zfcz5J+K6NGTzXVB+POYXtHDhw/V1y9/f2wNvWm7WLUUGrq5+HBw1pv09cs/SpUD
/dg5qz39pp3x2XpsKsZCT1+clrrc0K++MtQdgidN2e5NQbk10VCvE2m11/gPf2yVKOWuRj3q20Ctrqk0
xqtkNFBYv6UmRC4RDraSz61NtNcpm/hNUqiSbNrQW3x5iKExKfESVNnG0HsKrlba1+OpZegyClE02Uaz
WeAL+OdXR/hXDN+ghB7ol3Br9qWJVOuhIPCTQ9gpBlGFLuqtIa6v087gLw2h81u1IAGLVdgfOqClVFnD
pNgGZRR2u5rSQYOTdXv3cnOOFXzPWJ9u6GZAx4fDgKOsr2zNpwjd6s7ZJ8g+Pfj0oIEmNdrZH0GMNN1c
pFH7ArrYqlXMqXa9HpIIRI1GTQ+UkIiPmlW0XhTif61JK+Dg98QjzzbEdpv3Gf9HGMBhH+KOawbP4tIo
MKVA+w6uzK3O+Idd1aCvQmFJFdiM3Wpvb3M7gtL7dc+s1NQk7EDv2+/UfxC88Hu9od9b9NtO1s3Z+Fqa
1m6X2BFqoiW3odu2eSKwDT3OUskbvVvYBD0wIDeWjNmjjBtU56NxOpsZG5SRzlFfjA0VnTN622F7zxGS
/tnCNa+Fdiv0ZyQ/Z5JBGUOXokgiBEU/a81Ks0WsAaw0zppbwyLy70fYwGEIP0B2GLxmqPgZA+P+YcGl
msARFQ0hwEFvYRXAlpWztZRYi6mtNFqsCRVvLpbVKHWntUWZF4KqS9jHjiu7xEXRZ9S3xiVmH/VweOU0
/M1ItiHUx/PJm15GG84mHbkxWQQXufoV3QTvC/V91H7XdDEX9LPVe1vQh6H2ZijUG+0xFqIu6KeQ6LXf
GmfSpzrkdOallwvklxt6N+VDgn8cjHMMlJBcRSN+0NC7TDbP/Khy1iPE7ejhCpuidtR2pZLxgV7WFJKu
sr21+TSLZ+P629MopqwjH8+HwqI8HZJxDavzPqJQvqP3oxBVakPkuSErHos2k6rcn/VoLGPZ5O4lEVw1
HMydC+fRzQW+flxIapkyzPIly2I+HZFENH+29U6jiwCXT8ZWZU4fG9ZVxTZi8uMQvJGrSIwlmTFxzyiR
I9V0vpqcKdlDHNMgCMVksgPLVlcdlDaVBciD0zz8vZqhgiGIxaLxKbyDR/4K/OVZmC9xrb6uqhDH+RM4
+oV4GtI7FzAc0jw97gmm6uXKwZ3Al9ikwhEKMuOPiWRQidfBiIlT691A5rNFpGuxWahr8h3fi+kVPY31
VKBQ15i802d6cfx8XyyW6/by6tR/c2RXbFLnkBWE4oioIWcbDiv3VBol97oG9p7nXbs2H3vlnW+s5ySN
gEZimP83Xbw9d83VOUBcsq+zMIbhPw7dNM5SSLy6RuSB0MeAc3gFfpkusI1a4mDzOOds6cz/WFcwXK5A
POPhgSSjynAyNGA0n6dWp7JgQ1J8vAp5qtXQV6iQLzD0rfdw0vpltp76IoqnHwJPAm7VBb8VJQH0PGIr
nLgx38KLyNIpygZPOthHrvAsrzjL12XJocDzBTMrWlYY/lJ6zR3jiAZfG+G3akMSvVs8deSEPUYCv8Ss
PDbN56zYvL10NV5lc6kF9svzJ+vz0YS8XajAs6IyWgTzeEMS7IcjwlTOZrB8mJ5/Cs7jNyCNMUQkQPOd
B/DJVLjnkafWD2C69wGszh/AU1+zKkp9HD0q177fJdnM6FDogTT/17+4kiiA/AsAAA=="""
texts = eval(gzip.decompress(base64.b64decode(g.replace("\n", "").encode())).decode())

b = helper.basis.HierarchicalBSpline(p)
grid = helper.grid.RegularSparse()



fig = helper.figure.create()
ax = fig.add_subplot(111, projection="3d")



X, Xl, Xi = grid.generate(d, n)
N = X.shape[0]
Y = np.zeros((N,))

for k in range(N):
  x = X[k,:]
  Y[k] = np.prod([b.evaluate(l[t], i[t], X[k,t]) for t in range(d)])



xx1 = np.linspace(0, 1, 129)
xx2 = np.linspace(0, 1, 129)
XX1, XX2 = np.meshgrid(xx1, xx2)
XX = np.stack((XX1.flatten(), XX2.flatten()), axis=1)
NN = XX.shape[0]
YY = np.zeros((NN,))

for k in range(NN):
  YY[k] = np.prod([b.evaluate(l[t], i[t], XX[k,t]) for t in range(d)])

YY = np.reshape(YY, XX1.shape)

color1 = "k"
color2 = helper.figure.COLORS["anthrazit"]
text_color = (0.04, 0.04, 0.04)
text_size = 0.4

z = 0
ax.plot_surface(XX1, XX2, z, rstride=16, cstride=16, alpha=0, edgecolors=color2)
ax.plot(X[:,0], X[:,1], zs=z, marker="o", ls="", c=color2, zorder=-1)

ax.plot_surface(XX1, XX2, YY, rstride=16, cstride=16, alpha=0, edgecolors=color1)
ax.plot(X[:,0], X[:,1], zs=Y, marker="o", ls="", c=color1)

for pos, text in texts.items():
  for k in range(N):
    if (X[k,0] == pos[0]) and (X[k,1] == pos[1]):
      y = Y[k]
      break
  
  ax.text(pos[0], pos[1], y, text.strip(),
          ha="center", va="center", color=text_color, size=text_size)

ax.autoscale(tight=True)
ax.set_axis_off()

fig.save(1)
