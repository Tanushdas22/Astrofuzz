# test_suite.py
# 
# 5-Game Test Suite for Kessler Game
# Implements automated testing to verify controller performance against test_controller.py
# Format: 5 games, unlimited bullets, 3 lives per game
# Winner: Highest total score (asteroids hit) across 5 games
# Tie-breaker: Average accuracy

import time
from typing import List, Type
from dataclasses import dataclass

from kesslergame import Scenario, KesslerGame, GraphicsType
from test_controller import TestController
from main_controller import TeamFuzzyController


@dataclass
class GameResult:
    """Results from a single game"""
    game_number: int
    team1_asteroids_hit: int
    team2_asteroids_hit: int
    team1_accuracy: float
    team2_accuracy: float
    team1_deaths: int
    team2_deaths: int
    stop_reason: str
    sim_time: float


@dataclass
class TestResults:
    """Aggregated results from 5-game test"""
    team1_total_score: int
    team2_total_score: int
    team1_avg_accuracy: float
    team2_avg_accuracy: float
    team1_total_deaths: int
    team2_total_deaths: int
    individual_games: List[GameResult]
    winner: str
    victory_margin: int


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


def run_single_game(
    scenario: Scenario,
    controller1_class: Type,
    controller2_class: Type,
    game_number: int = 1,
    headless: bool = True
) -> GameResult:
    """
    Run a single game between two controllers.
    
    Args:
        scenario: Game scenario to run
        controller1_class: Controller class for team 1
        controller2_class: Controller class for team 2
        game_number: Game number (for reporting)
        headless: If True, disable graphics for faster execution
        
    Returns:
        GameResult with game statistics
    """
    # Configure game settings
    if headless:
        # Headless mode: no graphics for faster execution
        game_settings = {
            'perf_tracker': True,
            'graphics_type': GraphicsType.NoGraphics,  # No graphics
            'frequency': 30
        }
    else:
        # With graphics (for debugging/visualization)
        game_settings = {
            'perf_tracker': True,
            'graphics_type': GraphicsType.Tkinter,
            'realtime_multiplier': 1,
            'graphics_obj': None,
            'frequency': 30
        }
    
    # Create game instance
    game = KesslerGame(settings=game_settings)
    
    # Create controller instances
    controller1 = controller1_class()
    controller2 = controller2_class()
    
    # Run the game
    score, perf_data = game.run(
        scenario=scenario,
        controllers=[controller1, controller2]
    )
    
    # Extract results
    # Team 1 is first controller, Team 2 is second controller
    team1 = score.teams[0]
    team2 = score.teams[1]
    
    result = GameResult(
        game_number=game_number,
        team1_asteroids_hit=team1.asteroids_hit,
        team2_asteroids_hit=team2.asteroids_hit,
        team1_accuracy=team1.accuracy,
        team2_accuracy=team2.accuracy,
        team1_deaths=team1.deaths,
        team2_deaths=team2.deaths,
        stop_reason=str(score.stop_reason),
        sim_time=score.sim_time
    )
    
    return result


def run_5_game_test(
    controller1_class: Type,
    controller2_class: Type,
    scenarios: List[Scenario] = None,
    headless: bool = True
) -> TestResults:
    """
    Run 5 games between two controllers and aggregate results.
    
    Args:
        controller1_class: Controller class for team 1
        controller2_class: Controller class for team 2
        scenarios: List of scenarios to use (if None, uses default scenario 5 times)
        headless: If True, disable graphics for faster execution
        
    Returns:
        TestResults with aggregated statistics
    """
    # Use provided scenarios or create default ones
    if scenarios is None:
        scenarios = [create_test_scenario(f"Game {i+1}", num_asteroids=10) for i in range(5)]
    
    if len(scenarios) != 5:
        raise ValueError(f"Must provide exactly 5 scenarios, got {len(scenarios)}")
    
    # Run 5 games
    game_results = []
    total_time = 0.0
    
    print("=" * 70)
    print("Running 5-Game Test Suite")
    print("=" * 70)
    print(f"Team 1: {controller1_class.__name__}")
    print(f"Team 2: {controller2_class.__name__}")
    print("=" * 70)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nRunning Game {i}/5...")
        start_time = time.perf_counter()
        
        result = run_single_game(
            scenario=scenario,
            controller1_class=controller1_class,
            controller2_class=controller2_class,
            game_number=i,
            headless=headless
        )
        
        elapsed = time.perf_counter() - start_time
        total_time += elapsed
        
        game_results.append(result)
        
        # Print game result
        print(f"  Game {i} Results:")
        print(f"    Team 1: {result.team1_asteroids_hit} asteroids, "
              f"Accuracy: {result.team1_accuracy:.3f}, Deaths: {result.team1_deaths}")
        print(f"    Team 2: {result.team2_asteroids_hit} asteroids, "
              f"Accuracy: {result.team2_accuracy:.3f}, Deaths: {result.team2_deaths}")
        print(f"    Time: {elapsed:.2f}s")
    
    # Aggregate results
    team1_total_score = sum(r.team1_asteroids_hit for r in game_results)
    team2_total_score = sum(r.team2_asteroids_hit for r in game_results)
    team1_avg_accuracy = sum(r.team1_accuracy for r in game_results) / len(game_results)
    team2_avg_accuracy = sum(r.team2_accuracy for r in game_results) / len(game_results)
    team1_total_deaths = sum(r.team1_deaths for r in game_results)
    team2_total_deaths = sum(r.team2_deaths for r in game_results)
    
    # Determine winner
    if team1_total_score > team2_total_score:
        winner = controller1_class.__name__
        victory_margin = team1_total_score - team2_total_score
    elif team2_total_score > team1_total_score:
        winner = controller2_class.__name__
        victory_margin = team2_total_score - team1_total_score
    else:
        # Tie - use accuracy as tie-breaker
        if team1_avg_accuracy > team2_avg_accuracy:
            winner = f"{controller1_class.__name__} (tie-breaker: accuracy)"
            victory_margin = 0
        elif team2_avg_accuracy > team1_avg_accuracy:
            winner = f"{controller2_class.__name__} (tie-breaker: accuracy)"
            victory_margin = 0
        else:
            winner = "TIE"
            victory_margin = 0
    
    test_results = TestResults(
        team1_total_score=team1_total_score,
        team2_total_score=team2_total_score,
        team1_avg_accuracy=team1_avg_accuracy,
        team2_avg_accuracy=team2_avg_accuracy,
        team1_total_deaths=team1_total_deaths,
        team2_total_deaths=team2_total_deaths,
        individual_games=game_results,
        winner=winner,
        victory_margin=victory_margin
    )
    
    return test_results


