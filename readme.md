# Ticket to Ride AI - Dissertation Project

## Overview

This project implements and evaluates various artificial intelligence agents for playing the board game Ticket to Ride. It serves as a framework for comparing different AI approaches in a complex, partially observable game environment with both competitive and strategic elements.

## About Ticket to Ride

Ticket to Ride is a popular board game where players collect colored train cards to claim railway routes between cities across a map. Players earn points by completing routes, connecting destination cities from their ticket cards, and building the longest continuous train route. The game involves strategic decision-making, resource management, and competitive elements.

## Features

- Complete implementation of the Ticket to Ride game logic
- Multiple AI agent implementations with different strategies
- Customizable game setup with variable player count
- Performance evaluation and comparison between agents

## AI Agents Implemented

1. **MCTS (Monte Carlo Tree Search)** - Uses simulation-based search to find optimal moves
2. **Destination Heuristic** - Prioritizes routes that help complete destination tickets
3. **Longest Route Heuristic** - Focuses on building the longest continuous route
4. **Opportunistic Heuristic** - Makes moves that yield immediate point gains
5. **Best Move Heuristic** - Selects optimal moves based on current game state
6. **Random AI** - Makes random legal moves (baseline for comparison)
7. **Neural Network Agent** - Uses a trained neural network to evaluate game states and select actions

## Installation

### Prerequisites

- Python 3.10 or newer
- NumPy
- pypy (Recommended for faster execution but not required)

### Setup

1. Clone the repository:
```git clone [repository-url] cd ticket-to-ride-ai```

2. Install dependencies:
```Not finalised```

## Running the Game

Run ```python game.py``` or ```pypy game.py``` in cmd or any terminal application.  

Follow the interactive prompts to:

1. Select the number of players (2-4)
2. Choose AI agent types for each player
3. Watch the game play out automatically

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

- **Destination-focused**: Prioritizes routes needed for destination tickets
- **Longest Route**: Builds continuous connections for the longest route bonus
- **Opportunistic**: Takes immediate high-value moves
- **Best Move**: Evaluates and selects locally optimal actions

## Evaluation & Results

(TODO)
The framework allows for comparison between different agent strategies by:

- Win rates in head-to-head play
- Average score achieved
- Ability to complete destination tickets
- Efficiency in claiming key routes

## Future Work

- Implementing a GUI
- Neural Network agent
- Neural Network selection for MCTS

## Acknowledgments

This project was developed as part of a dissertation in artificial intelligence and game theory. It builds on research in the fields of:

- AI for board games
- Decision making under uncertainty
- Monte-Carlo tree search optimisation techniques

## License

[Specify license or note that it's for academic purposes]
