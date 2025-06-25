# SOLVING TRAVELING SALESMAN PROBLEM USING GENETIC ALGORITHM

## I. Introduction
The Traveling Salesman Problem (TSP) is a classic NP-hard combinatorial optimization problem. It requires finding the shortest possible route that visits a list of cities exactly once and returns to the origin city. TSP has numerous practical applications in logistics, route planning, network optimization, and manufacturing.

Our project implements a Genetic Algorithm (GA) to solve the TSP using real-world data from all 63 provinces and cities in Vietnam. We analyze how different GA operators and parameters affect convergence and solution quality. 

======
## II. Background and Motivation
**_Why Genetic Algorithm?_**

  GA is a metaheuristic inspired by the process of **natural selection**. It is highly effective for solving large, complex, and nonlinear search problems like TSP, where traditional methods may fail.

**_Practical Challenge_**

Most benchmark datasets (like TSPLIB) use Euclidean between cities. However, these distances do not account for real road networks, travel constraints, or traffic conditions, which creates a gap between theoretical models and practical use cases. Our project addresses this by using real-world coordinates and distances. 

======
## III. Objectives
* To model the TSP using realistic geographical data by applying city coordinates and Haversine distance calculations.
* To design and implement a Genetic Algorithm with key operators such as selection, crossover, and mutation.
* To analyze the effect of GA parameters (e.g, population size, mutation rate, generations) on convergence and solution quality.
* To compare multiple GA configurations (e.g, population size, mutation rate, generations) through systematic testing of over 60 operator combinations.
* To design an interactive GUI application to visualize routing solutions and demonstrate real-world applicability.

======
## IV. Key Contributions
* Designed a customizable GA engine with various selection, crossover, and mutation operators.
* Integrated real GPS coordinates (Vietnam) using the Haversine formula.
* Conducted in-depth experiments on datasets of different sizes (3-63 cities)
* Developed a PyQt5-based GUI that visualizes the route and allows users to configure GA settings.
* Compared traditional GA with Hybrid GA + Simulated Annealing (GASA) and Reinforcement Learning GA (RLGA)

====
## V. Literature review

The literature review covers foundational and advanced research related to the Traveling Salesman Problem (TSP) and the application of Genetic Algorithms (GA). It discusses key GA components including selection, crossover, and mutation strategies, and explores hybrid models such as Genetic Algorithm with Simulated Annealing (GASA) and Reinforcement Learning-based Genetic Algorithm (RLGA).

====
## VI. Methodology
**_Data collection_**

* **Real-world data**: GPS coordinates of 63 Vietnamese provinces and cities
* **Distance calculation**: Haversine formula (great-circle distance between 2 points on a sphere)

**_GA operators tested_**

* **Selection**: Tournament, Rank, Elitism, Roulette Wheel
* **Crossover**: Single-point, Two-point, Order, Uniform
* **Mutation**: Swap, Inversion, Scramble, Insertion

**_Parameters_**
* **Population size**: 100
* **Generations**: 200
* **Mutation rate**: 0.01
* Random seed fixed for reproducibility

====
## VII. Results summary
**_Parameter impact_**

* Larger population -> more stable convergence
* Mutation rate = 0.01 -> best convergence/ solution trade-off
* High mutation rate (0.1) -> unstable, noisy solutions
* More generations beyond 500 -> diminishing returns

**_Operators Performance_**
 * Best performing combination: _Rank Selection - Order Crossover - Swap Mutation_
 * Worst performing combination: _Roulette Wheel Selection - Uniform Crossover - Swap Mutation_

**_GA vs RLGA vs GASA_**

| **Algorithm** | **Best Fitness** | **Std.Dev.** | **FIR** | **Time(s)** |
|---|---|---|---|---|
| GA | 2392.1082 | 569.8687 | 29.6794 | 0.297 |
| RLGA | 2329.7092 | 551.3707 | 28.6336 | 0.162 |
| GASA | 2287.8776 | 251.7014 | 25.1403 | 2.916 |

====
## VIII. GUI Application

Developed with PyQt5 + folium, the GUI follows:
* Loading CSV files with coordinates
* Adjusting GA parameters (population, generations, mutation rate)
* Choosing the starting city and destination list
* Visualizing the optimized path on an interactive map
* Displaying route order and total distance

====
## IX. Limitations

*  Real distances estimated via Haversine, not real road networks (e.g., via Google Maps API)
*  No optimal ground-truth data for real-world instances
*  Performance drops for datasets > 50 cities without parallelization
*  GUI lacks batch mode, export features, and scalability for professional deployment

====
## X. Detailed Process

The workflow of this project is organized into multiple stages, with the following structure:

**1. Data Preparation**
* Location: ```data/```
* Contains both benchmark and real-world datasets (e.g, ```Viet Nam.csv```)
* Preprocessed using geographical coordinates of Vietnam's provinces

**2. Algorithm Implementation**
* Location: ```src/```
* Includes the core Genetic Algorithm logic, selection, crossover, and mutation methods
* Implements various configurations (e.g., population size, mutation rate)
* Key file: ```src/_ init.py _``` with main functions for GA execution

**3. Experiments & Evaluation**
*  Location: ```experiment/```
*  Contains scripts and results used to test different GA configurations
*  Tracks fitness value, FIR, AUC, and convergence behavior

**4. Visualization**
* File: ```best_route.html```
* Automatically generated HTML map displaying the optimized route using folium
* Open it in a browser to visualize the solution interactively

**5. GUI**
* File: ```vietnam_tsp_travel.py```
* Allows parameter tuning and map-based visualization with minimal code interaction

====
## Authors ##

1. Vuong Thuy Linh
   * Email: linhvuong.31221026306@st.ueh.edu.vn
   * Github: 
   
