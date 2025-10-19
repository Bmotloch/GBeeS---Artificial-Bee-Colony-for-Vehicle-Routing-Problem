# GBeeS: Vehicle Routing Problem Solver using the Artificial Bee Colony Algorithm
## Overview

GBeeS is a Python desktop application that solves the Vehicle Routing Problem (VRP) using the Artificial Bee Colony (ABC) algorithm.
The project features a PyQt5 GUI and matplotlib-based visualization for real-time route optimization.

## Features

Swarm Intelligence: Custom ABC implementation with scout, forager, and abandonment mechanisms

Multi-Vehicle Routing: Optimized route allocation across multiple vehicles

Interactive GUI: Parameter tuning and visualization with PyQt5

Real-Time Visualization: Live plotting of routes and optimization progress

Performance Testing: Built-in statistical testing and analysis

File Management: Save/load test cases and results in custom formats

## Technical Stack

Language: Python 3.11

GUI: PyQt5

Visualization: Matplotlib

Algorithm: Artificial Bee Colony Optimization

Domain: Vehicle Routing Problem (VRP)

## Algorithm Highlights

Scout Bees: Explore new random solutions

Forager Bees: Exploit promising routes with local search

Abandonment: Prevents stagnation in local optima

Neighborhood Operators:

Node swapping

Random relocation

Path segment reversal

## Skills Demonstrated

OOP Design: Modular class-based architecture

Multithreading: QThread for responsive UI during computation

Algorithm Development: Custom bio-inspired optimization design

Visualization: Real-time plotting and performance analysis

## Significance

The Vehicle Routing Problem is a classic NP-hard challenge central to logistics, transportation, and resource management.
Swarm intelligence can produce efficient (and good enough in a relatively short amount of time) solutions where traditional optimization methods struggle.
