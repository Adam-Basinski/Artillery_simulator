import ThrowingObject
from matplotlib import pyplot as plt
from time import perf_counter as perf
from math import log10

# Creating lists use to store data after calculations
Time_resolution_List = [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005]
Calculation_time = []
Calculation_time_log = []
Distance_flown = []
Steps_number = []

# This loop calculating calculation time and accuracy (based on horizontal distance) in dependence of time resolution value.
for i in Time_resolution_List:
    print("---------")
    print("Current time resolution:", i)
    print("---------")
    x = ThrowingObject.Ancient_cannon(
        rotation_angle=0,
        elevation_angle=10,
        height=0.5,
        time_resolution=i
    )
    startTime = perf()
    x.trajectory_calculation()
    endTime = perf()
    Calculation_time.append(endTime-startTime)
    Distance_flown.append(round(x.flight_Data["XY_Coord"].values[-1], 2))
    Steps_number.append(x.flight_Data.shape[0])

# Creating graph matrix
fig, axs = plt.subplots(nrows=1, ncols=2)

# Creating plots
# Left plot
axs[0].plot(Time_resolution_List, Calculation_time, "green")
axs[0].set_xlabel("Time resolution [s]")
axs[0].set_ylabel("Decimal log of calculation time [s]")
axs[0].set_yscale('log')

# Right plot
axs[1].plot(Time_resolution_List, Distance_flown, "blue")
axs[1].set_xlabel("Time resolution [s]")
axs[1].set_ylabel("XY distance [m]")

# printing result table
for i in range(len(Time_resolution_List)):
    print("Resolution", Time_resolution_List[i], "s, takes", round(
        Calculation_time[i], 5), "seconds and execute", Steps_number[i], "steps.")

# Displaying plots
plt.tight_layout()
plt.show()

# Hold the window displayed
_x = input("Press any key to exit")
