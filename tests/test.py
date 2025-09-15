import numpy as np


tmp = np.array([[0,0,],
                [0,1]])

print(np.any(tmp > 0, axis=1))
print(np.where(np.any(tmp > 0, axis=1)))
print(np.where(np.any(tmp > 0, axis=1))[0])

