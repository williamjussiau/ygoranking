#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 16:19:07 2020

@author: william
"""


import glicko2 as glk
import ygomanagement as ygom
import numpy as np
import fileinput

if ygom.TEST:
    DECK_RANK_FILE = 'test/deck_ranking.csv'
else:
    DECK_RANK_FILE = 'data/deck_ranking.csv'

elo_0 = 1500
glicko_0 = 1500
rd_0 = 350


"""
TODO: on adding a game, only compute scores of last pair
"""


def sort_decks(all_decks_ranked=None, sort_by='glicko'):
    """Sort deck by score (elo or glicko)"""
    if all_decks_ranked is None:
        all_decks_ranked = get_all_decks_ranked()
    all_decks_sorted = all_decks_ranked.sort_values(sort_by, ascending=False)
    all_decks_sorted.reset_index(drop=True, inplace=True)
    return all_decks_sorted


def rank_decks():
    """Print deck ranking and log to file"""
    all_decks_sorted = sort_decks()
    log_to_file(all_decks_sorted, logfile=DECK_RANK_FILE)
    print('Ranking decks by score in file: ' + DECK_RANK_FILE)
    print(all_decks_sorted)
    return all_decks_sorted


def log_to_file(df, logfile=DECK_RANK_FILE):
    """Log given DataFrame to base"""
    df.to_csv(logfile, index=False)


def compute_elo(elo1, elo2, K=40):
    """Compute Elo score of decks with initiale scores elo1, elo2
    given deck with 1 won"""
    # TODO : call compute_elo with K depending on nr of played games
    W = ygom.GameResult.WIN.value
    D = min(elo1 - elo2, 400)

    def pD(D):
        return 1/(1+10**(-D/400))

    elo1 = elo1 + K * (W - pD(D))
    elo2 = elo2 + K * (1 - W - pD(-D))
    return int(elo1), int(elo2)


def compute_glicko(glicko1, glicko2):
    """Compute Glicko2 score of decks with initial scores glicko1, glicko2
    given deck with 1 won"""
    gl1 = glk.Player(rating=glicko1[0], rd=glicko1[1])
    gl2 = glk.Player(rating=glicko2[0], rd=glicko2[1])

    gl1.update_player([gl2.rating], [gl2.rd], [ygom.GameResult.WIN.value])
    gl2.update_player([gl1.rating], [gl1.rd], [ygom.GameResult.LOSE.value])

    return gl1, gl2


def get_all_decks_ranked():
    """Return a DataFrame with all decks ranked"""
    return ygom.pd.read_csv(DECK_RANK_FILE)


def show_all_decks_ranked():
    """Print all decks"""
    all_decks_ranked = get_all_decks_ranked()
    print('Displaying all decks ranked...')
    print(all_decks_ranked)


def find_deck_rating(deck_name, all_decks_ranked=None):
    """Return deck rating given its name"""
    if all_decks_ranked is None:
        all_decks_ranked = get_all_decks_ranked()
    deck = all_decks_ranked.loc[all_decks_ranked.deck == deck_name].iloc[0]
    return deck


def compute_all_scores(sort_by='glicko'):
    """Compute all decks scores for each game played"""
    all_games = ygom.get_all_games()
    n_games = len(all_games)

    # Init score table
    all_scores = np.zeros((n_games, 6))  # elo1, elo2, gl1, gl2, rd1, rd2
    # Init deck table
    all_decks_ranked = ygom.get_all_decks()
    all_decks_ranked['winrate'] = 0
    all_decks_ranked['ngames'] = 0
    all_decks_ranked['nwins'] = 0
    all_decks_ranked['nloss'] = 0
    all_decks_ranked['elo'] = elo_0
    all_decks_ranked['glicko'] = glicko_0
    all_decks_ranked['rd'] = rd_0
    # Loop over games and update table
    for i in range(0, n_games):
        # Get game & decks
        game_i = all_games.iloc[i]
        deck1 = find_deck_rating(game_i.deck1, all_decks_ranked)
        deck2 = find_deck_rating(game_i.deck2, all_decks_ranked)
        # Compute newi= ratings
        elo1, elo2 = compute_elo(deck1.elo, deck2.elo)
        gl1, gl2 = compute_glicko([deck1.glicko, deck1.rd],
                                  [deck2.glicko, deck2.rd])
        glicko1 = int(gl1.rating)
        rd1 = int(gl1.rd)
        glicko2 = int(gl2.rating)
        rd2 = int(gl2.rd)
        # Update deck stats
        # deck 1
        deck1.ngames += 1
        deck1.nwins += 1
        deck1[['elo', 'glicko', 'rd']] = elo1, glicko1, rd1
        deck1.winrate = deck1.nwins / deck1.ngames
        # deck 2
        deck2.ngames += 1
        deck2.nloss += 1
        deck2[['elo', 'glicko', 'rd']] = elo2, glicko2, rd2
        deck2.winrate = deck2.nwins / deck2.ngames
        # Log deck in dataframe
        all_decks_ranked.iloc[deck1.name] = deck1
        all_decks_ranked.iloc[deck2.name] = deck2
        # Log scores in array
        all_scores[i, :] = [elo1, elo2, glicko1, rd1, glicko2, rd2]

    # Append new columns to games file
    all_games[['elo1',
               'elo2',
               'gl1',
               'rd1',
               'gl2',
               'rd2']] = all_scores

    # Log new games
    log_to_file(all_games, logfile=ygom.GAME_HIST_FILE)

    # Write ranking file
    all_decks_ranked = sort_decks(all_decks_ranked, sort_by=sort_by)
    log_to_file(all_decks_ranked, logfile=DECK_RANK_FILE)


def compute_scores_last():
    """Compute scores from given game"""
    """TODO"""
    pass
    # all_games = ygom.get_all_games()
    # last_games = all_games.loc[ygom.pd.isnull(all_games.elo1)]
    # n_last = len(last_games)

    # all_decks_ranked = get_all_decks_ranked()
    # for i in range(0, n_last):
    #     # Get game & decks
    #     game_i = last_games.iloc[i]
    #     deck1 = find_deck_rating(game_i.deck1, all_decks_ranked)
    #     deck2 = find_deck_rating(game_i.deck2, all_decks_ranked)


def rename_deck(old_name, new_name):
    """Rename a deck in every file"""
    """Note: function lies in the wrong module (should be ygomanagement)
    for independence purposes (i.e. ygomanagement should not know ranking)"""
    allfiles = [ygom.DECK_LIST_FILE,
                ygom.GAME_HIST_FILE,
                DECK_RANK_FILE]
    for thisfile in allfiles:
        with fileinput.FileInput(thisfile, inplace=True, backup='.bak') \
                as file:
            for line in file:
                print(line.replace(old_name, new_name), end='')
