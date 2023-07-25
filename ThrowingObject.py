import math
from matplotlib import pyplot as plt
import pandas as pd
import json
import requests
from Api_key import API_key
import datetime

# Next lines will check if the weather file named "TodaysWeather.py" is missing.
# In case this folder is missing, it will create one, but it will be empty.
# Folder will be filled later using "weather_execute()"


def create_weather_params_file():
    '''Creating file named "TodaysWeather.py", which contain weather data for further calculations.
    Created folder will be empty '''
    print("TodaysWeather file is missing, creating new one.")
    zero = str(0)

    file = ''
    file += '\ndate_day' + '=' + zero
    file += '\ndate_month' + '=' + zero
    file += '\ntemperature' + '=' + zero
    file += '\npressure' + '=' + zero
    file += '\nhumidity' + '=' + zero
    file += '\nwind_speed' + '=' + zero
    file += '\nwind_direction' + '=' + zero
    new_file = open("TodaysWeather.py", "w")
    new_file.write(file)
    new_file.flush()
    new_file.close()
    print("Creating new weather file done.")


try:
    import TodaysWeather
except ModuleNotFoundError:
    create_weather_params_file()
    import TodaysWeather

# Set style for plots
plt.style.use('bmh')


class Projectile():
    """
    Mass [kg],
    drag [-] (0-1.5),
    Velocity [m/s],
    Rotation angle in degrees (0-360 degrees),
    Elevation angle in degrees (0-90 degrees),
    Height of the cannon [m],
    """
    numberRoundParam = 5
    """Any value (which need to be rounded) will be rounded up to 5 decimal places as standard"""

    earthAcceleration = -9.80665
    """[m/s2]"""

    def __init__(Self, projectile_mass: float, drag: float, frontal_surface: float, velocity: float, rotation_angle: float, elevation_angle: float, height: float = 0.1, ifWind: bool = True, time_resolution: float = 0.01):
        print("Initializing...")

        # Creating new vectors
        # Used position, velocity and acceleration [force] as XYZ vectors
        # Cartesian co-ordinates of projectile. Starting co-ordinates are related to end of the cannon.
        Self.Coordinates_vector = [0.0, 0.0, 0]
        """[m]"""
        Self.Velocity_vector = [0.0, 0.0, 0.0]
        """[m/s]"""
        Self.Acceleration_vector = [0.0, 0.0, Self.earthAcceleration]
        """[m/s2]"""
        # Wind params
        Self.Wind_vector = [0.0, 0.0]
        """[m/s]"""
        # Time resolution
        Self.timeResolution = time_resolution
        """Defining calculation step [seconds]"""

        # Properties of projectile
        Self.mass = projectile_mass
        """[Kg]"""
        Self.dragCoefficient = drag
        """Drag of the projectile [-]"""
        Self.frontalSurface = frontal_surface
        """[m2]"""
        # Doing all things that need to be done with weather params, like:
        # checking if downloading is needed, downloading, setting params and calculating wind vector.
        # Also saving if needed
        Self.weather_execute(ifWind=ifWind)
        # Setting height of the cannon
        Self.Coordinates_vector[2] = height
        # Rotation angle must be within 0-360, it will correct value.
        # Elevation angle must be within 0-90, if angle = 0, height != 0, it will change value to 45
        Self.check_angles(elevation_angle=elevation_angle,
                          rotation_angle=rotation_angle)
        # Converting starting value of cannon position and projectile velocity to XYZ vector
        """THIS VELOCITY need to be converted to something like a rifle power."""
        Self.set_velocity_vector(velocity=velocity)
        Self.calc_acceleration_vector()
        print("Setting acceleration vector...")

        ###
        print("Initializing finished.")

    def check_angles(Self, elevation_angle, rotation_angle):
        """Check if angle is in correct range and converts degrees to radians"""
        print("Checking angles...")
        # Will set the rotation angle in usable range. It won't change results at all.
        while (rotation_angle < 0 or rotation_angle >= 360):
            # if the rotation angle is less than 0 it will correct it by adding 360.
            if rotation_angle < 360:
                rotation_angle += 360
            # if the rotation angle is less than 0 it will correct it by subtraction 360.
            elif rotation_angle > 360:
                rotation_angle -= 360
        Self.PhiDegree = rotation_angle
        Self.PhiRadian = math.radians(rotation_angle)

        # Check if elevation angle is set in range 0-90 degree.
        if (elevation_angle < 0 or elevation_angle > 90):
            print("Passed elevation angle is wrong (Should be set in range 0 - 90):",
                  elevation_angle, "\nElevation angle set 45 degrees.")
        # 90 degrees elevation angle is useless, cannon will shoot itSelf.
        #elif elevation_angle == 90:
            #print("You will shoot yourSelf! Decrease the value of the elevation angle a little.\nElevation angle set 45 degrees.")
        # 0 degrees and ground level won't work.
        elif (elevation_angle == 0 and Self.Coordinates_vector[2] == 0):
            print("Nothing will happen. Elevate the cannon a little.")
        else:
            Self.ThetaDegree = elevation_angle
            Self.ThetaRadian = math.radians(elevation_angle)

    def set_velocity_vector(Self, velocity):
        """Setting starting velocity vector"""
        print("Setting velocity vector...")
        # X velocity
        Self.Velocity_vector[0] = round(
            velocity * math.cos(Self.ThetaRadian) * math.cos(Self.PhiRadian), Self.numberRoundParam)
        # Y velocity
        Self.Velocity_vector[1] = round(
            velocity * math.cos(Self.ThetaRadian) * math.sin(Self.PhiRadian), Self.numberRoundParam)
        # Z (vertical) velocity
        Self.Velocity_vector[2] = round(
            velocity * math.sin(Self.ThetaRadian), Self.numberRoundParam)

    def weather_execute(Self, ifWind):
        """
        It will execute weather functions """
        print("Setting weather params...")
        weatherBool = Self.if_get_todays_weather()
        if weatherBool == True:
            print("Weather will be downloaded.")
        weatherParams = Self.get_weather(getWeatherBool=weatherBool)
        Self.set_weather_params(ifWind=ifWind, weatherData=weatherParams)
        if weatherBool == True:
            print("Saving todays weather...")
            Self.save_weather_params()
        pass

    def if_get_todays_weather(Self):
        """Check if weather needs to be downloaded."""
        try:
            if (TodaysWeather.date_day == datetime.datetime.today().day and TodaysWeather.date_month == datetime.datetime.today().month):
                return False
            else:
                return True
        except AttributeError:
            return True

    def get_weather(Self, getWeatherBool):
        """Downloading new weather data if needed."""
        if getWeatherBool == True:
            params = {
                "lat": 51.107883,
                "lon": 17.038538,
                'appid': API_key
            }
            request = requests.get(
                "https://api.openweathermap.org/data/2.5/weather", params=params)
            try:
                weather_data_requests = request.json()
                print("New weather data downloaded.")
            except json.decoder.JSONDecodeError:
                print("Something goes wrong, old weather data is used")
                weather_data_requests = False
        elif getWeatherBool == False:
            weather_data_requests = False
            pass
        return weather_data_requests

    def set_weather_params(Self, ifWind, weatherData):
        """It will refresh weather params if needed"""
        if weatherData == False:
            print("Using old data from:", TodaysWeather.date_day,
                  "th day of", TodaysWeather.date_month, "month.")
            pass
        else:
            TodaysWeather.temperature = weatherData['main']['temp']
            TodaysWeather.pressure = weatherData['main']['pressure']
            TodaysWeather.humidity = weatherData['main']['humidity']
            TodaysWeather.wind_speed = weatherData['wind']['speed']
            TodaysWeather.wind_direction = weatherData['wind']['deg']
        # The following code sets the effect of the wind on the projectile.
        if ifWind == True:
            Self.Wind_vector[0] = round(TodaysWeather.wind_speed * math.sin(
                math.radians(TodaysWeather.wind_direction)), Self.numberRoundParam)
            Self.Wind_vector[1] = round(TodaysWeather.wind_speed * math.cos(
                math.radians(TodaysWeather.wind_direction)), Self.numberRoundParam)
        elif ifWind == False:
            print("Windless conditions")
            Self.Wind_vector[0] = 0
            Self.Wind_vector[1] = 0
        else:
            Self.Wind_vector[0] = 0
            Self.Wind_vector[1] = 0
            print("Unknown ifWind parameter (should be True/False). Windless conditions")

    def save_weather_params(Self):
        file = ''
        file += '\ndate_day' + '=' + str(datetime.datetime.today().day)
        file += '\ndate_month' + '=' + str(datetime.datetime.today().month)
        file += '\ntemperature' + '=' + str(TodaysWeather.temperature)
        file += '\npressure' + '=' + str(TodaysWeather.pressure)
        file += '\nhumidity' + '=' + str(TodaysWeather.humidity)
        file += '\nwind_speed' + '=' + str(TodaysWeather.wind_speed)
        file += '\nwind_direction' + '=' + str(TodaysWeather.wind_direction)
        new_file = open("TodaysWeather.py", "w")
        new_file.write(file)
        new_file.flush()
        new_file.close()
        print("Saving done.")

    def calc_approximate_landing_time(Self):
        """It will calculate just the time needed for projectile to get to the ground (Including ONLY starting drag). """
        # Self made square root solver is easier to use.
        delt = 0
        delt = Self.Velocity_vector[2]**2 - 4 * \
            Self.Acceleration_vector[2] * Self.Coordinates_vector[2]
        if delt < 0:
            print("Error, delta < 0")
            return 0
        sqrt_delt = math.sqrt(delt)
        landing_time1 = (-Self.Velocity_vector[2] + sqrt_delt) / \
            (2 * Self.Acceleration_vector[2])
        landing_time2 = (-Self.Velocity_vector[2] - sqrt_delt) / \
            (2 * Self.Acceleration_vector[2])
        if landing_time1 >= 0:
            return round(landing_time1, Self.numberRoundParam)
        elif landing_time2 >= 0:
            return round(landing_time2, 5)
        else:
            print('both below zero')

    def calc_drag_force(Self):
        """It will calculate drag force at altitude"""
        # Molar mass of air =  0.0289644 kg/mol
        # R = 8.31432
        pressureAtAltitude = TodaysWeather.pressure * \
            math.exp((Self.earthAcceleration * 0.0289644 *
                     Self.Coordinates_vector[2]) / (8.31432 * TodaysWeather.temperature))
        p1_param = 6.1078*10**(7.5*(TodaysWeather.temperature-273.15) /
                               ((TodaysWeather.temperature-273.15)+237.3))
        # Convert from hPa to Pa, also convert humidity 0-100% to 0 - 1.
        pV_param = p1_param * TodaysWeather.humidity / 100 * 100
        pd_param = pressureAtAltitude * 100 - pV_param  # Pa
        # The specific gas constant for dry air 287.058 J/(kg·K)
        # The specific gas constant for wet air 461.495 J/(kg·K)
        airDensityAtAltitude = pd_param/(287.058 * TodaysWeather.temperature) + pV_param / \
            (461.495 * TodaysWeather.temperature)  # T in K, density in kg/m3
        dragForce = 0.5 * airDensityAtAltitude * Self.calc_relative_XYZ_velocity()**2 * \
            Self.frontalSurface * Self.dragCoefficient
        return -dragForce

    def calc_relative_XYZ_velocity(Self):
        """Used for drag force calculations, includes wind"""
        return math.sqrt((Self.Velocity_vector[0] + Self.Wind_vector[0])**2 + (Self.Velocity_vector[1] + Self.Wind_vector[1])**2 + Self.Velocity_vector[2]**2)

    def calc_XYZ_velocity(Self):
        """Calculate new scalar velocity needed for following calculation."""
        return math.sqrt(Self.Velocity_vector[0]**2 + Self.Velocity_vector[1]**2 + Self.Velocity_vector[2]**2)

    def calc_XY_velocity(Self):
        """Calculate horizontal velocity."""
        return math.sqrt(Self.Velocity_vector[0]**2 + Self.Velocity_vector[1]**2)

    def calc_acceleration_vector(Self):
        """Calculate acceleration vector"""
        drag_acceleration = Self.calc_drag_force() / Self.mass
        # X
        Self.Acceleration_vector[0] = (drag_acceleration * (Self.calc_XY_velocity() / Self.calc_XYZ_velocity()) * (
            Self.Velocity_vector[0] + Self.Wind_vector[0]) / Self.calc_XY_velocity())
        # Y
        Self.Acceleration_vector[1] = (drag_acceleration * (Self.calc_XY_velocity() / Self.calc_XYZ_velocity()) * (
            Self.Velocity_vector[1] + Self.Wind_vector[1]) / Self.calc_XY_velocity())
        # Z
        Self.Acceleration_vector[2] = (Self.earthAcceleration + (
            drag_acceleration * Self.Velocity_vector[2] / Self.calc_XYZ_velocity()))

    def calc_new_position(Self, deltaTime):
        """Calculate new position of projectile"""
        Self.Coordinates_vector[0] += Self.Velocity_vector[0] * \
            deltaTime + Self.Acceleration_vector[0] * deltaTime**2 / 2
        Self.Coordinates_vector[1] += Self.Velocity_vector[1] * \
            deltaTime + Self.Acceleration_vector[1] * deltaTime**2 / 2
        Self.Coordinates_vector[2] += Self.Velocity_vector[2] * \
            deltaTime + Self.Acceleration_vector[2] * deltaTime**2 / 2

    def calc_new_velocity(Self, deltaTime):
        """Calculate new velocity of projectile"""
        Self.Velocity_vector[0] += Self.Acceleration_vector[0] * deltaTime
        Self.Velocity_vector[1] += Self.Acceleration_vector[1] * deltaTime
        Self.Velocity_vector[2] += Self.Acceleration_vector[2] * deltaTime

    def calc_XY_distance(Self):
        """Calculate horizontal distance traveled."""
        return round(math.sqrt(Self.Coordinates_vector[0]**2 + Self.Coordinates_vector[1]**2), Self.numberRoundParam)

    def Append_flight_data(Self, presentTime):
        """Appends DataFrame with last step data."""
        new_flight_data_list = [
            presentTime,
            round(Self.Coordinates_vector[0], Self.numberRoundParam),
            round(Self.Coordinates_vector[1], Self.numberRoundParam),
            round(Self.Coordinates_vector[2], Self.numberRoundParam),
            round(Self.calc_XY_distance(), Self.numberRoundParam),
            round(Self.Velocity_vector[0], Self.numberRoundParam),
            round(Self.Velocity_vector[1], Self.numberRoundParam),
            round(Self.Velocity_vector[2], Self.numberRoundParam),
            round(Self.calc_XYZ_velocity(), Self.numberRoundParam),
            round(Self.calc_drag_force(), Self.numberRoundParam),
            round(Self.Acceleration_vector[0], Self.numberRoundParam),
            round(Self.Acceleration_vector[1], Self.numberRoundParam),
            round(Self.Acceleration_vector[2], Self.numberRoundParam)
        ]
        Self.flight_Data.loc[len(Self.flight_Data.index)
                             ] = new_flight_data_list

    def trajectory_calculation(Self):
        """It will calculate pandas DataFrame (.flight_Data) with data about flight."""
        presentTime = 0
        # Creating DataFrame
        Self.flight_Data = pd.DataFrame({
            "Time": [presentTime],
            "X_Coord": [Self.Coordinates_vector[0]],
            "Y_Coord": [Self.Coordinates_vector[1]],
            "Z_Coord": [Self.Coordinates_vector[2]],
            "XY_Coord": [Self.calc_XY_distance()],
            "X_Velocity": [Self.Velocity_vector[0]],
            "Y_Velocity": [Self.Velocity_vector[1]],
            "Z_Velocity": [Self.Velocity_vector[2]],
            "Total_Velocity": [Self.calc_XYZ_velocity()],
            "Drag_Force": [Self.calc_drag_force()],
            "X_Acc": [Self.Acceleration_vector[0]],
            "Y_Acc": [Self.Acceleration_vector[1]],
            "Z_Acc": [Self.Acceleration_vector[2]]
        })
        # It will calculate and append DataFrame with new params
        while Self.Coordinates_vector[2] > 0:
            # Creating time stamp for next step
            presentTime = round(
                presentTime + Self.timeResolution, Self.numberRoundParam)
            # Calculating new vectors. Old ones will be OVERWRITTEN.
            Self.calc_new_position(deltaTime=Self.timeResolution)
            if Self.Coordinates_vector[2] <= 0:
                Self.Coordinates_vector[0] = float(
                    Self.flight_Data.loc[Self.flight_Data.tail(1).index, 'X_Coord'])
                Self.Coordinates_vector[1] = float(
                    Self.flight_Data.loc[Self.flight_Data.tail(1).index, 'Y_Coord'])
                Self.Coordinates_vector[2] = float(
                    Self.flight_Data.loc[Self.flight_Data.tail(1).index, 'Z_Coord'])
                break
            Self.calc_new_velocity(deltaTime=Self.timeResolution)
            Self.calc_acceleration_vector()
            # Appending new
            Self.Append_flight_data(presentTime=presentTime)
        # After loop is break, it will find the landing spot and ad it to the DataFrame
        nextTimeStepForLanding = Self.calc_approximate_landing_time()
        Self.calc_new_position(deltaTime=nextTimeStepForLanding)
        Self.calc_new_velocity(deltaTime=nextTimeStepForLanding)
        Self.calc_acceleration_vector()
        Self.Append_flight_data(presentTime=(
            presentTime-Self.timeResolution + nextTimeStepForLanding))

    def result_graph_trajectory(Self):
        """It will print 3 plots with data about projectile's co-ordinates and altitude"""
        # Creating plot matrix
        fig, axs = plt.subplots(nrows=2, ncols=2, sharex=False)
        # Top left
        axs[0, 0].plot(Self.flight_Data["XY_Coord"],
                       Self.flight_Data["Z_Coord"])
        axs[0, 0].set(
            xlabel="Current XY distance [m]",
            ylabel="Current altitude [m]",
            # xlim=0,
            ylim=0
        )
        # Top right
        axs[0, 1].plot(Self.flight_Data["X_Coord"],
                       Self.flight_Data["Y_Coord"])
        axs[0, 1].set(
            xlabel="Current X distance [m]",
            ylabel="Current Y distance [m]",
            # xlim=0,
            # ylim=0
        )
        # Bottom
        # Combine bottom axis
        gs = axs[1, 1].get_gridspec()
        for ax in axs[-1, 0:]:
            ax.remove()
        ax_expanded = fig.add_subplot(gs[-1, 0:])
        ax_expanded.plot(Self.flight_Data["Time"], Self.flight_Data["Z_Coord"])
        ax_expanded.set(
            xlabel="Time [s]",
            ylabel="Current altitude [m]",
            # xlim=0,
            ylim=0
        )
        # Graph display
        fig.suptitle("Trajectory")
        plt.tight_layout()
        plt.show()

    def result_graph_trajectory_3D(Self):
        """It will print 3 graph, which will show how projectile will fly"""
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        ax.plot(Self.flight_Data["X_Coord"],
                Self.flight_Data["Y_Coord"],
                Self.flight_Data["Z_Coord"])
        ax.set(
            xlabel="X distance [m]",
            ylabel="Y distance [m]",
            zlabel="Altitude [m]",
            # xlim=0,
            # ylim=0,
            zlim=0,
            fc="#ffffff"
        )
        # Way of changing spine placement in 3D plot
        ax.zaxis._axinfo['juggled'] = (1, 2, 0)
        # Increasing "distance" of data plot (needed, because axis label was cut off)
        ax.dist = 12
        plt.title("Trajectory in 3 dimension")
        plt.tight_layout()
        plt.show()

    def result_graph_drag_force(Self):
        """Graph of drag force in velocity function"""
        plt.plot(Self.flight_Data["Total_Velocity"],
                 Self.flight_Data["Drag_Force"])
        plt.xlim = 0
        plt.title("Drag force in velocity function")
        plt.xlabel("Velocity [m/s]")
        plt.ylabel("Drag force [m/s^2]")
        plt.tight_layout()
        plt.show()

    def result_graph_velocity(Self):
        """Graph of projectile velocity in time function"""
        plt.plot(
            Self.flight_Data["Time"],
            Self.flight_Data["Total_Velocity"]
        )
        plt.xlim = 0
        plt.title("Velocity in time function")
        plt.xlabel("Time [s]")
        plt.ylabel("Velocity [m/s]")
        plt.tight_layout()
        plt.show()

    def result_table(Self):
        spacer = " "
        print(spacer, "---Final results---")
        print(spacer, "Impact speed:",
              round(Self.flight_Data["Total_Velocity"].values[-1], 3), "m/s.")
        print(spacer, "With projectile mass equal to:", Self.mass,
              "kg, momentum is equal to:", round(Self.flight_Data["Total_Velocity"].values[-1] * Self.mass, 3), "kg*m/s.")
        print(spacer, "Total distance flown:",
              round(Self.flight_Data["XY_Coord"].values[-1], 2), "m.")
        print(spacer, "Maximum height:", round(
            max(Self.flight_Data["Z_Coord"]), 3), "m.")
        print(spacer, "Time of flight:", round(
            Self.flight_Data["Time"].values[-1], 3), "s.")

