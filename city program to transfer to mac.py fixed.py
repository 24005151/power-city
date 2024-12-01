import random
import datetime
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import logging
from matplotlib.dates import DateFormatter
import threading
import platform
import os
import time
import unittest

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Use the TkAgg backend for matplotlib
plt.switch_backend('TkAgg')

# Initialize data
weather_data = []
energy_data = []

# Constants for default capacities
DEFAULT_HYDRO_CAPACITY = 1000
DEFAULT_SOLAR_CAPACITY = 1000
DEFAULT_WIND_CAPACITY = 1000
DEFAULT_BATTERY_CAPACITY = 1000  # kWh
DEFAULT_BATTERY_LEVEL = 500  # kWh

# Constants for battery and grid
DEFAULT_BATTERY_HEALTH = 100  # Battery health percentage (0-100)
GRID_COST_PER_KWH = 0.15  # Cost per kWh in GBP


def initialize_capacities():
    """Initialize the capacities for hydro, solar, wind, and battery.

    Attempts to load capacities from 'config.py'. If the file is not found
    or there is an import error, default values are used.

    Returns:
        tuple: A tuple containing hydro_capacity, solar_capacity,
               wind_capacity, battery_capacity, battery_level.
    """
    if os.path.exists('config.py'):
        try:
            import config  # type: ignore
            hydro_capacity = config.HYDRO_CAPACITY
            solar_capacity = config.SOLAR_CAPACITY
            wind_capacity = config.WIND_CAPACITY
            battery_capacity = config.BATTERY_CAPACITY
            battery_level = config.BATTERY_LEVEL
        except ImportError:
            logging.warning(
                "Error importing from config.py, using default values."
            )
            hydro_capacity = DEFAULT_HYDRO_CAPACITY
            solar_capacity = DEFAULT_SOLAR_CAPACITY
            wind_capacity = DEFAULT_WIND_CAPACITY
            battery_capacity = DEFAULT_BATTERY_CAPACITY
            battery_level = DEFAULT_BATTERY_LEVEL
    else:
        logging.warning("config.py not found, using default values.")
        hydro_capacity = DEFAULT_HYDRO_CAPACITY
        solar_capacity = DEFAULT_SOLAR_CAPACITY
        wind_capacity = DEFAULT_WIND_CAPACITY
        battery_capacity = DEFAULT_BATTERY_CAPACITY
        battery_level = DEFAULT_BATTERY_LEVEL

    return (hydro_capacity, solar_capacity, wind_capacity,
            battery_capacity, battery_level)


# Get the initialized capacities
(hydro_capacity, solar_capacity, wind_capacity, battery_capacity,
 battery_level) = initialize_capacities()

# Initialize active states
hydro_active = True
solar_active = True
wind_active = True
battery_active = True  # Track battery state

# Initialize grid usage and cost
grid_usage = 0.0
grid_usage_cost = 0.0
total_savings = 0.0

# Initialize battery health and age
battery_health = DEFAULT_BATTERY_HEALTH
battery_age = 0  # Battery age in years
charge_cycles = 0  # Number of charge cycles


def simulate_weather():
    """Simulate weather patterns based on the current date and time.

    Returns:
        tuple: A tuple containing temperature (Celsius), wind speed (m/s),
               and solar radiation (W/m^2).
    """
    now = datetime.datetime.now()
    month = now.month
    hour = now.hour

    # Simulate temperature based on month (seasonal variation)
    if month in [12, 1, 2]:  # Winter
        temperature = random.uniform(-5, 10)
    elif month in [3, 4, 5]:  # Spring
        temperature = random.uniform(5, 20)
    elif month in [6, 7, 8]:  # Summer
        temperature = random.uniform(15, 35)
    else:  # Autumn
        temperature = random.uniform(5, 25)

    # Simulate wind speed (higher during the day)
    if 6 <= hour <= 18:
        wind_speed = random.uniform(0, 20)
    else:
        wind_speed = random.uniform(0, 10)

    # Simulate solar radiation (higher during the day)
    solar_radiation = random.uniform(0, 1000) if 6 <= hour <= 18 else 0

    logging.debug(
        f"Weather simulated: temperature={temperature:.2f}°C, "
        f"wind_speed={wind_speed:.2f} m/s, "
        f"solar_radiation={solar_radiation:.2f} W/m^2"
    )
    return temperature, wind_speed, solar_radiation


# Function to simulate energy usage
def simulate_energy_usage(temperature):
    base_usage = 1000  # Base energy usage in kWh
    usage_variation = random.uniform(-200, 200)

    # Increase energy usage if temperature is very low or very high
    if temperature < 0 or temperature > 30:
        usage_variation += 200

    energy_usage = base_usage + usage_variation
    logging.debug(
        f"Energy usage simulated: temperature={temperature}, "
        f"energy_usage={energy_usage}"
    )
    return energy_usage


def simulate_hydroelectricity():
    """Simulate hydroelectricity generation.

    Returns:
        float: Hydroelectric power generated in kW.
    """
    if not hydro_active:
        return 0

    water_flow = random.uniform(50, 500)  # m^3/s
    efficiency = 0.9  # Efficiency
    hydro_power = (water_flow * efficiency * 9.81 *
                   hydro_capacity)  # kW
    hydro_power = min(hydro_power, hydro_capacity)  # Limit to capacity
    logging.debug(
        f"Hydroelectricity simulated: hydro_power={hydro_power:.2f} kW")
    return hydro_power


def simulate_solar_power(solar_radiation):
    """Simulate solar power generation.

    Args:
        solar_radiation (float): Solar radiation in W/m^2.

    Returns:
        float: Solar power generated in kW.
    """
    if not solar_active:
        return 0

    efficiency = 0.2  # Efficiency
    solar_power = (solar_radiation * efficiency * solar_capacity /
                   1000)  # kW
    solar_power = min(solar_power, solar_capacity)  # Limit to capacity
    logging.debug(
        f"Solar power simulated: solar_power={solar_power:.2f} kW")
    return solar_power


