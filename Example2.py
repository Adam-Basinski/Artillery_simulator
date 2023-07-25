from ThrowingObject import Karl_Gerat_mortar

Mortar = Karl_Gerat_mortar(
    rotation_angle=90,
    elevation_angle=55,
    height=0.1
)

Mortar.trajectory_calculation()

# Different possible build-in output's
Mortar.result_graph_trajectory()
Mortar.result_graph_trajectory_3D()
Mortar.result_graph_velocity()
Mortar.result_graph_drag_force()
Mortar.result_table()

# Hold the window displayed
_x = input("Press any key to exit")
