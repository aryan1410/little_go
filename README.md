# Little-Go AI Agents

This project implements intelligent agents to play a simplified version of the Go board game — "Little-Go" — on a 5x5 board. Designed as an AI project, it explores and integrates several core AI techniques including minimax with alpha-beta pruning, greedy heuristics, and reinforcement learning.

## 🧠 Project Overview

In this project, agents compete in the game of Little-Go using various AI strategies. The game is governed by standard rules including liberty, KO, and Komi (2.5 points for White). The goal is to build competitive agents capable of playing against predefined opponents and outperforming them through learned or hardcoded intelligence.

## ♟️ Game Rules Summary

* **Board Size:** 5x5
* **Players:** Black (goes first) and White
* **Objective:** Occupy more territory by the end of the game
* **Liberty Rule:** A stone must have at least one liberty or capture an opponent to survive
* **KO Rule:** Prevents immediate board state repetition
* **Komi:** White gets +2.5 score compensation
* **Game End:** After 24 moves or two consecutive passes

## 🤖 Implemented AI Agents

* `random_player.py`: Chooses moves randomly
* `greedy_player.py`: Selects the move that captures the most opponent stones immediately
* `aggressive_player.py`: Looks ahead two moves to maximize total captures
* `alpha_beta_player.py`: Minimax search with alpha-beta pruning (depth=2)
* `r_learner.py`: Reinforcement learning agent with Q-table updates and epsilon-greedy policy
* `minimax.py`: Custom agent using weighted evaluation metrics and enhanced minimax with pruning

## 📁 File Structure

* `host.py`: Game engine coordinating turns and validating moves
* `read.py` / `write.py`: I/O utilities for agent interaction
* `train.sh`, `train_white.sh`, `train_black.sh`: Scripts to train agents via self-play or evaluation
* `play.sh`: Script for agent-vs-agent testing
* `epsilon.txt`: Stores R-learner’s exploration rate
* `q_table_black.json` / `q_table_white.json`: Persistent Q-value storage (generated during training)

## 🚀 How to Run

To simulate or train matches between agents

```bash
# To test your agent against the random player
bash play.sh

# To train your agent as Black
bash train_black.sh

# To train your agent as White
bash train_white.sh

# To train both
bash train.sh
```

Ensure your player file is named `my_player3.py` or similar according to the expected script format.

## 🛠️ AI Techniques Used

* **Minimax Search with Alpha-Beta Pruning:** Reduces computation by pruning suboptimal branches
* **Greedy Heuristics:** Fast evaluations for capturing maximum stones
* **Reinforcement Learning:** Trains agents via exploration and exploitation, using cumulative rewards for actions
* **Custom Reward Function:** Evaluates Go states using liberty, territory, Ko threats, and positional control

## Best Player
The best player among these turned out to be the minimax player, taking move time, decision making and win rate into consideration.  
Win rate as Black: 90%  
Win rate as White: 100% 

## 🧪 Training Tips for Q-Learning Player
Long-term training of the Q-learning agent, with initial and majority exploration, results in significantly improved performance due to experience accumulation.