def simulate_wind_power(wind_speed):
    """Simulate wind power generation.

    Args:
        wind_speed (float): Wind speed in m/s.

    Returns:
        float: Wind power generated in kW.
    """
    if not wind_active:
        return 0

    efficiency = 0.4  # Efficiency
    wind_power = (wind_speed**3 * efficiency * wind_capacity / 1000
                  )  # kW
    wind_power = min(wind_power, wind_capacity)  # Limit to capacity
    logging.debug(f"Wind power simulated: wind_power={wind_power:.2f} kW")
    return wind_power


# Function to update data with hydroelectricity
def update_data():
    global weather_data, energy_data, battery_level, grid_usage
    global battery_health, battery_age, charge_cycles, grid_usage_cost
    global total_savings
    try:
        current_time = datetime.datetime.now()
        temperature, wind_speed, solar_radiation = simulate_weather()
        energy_usage = simulate_energy_usage(temperature)
        hydro_power = simulate_hydroelectricity()
        solar_power = simulate_solar_power(solar_radiation)
        wind_power = simulate_wind_power(wind_speed)

        total_generation = hydro_power + solar_power + wind_power
        net_energy = total_generation - energy_usage

        # Update battery level and grid usage
        if battery_active:
            if net_energy > 0 and battery_level < battery_capacity:
                battery_level = min(
                    battery_capacity,
                    battery_level + net_energy * (battery_health / 100))
                grid_usage = 0.0
                # Increment charge cycles if battery is charged
                if battery_level == battery_capacity:
                    charge_cycles += 1
            elif net_energy < 0:
                battery_level = max(
                    0, battery_level + net_energy * (battery_health / 100))
                if battery_level == 0:
                    grid_usage = abs(net_energy)
                    grid_usage_cost += grid_usage * GRID_COST_PER_KWH
                else:
                    grid_usage = 0.0
        else:
            grid_usage = abs(net_energy) if net_energy < 0 else 0.0
            grid_usage_cost += grid_usage * GRID_COST_PER_KWH

        # Calculate savings
        total_savings = (
            total_generation - grid_usage) * GRID_COST_PER_KWH

        # Simulate battery health degradation
        battery_age += 1 / (
            365 * 24
        )  # Increment battery age by one hour
        degradation_rate = 100 / (
            2 * 365 * 24
        )  # Degradation rate to reach 0% in 2 years
        battery_health = max(
            0, battery_health -
            degradation_rate)  # Decrease battery health over time and usage

        weather_data.append(
            [current_time, temperature, wind_speed, solar_radiation])
        energy_data.append([
            current_time, energy_usage, hydro_power, solar_power,
            wind_power, battery_level, grid_usage, battery_health,
            grid_usage_cost, total_savings
        ])

        if len(weather_data) > 100:
            weather_data.pop(0)
            energy_data.pop(0)

        logging.debug(
            f"Data updated: time={current_time}, temperature={temperature}, "
            f"wind_speed={wind_speed}, "
            f"solar_radiation={solar_radiation}, "
            f"energy_usage={energy_usage}, hydro_power={hydro_power}, "
            f"solar_power={solar_power}, wind_power={wind_power}, "
            f"battery_level={battery_level}, grid_usage={grid_usage}, "
            f"battery_health={battery_health}, "
            f"battery_age={battery_age:.2f} years, "
            f"charge_cycles={charge_cycles}, "
            f"grid_usage_cost={grid_usage_cost}, "
            f"total_savings={total_savings}")
        if 'root' in globals():
            root.after(
                1000, update_text_field, current_time, temperature,
                wind_speed, solar_radiation, energy_usage, hydro_power,
                solar_power, wind_power, battery_level, grid_usage,
                battery_health, grid_usage_cost, total_savings)
    except Exception as e:
        logging.error(f"Error updating data: {e}")


# Function to animate the graph with hydroelectricity
def animate(_):
    update_data()

    energy_df = pd.DataFrame(
        energy_data,
        columns=[
            'Time', 'Energy Usage', 'Hydro Power', 'Solar Power',
            'Wind Power', 'Battery Level', 'Grid Usage', 'Battery Health',
            'Grid Usage Cost', 'Total Savings'
        ])

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax5.clear()

    ax1.plot(energy_df['Time'],
             energy_df['Hydro Power'],
             label='Hydro Power (kW)',
             color='b')
    ax1.set_title('Hydro Power', fontsize=12)
    ax1.set_xlabel('Time', fontsize=10)
    ax1.set_ylabel('Power (kW)', fontsize=10)
    ax1.tick_params(axis='x', rotation=45, labelsize=10)
    ax1.tick_params(axis='y', labelsize=10)
    ax1.legend()
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_ylim(0, 5000)  # Set y-axis limit to 5000 kW

    ax2.plot(energy_df['Time'],
             energy_df['Solar Power'],
             label='Solar Power (kW)',
             color='y')
    ax2.set_title('Solar Power', fontsize=12)
    ax2.set_xlabel('Time', fontsize=10)
    ax2.set_ylabel('Power (kW)', fontsize=10)
    ax2.tick_params(axis='x', rotation=45, labelsize=10)
    ax2.tick_params(axis='y', labelsize=10)
    ax2.legend()
    ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax2.set_ylim(0, 5000)  # Set y-axis limit to 5000 kW

    ax3.plot(energy_df['Time'],
             energy_df['Wind Power'],
             label='Wind Power (kW)',
             color='g')
    ax3.set_title('Wind Power', fontsize=12)
    ax3.set_xlabel('Time', fontsize=10)
    ax3.set_ylabel('Power (kW)', fontsize=10)
    ax3.tick_params(axis='x', rotation=45, labelsize=10)
    ax3.tick_params(axis='y', labelsize=10)
    ax3.legend()
    ax3.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax3.set_ylim(0, 5000)  # Set y-axis limit to 5000 kW

    ax4.plot(energy_df['Time'],
             energy_df['Battery Level'],
             label='Battery Level (kWh)',
             color='m')
    ax4.set_title('Battery Level', fontsize=12)
    ax4.set_xlabel('Time', fontsize=10)
    ax4.set_ylabel('Energy (kWh)', fontsize=10)
    ax4.tick_params(axis='x', rotation=45, labelsize=10)
    ax4.tick_params(axis='y', labelsize=10)
    ax4.legend()
    ax4.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax4.set_ylim(0, 5000)  # Set y-axis limit to 5000 kWh

    ax5.plot(energy_df['Time'],
             energy_df['Grid Usage'],
             label='Grid Usage (kWh)',
             color='r')
    ax5.set_title('Grid Usage', fontsize=12)
    ax5.set_xlabel('Time', fontsize=10)
    ax5.set_ylabel('Energy (kWh)', fontsize=10)
    ax5.tick_params(axis='x', rotation=45, labelsize=10)
    ax5.tick_params(axis='y', labelsize=10)
    ax5.legend()
    ax5.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

    plt.tight_layout()


