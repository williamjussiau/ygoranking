# ygoranking
Ranking system for Yu-Gi-Oh! gaming with friends

So far, available functionalities are:
  - manage decks (essentially: add new deck with given owner)
  - manage gaming history (add new game, delete last games)
  - compute Elo and Glicko2 scores
  - visualize results on graphs 
 
Still to be implemented: neat statistics & user-interface (everything has to be done on command line)

# Ratings used
## Elo rating
More details about the Elo rating system can be found here: https://en.wikipedia.org/wiki/Elo_rating_system

## Glicko(2) rating
More details about the Glicko rating system can be found here: https://en.wikipedia.org/wiki/Glicko_rating_system
The score and related values are computed using Mark Glickman's original code, see: http://www.glicko.net/glicko.html

# User guide 
```python
# 1. Import modules
import ygomanagement as ygom
import ygoranking as ygor
import ygostats as ygos

# 2. Define files location if necessary
ygom.DECK_LIST_FILE = './...'
ygom.GAME_HIST_FILE = './...'
ygor.DECK_RANK_FILE = './...'

# 3. Add decks
ygom.add_deck('deck_name_1', 'deck_owner_1')
ygom.add_deck('deck_name_2', 'deck_owner_2')

# 4. Add games - first deck referenced is considered the winner
ygom.add_game('deck_name_1', 'deck_name_2') # player 1 won
ygom.add_game('deck_name_2', 'deck_name_1') # player 2 won
ygom.add_game('deck_name_1', 'deck_name_2') # player 1 won the BO3

# 5. Compute scores relative to games at previous steps - not done by automatically
ygor.compute_all_scores()

# 6. Visualize results - functions generally start with 'show_'
# Bar plot
ygos.show_bars()
# Match-ups map
ygos.show_map()
# Games frequency - GitHub-like, based on date of registration
ygos.show_games_frequency()
# Players winrate over time
ygos.show_player_stats()
# Optionally, export figures
ygos.export_examples()

# 7. When opening a new session, you can add new decks, new games and visualize new results
# Be careful to always recompute results based on registered games (step 5)
```

# Examples
## Bar plot
![Alt text](examples/bars.png?raw=true "Ranking of decks (bars)")

## Scores
![Alt text](examples/scores_default.png?raw=true "Ranking of decks (scores)")

## Match-up map
![Alt text](examples/map.png?raw=true "Match-up map")

## Games frequency
![Alt text](examples/games_frequency_map.png?raw=true "Games frequency")








