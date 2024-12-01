# Power City Simulation

This project simulates a power city with renewable energy sources, battery storage, and grid connection. It demonstrates the process of building an application, from algorithm design to code implementation and debugging, while exploring different programming paradigms.

## Learning Outcomes Covered

* **LO1:** Define basic algorithms and outline the programming process.
* **LO2:** Explain procedural, object-oriented, and event-driven programming.
* **LO3:** Implement algorithms in code using an IDE.
* **LO4:** Determine the debugging process and explain coding standards.

## Assessment Criteria Covered

* **P1:** Define an algorithm and outline the application building process.
* **P2:** Determine steps from writing code to execution.
* **P3:** Discuss procedural, object-oriented, and event-driven paradigms.
* **P4:** Write a program implementing an algorithm using an IDE.
* **P5:** Explain the debugging process and IDE debugging facilities.
* **P6:** Explain the coding standard used in the code.
* **M1:** Analyze the code writing process and potential challenges.
* **M2:** Compare paradigms in the source code.
* **M3:** Enhance the algorithm using IDE features.
* **M4:** Examine debugging for secure and robust applications.
* **D1:** Evaluate algorithm implementation and the algorithm-code relationship.
* **D2:** Critically evaluate source code implementing different paradigms.
* **D3:** Evaluate IDE use for application development.
* **D4:** Evaluate the role and purpose of a coding standard.

## Project Description

This Python program simulates a power city with:

* **Renewable energy sources:** Hydro, solar, and wind power.
* **Battery storage:**  Charges when there's excess energy and discharges when needed.
* **Grid connection:**  Used when renewable sources and battery cannot meet demand.

The simulation generates data for weather, energy generation, consumption, and battery usage. It includes a GUI built with Tkinter for visualization and interaction.

## Algorithm (P1)

The core algorithm simulates the energy flow in the city:

1. **Simulate weather:** Generate temperature, wind speed, and solar radiation.
2. **Simulate energy usage:** Calculate energy demand based on weather.
3. **Simulate energy generation:**  Calculate power output from each renewable source.
4. **Manage battery:** Charge or discharge the battery based on net energy (generation - usage).
5. **Calculate grid usage:** Determine if grid power is needed.
6. **Update data:** Store the simulation data for analysis and visualization.

## Programming Process (P1, P2, M1)

1. **Design:** Define the algorithm and plan the GUI layout.
2. **Code:** Implement the algorithm and GUI using Python and Tkinter.
3. **Test:** Run the simulation and check for errors.
4. **Debug:** Use the IDE's debugging tools to identify and fix issues.
5. **Refine:** Improve the code based on testing and feedback.

**Challenges (M1):**

* **Realism:**  Balancing simulation accuracy with computational efficiency.
* **GUI design:** Creating a user-friendly and informative interface.
* **Data handling:** Efficiently managing and visualizing large datasets.

## Programming Paradigms (P3, M2)

The code utilizes aspects of:

* **Procedural programming:** Functions like `simulate_weather`, `simulate_energy_usage` demonstrate a procedural approach.
* **Event-driven programming:** The GUI uses event handlers for button clicks and other user interactions.
* **Object-oriented programming:**  Potential for refactoring into classes for better organization (e.g., `PowerSource`, `Battery`, `GUI`).

## IDE and Debugging (P4, P5, M3, D3)

An IDE (e.g., VS Code, PyCharm) is crucial for efficient development:

* **Code editor:** Syntax highlighting, autocompletion.
* **Debugger:**  Setting breakpoints, stepping through code, inspecting variables.
* **Version control integration:**  Managing code changes (e.g., using Git).

**Debugging Process (P5):**

1. Identify errors (runtime errors, logical errors).
2. Use the debugger to locate the source of the error.
3. Analyze the code and fix the issue.
4. Test the code to ensure the error is resolved.

**Debugging for Security (M4):**

* Input validation to prevent malicious or invalid data.
* Error handling to gracefully handle unexpected situations.

## Coding Standard (P6, D4)

A consistent coding standard (e.g., PEP 8) is essential for:

* **Readability:** Makes the code easier to understand and maintain.
* **Collaboration:**  Ensures code consistency across a team.
* **Error reduction:**  Helps prevent common coding mistakes.

## Evaluation (D1, D2)

* **Algorithm implementation:** The code effectively translates the algorithm into a working simulation.
* **Paradigm implementation:**  While the current code is mainly procedural, it demonstrates event-driven elements in the GUI. Further refactoring could enhance object-oriented principles.
* **IDE benefits:**  An IDE significantly improves development efficiency through debugging tools, code analysis, and version control.

## Conclusion

This project provides a practical example of building an application, covering algorithm design, code implementation, debugging, and the use of an IDE. It also touches upon different programming paradigms and the importance of coding standards.
