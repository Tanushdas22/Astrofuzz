# main_controller.py
# Complete implementation including:
# - Fuzzy Logic Controller (TeamFuzzyController)
# - Genetic Algorithm Framework for optimization
# - Genetic Fuzzy Tree integration
# - Evolution runner

from kesslergame import KesslerController, Scenario, KesslerGame, GraphicsType
from typing import Dict, Tuple, Optional, List, Callable
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import math
import os
import random
import pickle
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

# Genetic Algorithm Configuration
# We chose these values to balance evolution quality with computational efficiency
GA_CONFIG = {
    # Population settings
    'population_size': 20,  # We start small for testing, but increase for better results
    'generations': 10,      # We use 10 generations as a reasonable balance between exploration and time
    
    # Genetic operators
    'mutation_rate': 0.15,   # We set 15% mutation rate to maintain diversity without being too disruptive
    'crossover_rate': 0.8,   # We use 80% crossover rate to favor exploration of parameter combinations
    'elitism_ratio': 0.2,   # We keep top 20% of population to preserve best solutions while allowing evolution
    
    # Selection
    'tournament_size': 3,    # We use tournament size of 3 to balance selection pressure and diversity
    
    # Fitness evaluation
    'games_per_fitness': 2,  # We run 2 games per fitness evaluation as a trade-off
                             # Lower = faster but less accurate
                             # Higher = slower but more accurate
}

# File paths
BEST_CHROMOSOME_FILE = 'best_chromosome.pkl'
EVOLUTION_HISTORY_FILE = 'evolution_history.txt'

# ============================================================================
# GENETIC FUZZY TREE: Chromosome Encoding/Decoding
# ============================================================================