# for drag coefficient, using: https://www.grc.nasa.gov/www/k-12/rocket/shaped.html last visit: 16.12.2022


class Glock_handgun(Projectile):
    """Simple handgun."""
    def __init__(Self, rotation_angle: float, elevation_angle: float, height: float, ifWind: bool = True, time_resolution: float = 0.01):
        print("---Calculation for Handgun---")
        projectile_mass = 0.00804
        frontal_surface = 0.00006362
        velocity = 350
        drag = 0.045
        # Params source https://en.wikipedia.org/wiki/9%C3%9719mm_Parabellum last visit: 16.12.2022
        # Bullet: Federal FMJ
        # Effective range 50 m.
        super().__init__(projectile_mass, drag, frontal_surface, velocity,
                         rotation_angle, elevation_angle, height, ifWind, time_resolution)


class Karl_Gerat_mortar(Projectile):
    """Big historical German self-propelled mortar (really big)"""
    def __init__(Self, rotation_angle: float, elevation_angle: float, height: float, ifWind: bool = True, time_resolution: float = 0.01):
        print("---Calculation for Karl Gerat mortar---")
        projectile_mass = 1700
        frontal_surface = 0.2827
        velocity = 283
        drag = 0.295
        # Params source https://en.wikipedia.org/wiki/Karl-Ger%C3%A4t last visit 16.12.2022
        # Range 6.440 m.

        super().__init__(projectile_mass, drag, frontal_surface, velocity,
                         rotation_angle, elevation_angle, height, ifWind, time_resolution)


