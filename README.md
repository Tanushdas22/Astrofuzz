# 🚀 AstroFuzz
**Genetic-Algorithm-Optimized Fuzzy Controller for Autonomous Agents**

## Overview
AstroFuzz is an autonomous game agent powered by a fuzzy logic controller whose parameters are optimized using a genetic algorithm. The agent operates in a real-time simulation environment, making adaptive decisions for navigation, targeting, and mine deployment based on dynamic game-state inputs.

## Key Features
- Declarative fuzzy logic controller for real-time decision-making
- Genetic algorithm optimization of membership function parameters
- Simulation-based fitness evaluation
- Modular agent architecture enabling extensibility and experimentation

## System Architecture
- **Inputs:** Distance to asteroids, relative velocity, heading angle, threat level
- **Controller:** Rule-based fuzzy inference system
- **Optimizer:** Genetic algorithm (selection, crossover, mutation, elitism)
- **Outputs:** Thrust, rotation, firing, and mine deployment actions

## Technologies Used
- Python
- scikit-fuzzy
- Genetic Algorithms
- Fuzzy Control Systems
- Autonomous Agent Design
- Simulation-Based Optimization

## Results
The GA-optimized fuzzy controller demonstrated improved survivability and task performance compared to a baseline hand-tuned fuzzy controller.

## Future Work
- Multi-objective fitness optimization
- Adaptive rule learning
- Hybrid neuro-fuzzy extensions

Reference:
- Thales Group's Kessler Game: https://github.com/ThalesGroup/kessler-game
