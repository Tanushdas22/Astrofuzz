# ECE 449 Group Project Assignment - Specifications

## Course Information
- **Course**: Intelligent Systems Engineering (ECE 449)
- **Term**: Fall 2025
- **Due Date**: Monday Dec. 8, 2025, 11:59:59pm

## Project Overview
Build a fuzzy control agent to play the Kessler implementation of the Asteroids arcade game, version 2.4.0, written by Thales North America as a part of the Explainable Fuzzy Challenge (XFC) competition at the NAFIPS annual conference.

## Team Requirements
- **Team Size**: Teams of three

## Core Requirements

### Minimum Requirements
1. **Fuzzy Controller Implementation**
   - Agent must use a **declarative fuzzy controller** to determine control outputs
   - Must control at minimum the following four outputs:
     - `thrust` (floating point value in m/sec²)
     - `turn_rate` (floating point value in degrees per sec)
     - `fire` (Boolean)
     - `drop_mine` (Boolean)

2. **Complete Control Coverage**
   - Agent must control **all four aspects** of ship actions
   - Must have rules that fire and yield non-zero actions for:
     - `thrust`
     - `turn_rate`
     - `fire`
     - `drop_mine`
   - Note: Not necessarily all four at every moment, but all must be controllable

3. **Game Compatibility**
   - Agent must be able to play the game
   - Must implement the `actions()` method that:
     - Accepts current game state and state of player's ship
     - Returns the four control values (thrust, turn_rate, fire, drop_mine)

### Full Credit Requirements
4. **Genetic Algorithm Optimization**
   - Fuzzy system must be optimized by a **genetic algorithm**
   - Must use a **genetic fuzzy tree** for optimization

5. **Performance Requirement**
   - Agent must be able to **defeat the trivial agent** `test_controller.py` from the Kessler GitHub examples directory
   - Testing format:
     - 5 game runs
     - Unlimited bullets
     - Three lives
     - Winner determined by total score across the five runs
     - Ties broken by average accuracy

## Testing Requirements
- Agent will be tested on the teaching team's own copy of the Kessler game
- Testing will use **different scenarios** than what is provided in the examples directory
- Testing format matches competition format:
  - 5 game runs
  - Unlimited bullets
  - Three lives
  - Winners judged by total score across the five runs
  - Ties broken by average accuracy

## Submission Requirements

### Main Submission
- **Deadline**: Monday Dec. 8, 2025, 11:59:59pm
- **Format**: Python file (.py)
- **Restriction**: NOT a Jupyter notebook
- **Location**: Submit via Canvas lecture page

### Competition Submission (Optional)
- **Deadline**: Friday Nov. 28, 2025, 11:59:59pm
- **Location**: Separate "competition" submission link on Canvas
- **Note**: Competition version may differ from final submission
- **Restriction**: No updates to competition agents after Nov. 28 deadline

## Competition Details (Optional)

### Participation
- Competition is **optional**
- Teams that wish to join must submit competition agent by Nov. 28 deadline

### Competition Format
1. **Round-Robin Stage** (Off-line)
   - Random division into pools
   - Head-to-head round-robin tournament between pairs of agents
   - Format: 5 games per matchup
   - Rules: Unlimited bullets, three lives
   - Winner: Agent with highest total score across all five games
   - Tie-breaker: Average accuracy across all five games
   - Result: Produces seedings for Round of 16

2. **Single-Elimination Round** (Live)
   - **Date**: Friday Dec. 5, 5-9pm
   - **Format**: Round of 16 single-elimination tournament
   - **Location**: Room TBD
   - **Streaming**: Livestreamed to the room
   - **Refreshments**: Pizza and sodas provided
   - **Format**: Same as round-robin (5 games, unlimited bullets, three lives)
   - **Winner determination**: Same as round-robin

### Competition Prizes (Extra Credit)
- **1st place**: 3 points on final grade
- **2nd place**: 2 points on final grade
- **3rd place**: 1 point on final grade

## Grading Breakdown
- **Agent uses a fuzzy controller and can play the game**: 75%
- **Agent optimizes a genetic fuzzy tree**: 15%
- **Agent defeats the agent from test_controller.py**: 10%

## Technical Details

### Game Version
- **Kessler Game Version**: 2.4.0

### Required Files
- `test_controller.py` - Simple example controller (target to defeat)
- `scenario_test.py` - Required to run the program
- `graphics_both.py` - Required to run the program

### Implementation Notes
- The `actions()` method is called at every time step of the game
- Simple controller (`test_controller.py`) behavior:
  - Thrust: 0 (ship does not move)
  - Turn rate: 90 degrees per second
  - Fire: Always True
  - Drop mine: Always False
- Dr. Dick's example agent (reference only):
  - Uses fuzzy logic for turn_rate and fire
  - Targets closest asteroid
  - Does NOT move ship (thrust always zero) - **not acceptable for submission**
  - Does NOT drop mines - **not acceptable for submission**

## Additional Resources
- Kessler Game Github: https://github.com/ThalesGroup/kessler-game/tree/main
- XFC Youtube Channel: https://www.youtube.com/@fuzzycompetition8326
- Calculating intercepts in 2D space: https://www.codeproject.com/Articles/990452/Interception-of-Two-Moving-Objects-in-D-Space
- Another Kessler Game Example: https://github.com/xfuzzycomp/KesslerGameExample
- Kessler Game Development Manual by Dr. Dick (on Canvas)
- Dr. Dick's Kessler Game Agent (on Canvas)

## Installation Requirements
- Install Kessler Game from PyPi
- Download current Kessler Game wheel file (pre-built executable)
- Install using `pip install` as per instructions on the site
- More details available in Kessler development manual by Dr. Dick

---

## Requirements Coverage Status

**See `REQUIREMENTS_COVERAGE.md` for detailed analysis.**

### ✅ Covered Requirements
- ✅ Fuzzy Controller Implementation (declarative fuzzy controller)
- ✅ All Four Control Outputs (thrust, turn_rate, fire, drop_mine)
- ✅ Complete Control Coverage (rules for all four outputs)
- ✅ Game Compatibility (actions() method implemented)
- ✅ Required Files (test_controller.py, scenario_test.py, graphics_both.py)
- ✅ Kessler Game Installation (version 2.4.0)

### ❌ Missing Requirements (Critical for Full Credit)
- ❌ **Genetic Algorithm Optimization** (15% of grade) - NOT IMPLEMENTED
- ❌ **Genetic Fuzzy Tree** (part of 15%) - NOT IMPLEMENTED
- ❌ **5-Game Test Suite** - NOT IMPLEMENTED (only 1-game test exists)
- ❌ **Verification Against test_controller.py** (10% of grade) - NOT VERIFIED
- ⚠️ **Drop Mine Functionality** - Rules exist but currently disabled in code

### Current Grade Estimate
- **75%** - Fuzzy controller implemented and functional
- **Missing 25%** - Genetic optimization (15%) + Defeat test_controller.py (10%)

**Estimated Current Grade: 75% / 100%**