class Sniper_rifle_M2010(Projectile):
    """Randomly chose sniper rifle"""
    def __init__(Self, rotation_angle: float, elevation_angle: float, height: float, ifWind: bool = True, time_resolution: float = 0.01):
        print("---Calculation for Sniper rifle M2010---")
        projectile_mass = 0.01166
        frontal_surface = 0.00005849
        velocity = 869
        drag = 0.045
        # Params source https://en.wikipedia.org/wiki/M2010_Enhanced_Sniper_Rifle last visit 16.12.2022
        # Bullet: MK 248 MOD 1 .300 Winchester Magnum
        # Effective range 1.370 m.
        super().__init__(projectile_mass, drag, frontal_surface, velocity,
                         rotation_angle, elevation_angle, height, ifWind, time_resolution)


class Ancient_cannon(Projectile):
    """Ancient cannon, that used to be mounted on ships"""
    def __init__(Self, rotation_angle: float, elevation_angle: float, height: float, ifWind: bool = True, time_resolution: float = 0.01):
        print("---Calculation for ancient cannon---")
        projectile_mass = 14.51
        frontal_surface = 0.01979
        velocity = 487
        drag = 0.2
        # Params source https://www.military-history.org/fact-file/the-broadside.htm, http://www.relicman.com/artillery/Artillery1500-Ball32pdr.html last visit 16.12.2022
        super().__init__(projectile_mass, drag, frontal_surface, velocity,
                         rotation_angle, elevation_angle, height, ifWind, time_resolution)
