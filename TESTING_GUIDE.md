# Testing Guide for main_controller.py

This guide explains how to test your `main_controller.py` file using different methods.

---

## Quick Start

### 1. Basic Import Test
Verify the controller can be imported and instantiated:

```bash
python -c "from main_controller import TeamFuzzyController; c = TeamFuzzyController(); print('✓ Controller works!')"
```

Or in Python:
```python
from main_controller import TeamFuzzyController
controller = TeamFuzzyController()
print("Controller initialized successfully!")
```

---

## Testing Methods

### Method 1: Single Game Test (With Graphics)
**File**: `scenario_test.py`

Run a single game with visual graphics to see your controller in action:

```bash
python scenario_test.py
```

**What it does**:
- Runs 1 game: `TeamFuzzyController` vs `TestController`
- Shows visual graphics (Tkinter window)
- Prints results: asteroids hit, deaths, accuracy
- Good for: Visual debugging and quick testing

**Output Example**:
```
Scenario eval time: 60.123
Stop Reason: time_limit
Asteroids hit: [15, 8]
Deaths: [0, 2]
Accuracy: [0.75, 0.40]
Mean eval time: [0.001, 0.0005]
```

---

### Method 2: 5-Game Test Suite (Required Format)
**File**: `test_suite.py`

Run the official 5-game test format as required by the assignment:

```bash
python test_suite.py
```

**What it does**:
- Runs 5 games: `TeamFuzzyController` vs `TestController`
- Uses competition format: unlimited bullets, 3 lives
- Aggregates scores across all 5 games
- Determines winner by total score (tie-breaker: accuracy)
- Good for: Verifying you can defeat `test_controller.py` (10% of grade)

**Output Example**:
```
--- Running 5 Games Test ---
Starting Game 1/5...
Game 1 finished. Team 1 Score: 12, Team 2 Score: 8
Starting Game 2/5...
...
======================================================================
5-GAME TEST RESULTS
======================================================================

Individual Game Results:
...
Aggregate Results (5 Games):
TeamFuzzyController:
  Total Score: 65
  Average Accuracy: 0.72
  Total Deaths: 1

TestController:
  Total Score: 42
  Average Accuracy: 0.38
  Total Deaths: 5

======================================================================
WINNER: TeamFuzzyController
Victory Margin: 23 asteroids
======================================================================
```

**To run headless (faster, no graphics)**:
Edit `test_suite.py` and change:
```python
test_against_test_controller(headless=True)  # Set to True for faster runs
```

---

### Method 3: Run Evolution (Optimize Controller)
**File**: `main_controller.py` (built-in)

Run the genetic algorithm to optimize your fuzzy controller parameters:

```bash
python main_controller.py
```

**What it does**:
- Prompts for confirmation
- Creates baseline controller and evaluates its fitness
- Runs genetic algorithm evolution (10 generations, 20 population)
- Saves best chromosome to `best_chromosome.pkl`
- Optionally tests the evolved controller

**Interactive Prompts**:
1. "Proceed with evolution? (yes/no):" - Type `yes` to start
2. "Seed initial population with baseline? (yes/no, default: yes):" - Type `yes` (recommended)
3. "Test best evolved controller against TestController? (yes/no):" - Type `yes` to verify

**Output Example**:
```
======================================================================
Starting Genetic Algorithm Evolution
======================================================================
Population size: 20
Generations: 10
Chromosome length: 76
======================================================================

Evaluating initial population...
  Individual 1/20: Fitness = 15.00
  Individual 2/20: Fitness = 8.00
  ...

Generation 1/10
======================================================================
Best fitness: 18.00
Average fitness: 12.50
Overall best: 18.00
...

Evolution Complete!
Best fitness: 45.00
Baseline fitness: 12.00
Improvement: +33.00

✓ Evolved controller outperforms baseline by 33.00 points!
```

**Note**: Evolution can take 30-60 minutes depending on your computer. The controller will automatically use optimized parameters on next run if `best_chromosome.pkl` exists.