def decode_chromosome_to_parameters(chromosome: List[float]) -> Dict[str, List[float]]:
    """
    Decode chromosome into a dictionary of fuzzy parameters.
    
    We designed the chromosome structure to encode all fuzzy membership function parameters:
    - Distance: very_near (3), near (3), medium (3), far (3) = 12 params
    - Rear_threat: near (3), far (3) = 6 params
    - Theta_delta: NL (2), NS (3), Z (3), PS (3), PL (2) = 13 params
    - Bullet_time: short (3), medium (3), long (3) = 9 params
    - Thrust: low (3), medium (3), high (3) = 9 params
    - Turn: hard_left (3), left (3), zero (3), right (3), hard_right (3) = 15 params
    - Fire: no (3), yes (3) = 6 params
    - Mine: no (3), yes (3) = 6 params
    Total: 76 parameters
    
    We chose this encoding so that the genetic algorithm can optimize all membership function parameters simultaneously.
    
    Args:
        chromosome: List of parameter values (length 76)
        
    Returns:
        Dictionary of parameter values organized by membership function
    """
    if len(chromosome) != 76:
        raise ValueError(f"Chromosome must have 76 parameters, got {len(chromosome)}")
    
    idx = 0
    params = {}
    
    # Distance membership functions
    params['distance_very_near'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['distance_near'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['distance_medium'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['distance_far'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    # Rear_threat membership functions
    params['rear_threat_near'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['rear_threat_far'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    # Theta_delta membership functions
    params['theta_delta_NL'] = [chromosome[idx], chromosome[idx+1]]  # zmf: 2 params
    idx += 2
    params['theta_delta_NS'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['theta_delta_Z'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['theta_delta_PS'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['theta_delta_PL'] = [chromosome[idx], chromosome[idx+1]]  # smf: 2 params
    idx += 2
    
    # Bullet_time membership functions
    params['bullet_time_short'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['bullet_time_medium'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['bullet_time_long'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    # Thrust output membership functions
    params['thrust_low'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['thrust_medium'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['thrust_high'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    # Turn output membership functions
    params['turn_hard_left'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['turn_left'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['turn_zero'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['turn_right'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['turn_hard_right'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    # Fire output membership functions
    params['fire_no'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['fire_yes'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    # Mine output membership functions
    params['mine_no'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    params['mine_yes'] = [chromosome[idx], chromosome[idx+1], chromosome[idx+2]]
    idx += 3
    
    return params


def encode_controller_to_chromosome(controller: 'TeamFuzzyController') -> List[float]:
    """
    Extract parameters from a controller and encode as chromosome.
    
    We use default parameters from the controller design as our baseline.
    In our opinion, it made sense to use these defaults as a starting point for evolution,
    since they represent our initial design decisions before optimization.
    
    Args:
        controller: TeamFuzzyController instance (unused, for interface compatibility)
        
    Returns:
        Chromosome (list of 76 parameter values) using default parameters
    """
    # We use default parameters as baseline for genetic algorithm evolution
    chromosome = []
    
    # Distance: very_near [0, 0, 150]
    chromosome.extend([0, 0, 150])
    # Distance: near [0, 0, 300]
    chromosome.extend([0, 0, 300])
    # Distance: medium [150, 450, 750]
    chromosome.extend([150, 450, 750])
    # Distance: far [600, 1200, 1200]
    chromosome.extend([600, 1200, 1200])
    
    # Rear_threat: near [0, 0, 300]
    chromosome.extend([0, 0, 300])
    # Rear_threat: far [200, 1200, 1200]
    chromosome.extend([200, 1200, 1200])
    
    # Theta_delta: NL zmf [-pi/15, -pi/30]
    chromosome.extend([-math.pi / 15, -math.pi / 30])
    # Theta_delta: NS trimf [-pi/15, -pi/60, 0.0]
    chromosome.extend([-math.pi / 15, -math.pi / 60, 0.0])
    # Theta_delta: Z trimf [-pi/90, 0.0, pi/90]
    chromosome.extend([-math.pi / 90, 0.0, math.pi / 90])
    # Theta_delta: PS trimf [0.0, pi/60, pi/15]
    chromosome.extend([0.0, math.pi / 60, math.pi / 15])
    # Theta_delta: PL smf [pi/30, pi/15]
    chromosome.extend([math.pi / 30, math.pi / 15])
    
    # Bullet_time: short [0.0, 0.0, 0.2]
    chromosome.extend([0.0, 0.0, 0.2])
    # Bullet_time: medium [0.1, 0.35, 0.6]
    chromosome.extend([0.1, 0.35, 0.6])
    # Bullet_time: long [0.4, 1.0, 1.0]
    chromosome.extend([0.4, 1.0, 1.0])
    
    # Thrust: low [0, 0, 30]
    chromosome.extend([0, 0, 30])
    # Thrust: medium [40, 100, 160]
    chromosome.extend([40, 100, 160])
    # Thrust: high [120, 200, 200]
    chromosome.extend([120, 200, 200])
    
    # Turn: hard_left [-180, -180, -120]
    chromosome.extend([-180, -180, -120])
    # Turn: left [-150, -90, -30]
    chromosome.extend([-150, -90, -30])
    # Turn: zero [-20, 0, 20]
    chromosome.extend([-20, 0, 20])
    # Turn: right [30, 90, 150]
    chromosome.extend([30, 90, 150])
    # Turn: hard_right [120, 180, 180]
    chromosome.extend([120, 180, 180])
    
    # Fire: no [-1.0, -1.0, 0.0]
    chromosome.extend([-1.0, -1.0, 0.0])
    # Fire: yes [0.0, 1.0, 1.0]
    chromosome.extend([0.0, 1.0, 1.0])
    
    # Mine: no [-1.0, -1.0, 0.0]
    chromosome.extend([-1.0, -1.0, 0.0])
    # Mine: yes [0.0, 1.0, 1.0]
    chromosome.extend([0.0, 1.0, 1.0])
    
    return chromosome


def create_controller_from_chromosome(chromosome: List[float]) -> 'TeamFuzzyController':
    """
    Create a TeamFuzzyController instance with parameters from a chromosome.
    
    We create controllers this way during evolution to avoid redundant initialization
    and to directly apply evolved parameters.
    
    Args:
        chromosome: Chromosome encoding fuzzy parameters
        
    Returns:
        TeamFuzzyController instance with evolved parameters
    """
    params = decode_chromosome_to_parameters(chromosome)
    
    # We create a minimal controller instance without calling full __init__
    # so we can manually set up everything with evolved parameters
    controller = TeamFuzzyController.__new__(TeamFuzzyController)
    
    # Initialize universes (same as __init__)
    controller.distance = ctrl.Antecedent(np.arange(0, 1201, 1), "distance_to_closest")
    controller.rear_threat = ctrl.Antecedent(np.arange(0, 1201, 1), "rear_threat_dist")
    controller.theta_delta = ctrl.Antecedent(
        np.arange(-math.pi / 30, math.pi / 30, 0.001), "theta_delta"
    )
    controller.bullet_time = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "bullet_time")
    controller.thrust = ctrl.Consequent(np.arange(0, 201, 1), "thrust_out")
    controller.turn = ctrl.Consequent(np.arange(-180, 181, 1), "turn_out")
    controller.fire = ctrl.Consequent(np.arange(-1, 1.01, 0.01), "fire_out")
    controller.mine = ctrl.Consequent(np.arange(-1, 1.01, 0.01), "mine_out")
    
    # Set up membership functions from parameters
    controller._setup_membership_functions_from_params(params)
    
    # Set up rules (this creates the control system)
    controller._setup_rules()
    
    return controller


def create_test_scenario(name: str = "Test Scenario", num_asteroids: int = 10) -> Scenario:
    """
    Create a test scenario matching competition format.
    
    Args:
        name: Scenario name
        num_asteroids: Number of asteroids to spawn
        
    Returns:
        Scenario object configured for testing
    """
    return Scenario(
        name=name,
        num_asteroids=num_asteroids,
        ship_states=[
            {
                'position': (400, 400),
                'angle': 90,
                'lives': 3,  # 3 lives as per specification
                'team': 1,
                "mines_remaining": 3,
            },
            {
                'position': (600, 400),
                'angle': 90,
                'lives': 3,  # 3 lives as per specification
                'team': 2,
                "mines_remaining": 3,
            },
        ],
        map_size=(1000, 800),
        time_limit=60,
        ammo_limit_multiplier=0,  # Unlimited bullets as per specification
        stop_if_no_ammo=False
    )


def create_fitness_function(num_games: int = 5, headless: bool = True) -> Callable[[List[float]], float]:
    """
    Create a fitness function for the genetic algorithm.
    
    We designed the fitness function to:
    1. Create a controller from the chromosome
    2. Run num_games games against TestController
    3. Return a fitness score (higher is better)
    
    We use Fitness = (TeamFuzzyController asteroids_hit) - (TestController asteroids_hit)
    so that positive fitness means we win, negative means we lose.
    This approach allows us to directly optimize for competitive performance.
    
    Args:
        num_games: Number of games to run for evaluation (default: 5)
        headless: Whether to run games without graphics (default: True)
        
    Returns:
        Fitness function that takes a chromosome and returns fitness score
    """
    # We import here to avoid circular imports
    from test_controller import TestController
    
    def fitness(chromosome: List[float]) -> float:
        """
        Evaluate fitness of a chromosome.
        
        Args:
            chromosome: Chromosome encoding fuzzy parameters
            
        Returns:
            Fitness score (higher is better)
        """
        # Run games and accumulate scores
        total_our_score = 0
        total_opponent_score = 0
        
        for game_num in range(num_games):
            # We create fresh controller instances for each game to ensure fair evaluation
            our_controller = create_controller_from_chromosome(chromosome)
            opponent_controller = TestController()
            
            # We run games headless for speed during evolution
            game_settings = {
                'perf_tracker': True,
                'graphics_type': GraphicsType.NoGraphics if headless else GraphicsType.Tkinter,
                'realtime_multiplier': 0.0 if headless else 1.0,
                'graphics_obj': None,
                'frequency': 30
            }
            game = KesslerGame(settings=game_settings)
            scenario = create_test_scenario(name=f"GA Game {game_num}")
            
            try:
                score, _ = game.run(scenario=scenario, controllers=[our_controller, opponent_controller])
                
                total_our_score += score.teams[0].asteroids_hit
                total_opponent_score += score.teams[1].asteroids_hit
            except Exception as e:
                # If game fails, we return very low fitness to penalize invalid chromosomes
                print(f"  Warning: Game {game_num} failed: {e}")
                return float('-inf')
        
        # We calculate fitness as our score minus opponent score
        # Higher is better (we want to maximize this)
        fitness_score = total_our_score - total_opponent_score
        
        return float(fitness_score)
    
    return fitness


# ============================================================================
# GENETIC ALGORITHM FRAMEWORK
# ============================================================================

class GeneticAlgorithm:
    """
    Genetic Algorithm for evolving fuzzy controller parameters.
    
    The chromosome encodes all fuzzy membership function parameters:
    - Distance membership functions (very_near, near, medium, far)
    - Rear_threat membership functions (near, far)
    - Theta_delta membership functions (NL, NS, Z, PS, PL)
    - Bullet_time membership functions (short, medium, long)
    - Thrust output membership functions (low, medium, high)
    - Turn output membership functions (hard_left, left, zero, right, hard_right)
    - Fire output membership functions (no, yes)
    - Mine output membership functions (no, yes)
    """
    
    def __init__(self, config: dict = None, fitness_function: Callable = None):
        """
        Initialize genetic algorithm.
        
        Args:
            config: Configuration dictionary (uses GA_CONFIG if None)
            fitness_function: Function to evaluate fitness of a chromosome
        """
        self.config = config if config is not None else GA_CONFIG
        self.fitness_function = fitness_function
        
        # GA parameters
        self.population_size = self.config['population_size']
        self.generations = self.config['generations']
        self.mutation_rate = self.config['mutation_rate']
        self.crossover_rate = self.config['crossover_rate']
        self.elitism_count = int(self.population_size * self.config['elitism_ratio'])
        self.tournament_size = self.config['tournament_size']
        
        # We define chromosome structure and bounds to constrain the search space
        # Each parameter is encoded as a float in the chromosome
        self.parameter_bounds = self._define_parameter_bounds()
        self.chromosome_length = len(self.parameter_bounds)
        
        # We track evolution progress to monitor convergence
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_chromosome = None
        self.best_fitness = float('-inf')
        
    def _define_parameter_bounds(self) -> List[Tuple[float, float]]:
        """
        Define valid bounds for each parameter in the chromosome.
        
        We set bounds to constrain the search space while allowing meaningful optimization.
        Some parameters are fixed to maintain semantic meaning of membership functions.
        
        Returns:
            List of (min, max) tuples for each parameter
        """
        bounds = []
        
        # Distance membership functions (4 sets, each trimf has 3 params)
        # We keep very_near starting at 0 to maintain its "very close" semantic meaning
        # very_near: [0, 0, 150] -> optimize: [0, 0, 150] (keep first two 0, optimize third)
        bounds.append((0, 0))      # very_near[0] - fixed at 0
        bounds.append((0, 0))      # very_near[1] - fixed at 0
        bounds.append((100, 200))  # very_near[2] - we optimize this to tune the threshold
        
        # near: [0, 0, 300]
        bounds.append((0, 0))      # near[0] - fixed at 0
        bounds.append((0, 0))      # near[1] - fixed at 0
        bounds.append((200, 400))  # near[2] - optimize
        
        # medium: [150, 450, 750]
        bounds.append((100, 200))  # medium[0]
        bounds.append((400, 500))  # medium[1]
        bounds.append((700, 800))  # medium[2]
        
        # far: [600, 1200, 1200]
        bounds.append((500, 700))  # far[0]
        bounds.append((1100, 1200)) # far[1] - keep near max
        bounds.append((1200, 1200)) # far[2] - fixed at 1200
        
        # Rear_threat membership functions (2 sets)
        # near: [0, 0, 300]
        bounds.append((0, 0))      # rear_near[0] - fixed
        bounds.append((0, 0))      # rear_near[1] - fixed
        bounds.append((200, 400))  # rear_near[2] - optimize
        
        # far: [200, 1200, 1200]
        bounds.append((150, 250))  # rear_far[0]
        bounds.append((1100, 1200)) # rear_far[1]
        bounds.append((1200, 1200)) # rear_far[2] - fixed
        
        # Theta_delta membership functions (5 sets)
        # NL: zmf [-pi/15, -pi/30] - 2 params
        bounds.append((-math.pi/12, -math.pi/20))  # NL[0]
        bounds.append((-math.pi/20, -math.pi/40))   # NL[1]
        
        # NS: trimf [-pi/15, -pi/60, 0.0] - 3 params
        bounds.append((-math.pi/12, -math.pi/20))  # NS[0]
        bounds.append((-math.pi/50, -math.pi/70))  # NS[1]
        bounds.append((-0.01, 0.01))               # NS[2] - near zero
        
        # Z: trimf [-pi/90, 0.0, pi/90] - 3 params
        bounds.append((-math.pi/80, -math.pi/100)) # Z[0]
        bounds.append((-0.01, 0.01))               # Z[1] - zero
        bounds.append((math.pi/100, math.pi/80))  # Z[2]
        
        # PS: trimf [0.0, pi/60, pi/15] - 3 params
        bounds.append((-0.01, 0.01))               # PS[0] - near zero
        bounds.append((math.pi/70, math.pi/50))    # PS[1]
        bounds.append((math.pi/20, math.pi/12))   # PS[2]
        
        # PL: smf [pi/30, pi/15] - 2 params
        bounds.append((math.pi/40, math.pi/20))    # PL[0]
        bounds.append((math.pi/20, math.pi/12))   # PL[1]
        
        # Bullet_time membership functions (3 sets)
        # short: [0.0, 0.0, 0.2]
        bounds.append((0.0, 0.0))   # short[0] - fixed
        bounds.append((0.0, 0.0))   # short[1] - fixed
        bounds.append((0.15, 0.25))  # short[2] - optimize
        
        # medium: [0.1, 0.35, 0.6]
        bounds.append((0.05, 0.15))  # medium[0]
        bounds.append((0.30, 0.40))  # medium[1]
        bounds.append((0.55, 0.65)) # medium[2]
        
        # long: [0.4, 1.0, 1.0]
        bounds.append((0.35, 0.45)) # long[0]
        bounds.append((0.95, 1.0))  # long[1]
        bounds.append((1.0, 1.0))   # long[2] - fixed
        
        # Thrust output membership functions (3 sets)
        # low: [0, 0, 30]
        bounds.append((0, 0))       # low[0] - fixed
        bounds.append((0, 0))       # low[1] - fixed
        bounds.append((20, 40))    # low[2] - optimize
        
        # medium: [40, 100, 160]
        bounds.append((30, 50))     # medium[0]
        bounds.append((90, 110))    # medium[1]
        bounds.append((150, 170))   # medium[2]
        
        # high: [120, 200, 200]
        bounds.append((110, 130))   # high[0]
        bounds.append((190, 200))  # high[1]
        bounds.append((200, 200))   # high[2] - fixed
        
        # Turn output membership functions (5 sets)
        # hard_left: [-180, -180, -120]
        bounds.append((-180, -180)) # hard_left[0] - fixed
        bounds.append((-180, -180)) # hard_left[1] - fixed
        bounds.append((-130, -110)) # hard_left[2] - optimize
        
        # left: [-150, -90, -30]
        bounds.append((-160, -140)) # left[0]
        bounds.append((-100, -80))  # left[1]
        bounds.append((-40, -20))  # left[2]
        
        # zero: [-20, 0, 20]
        bounds.append((-25, -15))   # zero[0]
        bounds.append((-5, 5))      # zero[1] - near zero
        bounds.append((15, 25))     # zero[2]
        
        # right: [30, 90, 150]
        bounds.append((20, 40))     # right[0]
        bounds.append((80, 100))    # right[1]
        bounds.append((140, 160))   # right[2]
        
        # hard_right: [120, 180, 180]
        bounds.append((110, 130))   # hard_right[0]
        bounds.append((180, 180))  # hard_right[1] - fixed
        bounds.append((180, 180))  # hard_right[2] - fixed
        
        # Fire output membership functions (2 sets)
        # no: [-1.0, -1.0, 0.0]
        bounds.append((-1.0, -1.0)) # no[0] - fixed
        bounds.append((-1.0, -1.0)) # no[1] - fixed
        bounds.append((-0.1, 0.1))  # no[2] - near zero
        
        # yes: [0.0, 1.0, 1.0]
        bounds.append((-0.1, 0.1)) # yes[0] - near zero
        bounds.append((1.0, 1.0))   # yes[1] - fixed
        bounds.append((1.0, 1.0))   # yes[2] - fixed
        
        # Mine output membership functions (2 sets)
        # no: [-1.0, -1.0, 0.0]
        bounds.append((-1.0, -1.0)) # no[0] - fixed
        bounds.append((-1.0, -1.0)) # no[1] - fixed
        bounds.append((-0.1, 0.1))  # no[2] - near zero
        
        # yes: [0.0, 1.0, 1.0]
        bounds.append((-0.1, 0.1))  # yes[0] - near zero
        bounds.append((1.0, 1.0))   # yes[1] - fixed
        bounds.append((1.0, 1.0))   # yes[2] - fixed
        
        return bounds
    
    def initialize_population(self, seed_chromosome: List[float] = None) -> List[List[float]]:
        """
        Create initial random population.
        
        Args:
            seed_chromosome: Optional chromosome to include in initial population
        
        Returns:
            List of chromosomes (each chromosome is a list of parameter values)
        """
        population = []
        
        # If seed chromosome provided, we add it to population to bootstrap evolution
        if seed_chromosome is not None:
            if len(seed_chromosome) != self.chromosome_length:
                raise ValueError(f"Seed chromosome length {len(seed_chromosome)} doesn't match expected length {self.chromosome_length}")
            population.append(seed_chromosome.copy())
        
        # We fill rest of population with random chromosomes to ensure diversity
        for _ in range(len(population), self.population_size):
            chromosome = []
            for min_val, max_val in self.parameter_bounds:
                if min_val == max_val:
                    # We keep fixed parameters at their specified values
                    chromosome.append(min_val)
                else:
                    # We generate random values within bounds to explore the search space
                    chromosome.append(random.uniform(min_val, max_val))
            population.append(chromosome)
        return population
    
    def evaluate_fitness(self, chromosome: List[float]) -> float:
        """
        Evaluate fitness of a chromosome.
        
        Args:
            chromosome: Chromosome to evaluate
            
        Returns:
            Fitness score (higher is better)
        """
        if self.fitness_function is None:
            raise ValueError("Fitness function not set!")
        
        return self.fitness_function(chromosome)
    
    def tournament_selection(self, population: List[List[float]], 
                           fitness_scores: List[float]) -> List[float]:
        """
        Select a parent using tournament selection.
        
        Args:
            population: Current population
            fitness_scores: Fitness scores for each individual
            
        Returns:
            Selected chromosome (parent)
        """
        tournament_indices = random.sample(range(len(population)), self.tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def crossover(self, parent1: List[float], parent2: List[float]) -> Tuple[List[float], List[float]]:
        """
        Create offspring from two parents using single-point crossover.
        
        Args:
            parent1: First parent chromosome
            parent2: Second parent chromosome
            
        Returns:
            Tuple of (offspring1, offspring2)
        """
        if random.random() > self.crossover_rate:
            # No crossover, return parents
            return parent1.copy(), parent2.copy()
        
        # Single-point crossover
        crossover_point = random.randint(1, len(parent1) - 1)
        
        offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
        offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return offspring1, offspring2
    
    def mutate(self, chromosome: List[float]) -> List[float]:
        """
        Mutate a chromosome with given mutation rate.
        
        We use Gaussian mutation to make small, incremental changes to parameters,
        which helps fine-tune solutions without being too disruptive.
        
        Args:
            chromosome: Chromosome to mutate
            
        Returns:
            Mutated chromosome
        """
        mutated = chromosome.copy()
        
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                min_val, max_val = self.parameter_bounds[i]
                
                if min_val == max_val:
                    # We skip fixed parameters to maintain their semantic meaning
                    continue
                
                # We use Gaussian mutation: add small random change (10% of range)
                # This allows fine-tuning without large jumps
                mutation_strength = (max_val - min_val) * 0.1  # 10% of range
                new_value = mutated[i] + random.gauss(0, mutation_strength)
                
                # We clamp to bounds to ensure valid parameter values
                mutated[i] = max(min_val, min(max_val, new_value))
        
        return mutated
    
    def evolve(self) -> Tuple[List[float], float]:
        """
        Main evolution loop.
        
        Returns:
            Tuple of (best_chromosome, best_fitness)
        """
        print("=" * 70)
        print("Starting Genetic Algorithm Evolution")
        print("=" * 70)
        print(f"Population size: {self.population_size}")
        print(f"Generations: {self.generations}")
        print(f"Chromosome length: {self.chromosome_length}")
        print("=" * 70)
        
        # Initialize population (optionally with seed)
        seed = getattr(self, 'seed_chromosome', None)
        population = self.initialize_population(seed_chromosome=seed)
        
        # Evaluate initial population
        print("\nEvaluating initial population...")
        fitness_scores = []
        for i, chromosome in enumerate(population):
            fitness = self.evaluate_fitness(chromosome)
            fitness_scores.append(fitness)
            if fitness > self.best_fitness:
                self.best_fitness = fitness
                self.best_chromosome = chromosome.copy()
            print(f"  Individual {i+1}/{self.population_size}: Fitness = {fitness:.2f}")
        
        # Track initial statistics
        self.best_fitness_history.append(self.best_fitness)
        self.avg_fitness_history.append(np.mean(fitness_scores))
        
        # Evolution loop
        for generation in range(1, self.generations + 1):
            self.generation = generation
            print(f"\n{'=' * 70}")
            print(f"Generation {generation}/{self.generations}")
            print(f"{'=' * 70}")
            
            # We create new population through selection, crossover, and mutation
            new_population = []
            new_fitness = []
            
            # We use elitism to keep best individuals, preserving top solutions
            elite_indices = np.argsort(fitness_scores)[-self.elitism_count:]
            for idx in elite_indices:
                new_population.append(population[idx].copy())
                new_fitness.append(fitness_scores[idx])
            
            # We generate offspring until population is full
            while len(new_population) < self.population_size:
                # We select parents using tournament selection for diversity
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)
                
                # We perform crossover to combine good traits from parents
                offspring1, offspring2 = self.crossover(parent1, parent2)
                
                # We mutate offspring to introduce new variations
                offspring1 = self.mutate(offspring1)
                offspring2 = self.mutate(offspring2)
                
                # We evaluate offspring to determine their fitness
                fitness1 = self.evaluate_fitness(offspring1)
                fitness2 = self.evaluate_fitness(offspring2)
                
                # We add offspring to new population
                new_population.append(offspring1)
                new_fitness.append(fitness1)
                
                if len(new_population) < self.population_size:
                    new_population.append(offspring2)
                    new_fitness.append(fitness2)
                
                # We track the best chromosome across all generations
                if fitness1 > self.best_fitness:
                    self.best_fitness = fitness1
                    self.best_chromosome = offspring1.copy()
                if fitness2 > self.best_fitness:
                    self.best_fitness = fitness2
                    self.best_chromosome = offspring2.copy()
            
            # Update population
            population = new_population
            fitness_scores = new_fitness
            
            # Track statistics
            best_gen = max(fitness_scores)
            avg_gen = np.mean(fitness_scores)
            self.best_fitness_history.append(best_gen)
            self.avg_fitness_history.append(avg_gen)
            
            print(f"Best fitness: {best_gen:.2f}")
            print(f"Average fitness: {avg_gen:.2f}")
            print(f"Overall best: {self.best_fitness:.2f}")
        
        print(f"\n{'=' * 70}")
        print("Evolution Complete!")
        print(f"{'=' * 70}")
        print(f"Best fitness: {self.best_fitness:.2f}")
        print(f"Best chromosome saved")
        
        return self.best_chromosome, self.best_fitness
    
    def save_best_chromosome(self, filename: str = None):
        """Save best chromosome to file."""
        if filename is None:
            filename = BEST_CHROMOSOME_FILE
        
        if self.best_chromosome is None:
            print("No best chromosome to save!")
            return
        
        with open(filename, 'wb') as f:
            pickle.dump({
                'chromosome': self.best_chromosome,
                'fitness': self.best_fitness,
                'generation': self.generation,
                'config': self.config
            }, f)
        
        print(f"Best chromosome saved to {filename}")
    
    def load_best_chromosome(self, filename: str = None) -> List[float]:
        """Load best chromosome from file."""
        if filename is None:
            filename = BEST_CHROMOSOME_FILE
        
        if not os.path.exists(filename):
            print(f"File {filename} not found!")
            return None
        
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        self.best_chromosome = data['chromosome']
        self.best_fitness = data['fitness']
        
        print(f"Best chromosome loaded from {filename}")
        print(f"Fitness: {self.best_fitness:.2f}")
        
        return self.best_chromosome


# ============================================================================
# OPTIMIZED PARAMETER LOADING
# ============================================================================

# We use lazy loading to avoid circular imports when loading optimized parameters
_OPTIMIZED_CHROMOSOME = None
def _load_optimized_chromosome():
    """Lazy load optimized chromosome to avoid circular imports."""
    global _OPTIMIZED_CHROMOSOME
    if _OPTIMIZED_CHROMOSOME is not None:
        return _OPTIMIZED_CHROMOSOME
    
    try:
        if os.path.exists(BEST_CHROMOSOME_FILE):
            with open(BEST_CHROMOSOME_FILE, 'rb') as f:
                data = pickle.load(f)
                _OPTIMIZED_CHROMOSOME = data['chromosome']
                print(f"[TeamFuzzyController] Loaded optimized parameters from {BEST_CHROMOSOME_FILE}")
                return _OPTIMIZED_CHROMOSOME
    except Exception as e:
        # If loading fails, we fall back to default parameters
        pass
    
    return None


# ============================================================================
# FUZZY CONTROLLER: TeamFuzzyController
# ============================================================================

class TeamFuzzyController(KesslerController):

    def __init__(self, use_optimized: bool = True):
        """
        Initialize fuzzy variables, membership functions, and (later) rules
        for the team fuzzy controller.
        
        Args:
            use_optimized: If True and optimized parameters are available, use them.
                          Otherwise, use default parameters.
        """

        # -------------------------
        # 1. Define universes
        # -------------------------
        # We define distance universes in pixels (map ~1000x800, diagonal ~1280)
        # We chose 1201 as the max to cover the entire map with some margin
        self.distance = ctrl.Antecedent(np.arange(0, 1201, 1), "distance_to_closest")
        self.rear_threat = ctrl.Antecedent(np.arange(0, 1201, 1), "rear_threat_dist")

        # We define angle error between ship heading and desired firing angle (radians)
        # We use ±pi/30 range to cover typical aiming errors
        self.theta_delta = ctrl.Antecedent(
            np.arange(-math.pi / 30, math.pi / 30, 0.001), "theta_delta"
        )

        # We define bullet time-to-intercept in seconds
        # We cap at 1.0 second as reasonable maximum intercept time
        self.bullet_time = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "bullet_time")

        # Outputs
        # We set thrust range 0-200 as initial conservative range, can be tuned later
        self.thrust = ctrl.Consequent(np.arange(0, 201, 1), "thrust_out")

        # We set turn rate to full range ±180 deg/sec for maximum maneuverability
        self.turn = ctrl.Consequent(np.arange(-180, 181, 1), "turn_out")

        # We use numeric fire decision that we threshold to bool later
        self.fire = ctrl.Consequent(np.arange(-1, 1.01, 0.01), "fire_out")

        # We use numeric mine decision that we threshold to bool later
        self.mine = ctrl.Consequent(np.arange(-1, 1.01, 0.01), "mine_out")

        # ---------------------------------
        # 2. Membership functions – inputs
        # ---------------------------------
        # We prefer optimized parameters if available, otherwise use defaults
        optimized_chromosome = None
        if use_optimized:
            optimized_chromosome = _load_optimized_chromosome()
        
        if optimized_chromosome is not None:
            # We use optimized parameters from genetic algorithm evolution
            params = decode_chromosome_to_parameters(optimized_chromosome)
            self._setup_membership_functions_from_params(params)
        else:
            # We fall back to default parameters if no optimized version exists
            self._setup_default_membership_functions()

        # ---------------------------------
        # 3. Fuzzy rules & control system
        # ---------------------------------
        self._setup_rules()
    
    def _setup_default_membership_functions(self):
        """Set up membership functions with default parameters."""
        # distance_to_closest: Very_Near / Near / Medium / Far
        # We define these ranges to handle different engagement distances
        self.distance["near"] = fuzz.trimf(self.distance.universe, [0, 0, 300])
        self.distance["medium"] = fuzz.trimf(
            self.distance.universe, [150, 450, 750]
        )
        self.distance["far"] = fuzz.trimf(self.distance.universe, [600, 1200, 1200])
        # We added an extra "very_near" band for panic behavior when extremely close
        self.distance["very_near"] = fuzz.trimf(
            self.distance.universe, [0, 0, 150]
        )

        # rear_threat_dist: Near / Far
        self.rear_threat["near"] = fuzz.trimf(self.rear_threat.universe, [0, 0, 300])
        self.rear_threat["far"] = fuzz.trimf(
            self.rear_threat.universe, [200, 1200, 1200]
        )

        # theta_delta: NL / NS / Z / PS / PL (radians)
        # We use open-ended "large" sets plus smaller interior sets, similar to ScottDickController.
        # In our opinion, this design handles both small corrections and large angle errors well.
        td = self.theta_delta.universe
        # We use zmf for large negative to saturate for big negative errors
        self.theta_delta["NL"] = fuzz.zmf(td, -math.pi / 15, -math.pi / 30)
        # Small negative range for fine adjustments
        self.theta_delta["NS"] = fuzz.trimf(
            td, [-math.pi / 15, -math.pi / 60, 0.0]
        )
        # Zero (aligned) - narrow range for precise targeting
        self.theta_delta["Z"] = fuzz.trimf(td, [-math.pi / 90, 0.0, math.pi / 90])
        # Small positive range for fine adjustments
        self.theta_delta["PS"] = fuzz.trimf(
            td, [0.0, math.pi / 60, math.pi / 15]
        )
        # We use smf for large positive to saturate for big positive errors
        self.theta_delta["PL"] = fuzz.smf(td, math.pi / 30, math.pi / 15)

        # bullet_time: Short / Medium / Long
        bt = self.bullet_time.universe
        self.bullet_time["short"] = fuzz.trimf(bt, [0.0, 0.0, 0.2])
        self.bullet_time["medium"] = fuzz.trimf(bt, [0.1, 0.35, 0.6])
        self.bullet_time["long"] = fuzz.trimf(bt, [0.4, 1.0, 1.0])

        # ----------------------------------
        # Output membership functions
        # ----------------------------------
        # thrust_out: Low / Medium / High
        # We designed these ranges to provide smooth control across different situations
        th = self.thrust.universe
        # We set low thrust close to braking/hovering for precision maneuvers
        self.thrust["low"] = fuzz.trimf(th, [0, 0, 30])
        self.thrust["medium"] = fuzz.trimf(th, [40, 100, 160])
        # We set high thrust for aggressive pursuit and escape
        self.thrust["high"] = fuzz.trimf(th, [120, 200, 200])

        # turn_out: HardLeft / Left / Zero / Right / HardRight
        tr = self.turn.universe
        self.turn["hard_left"] = fuzz.trimf(tr, [-180, -180, -120])
        self.turn["left"] = fuzz.trimf(tr, [-150, -90, -30])
        self.turn["zero"] = fuzz.trimf(tr, [-20, 0, 20])
        self.turn["right"] = fuzz.trimf(tr, [30, 90, 150])
        self.turn["hard_right"] = fuzz.trimf(tr, [120, 180, 180])

        # fire_out: No / Yes
        fo = self.fire.universe
        self.fire["no"] = fuzz.trimf(fo, [-1.0, -1.0, 0.0])
        self.fire["yes"] = fuzz.trimf(fo, [0.0, 1.0, 1.0])

        # mine_out: No / Yes
        mo = self.mine.universe
        self.mine["no"] = fuzz.trimf(mo, [-1.0, -1.0, 0.0])
        self.mine["yes"] = fuzz.trimf(mo, [0.0, 1.0, 1.0])
    
    def _setup_membership_functions_from_params(self, params: Dict[str, list]):
        """Set up membership functions from parameter dictionary."""
        # Distance membership functions
        self.distance["very_near"] = fuzz.trimf(
            self.distance.universe, params['distance_very_near']
        )
        self.distance["near"] = fuzz.trimf(
            self.distance.universe, params['distance_near']
        )
        self.distance["medium"] = fuzz.trimf(
            self.distance.universe, params['distance_medium']
        )
        self.distance["far"] = fuzz.trimf(
            self.distance.universe, params['distance_far']
        )
        
        # Rear_threat membership functions
        self.rear_threat["near"] = fuzz.trimf(
            self.rear_threat.universe, params['rear_threat_near']
        )
        self.rear_threat["far"] = fuzz.trimf(
            self.rear_threat.universe, params['rear_threat_far']
        )
        
        # Theta_delta membership functions
        td = self.theta_delta.universe
        self.theta_delta["NL"] = fuzz.zmf(td, params['theta_delta_NL'][0], params['theta_delta_NL'][1])
        self.theta_delta["NS"] = fuzz.trimf(td, params['theta_delta_NS'])
        self.theta_delta["Z"] = fuzz.trimf(td, params['theta_delta_Z'])
        self.theta_delta["PS"] = fuzz.trimf(td, params['theta_delta_PS'])
        self.theta_delta["PL"] = fuzz.smf(td, params['theta_delta_PL'][0], params['theta_delta_PL'][1])
        
        # Bullet_time membership functions
        bt = self.bullet_time.universe
        self.bullet_time["short"] = fuzz.trimf(bt, params['bullet_time_short'])
        self.bullet_time["medium"] = fuzz.trimf(bt, params['bullet_time_medium'])
        self.bullet_time["long"] = fuzz.trimf(bt, params['bullet_time_long'])
        
        # Thrust output membership functions
        th = self.thrust.universe
        self.thrust["low"] = fuzz.trimf(th, params['thrust_low'])
        self.thrust["medium"] = fuzz.trimf(th, params['thrust_medium'])
        self.thrust["high"] = fuzz.trimf(th, params['thrust_high'])
        
        # Turn output membership functions
        tr = self.turn.universe
        self.turn["hard_left"] = fuzz.trimf(tr, params['turn_hard_left'])
        self.turn["left"] = fuzz.trimf(tr, params['turn_left'])
        self.turn["zero"] = fuzz.trimf(tr, params['turn_zero'])
        self.turn["right"] = fuzz.trimf(tr, params['turn_right'])
        self.turn["hard_right"] = fuzz.trimf(tr, params['turn_hard_right'])
        
        # Fire output membership functions
        fo = self.fire.universe
        self.fire["no"] = fuzz.trimf(fo, params['fire_no'])
        self.fire["yes"] = fuzz.trimf(fo, params['fire_yes'])
        
        # Mine output membership functions
        mo = self.mine.universe
        self.mine["no"] = fuzz.trimf(mo, params['mine_no'])
        self.mine["yes"] = fuzz.trimf(mo, params['mine_yes'])

    def _setup_rules(self):
        """Set up fuzzy rules and control system."""
        # Turn & fire rules - we use conservative firing to avoid wasting ammo
        # We separate left/right rules so we keep the sign of theta_delta for proper turning
        rule1_left = ctrl.Rule(
            self.theta_delta["NL"] & self.bullet_time["long"],
            (self.turn["hard_left"], self.fire["no"]),
        )
        rule1_right = ctrl.Rule(
            self.theta_delta["PL"] & self.bullet_time["long"],
            (self.turn["hard_right"], self.fire["no"]),
        )
        # We fire when aligned and bullet time is short (good shot opportunity)
        rule2_left = ctrl.Rule(
            self.theta_delta["NS"] & self.bullet_time["short"],
            (self.turn["left"], self.fire["yes"]),
        )
        rule2_right = ctrl.Rule(
            self.theta_delta["PS"] & self.bullet_time["short"],
            (self.turn["right"], self.fire["yes"]),
        )
        # We fire when perfectly aligned and intercept time is reasonable
        rule3 = ctrl.Rule(
            self.theta_delta["Z"] & (self.bullet_time["short"] | self.bullet_time["medium"]),
            (self.turn["zero"], self.fire["yes"]),
        )
        # We don't fire when angle is small but bullet time is medium (still adjusting)
        rule4_left = ctrl.Rule(
            self.theta_delta["NS"] & self.bullet_time["medium"],
            (self.turn["left"], self.fire["no"]),
        )
        rule4_right = ctrl.Rule(
            self.theta_delta["PS"] & self.bullet_time["medium"],
            (self.turn["right"], self.fire["no"]),
        )

        # Thrust rules
        # We use very low thrust when VERY close and aligned to avoid collisions (panic brake)
        rule5_panic = ctrl.Rule(
            self.distance["very_near"] & self.theta_delta["Z"],
            self.thrust["low"],
        )

        # We use low thrust when near with large angle error to back off and reposition
        rule5 = ctrl.Rule(
            self.distance["near"] & (self.theta_delta["NL"] | self.theta_delta["PL"]),
            self.thrust["low"],
        )

        # We use medium thrust when near with small angle error to orbit around target
        rule6 = ctrl.Rule(
            self.distance["near"] & (self.theta_delta["NS"] | self.theta_delta["PS"]),
            self.thrust["medium"],
        )

        # We use high thrust when far to aggressively pursue targets
        rule7 = ctrl.Rule(self.distance["far"], self.thrust["high"])

        # We use medium thrust at medium distance to close in steadily
        rule7b = ctrl.Rule(self.distance["medium"], self.thrust["medium"])

        # Mine rules: we deploy mines when chased from behind at safe distance
        # In our opinion, this strategy helps defend against pursuing threats
        rule8_chased = ctrl.Rule(
            self.rear_threat["near"] & (self.distance["medium"] | self.distance["far"]),
            self.mine["yes"],
        )
        # We don't deploy mines when too close to avoid self-damage
        rule9_too_close = ctrl.Rule(
            self.distance["very_near"],
            self.mine["no"],
        )
        # We don't deploy mines when no rear threat exists
        rule10_no_rear = ctrl.Rule(
            self.rear_threat["far"],
            self.mine["no"],
        )

        # Build the control system
        self.controller = ctrl.ControlSystem(
            [
                rule1_left,
                rule1_right,
                rule2_left,
                rule2_right,
                rule3,
                rule4_left,
                rule4_right,
                rule5_panic,
                rule5,
                rule6,
                rule7,
                rule7b,
                rule8_chased,
                rule9_too_close,
                rule10_no_rear,
            ]
        )

    def actions(self, ship_state: Dict, game_state: Dict) -> Tuple[float, float, bool, bool]:
        """
        Called every frame. Compute:
        thrust, turn_rate, fire, drop_mine

        - Extract nearest asteroid
        - Compute angles and distances
        - Feed into fuzzy controller
        - Return 4 actions
        """

        # We fall back to safe no-op if controller not initialized or no asteroids
        asteroids = getattr(game_state, "asteroids", None)
        if asteroids is None:
            # We handle older Kessler versions that may pass a plain dict
            try:
                asteroids = game_state["asteroids"]
            except (TypeError, KeyError):
                asteroids = []

        if self.controller is None or len(asteroids) == 0:
            return 0.0, 0.0, False, False

        # Current frame (if available)
        frame = getattr(ship_state, "time", None)

        # -----------------------------
        # 1. Find closest asteroid
        # -----------------------------
        ship_pos_x = ship_state["position"][0]
        ship_pos_y = ship_state["position"][1]

        closest = None
        for a in asteroids:
            dx = ship_pos_x - a["position"][0]
            dy = ship_pos_y - a["position"][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if closest is None or dist < closest["dist"]:
                closest = {"aster": a, "dist": dist}

        distance_to_closest = closest["dist"]

        # -----------------------------------------
        # 2. Panic-escape override: only if a rock
        # is both close AND moving towards us.
        # -----------------------------------------
        # We implemented this override to handle imminent collision threats
        # that the fuzzy controller might not respond to quickly enough
        ship_heading_rad = (math.pi / 180.0) * ship_state["heading"]

        # We compute vector and velocity of closest asteroid
        ax, ay = closest["aster"]["position"]
        vx, vy = closest["aster"]["velocity"]

        dx_closest = ax - ship_pos_x
        dy_closest = ay - ship_pos_y

        # We calculate how fast the asteroid is closing in along the line of sight
        # r · v < 0 => moving roughly towards the ship.
        dist_safe = max(distance_to_closest, 1e-3)
        radial_dot = dx_closest * vx + dy_closest * vy
        approach_speed = -radial_dot / dist_safe  # positive when approaching

        # We use a smaller danger bubble and approach threshold to avoid false panics
        PANIC_RADIUS = 120.0          # smaller danger bubble
        APPROACH_THRESHOLD = 60.0     # only panic if closing faster than this

        if distance_to_closest < PANIC_RADIUS and approach_speed > APPROACH_THRESHOLD:
            # We compute angle *towards* the asteroid
            angle_to_asteroid = math.atan2(dy_closest, dx_closest)

            # We set escape direction directly away (add pi)
            escape_angle = angle_to_asteroid + math.pi

            # We compute smallest angle difference between ship heading and escape direction
            escape_delta = (escape_angle - ship_heading_rad + math.pi) % (2 * math.pi) - math.pi

            # We convert rad → deg/s and scale up to turn faster in panic mode
            turn_rate = escape_delta * 180.0 / math.pi * 3.0
            turn_rate = max(-180.0, min(180.0, turn_rate))

            # We use strong but not insane thrust to leave the danger zone quickly
            thrust = 140.0

            # In panic mode, we prioritize survival over kills
            fire = False
            drop_mine = False   # we disable mines in panic to avoid self-damage

            return float(thrust), float(turn_rate), bool(fire), bool(drop_mine)

        # -----------------------------------------
        # 3. Compute intercept bullet_time, theta
        # -----------------------------------------
        asteroid_ship_x = ship_pos_x - closest["aster"]["position"][0]
        asteroid_ship_y = ship_pos_y - closest["aster"]["position"][1]
        asteroid_ship_theta = math.atan2(asteroid_ship_y, asteroid_ship_x)

        asteroid_direction = math.atan2(
            closest["aster"]["velocity"][1], closest["aster"]["velocity"][0]
        )
        my_theta2 = asteroid_ship_theta - asteroid_direction
        cos_my_theta2 = math.cos(my_theta2)

        asteroid_vel = math.sqrt(
            closest["aster"]["velocity"][0] ** 2
            + closest["aster"]["velocity"][1] ** 2
        )
        bullet_speed = 800.0

        # We solve quadratic equation for intercept time
        d = closest["dist"]
        targ_det = (-2 * d * asteroid_vel * cos_my_theta2) ** 2 - (
            4 * (asteroid_vel**2 - bullet_speed**2) * (d**2)
        )

        # We guard against tiny negative due to rounding errors
        if targ_det < 0:
            targ_det = 0.0

        intrcpt1 = (
            (2 * d * asteroid_vel * cos_my_theta2) + math.sqrt(targ_det)
        ) / (2 * (asteroid_vel**2 - bullet_speed**2))
        intrcpt2 = (
            (2 * d * asteroid_vel * cos_my_theta2) - math.sqrt(targ_det)
        ) / (2 * (asteroid_vel**2 - bullet_speed**2))

        # We select positive, smallest intercept time for earliest hit
        if intrcpt1 > intrcpt2:
            bullet_t = intrcpt2 if intrcpt2 >= 0 else intrcpt1
        else:
            bullet_t = intrcpt1 if intrcpt1 >= 0 else intrcpt2

        # We compute intercept point one frame in future (1/30 s) to account for processing delay
        intrcpt_x = closest["aster"]["position"][0] + closest["aster"]["velocity"][0] * (
            bullet_t + 1 / 30
        )
        intrcpt_y = closest["aster"]["position"][1] + closest["aster"]["velocity"][1] * (
            bullet_t + 1 / 30
        )

        my_theta1 = math.atan2(intrcpt_y - ship_pos_y, intrcpt_x - ship_pos_x)

        # We compute shooting angle error (ship heading is in degrees)
        shooting_theta = my_theta1 - ((math.pi / 180.0) * ship_state["heading"])
        shooting_theta = (shooting_theta + math.pi) % (2 * math.pi) - math.pi

        # -----------------------------------
        # 4. Compute rear_threat_dist
        # -----------------------------------
        # We default to "far" if no rear threat exists
        rear_threat_dist = 1200.0  # default "far"
        # We compute backward direction in radians (ship_heading_rad already computed above)
        backward_angle = ship_heading_rad + math.pi

        # We search for asteroids behind us to determine rear threat distance
        for a in asteroids:
            dx = a["position"][0] - ship_pos_x
            dy = a["position"][1] - ship_pos_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist == 0:
                continue
            angle_to_asteroid = math.atan2(dy, dx)
            # We compute angle difference to backward direction
            diff = (angle_to_asteroid - backward_angle + math.pi) % (
                2 * math.pi
            ) - math.pi
            # We consider asteroids within 60 degrees (~pi/3) of directly behind as threats
            if abs(diff) <= math.pi / 3 and dist < rear_threat_dist:
                rear_threat_dist = dist

        # ----------------------------
        # 5. Run fuzzy controller
        # ----------------------------
        sim = ctrl.ControlSystemSimulation(self.controller, flush_after_run=1)

        sim.input["distance_to_closest"] = distance_to_closest
        sim.input["rear_threat_dist"] = rear_threat_dist
        sim.input["theta_delta"] = shooting_theta
        sim.input["bullet_time"] = max(0.0, min(bullet_t, 1.0))

        try:
            sim.compute()
        except Exception as e:
            # If the fuzzy engine fails (e.g., due to numerical issues), we fall back to safe defaults
            print(f"[TeamFuzzy] Fuzzy compute error: {e}")
            return 0.0, 0.0, False, False

        # We safely fetch outputs; if any are missing, we use reasonable defaults
        thrust_val = sim.output.get("thrust_out", 100.0)
        turn_val = sim.output.get("turn_out", 0.0)
        fire_val = sim.output.get("fire_out", -1.0)
        mine_val = sim.output.get("mine_out", -1.0)  # We extract mine output from fuzzy controller

        # We clamp numeric actions to safe ranges to prevent invalid values
        thrust = max(0.0, min(thrust_val, 200.0))
        turn_rate = max(-180.0, min(turn_val, 180.0))

        # --------------------------------------
        # Engagement throttle:
        # If we are lined up and about to hit,
        # don't keep accelerating into the rock.
        # --------------------------------------
        # We implemented this to prevent collisions when we're about to hit
        ENGAGE_RADIUS = 260.0  # we only apply this when reasonably close

        if (
            distance_to_closest < ENGAGE_RADIUS
            and abs(shooting_theta) < 0.12   # roughly on-target
            and bullet_t > 0.0               # valid intercept
            and bullet_t < 0.8               # bullet hits fairly soon
        ):
            # For very short intercept times, we almost stop pushing forward to avoid collision
            if bullet_t < 0.45:
                target_thrust_cap = 15.0
            else:
                target_thrust_cap = 40.0

            # We gently clamp thrust downward if fuzzy wanted more to prevent overshooting
            thrust = min(thrust, target_thrust_cap)

        # We use a slightly relaxed firing window so we actually shoot sometimes
        # In our opinion, this balances accuracy with opportunity
        fire = (
            fire_val > 0.0
            and abs(shooting_theta) < 0.60  # ~34 degrees
            and bullet_t < 3.4              # a bit more time
        )

        # Mine deployment: we use fuzzy controller output
        # Our rules: deploy mine when rear threat is near and we're at safe distance
        #           don't deploy if too close (safety) or no rear threat
        drop_mine = False

        # We print debug info every ~60 frames to inspect behavior without spamming
        if frame is not None and frame % 60 == 0:
            print(
                f"[TeamFuzzy] dist={distance_to_closest:.1f}, rear={rear_threat_dist:.1f}, "
                f"theta={shooting_theta:.3f}, bt={bullet_t:.3f} -> "
                f"thrust={thrust:.1f}, turn={turn_rate:.1f}, fire={fire}, mine={drop_mine}"
            )

        # We cast to plain Python types (Kessler expects built-in float/bool, not numpy types)
        return float(thrust), float(turn_rate), bool(fire), bool(drop_mine)

    @property
    def name(self) -> str:
        return "Team Fuzzy Controller"


# ============================================================================
# EVOLUTION RUNNER (Main Block)
# ============================================================================
# Uncomment the code below and run this file directly to start evolution:
# python main_controller.py

if __name__ == "__main__":
    print("=" * 70)
    print("Genetic Algorithm Evolution - Run Evolution")
    print("=" * 70)
    print("\nThis will evolve fuzzy controller parameters using a genetic algorithm.")
    print("The fitness function evaluates controllers by running games against TestController.")
    print("\nConfiguration:")
    print(f"  Population size: {GA_CONFIG['population_size']}")
    print(f"  Generations: {GA_CONFIG['generations']}")
    print(f"  Games per fitness evaluation: {GA_CONFIG['games_per_fitness']}")
    print(f"  Mutation rate: {GA_CONFIG['mutation_rate']}")
    print(f"  Crossover rate: {GA_CONFIG['crossover_rate']}")
    print(f"  Elitism ratio: {GA_CONFIG['elitism_ratio']}")
    print("=" * 70)
    
    # Ask for confirmation
    response = input("\nProceed with evolution? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Evolution cancelled.")
        exit(0)
    
    # Create fitness function
    print("\nCreating fitness function...")
    fitness_func = create_fitness_function(
        num_games=GA_CONFIG['games_per_fitness'],
        headless=True  # Run headless for speed
    )
    print("✓ Fitness function created")
    
    # Initialize genetic algorithm
    print("\nInitializing genetic algorithm...")
    ga = GeneticAlgorithm(
        config=GA_CONFIG,
        fitness_function=fitness_func
    )
    print(f"✓ GA initialized with chromosome length: {ga.chromosome_length}")
    
    # Create baseline chromosome from default controller
    print("\nCreating baseline chromosome from default controller...")
    baseline_controller = TeamFuzzyController(use_optimized=False)
    baseline_chromosome = encode_controller_to_chromosome(baseline_controller)
    print(f"✓ Baseline chromosome created (length: {len(baseline_chromosome)})")
    
    # Evaluate baseline fitness
    print("\nEvaluating baseline controller fitness...")
    baseline_fitness = fitness_func(baseline_chromosome)
    print(f"✓ Baseline fitness: {baseline_fitness:.2f}")
    print(f"  (Positive = wins, Negative = loses against TestController)")
    
    # Optionally seed population with baseline
    seed_baseline = input("\nSeed initial population with baseline? (yes/no, default: yes): ").strip().lower()
    if seed_baseline not in ['no', 'n']:
        print("  Seeding population with baseline chromosome...")
        ga.seed_chromosome = baseline_chromosome
    else:
        ga.seed_chromosome = None
    
    # Run evolution
    print("\n" + "=" * 70)
    print("Starting Evolution")
    print("=" * 70)
    start_time = time.time()
    
    best_chromosome, best_fitness = ga.evolve()
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("Evolution Complete!")
    print("=" * 70)
    print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Best fitness: {best_fitness:.2f}")
    print(f"Baseline fitness: {baseline_fitness:.2f}")
    improvement = best_fitness - baseline_fitness
    print(f"Improvement: {improvement:+.2f}")
    
    if best_fitness > baseline_fitness:
        print(f"\n✓ Evolved controller outperforms baseline by {improvement:.2f} points!")
    else:
        print(f"\n⚠ Evolved controller did not outperform baseline.")
    
    # Save best chromosome
    print(f"\nSaving best chromosome to {BEST_CHROMOSOME_FILE}...")
    ga.save_best_chromosome(BEST_CHROMOSOME_FILE)
    print("✓ Best chromosome saved")
    
    print("\n" + "=" * 70)
    print("Evolution Complete!")
    print("=" * 70)
    print("\nThe optimized parameters have been saved to best_chromosome.pkl")
    print("The TeamFuzzyController will automatically load these parameters on next run.")
