#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 16:19:07 2020

@author: william
"""

"""
TODO: on adding a game, only compute scores of last pair
"""

import glicko2 as glk
import ygomanagement as ygom
import numpy as np

if ygom.TEST:
    DECK_RANK_FILE = 'test/deck_ranking.csv'
else:
    DECK_RANK_FILE = 'data/deck_ranking.csv'

elo_0 = 1500
glicko_0 = 1500
rd_0 = 350

def sort_decks(all_decks_ranked=None, sort_by='elo'):
    """Classe les decks par score (Elo ou Glicko) dans le fichier"""
    if all_decks_ranked is None:
        all_decks_ranked = get_all_decks_ranked()
    all_decks_sorted = all_decks_ranked.sort_values(sort_by, ascending=False)
    all_decks_sorted.reset_index(drop=True, inplace=True)
    return all_decks_sorted

def rank_decks():
    """Affiche le classement de decks dans la ligne de commande"""
    all_decks_sorted = sort_decks()
    log_to_file(all_decks_sorted, logfile=DECK_RANK_FILE)
    print('Ranking decks by score in file: ' + DECK_RANK_FILE)
    print(all_decks_sorted)
    return all_decks_sorted

def log_to_file(df, logfile=DECK_RANK_FILE):
    """Enregistre la DataFrame dans le fichier donné """
    df.to_csv(logfile, index=False)
    #print('Printing to log file')

def compute_elo(elo1, elo2):
    """Calcule le score Elo de deux decks étant donné un match
    Le joueur 1 a gagné par défaut"""
    K = 40
    W = ygom.GameResult.WIN.value
    D = min(elo1 - elo2, 400)
    pD = lambda D: 1/(1+10**(-D/400))
    elo1 = elo1 + K * (W - pD(D))
    elo2 = elo2 + K * (1 - W - pD(-D))
    return int(elo1), int(elo2)

def compute_glicko(glicko1, glicko2):
    """Calcule le score Glicko de deux decks étant donné un match"""
    gl1 = glk.Player(rating=glicko1[0], rd=glicko1[1])
    gl2 = glk.Player(rating=glicko2[0], rd=glicko2[1])
        
    gl1.update_player([gl2.rating], [gl2.rd], [ygom.GameResult.WIN.value])
    gl2.update_player([gl1.rating], [gl1.rd], [ygom.GameResult.LOSE.value])
    
    return gl1, gl2

def get_all_decks_ranked():
    '''Return a DataFrame with all decks ranked'''
    return ygom.pd.read_csv(DECK_RANK_FILE)

def find_deck_rating(deck_name, all_decks_ranked=None):
    if all_decks_ranked is None:
        all_decks_ranked = get_all_decks_ranked()
    deck = all_decks_ranked.loc[all_decks_ranked.deck == deck_name].iloc[0]
    return deck

def compute_all_scores(sort_by='elo'):
    '''Calcule le score Elo des decks étant donnés tous les matchs'''
    all_games = ygom.get_all_games()
    n_games = len(all_games)
    
    # Init score table
    all_scores = np.zeros((n_games, 6)) # elo1, elo2, gl1, gl2, rd1, rd2
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
        gl1, gl2 = compute_glicko([deck1.glicko, deck1.rd], [deck2.glicko, deck2.rd])
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
    all_games[['elo1','elo2','gl1','rd1','gl2','rd2']] = all_scores
    
    # Log new games
    log_to_file(all_games, logfile=ygom.GAME_HIST_FILE)
        
    # Write ranking file
    all_decks_ranked = sort_decks(all_decks_ranked, sort_by=sort_by)
    log_to_file(all_decks_ranked, logfile=DECK_RANK_FILE)

def compute_scores_last():
    '''calcule les scores à partir du match i (match à partir duquel 
    les scores sont absents par exemple)'''
    all_games = ygom.get_all_games()
    last_games = all_games.loc[ygom.pd.isnull(all_games.elo1)]
    n_last = len(last_games)
    
    all_decks_ranked = get_all_decks_ranked()
    for i in range(0,n_last):
        # Get game & decks
        game_i = last_games.iloc[i]
        deck1 = find_deck_rating(game_i.deck1, all_decks_ranked)
        deck2 = find_deck_rating(game_i.deck2, all_decks_ranked)