---

### Method 4: Quick Fitness Check
Test a single controller's fitness without running full evolution:

```python
from main_controller import TeamFuzzyController, create_fitness_function, encode_controller_to_chromosome

# Create controller
controller = TeamFuzzyController(use_optimized=False)  # Use default parameters

# Encode to chromosome
chromosome = encode_controller_to_chromosome(controller)

# Create fitness function (runs 5 games by default)
fitness_func = create_fitness_function(num_games=5, headless=True)

# Evaluate fitness
fitness = fitness_func(chromosome)
print(f"Fitness: {fitness:.2f} (positive = wins, negative = loses)")
```

---

## Testing Checklist

### ✅ Basic Functionality
- [ ] Controller imports without errors
- [ ] Controller can be instantiated
- [ ] `actions()` method returns correct types: `(float, float, bool, bool)`

### ✅ Single Game Test
- [ ] Run `scenario_test.py` - controller plays the game
- [ ] No crashes or errors
- [ ] Controller moves, turns, and fires

### ✅ 5-Game Test (Required)
- [ ] Run `test_suite.py` - runs 5 games
- [ ] Controller wins (total score > TestController)
- [ ] Results printed correctly

### ✅ Genetic Algorithm
- [ ] Run `python main_controller.py` - evolution starts
- [ ] Evolution completes without errors
- [ ] `best_chromosome.pkl` is created
- [ ] Controller loads optimized parameters automatically

### ✅ Optimized Parameters
- [ ] Delete `best_chromosome.pkl` - controller uses defaults
- [ ] Restore `best_chromosome.pkl` - controller uses optimized
- [ ] Optimized controller performs better than default

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'kesslergame'"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "ImportError: cannot import name 'TestController'"
**Solution**: Make sure `test_controller.py` is in the same directory

### Issue: Evolution takes too long
**Solution**: Edit `GA_CONFIG` in `main_controller.py`:
```python
GA_CONFIG = {
    'population_size': 10,  # Reduce from 20
    'generations': 5,       # Reduce from 10
    'games_per_fitness': 1, # Reduce from 2
    ...
}
```

### Issue: Controller doesn't move/fire
**Solution**: 
- Check that fuzzy rules are set up correctly
- Verify `actions()` method is being called
- Check console for error messages

### Issue: Graphics window doesn't appear
**Solution**: 
- Make sure Tkinter is installed: `pip install tk`
- Try running headless: set `headless=True` in test scripts

---

## Performance Benchmarks

### Expected Performance (Default Controller)
- **vs TestController**: Should win consistently (score > opponent)
- **Asteroids hit**: 10-20 per game
- **Accuracy**: 0.60-0.80
- **Deaths**: 0-2 per game

### Expected Performance (Optimized Controller)
- **vs TestController**: Should win by larger margin
- **Asteroids hit**: 15-25 per game
- **Accuracy**: 0.70-0.85
- **Deaths**: 0-1 per game
- **Fitness improvement**: +20 to +50 points over baseline

---

## Quick Test Commands

```bash
# Test 1: Import check
python -c "from main_controller import TeamFuzzyController; print('OK')"

# Test 2: Single game (with graphics)
python scenario_test.py

# Test 3: 5-game test (headless, faster)
# Edit test_suite.py: test_against_test_controller(headless=True)
python test_suite.py

# Test 4: Run evolution
python main_controller.py

# Test 5: Verify optimized parameters loaded
python -c "from main_controller import TeamFuzzyController; c = TeamFuzzyController(); print('Using optimized:', hasattr(c, '_optimized'))"
```

---

## Next Steps

1. **Start with single game test**: `python scenario_test.py`
2. **Run 5-game test**: `python test_suite.py` to verify you can defeat TestController
3. **If needed, run evolution**: `python main_controller.py` to optimize parameters
4. **Re-test after evolution**: Run `test_suite.py` again to verify improvement

---

**Good luck with your testing!** 🚀

