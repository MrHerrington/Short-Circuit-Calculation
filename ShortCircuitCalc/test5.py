import matplotlib.pyplot as plt
import numpy as np
import time
from ShortCircuitCalc.gui.windows import BlitManager

# Generate data
x = []
y = []

x2 = np.random.rand(100)
y2 = np.random.rand(100)

# make a new figure
fig, ax = plt.subplots()
scatter = ax.scatter(x, y)

bm = BlitManager(fig.canvas, [scatter])
plt.axis([0, 1, 0, 1])
# plt.show(block=False)
# plt.pause(.1)

for i in range(100):
    x = np.append(x, np.random.rand())
    y = np.append(y, np.random.rand())
    scatter.set_offsets(np.c_[x, y])
    bm.update()

plt.show()
