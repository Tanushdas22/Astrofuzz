# scenario_test.py

import time

from kesslergame import Scenario, KesslerGame, GraphicsType
from test_controller import TestController
from main_controller import TeamFuzzyController
from graphics_both import GraphicsBoth

# Define game scenario
my_test_scenario = Scenario(
    name='Test Scenario',
    num_asteroids=10,
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
    ammo_limit_multiplier=0,
    stop_if_no_ammo=False
)

# Game graphics configuration
game_settings = {
    'perf_tracker': True,
    'graphics_type': GraphicsType.Tkinter,
    'realtime_multiplier': 1,
    'graphics_obj': None,
    'frequency': 30
}

game = KesslerGame(settings=game_settings)

# Run game comparing YOUR controller vs TestController
pre = time.perf_counter()

score, perf_data = game.run(
    scenario=my_test_scenario,
    controllers=[
        TeamFuzzyController(),       # <-- YOUR AGENT
        TestController()             # <-- DUMB BOT
    ]
)

# Print results
print('Scenario eval time: ' + str(time.perf_counter() - pre))
print('Stop Reason:', score.stop_reason)
print('Asteroids hit:', [team.asteroids_hit for team in score.teams])
print('Deaths:', [team.deaths for team in score.teams])
print('Accuracy:', [team.accuracy for team in score.teams])
print('Mean eval time:', [team.mean_eval_time for team in score.teams])
