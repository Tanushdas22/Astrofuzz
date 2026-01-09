# test_controller_match.py
# Test script to run TeamFuzzyController against TestController 5 times
# and determine the winner

import time
from kesslergame import Scenario, KesslerGame, GraphicsType
from test_controller import TestController
from main_controller import TeamFuzzyController


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
                'lives': 3,
                'team': 1,
                "mines_remaining": 3,
            },
            {
                'position': (600, 400),
                'angle': 90,
                'lives': 3,
                'team': 2,
                "mines_remaining": 3,
            },
        ],
        map_size=(1000, 800),
        time_limit=60,
        ammo_limit_multiplier=0,  # Unlimited bullets
        stop_if_no_ammo=False
    )


def run_match(num_games: int = 5, headless: bool = True):
    """
    Run multiple games between TeamFuzzyController and TestController.
    
    Args:
        num_games: Number of games to run (default: 5)
        headless: Whether to run games without graphics (default: True)
    """
    print("=" * 70)
    print("TeamFuzzyController vs TestController Match")
    print("=" * 70)
    print(f"Running {num_games} games...")
    print(f"Mode: {'Headless' if headless else 'With Graphics'}")
    print("=" * 70)
    
    # Statistics tracking
    team_fuzzy_wins = 0
    test_controller_wins = 0
    ties = 0
    
    team_fuzzy_total_asteroids = 0
    test_controller_total_asteroids = 0
    
    team_fuzzy_total_deaths = 0
    test_controller_total_deaths = 0
    
    team_fuzzy_total_accuracy = 0.0
    test_controller_total_accuracy = 0.0
    
    game_results = []
    
    # Game settings
    game_settings = {
        'perf_tracker': True,
        'graphics_type': GraphicsType.NoGraphics if headless else GraphicsType.Tkinter,
        'realtime_multiplier': 0.0 if headless else 1.0,
        'graphics_obj': None,
        'frequency': 30
    }
    
    # Run games
    start_time = time.time()
    
    for game_num in range(1, num_games + 1):
        print(f"\n--- Game {game_num}/{num_games} ---")
        
        # Create fresh controller instances for each game
        team_fuzzy = TeamFuzzyController()
        test_controller = TestController()
        
        # Create scenario
        scenario = create_test_scenario(name=f"Match Game {game_num}")
        
        # Run game
        game = KesslerGame(settings=game_settings)
        
        try:
            score, perf_data = game.run(
                scenario=scenario,
                controllers=[team_fuzzy, test_controller]
            )
            
            # Extract scores
            team_fuzzy_score = score.teams[0].asteroids_hit
            test_controller_score = score.teams[1].asteroids_hit
            
            team_fuzzy_deaths = score.teams[0].deaths
            test_controller_deaths = score.teams[1].deaths
            
            team_fuzzy_accuracy = score.teams[0].accuracy
            test_controller_accuracy = score.teams[1].accuracy
            
            # Update totals
            team_fuzzy_total_asteroids += team_fuzzy_score
            test_controller_total_asteroids += test_controller_score
            
            team_fuzzy_total_deaths += team_fuzzy_deaths
            test_controller_total_deaths += test_controller_deaths
            
            team_fuzzy_total_accuracy += team_fuzzy_accuracy
            test_controller_total_accuracy += test_controller_accuracy
            
            # Determine winner
            if team_fuzzy_score > test_controller_score:
                winner = "TeamFuzzyController"
                team_fuzzy_wins += 1
            elif test_controller_score > team_fuzzy_score:
                winner = "TestController"
                test_controller_wins += 1
            else:
                winner = "Tie"
                ties += 1
            
            # Store result
            game_results.append({
                'game': game_num,
                'team_fuzzy_score': team_fuzzy_score,
                'test_controller_score': test_controller_score,
                'winner': winner,
                'stop_reason': score.stop_reason
            })
            
            # Print game result
            print(f"  TeamFuzzyController: {team_fuzzy_score} asteroids hit")
            print(f"  TestController: {test_controller_score} asteroids hit")
            print(f"  Winner: {winner}")
            print(f"  Stop Reason: {score.stop_reason}")
            print(f"  TeamFuzzyController deaths: {team_fuzzy_deaths}")
            print(f"  TestController deaths: {test_controller_deaths}")
            print(f"  TeamFuzzyController accuracy: {team_fuzzy_accuracy:.2%}")
            print(f"  TestController accuracy: {test_controller_accuracy:.2%}")
            
        except Exception as e:
            print(f"  ERROR: Game {game_num} failed: {e}")
            game_results.append({
                'game': game_num,
                'error': str(e)
            })
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 70)
    print("MATCH SUMMARY")
    print("=" * 70)
    print(f"\nTotal games: {num_games}")
    print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Average time per game: {elapsed_time/num_games:.2f} seconds")
    
    print(f"\n--- Wins ---")
    print(f"TeamFuzzyController: {team_fuzzy_wins} wins")
    print(f"TestController: {test_controller_wins} wins")
    print(f"Ties: {ties} ties")
    
    print(f"\n--- Total Asteroids Hit ---")
    print(f"TeamFuzzyController: {team_fuzzy_total_asteroids} asteroids")
    print(f"TestController: {test_controller_total_asteroids} asteroids")
    print(f"Difference: {team_fuzzy_total_asteroids - test_controller_total_asteroids:+d} asteroids")
    
    print(f"\n--- Average Asteroids Hit per Game ---")
    print(f"TeamFuzzyController: {team_fuzzy_total_asteroids/num_games:.2f} asteroids/game")
    print(f"TestController: {test_controller_total_asteroids/num_games:.2f} asteroids/game")
    
    print(f"\n--- Total Deaths ---")
    print(f"TeamFuzzyController: {team_fuzzy_total_deaths} deaths")
    print(f"TestController: {test_controller_total_deaths} deaths")
    
    print(f"\n--- Average Accuracy ---")
    print(f"TeamFuzzyController: {team_fuzzy_total_accuracy/num_games:.2%}")
    print(f"TestController: {test_controller_total_accuracy/num_games:.2%}")
    
    # Determine overall winner
    print(f"\n" + "=" * 70)
    print("OVERALL WINNER")
    print("=" * 70)
    
    if team_fuzzy_wins > test_controller_wins:
        print(f"🏆 TeamFuzzyController WINS!")
        print(f"   Won {team_fuzzy_wins} out of {num_games} games")
        print(f"   Total score: {team_fuzzy_total_asteroids} vs {test_controller_total_asteroids}")
    elif test_controller_wins > team_fuzzy_wins:
        print(f"🏆 TestController WINS!")
        print(f"   Won {test_controller_wins} out of {num_games} games")
        print(f"   Total score: {test_controller_total_asteroids} vs {team_fuzzy_total_asteroids}")
    else:
        print(f"🤝 TIE!")
        print(f"   Both controllers won {team_fuzzy_wins} games each")
        if team_fuzzy_total_asteroids > test_controller_total_asteroids:
            print(f"   TeamFuzzyController wins on total score: {team_fuzzy_total_asteroids} vs {test_controller_total_asteroids}")
        elif test_controller_total_asteroids > team_fuzzy_total_asteroids:
            print(f"   TestController wins on total score: {test_controller_total_asteroids} vs {team_fuzzy_total_asteroids}")
        else:
            print(f"   Perfect tie on total score: {team_fuzzy_total_asteroids}")
    
    print("=" * 70)
    
    return {
        'team_fuzzy_wins': team_fuzzy_wins,
        'test_controller_wins': test_controller_wins,
        'ties': ties,
        'team_fuzzy_total_asteroids': team_fuzzy_total_asteroids,
        'test_controller_total_asteroids': test_controller_total_asteroids,
        'game_results': game_results
    }


if __name__ == "__main__":
    # Run the match
    results = run_match(num_games=5, headless=True)
    
    print("\nMatch complete!")

