Power City Simulation Documentation

Student ID: [Insert Your Student ID Here]

Project Overview

The Power City Simulation is an energy modeling tool designed to demonstrate renewable energy production, consumption, and battery storage in a smart grid environment. It features interactive controls, real-time data visualization, and detailed reporting. Built in Python, the application uses Tkinter for the graphical interface and Matplotlib for dynamic graphing.

This document provides comprehensive setup instructions, detailed descriptions of algorithms, and insights into the system's inputs, outputs, and calculations.

Setup Instructions

Prerequisites
Python Version: Ensure Python 3.8 or higher is installed.
Download Python
Required Libraries:
Tkinter (pre-installed with Python)
Matplotlib (install via pip)
Installation
Clone or download the project repository.
Navigate to the project directory in your terminal or command prompt.
Dependencies
Install the required library using pip:

pip install matplotlib
Running the Program
Run the main Python file:

python power_city_simulation.py
Files Included
Source Code: power_city_simulation.py
Documentation: README.md
Screenshots: Located in the screenshots/ directory.
Algorithm Design

The application employs modular algorithms for weather simulation, energy production, consumption, and battery management. These algorithms integrate environmental variables and energy equations to compute system dynamics.

Key Algorithms
1. Weather Simulation

Purpose: Generate realistic weather data, including temperature, wind speed, and solar radiation.
Inputs:
Month: Determines seasonal conditions (e.g., colder temperatures in winter).
Time of Day: Affects wind speed and solar radiation.
Outputs:
Temperature (°C): Seasonal and random variations.
Wind Speed (m/s): Higher during the day.
Solar Radiation (W/m²): Available only during daylight hours.
Calculations:
Temperature: Randomized values within seasonal ranges.
Wind Speed: Randomized daily variation.
Solar Radiation: Generated based on sunlight hours.
if month in [12, 1, 2]:  # Winter
    temperature = random.uniform(-5, 10)
if 6 <= hour <= 18:  # Daytime
    solar_radiation = random.uniform(0, 1000)
2. Energy Consumption

Purpose: Simulate household or industrial energy usage.
Inputs:
Temperature (°C): Affects heating or cooling demands.
Random Variation: Adds variability.
Outputs:
Energy Usage (kWh): Higher during extreme temperatures.
Calculations:
Base Usage: Constant daily consumption baseline.
Adjustment: Increases for temperatures below 0°C or above 30°C.
if temperature < 0 or temperature > 30:
    usage_variation += 200
energy_usage = base_usage + usage_variation
3. Renewable Energy Production

Each energy source is modeled using specific algorithms:

Hydroelectric Power:
Inputs:
Water flow rate (randomized).
Efficiency (fixed at 90%).
Outputs: Power generated in kW.
Calculations:
hydro_power = min(water_flow * efficiency * 9.81 * hydro_capacity, hydro_capacity)
Solar Power:
Inputs:
Solar radiation (W/m²).
Panel efficiency (20%).
Outputs: Power generated in kW.
Calculations:
solar_power = (solar_radiation * efficiency * solar_capacity) / 1000
Wind Power:
Inputs:
Wind speed (m/s).
Turbine efficiency (40%).
Outputs: Power generated in kW.
Calculations:
wind_power = (wind_speed**3 * efficiency * wind_capacity) / 1000
4. Battery Management

Purpose: Manage surplus and deficit energy.
Inputs:
Net Energy (kWh): Generation minus usage.
Battery Level (kWh).
Battery Health (%): Determines charge efficiency.
Outputs:
Updated Battery Level.
Grid Usage: Used when battery is empty.
Calculations:
Charge or discharge the battery based on net energy.
If battery is empty, compute grid energy requirements.
if net_energy > 0 and battery_level < battery_capacity:
    battery_level = min(battery_capacity, battery_level + net_energy * (battery_health / 100))
elif net_energy < 0:
    grid_usage = abs(net_energy) if battery_level == 0 else 0
Algorithm Workflow
Weather Simulation: Generate environmental conditions.
Energy Usage Calculation: Compute consumption based on conditions.
Energy Production: Generate power from renewable sources.
Energy Balancing:
If production exceeds usage, charge the battery.
If consumption exceeds production, discharge the battery or use the grid.
Dynamic Interactions
User Inputs:
Enable/disable renewable sources (buttons).
Adjust energy source capacities (GUI).
System Outputs:
Real-time graphs for energy generation and battery level.
Reports summarizing energy usage, savings, and costs.
Inputs, Outputs, and Calculations Summary

Component	Inputs	Outputs	Key Calculations
Weather Simulation	Month, time of day	Temperature, wind speed, solar radiation	Seasonal temperature ranges, random variations
Energy Consumption	Temperature	Energy usage (kWh)	Base usage + seasonal adjustment
Hydroelectric Power	Water flow, efficiency	Power (kW)	Flow * efficiency * capacity
Solar Power	Solar radiation, efficiency	Power (kW)	Radiation * efficiency / 1000
Wind Power	Wind speed, efficiency	Power (kW)	Speed³ * efficiency / 1000
Battery Management	Net energy, battery level	Battery level, grid usage (kWh)	Charge/discharge battery, calculate grid usage
Real-Time Visualizations

Graphs: Dynamic graphs display hydro, solar, and wind power alongside energy usage and battery status.
Reports:
Daily, weekly, monthly, and yearly summaries.
Breakdown of energy production, grid costs, and total savings.
Debugging and IDE Usage

Breakpoints: Debug variable values in algorithms (e.g., battery health).
Logs: Inspect runtime errors and ensure robust behavior.
Real-Time Testing: Validate outputs by visualizing dynamic graphs during simulation.
