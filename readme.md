# Ticket to Ride Engine with complex AI

## Overview

This project implements various artificial intelligence agents for playing the board game Ticket to Ride. It serves as a framework for comparing and evaluating different AI approaches. It can also be used by players who want to play against the strongest TTR AI available for entertainment or practice.

The code for this program is designed to be extendable and interpretable, if you would like to add a new map or agent to the game, it should be easy. If you need any help, feel free to message me.

## About Ticket to Ride

Ticket to Ride is a popular board game where players collect colored train cards to claim railway routes between cities across a map. Players earn points by completing routes, connecting destination cities from their ticket cards, and building the longest continuous train route. The game involves strategic decision-making, resource management, and competitive elements.

## Features

- Complete implementation of the Ticket to Ride game logic
- USA and European maps
- Multiple AI agent implementations with different strategies
- Customisable game setup with variable player count
- Performance evaluation and comparison between agents
- GUI For visualisation

## AI Agents Implemented

1. **MCTS (Monte Carlo Tree Search)** - Future planning AI which uses simulation-based search to find optimal moves
2. **Sequential Heuristic Agents** -  Simple agents which use a set of pre-determined heuristics to evaluate move suitability.

## Installation

### Prerequisites

- Python 3.10 or newer
- rich.live (Required)
- PyGame (Recommended for GUI)
- PyPy (Can be used for faster simulation time, doesn't use GUI or rich console)

### Setup

1.1. Clone the repository:
```git clone https://github.com/bingsoup/ticket-to-ride-ai cd ticket-to-ride-ai```

or 

1.2. Download the latest release and unzip it to your chosen folder.

2. Install dependencies:
Navigate your terminal to the folder within which the code has been stored, then.
- Install Rich ```pip install rich```

3. (Optional):
- Install PyGame for GUI elements ```pip install pygame``` **(Recommended)**
- Use PyPy for 2-3x increase in MCTS performance [PyPy Download Page](pypy.org/download.html)

## Running the Game

Run ```python game.py``` or ```pypy game.py``` in cmd or any terminal application.  

Follow the interactive prompts to:

1. Select the number of players (2-4)
2. Choose AI agent types or play yourself for each player
3. Watch the game play out or play against AI

## Project Structure

- `game.py` - Main game engine and state management
- `mcts.py` - Monte Carlo Tree Search implementation
- `heuristic_agents.py` - Various heuristic-based agents
- `map_data.py` - Ticket to Ride map and route data
- `helper_classes.py` - Supporting classes (Player, Route, Destination, etc.)
- `fw.py` - Floyd-Warshall algorithm for path finding

## Implementation Details

### Game State Representation

The game state includes:

- Player information (cards, claimed routes, destinations, points)
- Board state (available routes, face-up cards)
- Deck information (train cards, destination tickets)

### MCTS Agent

The Monte Carlo Tree Search agent:

- Uses simulation-based search to evaluate potential moves
- Balances exploration vs. exploitation
- Incorporates game-specific heuristics to guide search
- Parameters: simulation count and maximum search depth

### Heuristic Agents

Various specialized strategies:

- **Destination-focused**: Prioritises routes needed for destination tickets
- **Longest Route**: Builds continuous connections for the longest route bonus
- **Best Move**: Evaluates and selects locally optimal actions
