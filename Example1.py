import ThrowingObject

Handgun = ThrowingObject.Glock_handgun(
    rotation_angle=0,
    elevation_angle=0,
    height=1.8
)

Mortar = ThrowingObject.Karl_Gerat_mortar(
    rotation_angle=0,
    elevation_angle=60,
    height=5
)

Rife = ThrowingObject.Sniper_rifle_M2010(
    rotation_angle=0,
    elevation_angle=0,
    height=1.8
)

# Function that actually calculate.
Handgun.trajectory_calculation()
Mortar.trajectory_calculation()
Rife.trajectory_calculation()

print("------Handgun------")
Handgun.result_table()
print("------Mortar------")
Mortar.result_table()
print("------Rife------")
Rife.result_table()

# Hold the window displayed
_x = input("Press any key to exit")
