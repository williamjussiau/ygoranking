#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 22:46:11 2020

@author: william
"""

import ygoranking as ygo
import matplotlib.pyplot as plt
import numpy as np

# Afficher la progression d'un deck au cours du temps
# Afficher les taux de victoire d'un deck
# Afficher les meilleurs/pires matchups d'un deck
# Winrate so far

# Afficher une matrice des matchs comme sur l'excel
# Afficher la progression de tous les decks

def get_games(deck_name):
    """
    Extrait les matchs du deck donné
    """
    all_games = ygo.pd.read_csv(ygo.gameHistoryFile)
    played_games = all_games.loc[(all_games.deck1 == deck_name) |
                               (all_games.deck2 == deck_name)]
    return played_games

def get_scores(deck_name):
    """Extrait la progression (score) du deck donné"""
    gm = get_games(deck_name)
    ngames = len(gm)
    scores = {'elo': np.zeros([ngames,]),
              'glicko': np.zeros([ngames,]),
              'rd': np.zeros([ngames,])}
    sc = ygo.pd.DataFrame(data=scores)
    for i in range(0, ngames):
        if(gm.deck1.iloc[i]==deck_name):
            # Deck has won this game
            sc.iloc[i].elo = gm.iloc[i].elo1
            sc.iloc[i].glicko = gm.iloc[i].glicko1
            sc.iloc[i].rd = gm.iloc[i].rd1
        else:
            # Deck has lost this game
            sc.iloc[i].elo = gm.iloc[i].elo2
            sc.iloc[i].glicko = gm.iloc[i].glicko2
            sc.iloc[i].rd = gm.iloc[i].rd2
    return sc

def get_win_rate(deck_name):
    """Calcule le winrate-so-far d'un deck
    C'est-à-dire pour chaque match joué, le winrate actuel en prenant tous
    les matchs précédents"""
    gm = get_games(deck_name)
    ngames = len(gm)
    win_rate = ygo.pd.DataFrame(data={'wr': np.zeros([ngames,])})
    nwins = 0
    for i in range(0, ngames):
        if(gm.deck1.iloc[i]==deck_name):
            # Deck has won this game
            nwins += 1
        # Else deck has lost this game
        win_rate.iloc[i].wr = nwins / (i+1)
    return win_rate

def show_deck_stats(deck_name):
    """
    Affiche les stats du deck donné
    Les stats comprennent : WR, progression de score, meilleur/pire match-up
    """
    scores = get_scores(deck_name)
    win_rate = get_win_rate(deck_name)
    ngames = len(scores)
    xx = np.linspace(1, ngames, ngames)
    
    # Scores
    plt.figure()
    plt.plot(xx, scores.elo, color='g')
    plt.plot(xx, scores.glicko, color='b')
    plt.plot(xx, scores.glicko + 2*scores.rd, linestyle='--', color='b')
    plt.plot(xx, scores.glicko - 2*scores.rd, linestyle='--', color='b')
    plt.fill(np.concatenate([xx, xx[::-1]]),
             np.concatenate([scores.glicko - 1.9600 * scores.rd,
                             (scores.glicko + 1.9600 * scores.rd)[::-1]]), alpha=0.3)
    # Win rate
    plt.figure()
    plt.plot(win_rate.wr)
    
def show_all_stats():
    pass
        