# Function to update the text field
def update_text_field(current_time, temperature, wind_speed, solar_radiation,
                      energy_usage, hydro_power, solar_power, wind_power,
                      battery_level, grid_usage, battery_health,
                      grid_usage_cost, total_savings):
    text_field.config(state=tk.NORMAL)
    text_field.delete(1.0, tk.END)
    text_field.insert(tk.END, f"Time: {current_time}\n")
    text_field.insert(tk.END, f"Temperature: {temperature:.2f} C\n")
    text_field.insert(tk.END, f"Wind Speed: {wind_speed:.2f} m/s\n")
    text_field.insert(
        tk.END, f"Solar Radiation: {solar_radiation:.2f} W/m^2\n")
    text_field.insert(tk.END, f"Energy Usage: {energy_usage:.2f} kWh\n")
    text_field.insert(
        tk.END, f"Hydro Power: {hydro_power:.2f} kW\n",
        ("green", ) if hydro_active else ())
    text_field.insert(
        tk.END, f"Solar Power: {solar_power:.2f} kW\n",
        ("green", ) if solar_active else ())
    text_field.insert(
        tk.END, f"Wind Power: {wind_power:.2f} kW\n",
        ("green", ) if wind_active else ())
    text_field.insert(tk.END, f"Battery Level: {battery_level:.2f} kWh\n")
    if grid_usage > 0:
        text_field.insert(tk.END,
                         f"Grid Usage: {grid_usage:.2f} kWh\n", ("red", ))
    else:
        text_field.insert(tk.END, f"Grid Usage: {grid_usage:.2f} kWh\n")
    text_field.insert(tk.END, f"Battery Health: {battery_health:.2f}%\n")
    text_field.insert(tk.END, f"Battery Age: {battery_age:.2f} years\n")
    text_field.insert(tk.END, f"Charge Cycles: {charge_cycles:.2f}\n")
    text_field.insert(tk.END, f"Grid Usage Cost: £{grid_usage_cost:.2f}\n")
    text_field.insert(tk.END, f"Total Savings: £{total_savings:.2f}\n")
    text_field.config(state=tk.DISABLED)
    update_weather_readings(temperature, wind_speed, solar_radiation)
    update_battery_readings(battery_level, battery_health, battery_age,
                            charge_cycles, grid_usage_cost, total_savings)


# Function to update weather readings
def update_weather_readings(temperature, wind_speed, solar_radiation):
    temperature_label.config(text=f"Temperature: {temperature:.2f} C")
    wind_speed_label.config(text=f"Wind Speed: {wind_speed:.2f} m/s")
    solar_radiation_label.config(
        text=f"Solar Radiation: {solar_radiation:.2f} W/m^2")


# Function to update battery readings
def update_battery_readings(battery_level, battery_health, battery_age,
                            charge_cycles, grid_usage_cost, total_savings):
    battery_level_label.config(
        text=f"Battery Level: {battery_level:.2f} kWh")
    battery_health_label.config(
        text=f"Battery Health: {battery_health:.2f}%")
    battery_age_label.config(text=f"Battery Age: {battery_age:.2f} years")
    charge_cycles_label.config(text=f"Charge Cycles: {charge_cycles:.2f}")
    grid_usage_cost_label.config(
        text=f"Grid Usage Cost: £{grid_usage_cost:.2f}")
    total_savings_label.config(
        text=f"Total Savings: £{total_savings:.2f}")


# Set up the figure and axes
fig, ((ax1, ax2), (ax3, ax4), (ax5,
                              ax6)) = plt.subplots(3,
                                                 2,
                                                 figsize=(12, 10))

# Hide the unused subplot (ax6)
fig.delaxes(ax6)

# Animate the graph
ani = animation.FuncAnimation(fig, animate, interval=1000)

plt.tight_layout()


# Function to start the animation
def start_animation():
    global ani
    ani.event_source.start()
    play_sound()


# Function to stop the animation
def stop_animation():
    global ani
    ani.event_source.stop()
    play_sound()


# Functions to toggle renewable sources
def toggle_hydro():
    global hydro_active
    hydro_active = not hydro_active
    hydro_button.config(text=f"Hydro {'ON' if hydro_active else 'OFF'}",
                       bg="green" if hydro_active else "red")
    logging.debug(f"Hydro active state toggled: {hydro_active}")
    play_sound()


def toggle_solar():
    global solar_active
    solar_active = not solar_active
    solar_button.config(text=f"Solar {'ON' if solar_active else 'OFF'}",
                       bg="green" if solar_active else "red")
    logging.debug(f"Solar active state toggled: {solar_active}")
    play_sound()


def toggle_wind():
    global wind_active
    wind_active = not wind_active
    wind_button.config(text=f"Wind {'ON' if wind_active else 'OFF'}",
                       bg="green" if wind_active else "red")
    logging.debug(f"Wind active state toggled: {wind_active}")
    play_sound()


