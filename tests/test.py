from matplotlib import pyplot as plt
import numpy as np

plt.figure()
a = [1,2,5,6,9,11,15,17,18]
plt.hlines(1,1,20)  # Draw a horizontal line (at y=1, from x=1 to x=20)
plt.eventplot(a, orientation='horizontal', colors='b')
plt.axis('off')
plt.show()