import matplotlib.pyplot as plt


x1 = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.25, 4.5, 5.75, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]

y1 = [30.125, 30.157, 30.147, 30.444, 0.079, 0.094, 0.128, 1.077, 1.498, 3.105, 8.328, 8.625, 8.803, 10.111, 15.027, 0.083, 0.093, 0.087, 0.093, 0.083, 0.093, 0.087, 0.093, 0.079, 0.082]

x2 = [4.75, 5, 5.25, 5.5]

y2 = [40, 40, 40, 40]

x = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.25, 4.5] + [4.75, 5, 5.25, 5.5] + [5.75, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]



y = [30.125, 30.157, 30.147, 30.444, 0.079, 0.094, 0.128, 1.077, 1.498, 3.105, 8.328, 8.625, 8.803, 10.111, 15.027, 40, 40, 40, 40, 0.083, 0.093, 0.087, 0.093, 0.083, 0.093, 0.087, 0.093, 0.079, 0.082]
# ==================================
# Plot everything normally
# ==================================
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x1, y1, 'o', markerfacecolor='green', label='Feasible')
ax.plot(x2, y2, 'x', markeredgecolor='red', markerfacecolor='red', label='Timeout')
#ax.plot(x_model, model1, '-k', label='Model (k=1)')
#ax.plot(x_model, model2, '--k', label='Model (k=2)')

# ==================================
# Format plot
# ==================================
ax.set_xlabel('Threshold')
ax.set_ylabel('Time (s)')
ax.set_xlim((0, 11))
ax.set_ylim((-2, 50))
ax.set_title('Graph showing the required time to produce a result (z3)')
ax.legend()
fig.tight_layout()

plt.plot(x, y, color='green', linestyle='dashed', linewidth = 1)

plt.show()

# plotting the points 
#plt.plot(x, y, color='green', linestyle='dashed', linewidth = 3,
#         marker='o', markerfacecolor='blue', markersize=12)
 
# setting x and y axis range
#plt.xlim(1,6)
#plt.ylim(0,35)
 
# naming the x axis
#plt.xlabel('Threshold')
# naming the y axis
#plt.ylabel('Time (s)')
 
# giving a title to my graph
#plt.title('Graph showing the required time to produce a result (z3)')
 
# function to show the plot
#plt.show()


