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
import Python modules
set file names and location
ygomanagement.add_deck >> add a new deck
ygomanagement.add_game >> add a new game
ygoranking.compute_all_scores >> compute scores of all given decks & games played
ygostats >> visualize results