# Function to toggle battery
def toggle_battery():
    global battery_active
    battery_active = not battery_active
    battery_button.config(
        text=f"Battery {'ON' if battery_active else 'OFF'}",
        bg="green" if battery_active else "red")
    logging.debug(f"Battery active state toggled: {battery_active}")
    play_sound()


# Function to update hydro status
def update_hydro_status(status):
    global hydro_active
    hydro_active = status
    hydro_button.config(text=f"Hydro {'ON' if hydro_active else 'OFF'}",
                       bg="green" if hydro_active else "red")
    logging.debug(f"Hydro active state updated: {hydro_active}")


# Function to update solar status
def update_solar_status(status):
    global solar_active
    solar_active = status
    solar_button.config(text=f"Solar {'ON' if solar_active else 'OFF'}",
                       bg="green" if solar_active else "red")
    logging.debug(f"Solar active state updated: {solar_active}")


# Function to update wind status
def update_wind_status(status):
    global wind_active
    wind_active = status
    wind_button.config(text=f"Wind {'ON' if wind_active else 'OFF'}",
                       bg="green" if wind_active else "red")
    logging.debug(f"Wind active state updated: {wind_active}")


# Function to update battery status
def update_battery_status(status):
    global battery_active
    battery_active = status
    battery_button.config(
        text=f"Battery {'ON' if battery_active else 'OFF'}",
        bg="green" if battery_active else "red")
    logging.debug(f"Battery active state updated: {battery_active}")


# Function to play a sound
def play_sound():
    if platform.system() == "Windows":
        pass  # No sound on Windows
    else:
        # Use the 'afplay' command on macOS
        os.system('afplay /System/Library/Sounds/Glass.aiff')


# Create the main window
root = tk.Tk()
root.title("Power City Simulation")
root.geometry("1400x900")

# Create a canvas widget
main_canvas = tk.Canvas(root)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add scrollbars to the canvas
main_scrollbar_y = tk.Scrollbar(root,
                               orient=tk.VERTICAL,
                               command=main_canvas.yview)
main_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

main_scrollbar_x = tk.Scrollbar(root,
                               orient=tk.HORIZONTAL,
                               command=main_canvas.xview)
main_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

main_canvas.config(yscrollcommand=main_scrollbar_y.set,
                   xscrollcommand=main_scrollbar_x.set)

# Create a frame inside the canvas
main_frame = tk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=main_frame, anchor="nw")


# Function to update the scroll region
def on_configure(_):
    main_canvas.config(scrollregion=main_canvas.bbox("all"))


main_frame.bind("<Configure>", on_configure)

# Create a frame for the matplotlib figure
frame = tk.Frame(main_frame)
frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Create a frame for the buttons
button_frame = tk.Frame(main_frame)
button_frame.grid(row=1,
                  column=0,
                  columnspan=3,
                  padx=10,
                  pady=10,
                  sticky="ew")

# Add buttons to start and stop the animation
start_button = tk.Button(button_frame,
                         text="Start",
                         command=start_animation,
                         bg="lightgreen",
                         font=("Arial", 12, "bold"))
start_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

stop_button = tk.Button(button_frame,
                        text="Stop",
                        command=stop_animation,
                        bg="lightcoral",
                        font=("Arial", 12, "bold"))
stop_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

# Create a frame for the renewable source buttons
renewable_frame = tk.LabelFrame(main_frame,
                               text="Renewable Source Controls",
                               padx=10,
                               pady=10,
                               font=("Arial", 12, "bold"))
renewable_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

# Add buttons to activate/deactivate renewable sources
hydro_button = tk.Button(renewable_frame,
                         text="Hydro ON",
                         bg="green",
                         command=toggle_hydro,
                         font=("Arial", 10, "bold"))
hydro_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")


def update_capacity_display():
    hydro_capacity_label.config(text=f"{hydro_capacity} kW")
    solar_capacity_label.config(text=f"{solar_capacity} kW")
    wind_capacity_label.config(text=f"{wind_capacity} kW")
    battery_capacity_label.config(text=f"{battery_capacity} kWh")


solar_button = tk.Button(renewable_frame,
                         text="Solar ON",
                         bg="green",
                         command=toggle_solar,
                         font=("Arial", 10, "bold"))
solar_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

wind_button = tk.Button(renewable_frame,
                         text="Wind ON",
                         bg="green",
                         command=toggle_wind,
                         font=("Arial", 10, "bold"))
wind_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

# Add the battery button to the renewable_frame
battery_button = tk.Button(renewable_frame,
                           text="Battery ON",
                           bg="green",
                           command=toggle_battery,
                           font=("Arial", 10, "bold"))
battery_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

# Update the grid layout to accommodate the new button
renewable_frame.grid_rowconfigure(3, weight=1)

# Create a frame for the capacity input fields
capacity_frame = tk.LabelFrame(main_frame,
                               text="Update Capacities",
                               padx=10,
                               pady=10,
                               font=("Arial", 12, "bold"))
capacity_frame.grid(row=3,
                    column=0,
                    columnspan=2,
                    padx=10,
                    pady=10,
                    sticky="nsew")

