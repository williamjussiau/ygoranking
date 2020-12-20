# ygoranking
Ranking system for Yu-Gi-Oh! gaming with friends

Available functionalities are:
  - add a new deck (no decklist shall be provided)
  - add a played game with result
  - compute Elo and Glicko2 scores
  - visualize results on graphs
 
Still to be implemented: neat statistics & user-interface
So far, everything has to be done on command line (add_deck, add_game, compute_all_scores...)

# Elo rating
More details about the Elo rating system can be found here: https://en.wikipedia.org/wiki/Elo_rating_system

# Glicko rating
More details about the Glicko rating system can be found here: https://en.wikipedia.org/wiki/Glicko_rating_system
The score and related values are computed using Mark Glickman's original code, see: http://www.glicko.net/glicko.html
