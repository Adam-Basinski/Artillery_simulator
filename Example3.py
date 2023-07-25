import ThrowingObject
from matplotlib import pyplot as plt

# Creating list for plots.
x_axis = []
range_axis = []
momentum_axis = []

# This loop is calculating trajectory for different elevation degree and appends lists with results.
for i in range(40, 71):
    print("---------")
    print("Current Elevation degree:", i)
    print("---------")
    x = ThrowingObject.Karl_Gerat_mortar(
        rotation_angle=0,
        elevation_angle=i,
        height=0.5
    )
    x.trajectory_calculation()
    x.flight_Data
    x_axis.append(i)
    range_axis.append(round(x.flight_Data["XY_Coord"].values[-1], 2))
    momentum_axis.append(
        round(x.flight_Data["Total_Velocity"].values[-1] * x.mass, 3))

# Creating plot's axis.
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(x_axis, range_axis, 'green')
ax2.plot(x_axis, momentum_axis, 'blue')

# Signs data in plots.
ax1.set_xlabel("Elevation degree")
ax1.set_ylabel("range [m]", color='green')
ax2.set_ylabel("Contact momentum [kg*m/s]", color='blue')

# Displaying plot.
plt.tight_layout()
plt.show()

# Hold the window displayed
_x = input("Press any key to exit")