# Add input fields for hydro, solar, wind, and battery capacities
tk.Label(capacity_frame,
         text="Hydro Capacity (kW):",
         font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
hydro_capacity_entry = tk.Entry(capacity_frame, font=("Arial", 10))
hydro_capacity_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
hydro_capacity_entry.insert(0, str(hydro_capacity))
hydro_capacity_label = tk.Label(capacity_frame,
                                 text=f"{hydro_capacity} kW",
                                 font=("Arial", 10))
hydro_capacity_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

tk.Label(capacity_frame,
         text="Solar Capacity (kW):",
         font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
solar_capacity_entry = tk.Entry(capacity_frame, font=("Arial", 10))
solar_capacity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
solar_capacity_entry.insert(0, str(solar_capacity))
solar_capacity_label = tk.Label(capacity_frame,
                                 text=f"{solar_capacity} kW",
                                 font=("Arial", 10))
solar_capacity_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")

tk.Label(capacity_frame,
         text="Wind Capacity (kW):",
         font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
wind_capacity_entry = tk.Entry(capacity_frame, font=("Arial", 10))
wind_capacity_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
wind_capacity_entry.insert(0, str(wind_capacity))
wind_capacity_label = tk.Label(capacity_frame,
                                 text=f"{wind_capacity} kW",
                                 font=("Arial", 10))
wind_capacity_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")

tk.Label(capacity_frame,
         text="Battery Capacity (kWh):",
         font=("Arial", 10)).grid(row=3, column=0, padx=5, pady=5, sticky="e")
battery_capacity_entry = tk.Entry(capacity_frame, font=("Arial", 10))
battery_capacity_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
battery_capacity_entry.insert(0, str(battery_capacity))
battery_capacity_label = tk.Label(capacity_frame,
                                 text=f"{battery_capacity} kWh",
                                 font=("Arial", 10))
battery_capacity_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")

# Add input field and label for grid cost
tk.Label(
    capacity_frame,
    text="Grid Cost (per kWh):",
    font=("Arial", 10)
).grid(row=4, column=0, padx=5, pady=5, sticky="e")

grid_cost_entry = tk.Entry(capacity_frame, font=("Arial", 10))
grid_cost_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
grid_cost_entry.insert(0, str(GRID_COST_PER_KWH))

grid_cost_label = tk.Label(
    capacity_frame,
    text=f"£{GRID_COST_PER_KWH:.2f} per kWh",
    font=("Arial", 10)
)
grid_cost_label.grid(row=4, column=2, padx=5, pady=5, sticky="w")


# Function to update capacities
def update_capacities():
    global hydro_capacity, solar_capacity, wind_capacity
    global battery_capacity, battery_level
    try:
        hydro_capacity = float(hydro_capacity_entry.get())
        solar_capacity = float(solar_capacity_entry.get())
        wind_capacity = float(wind_capacity_entry.get())
        battery_capacity = float(battery_capacity_entry.get())
        battery_level = min(
            battery_level, battery_capacity
        )  # Ensure battery level does not exceed new capacity
        update_capacity_display()
        messagebox.showinfo("Success", "Capacities updated successfully!")
        # Reflect updated capacities in simulations
        update_data()
        play_sound()
    except ValueError as e:
        logging.error(f"Error updating capacities: {e}")
        messagebox.showerror(
            "Error", "Please enter valid numeric values for capacities.")
        play_sound()


# Function to update grid cost
def update_grid_cost():
    global GRID_COST_PER_KWH
    try:
        GRID_COST_PER_KWH = float(grid_cost_entry.get())
        grid_cost_label.config(text=f"£{GRID_COST_PER_KWH:.2f} per kWh")
        messagebox.showinfo("Success", "Grid cost updated successfully!")
        play_sound()
    except ValueError as e:
        logging.error(f"Error updating grid cost: {e}")
        messagebox.showerror(
            "Error", "Please enter a valid numeric value for grid cost."
        )
        play_sound()


# Function to update grid cost display
def update_grid_cost_display():
    grid_cost_label.config(text=f"£{GRID_COST_PER_KWH:.2f} per kWh")


# Add a button to update capacities
update_button = tk.Button(capacity_frame,
                         text="Update Capacities",
                         command=update_capacities,
                         bg="lightblue",
                         font=("Arial", 12, "bold"))
update_button.grid(row=5,
                  column=0,columnspan=3,
                  padx=10,
                  pady=10,
                  sticky="ew")

# Initial capacity display update
update_capacity_display()

text_frame = tk.LabelFrame(main_frame,
                           text="Simulation Output",
                           padx=10,
                           pady=10,
                           font=("Arial", 12, "bold"))
text_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

# Add a text field to display updates with a scrollbar
text_scrollbar = tk.Scrollbar(text_frame)
text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_field = tk.Text(text_frame,
                    height=15,
                    width=40,
                    state=tk.DISABLED,
                    font=("Arial", 10),
                    yscrollcommand=text_scrollbar.set)
text_field.pack(fill=tk.BOTH, expand=True)

text_scrollbar.config(command=text_field.yview)

text_field.tag_configure("red", foreground="red")

text_field.tag_configure("green", foreground="green")

# Add labels for weather readings
weather_frame = tk.LabelFrame(main_frame,
                              text="Weather Readings",
                              padx=10,
                              pady=10,
                              font=("Arial", 12, "bold"))
weather_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

temperature_label = tk.Label(weather_frame,
                             text="Temperature: N/A",
                             font=("Arial", 10))
temperature_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

wind_speed_label = tk.Label(weather_frame,
                            text="Wind Speed: N/A",
                            font=("Arial", 10))
wind_speed_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

solar_radiation_label = tk.Label(weather_frame,
                                 text="Solar Radiation: N/A",
                                 font=("Arial", 10))
solar_radiation_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# Add a new frame for battery readings
battery_frame = tk.LabelFrame(main_frame,
                              text="Battery Readings",
                              padx=10,
                              pady=10,
                              font=("Arial", 12, "bold"))
battery_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

battery_level_label = tk.Label(battery_frame,
                                text="Battery Level: N/A",
                                font=("Arial", 10))
battery_level_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

battery_health_label = tk.Label(battery_frame,
                                text="Battery Health: N/A",
                                font=("Arial", 10))
battery_health_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

battery_age_label = tk.Label(battery_frame,
                             text="Battery Age: N/A",
                             font=("Arial", 10))
battery_age_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

charge_cycles_label = tk.Label(battery_frame,
                               text="Charge Cycles: N/A",
                               font=("Arial", 10))
charge_cycles_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Create a frame for grid costs breakdown
grid_costs_frame = tk.LabelFrame(main_frame,
                                 text="Grid Costs Breakdown",
                                 padx=10,
                                 pady=10,
                                 font=("Arial", 12, "bold"))
grid_costs_frame.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

# Add labels for grid costs breakdown
grid_usage_cost_label = tk.Label(grid_costs_frame,
                                 text="Grid Usage Cost: N/A",
                                 font=("Arial", 10))
grid_usage_cost_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

total_savings_label = tk.Label(grid_costs_frame,
                               text="Total Savings: N/A",
                               font=("Arial", 10))
total_savings_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Remove grid usage cost and total savings labels
# grid_usage_cost_label = tk.Label(battery_frame,
#                                  text="Grid Usage Cost: N/A",
#                                  font=("Arial", 10))
# grid_usage_cost_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# total_savings_label = tk.Label(battery_frame,
#                                text="Total Savings: N/A",
#                                font=("Arial", 10))
# total_savings_label.grid(row=1, column=2, padx=5, pady=5, sticky="ew")


# Function to generate report text
def generate_report(data, title):
    report_text = f"{title}\n\n"
    report_text += (
        f"Current Capacities:\n"
        f"Hydro Capacity: {hydro_capacity} kW\n"
        f"Solar Capacity: {solar_capacity} kW\n"
        f"Wind Capacity: {wind_capacity} kW\n"
        f"Battery Capacity: {battery_capacity} kWh\n\n")
    for entry in data:
        (time, energy_usage, hydro_power, solar_power, wind_power,
         battery_level, grid_usage, battery_health, grid_usage_cost,
         total_savings) = entry
        report_text += (f"Time: {time}\n"
                        f"Energy Usage: {energy_usage:.2f} kWh\n"
                        f"Hydro Power: {hydro_power:.2f} kW\n"
                        f"Solar Power: {solar_power:.2f} kW\n"
                        f"Wind Power: {wind_power:.2f} kW\n"
                        f"Battery Level: {battery_level:.2f} kWh\n"
                        f"Grid Usage: {grid_usage:.2f} kWh\n"
                        f"Battery Health: {battery_health:.2f}%\n"
                        f"Grid Usage Cost: £{grid_usage_cost:.2f}\n"
                        f"Total Savings: £{total_savings:.2f}\n\n")
    return report_text


# Function to update the report text field
def update_report_text(report_text):
    report_text_field.config(state=tk.NORMAL)
    report_text_field.delete(1.0, tk.END)
    report_text_field.insert(tk.END, report_text)
    report_text_field.config(state=tk.DISABLED)


# Function to plot daily data
def plot_daily_data():
    def generate():
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(days=1)
        daily_data = [entry for entry in energy_data
                      if entry[0] >= one_day_ago]

        if not daily_data:
            messagebox.showinfo(
                "Daily Report", "No data available for the last 24 hours.")
            return

        report_text = generate_report(daily_data, "Daily Report")
        update_report_text(report_text)

    threading.Thread(target=generate).start()


# Function to plot weekly data
def plot_weekly_data():
    def generate():
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)
        weekly_data = [entry for entry in energy_data
                       if entry[0] >= one_week_ago]

        if not weekly_data:
            messagebox.showinfo("Weekly Report",
                                "No data available for the last 7 days.")
            return

        report_text = generate_report(weekly_data, "Weekly Report")
        update_report_text(report_text)

    threading.Thread(target=generate).start()


# Function to plot monthly data
def plot_monthly_data():
    def generate():
        now = datetime.datetime.now()
        one_month_ago = now - datetime.timedelta(days=30)
        monthly_data = [entry for entry in energy_data
                        if entry[0] >= one_month_ago]

        if not monthly_data:
            messagebox.showinfo("Monthly Report",
                                "No data available for the last 30 days.")
            return

        report_text = generate_report(monthly_data, "Monthly Report")
        update_report_text(report_text)

    threading.Thread(target=generate).start()


# Function to plot yearly data
def plot_yearly_data():
    def generate():
        now = datetime.datetime.now()
        one_year_ago = now - datetime.timedelta(days=365)
        yearly_data = [entry for entry in energy_data
                       if entry[0] >= one_year_ago]

        if not yearly_data:
            messagebox.showinfo("Yearly Report",
                                "No data available for the last 365 days.")
            return

        report_text = generate_report(yearly_data, "Yearly Report")
        update_report_text(report_text)

    threading.Thread(target=generate).start()


# Add a new text box for the reports
report_frame = tk.LabelFrame(main_frame,
                             text="Reports",
                             padx=10,
                             pady=10,
                             font=("Arial", 12, "bold"))
report_frame.grid(row=5,
                  column=0,
                  columnspan=3,
                  padx=10,
                  pady=10,
                  sticky="nsew")

report_scrollbar = tk.Scrollbar(report_frame)
report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

report_text_field = tk.Text(report_frame,
                            height=15,
                            width=40,
                            state=tk.DISABLED,
                            font=("Arial", 10),
                            yscrollcommand=report_scrollbar.set)
report_text_field.pack(fill=tk.BOTH, expand=True)

report_scrollbar.config(command=report_text_field.yview)

# Make the window resizable
root.grid_rowconfigure(0, weight=3)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=2)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)