def print_test_report(results: TestResults, controller1_name: str, controller2_name: str):
    """
    Print a detailed test report.
    
    Args:
        results: TestResults object
        controller1_name: Name of controller 1
        controller2_name: Name of controller 2
    """
    print("\n" + "=" * 70)
    print("5-GAME TEST RESULTS")
    print("=" * 70)
    
    # Individual game results
    print("\nIndividual Game Results:")
    print("-" * 70)
    print(f"{'Game':<6} {controller1_name:<30} {controller2_name:<30}")
    print(f"{'#':<6} {'Score':<10} {'Acc':<8} {'Deaths':<8} {'Score':<10} {'Acc':<8} {'Deaths':<8}")
    print("-" * 70)
    
    for game in results.individual_games:
        print(f"{game.game_number:<6} "
              f"{game.team1_asteroids_hit:<10} {game.team1_accuracy:<8.3f} {game.team1_deaths:<8} "
              f"{game.team2_asteroids_hit:<10} {game.team2_accuracy:<8.3f} {game.team2_deaths:<8}")
    
    # Aggregate results
    print("\n" + "-" * 70)
    print("Aggregate Results (5 Games):")
    print("-" * 70)
    print(f"{controller1_name}:")
    print(f"  Total Score: {results.team1_total_score}")
    print(f"  Average Accuracy: {results.team1_avg_accuracy:.3f}")
    print(f"  Total Deaths: {results.team1_total_deaths}")
    print(f"\n{controller2_name}:")
    print(f"  Total Score: {results.team2_total_score}")
    print(f"  Average Accuracy: {results.team2_avg_accuracy:.3f}")
    print(f"  Total Deaths: {results.team2_total_deaths}")
    
    # Winner
    print("\n" + "=" * 70)
    if results.victory_margin > 0:
        print(f"WINNER: {results.winner}")
        print(f"Victory Margin: {results.victory_margin} asteroids")
    else:
        print(f"RESULT: {results.winner}")
    print("=" * 70)


def test_against_test_controller(headless: bool = True) -> TestResults:
    """
    Main function: Test TeamFuzzyController against TestController.
    
    This is the primary test function to verify that TeamFuzzyController
    can defeat test_controller.py as required by the specification.
    
    Args:
        headless: If True, disable graphics for faster execution
        
    Returns:
        TestResults object with all statistics
    """
    print("Testing TeamFuzzyController vs TestController")
    print("Format: 5 games, unlimited bullets, 3 lives per game")
    print("Winner: Highest total score, tie-breaker: average accuracy\n")
    
    results = run_5_game_test(
        controller1_class=TeamFuzzyController,
        controller2_class=TestController,
        scenarios=None,  # Use default scenarios
        headless=headless
    )
    
    print_test_report(
        results,
        controller1_name="TeamFuzzyController",
        controller2_name="TestController"
    )
    
    return results


if __name__ == "__main__":
    # Run the test when script is executed directly
    # Set headless=False to see graphics (slower but visual)
    results = test_against_test_controller(headless=True)
    
    # Check if TeamFuzzyController won
    if "TeamFuzzyController" in results.winner:
        print("\n✓ SUCCESS: TeamFuzzyController defeats TestController!")
    else:
        print("\n✗ FAILURE: TeamFuzzyController did not defeat TestController")
        print("   Continue optimization to improve performance.")