# Function to generate the daily report
def generate_daily_report():
    now = datetime.datetime.now()
    one_day_ago = now - datetime.timedelta(days=1)
    daily_data = [entry for entry in energy_data
                  if entry[0] >= one_day_ago]

    if not daily_data:
        messagebox.showinfo(
            "Daily Report", "No data available for the last 24 hours.")
        play_sound()
        return

    # Group data by hour
    hourly_data = {}
    for entry in daily_data:
        hour = entry[0].replace(minute=0, second=0, microsecond=0)
        if hour not in hourly_data:
            hourly_data[hour] = []
        hourly_data[hour].append(entry)

    report_text = "Daily Report\n\n"
    report_text += (
        f"Current Capacities:\n"
        f"Hydro Capacity: {hydro_capacity} kW\n"
        f"Solar Capacity: {solar_capacity} kW\n"
        f"Wind Capacity: {wind_capacity} kW\n"
        f"Battery Capacity: {battery_capacity} kWh\n\n"
    )

    total_cost_savings = 0.0
    for hour, entries in sorted(hourly_data.items()):
        avg_energy_usage = sum(entry[1] for entry in entries) / len(entries)
        avg_hydro_power = sum(entry[2] for entry in entries) / len(entries)
        avg_solar_power = sum(entry[3] for entry in entries) / len(entries)
        avg_wind_power = sum(entry[4] for entry in entries) / len(entries)
        avg_battery_level = sum(entry[5] for entry in entries) / len(entries)
        avg_grid_usage = sum(entry[6] for entry in entries) / len(entries)
        avg_battery_health = sum(entry[7] for entry in entries)
        avg_grid_usage_cost = sum(entry[8] for entry in entries)
        avg_total_savings = sum(entry[9] for entry in entries)
        total_cost_savings += avg_total_savings

        report_text += (
            f"Hour: {hour.strftime('%H:%M')}\n"
            f"Average Energy Usage: {avg_energy_usage:.2f} kWh\n"
            f"Average Hydro Power: {avg_hydro_power:.2f} kW\n"
            f"Average Solar Power: {avg_solar_power:.2f} kW\n"
            f"Average Wind Power: {avg_wind_power:.2f} kW\n"
            f"Average Battery Level: {avg_battery_level:.2f} kWh\n"
            f"Average Grid Usage: {avg_grid_usage:.2f} kWh\n"
            f"Average Battery Health: {avg_battery_health:.2f}%\n"
            f"Average Grid Usage Cost: £{avg_grid_usage_cost:.2f}\n"
            f"Average Total Savings: £{avg_total_savings:.2f}\n\n"
        )

    report_text += f"Total Cost Savings: £{total_cost_savings:.2f}\n"

    report_text_field.config(state=tk.NORMAL)
    report_text_field.delete(1.0, tk.END)
    report_text_field.insert(tk.END, report_text)
    report_text_field.config(state=tk.DISABLED)
    play_sound()


# Function to generate the weekly report
def generate_weekly_report():
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(days=7)
    weekly_data = [
        entry for entry in energy_data if entry[0] >= one_week_ago
    ]

    if not weekly_data:
        messagebox.showinfo(
            "Weekly Report", "No data available for the last 7 days."
        )
        play_sound()
        return

    # Group data by day
    daily_data = {}
    for entry in weekly_data:
        day = entry[0].date()
        if day not in daily_data:
            daily_data[day] = []
        daily_data[day].append(entry)

    report_text = "Weekly Report\n\n"
    report_text += (
        f"Current Capacities:\n"
        f"Hydro Capacity: {hydro_capacity} kW\n"
        f"Solar Capacity: {solar_capacity} kW\n"
        f"Wind Capacity: {wind_capacity} kW\n"
        f"Battery Capacity: {battery_capacity} kWh\n\n"
    )

    total_cost_savings = 0.0
    for day, entries in sorted(daily_data.items()):
        avg_energy_usage = sum(entry[1] for entry in entries) / len(entries)
        avg_hydro_power = sum(entry[2] for entry in entries) / len(entries)
        avg_solar_power = sum(entry[3] for entry in entries) / len(entries)
        avg_wind_power = sum(entry[4] for entry in entries) / len(entries)
        avg_battery_level = sum(entry[5] for entry in entries) / len(entries)
        avg_grid_usage = sum(entry[6] for entry in entries) / len(entries)
        avg_battery_health = sum(entry[7] for entry in entries)
        avg_grid_usage_cost = sum(entry[8] for entry in entries)
        avg_total_savings = sum(entry[9] for entry in entries)
        total_cost_savings += avg_total_savings

        report_text += (
            f"Day: {day.strftime('%d %B')}\n"
            f"Average Energy Usage: {avg_energy_usage:.2f} kWh\n"
            f"Average Hydro Power: {avg_hydro_power:.2f} kW\n"
            f"Average Solar Power: {avg_solar_power:.2f} kW\n"
            f"Average Wind Power: {avg_wind_power:.2f} kW\n"
            f"Average Battery Level: {avg_battery_level:.2f} kWh\n"
            f"Average Grid Usage: {avg_grid_usage:.2f} kWh\n"
            f"Average Battery Health: {avg_battery_health:.2f}%\n"
            f"Average Grid Usage Cost: £{avg_grid_usage_cost:.2f}\n"
            f"Average Total Savings: £{avg_total_savings:.2f}\n\n"
        )

    report_text += f"Total Cost Savings: £{total_cost_savings:.2f}\n"

    report_text_field.config(state=tk.NORMAL)
    report_text_field.delete(1.0, tk.END)
    report_text_field.insert(tk.END, report_text)
    report_text_field.config(state=tk.DISABLED)
    play_sound()


# Function to generate the monthly report
def generate_monthly_report():
    now = datetime.datetime.now()
    one_month_ago = now - datetime.timedelta(days=30)
    monthly_data = [
        entry for entry in energy_data if entry[0] >= one_month_ago
    ]

    if not monthly_data:
        messagebox.showinfo(
            "Monthly Report", "No data available for the last 30 days."
        )
        play_sound()
        return

    # Group data by day
    daily_data = {}
    for entry in monthly_data:
        day = entry[0].date()
        if day not in daily_data:
            daily_data[day] = []
        daily_data[day].append(entry)

    report_text = "Monthly Report\n\n"
    report_text += (
        f"Current Capacities:\n"
        f"Hydro Capacity: {hydro_capacity} kW\n"
        f"Solar Capacity: {solar_capacity} kW\n"
        f"Wind Capacity: {wind_capacity} kW\n"
        f"Battery Capacity: {battery_capacity} kWh\n\n"
    )

    total_cost_savings = 0.0
    for day, entries in sorted(daily_data.items()):
        avg_energy_usage = sum(entry[1] for entry in entries) / len(entries)
        avg_hydro_power = sum(entry[2] for entry in entries) / len(entries)
        avg_solar_power = sum(entry[3] for entry in entries) / len(entries)
        avg_wind_power = sum(entry[4] for entry in entries) / len(entries)
        avg_battery_level = sum(entry[5] for entry in entries) / len(entries)
        avg_grid_usage = sum(entry[6] for entry in entries) / len(entries)
        avg_battery_health = sum(entry[7] for entry in entries)
        avg_grid_usage_cost = sum(entry[8] for entry in entries)
        avg_total_savings = sum(entry[9] for entry in entries)
        total_cost_savings += avg_total_savings

        report_text += (
            f"Day: {day.strftime('%d %B')}\n"
            f"Average Energy Usage: {avg_energy_usage:.2f} kWh\n"
            f"Average Hydro Power: {avg_hydro_power:.2f} kW\n"
            f"Average Solar Power: {avg_solar_power:.2f} kW\n"
            f"Average Wind Power: {avg_wind_power:.2f} kW\n"
            f"Average Battery Level: {avg_battery_level:.2f} kWh\n"
            f"Average Grid Usage: {avg_grid_usage:.2f} kWh\n"
            f"Average Battery Health: {avg_battery_health:.2f}%\n"
            f"Average Grid Usage Cost: £{avg_grid_usage_cost:.2f}\n"
            f"Average Total Savings: £{avg_total_savings:.2f}\n\n"
        )

    report_text += f"Total Cost Savings: £{total_cost_savings:.2f}\n"

    report_text_field.config(state=tk.NORMAL)
    report_text_field.delete(1.0, tk.END)
    report_text
    report_text_field.insert(tk.END, report_text)
    report_text_field.config(state=tk.DISABLED)
    play_sound()


# Function to generate the yearly report
def generate_yearly_report():
    now = datetime.datetime.now()
    one_year_ago = now - datetime.timedelta(days=365)
    yearly_data = [
        entry for entry in energy_data if entry[0] >= one_year_ago
    ]

    if not yearly_data:
        messagebox.showinfo(
            "Yearly Report", "No data available for the last 365 days."
        )
        play_sound()
        return

    # Group data by month
    monthly_data = {}
    for entry in yearly_data:
        month = entry[0].replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        if month not in monthly_data:
            monthly_data[month] = []
        monthly_data[month].append(entry)

    report_text = "Yearly Report\n\n"
    report_text += (
        f"Current Capacities:\n"
        f"Hydro Capacity: {hydro_capacity} kW\n"
        f"Solar Capacity: {solar_capacity} kW\n"
        f"Wind Capacity: {wind_capacity} kW\n"
        f"Battery Capacity: {battery_capacity} kWh\n\n"
    )

    total_cost_savings = 0.0
    for month, entries in sorted(monthly_data.items()):
        avg_energy_usage = sum(entry[1] for entry in entries) / len(entries)
        avg_hydro_power = sum(entry[2] for entry in entries) / len(entries)
        avg_solar_power = sum(entry[3] for entry in entries) / len(entries)
        avg_wind_power = sum(entry[4] for entry in entries) / len(entries)
        avg_battery_level = sum(entry[5] for entry in entries) / len(entries)
        avg_grid_usage = sum(entry[6] for entry in entries) / len(entries)
        avg_battery_health = sum(entry[7] for entry in entries)
        avg_grid_usage_cost = sum(entry[8] for entry in entries)
        avg_total_savings = sum(entry[9] for entry in entries)
        total_cost_savings += avg_total_savings

        report_text += (
            f"Month: {month.strftime('%B %Y')}\n"
            f"Average Energy Usage: {avg_energy_usage:.2f} kWh\n"
            f"Average Hydro Power: {avg_hydro_power:.2f} kW\n"
            f"Average Solar Power: {avg_solar_power:.2f} kW\n"
            f"Average Wind Power: {avg_wind_power:.2f} kW\n"
            f"Average Battery Level: {avg_battery_level:.2f} kWh\n"
            f"Average Grid Usage: {avg_grid_usage:.2f} kWh\n"
            f"Average Battery Health: {avg_battery_health:.2f}%\n"
            f"Average Grid Usage Cost: £{avg_grid_usage_cost:.2f}\n"
            f"Average Total Savings: £{avg_total_savings:.2f}\n\n"
        )

    report_text += f"Total Cost Savings: £{total_cost_savings:.2f}\n"

    report_text_field.config(state=tk.NORMAL)
    report_text_field.delete(1.0, tk.END)
    report_text_field.insert(tk.END, report_text)
    report_text_field.config(state=tk.DISABLED)
    play_sound()


# Create a frame for the report buttons
report_button_frame = tk.Frame(main_frame)
report_button_frame.grid(
    row=6,
    column=0,
    columnspan=3,
    padx=10,
    pady=10,
    sticky="ew"
)

# Add a button to generate the daily report
daily_report_button = tk.Button(
    report_button_frame,
    text="Generate Daily Report",
    command=generate_daily_report,
    bg="lightblue",
    font=("Arial", 12, "bold")
)
daily_report_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

# Add a button to generate the weekly report
weekly_report_button = tk.Button(
    report_button_frame,
    text="Generate Weekly Report",
    command=generate_weekly_report,
    bg="lightblue",
    font=("Arial", 12, "bold")
)
weekly_report_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

# Add buttons to generate the monthly and yearly reports
monthly_report_button = tk.Button(
    report_button_frame,
    text="Generate Monthly Report",
    command=generate_monthly_report,
    bg="lightblue",
    font=("Arial", 12, "bold")
)
monthly_report_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

yearly_report_button = tk.Button(
    report_button_frame,
    text="Generate Yearly Report",
    command=generate_yearly_report,
    bg="lightblue",
    font=("Arial", 12, "bold")
)
yearly_report_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

if __name__ == '__main__':
    root.mainloop()
