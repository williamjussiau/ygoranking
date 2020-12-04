#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 22:46:11 2020

@author: william
"""

import ygoranking as ygo
import matplotlib.pyplot as plt
import numpy as np

# Afficher les meilleurs/pires matchups d'un deck
# Afficher une matrice des matchs comme sur l'excel
# Afficher la progression de tous les decks

def get_games(deck_name):
    """
    Extrait les matchs du deck donné
    """
    all_games = ygo.pd.read_csv(ygo.GAME_HIST_FILE)
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
    # Prepend initial scores
    initial_scores = ygo.pd.DataFrame({'elo': [ygo.elo_0],
                                       'glicko': [ygo.glicko_0],
                                       'rd': [ygo.rd_0]})
    sc = ygo.pd.concat([initial_scores, sc], ignore_index=True)
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
    # Preprend initial win rate (default: nan)
    wr_0 = ygo.pd.DataFrame({'wr': [np.nan]})
    win_rate = ygo.pd.concat([wr_0, win_rate], ignore_index=True)
    return win_rate, nwins, ngames

def show_deck_stats(deck_name):
    """
    Affiche les stats du deck donné
    Les stats comprennent : WR, progression de score, meilleur/pire match-up
    """
    # Scores
    scores = get_scores(deck_name)
    ngames = len(scores) - 1
    # Win rate
    win_rate = get_win_rate(deck_name)

    # Plot utilities
    xx = np.linspace(0, ngames, ngames+1)
    deck_title = 'Deck: ' + deck_name
    
    # Plot scores
    plt.figure()
    plt.plot(xx, scores.elo,
             color='g', label='elo', marker='.')
    plt.plot(xx, scores.glicko,
             color='b', label='glicko', marker='.')
    plt.plot(xx, scores.glicko + 2*scores.rd,
             linestyle=':', color='b')
    plt.plot(xx, scores.glicko - 2*scores.rd,
             linestyle=':', color='b')
    plt.fill(np.concatenate([xx, xx[::-1]]),
             np.concatenate([scores.glicko - 1.9600 * scores.rd,
                             (scores.glicko + 1.9600 * scores.rd)[::-1]]),
             alpha=0.3, label='+-2rd')
    plt.hlines(ygo.elo_0, 0, ngames, color='r', linestyle='--')
    plt.xlabel('Number of games')
    plt.ylabel('Score')
    plt.legend()
    plt.axis([0, ngames, 1200, 1800])
    plt.title(deck_title)
    plt.grid()
    
    # Plot win rate
    plt.figure()
    plt.plot(win_rate.wr, label='Win rate', marker='o')
    plt.xlabel('Number of games')
    plt.ylabel('Win rate')
    plt.hlines(0.5, 0, ngames, color='r', linestyle='--')
    plt.axis([0, ngames, 0, 1])
    plt.legend()
    plt.title(deck_title)
    plt.grid()
    
def show_all_elo():
    """
    Affiche la progression du score elo de tous les decks au cours du temps
    C'est assez different de ce qui est fait dans show_deck_stats car on
    veut ici voir la totalite des matchs et l'evolution du score de chaque
    deck (i.e. si le deck ne joue pas, son score reste constant)
    """
    # Retrieve decks
    all_decks = ygo.get_all_decks()
    n_decks = len(all_decks)
    
    # Retrieve games
    all_games = ygo.get_all_games()
    n_games = len(all_games)
    
    # Make score vectors
    elo_scores = np.zeros([n_games, n_decks])
    n_decks = len(all_decks)
    for i in range(0, n_decks):
        print(i)
    
def complete_ranking():
    """Augmente le classement des decks avec quelques infos
    Notamment : winrate, nombre de matchs"""
    # Get decks
    all_decks = ygo.sort_decks()
    n_decks = len(all_decks)
    
    # Init new variables
    WINRATES = n_decks*[0]
    NGAMES = n_decks*[0]
    NWINS = n_decks*[0]
    NLOSS = n_decks*[0]
    
    # Loop on all decks
    for i in range(0, n_decks):
        deck = all_decks.iloc[i]
        deck_name = deck.deck
        wr, nwins, ngames = get_win_rate(deck_name)
        nloss = ngames - nwins
        wr = wr.iloc[-1,0]
        WINRATES[i] = wr
        NGAMES[i] = ngames
        NWINS[i] = nwins
        NLOSS[i] = nloss
    
    # Append to all decks
    all_decks['winrate'] = WINRATES
    all_decks['ngames'] = NGAMES
    all_decks['nwins'] = NWINS
    all_decks['nloss'] = NLOSS

    # Log new data
    ygo.log_to_file(all_decks)
    return all_decks
    
def show_bars():
    """Affiche un graphique en barres, stylé"""
    all_decks = complete_ranking()
    n_decks = len(all_decks)
    
    ngames = all_decks.ngames.tolist()
    nwins = all_decks.nwins.tolist()
    nloss = all_decks.nloss.tolist()
    labels = all_decks.deck.tolist()
    scores = all_decks.elo.tolist()
    winrates = all_decks.winrate.tolist()
    
    # Setup
    fig, ax1 = plt.subplots()
    color1 = 'tab:blue'
    color2 = 'tab:red'
    color3 = 'tab:green'
    alpha = 0.75
    
    # ax1: number of games
    ax1.set_ylabel('Number of games', color=color1)
    ax1.tick_params(axis='x', labelrotation=75)
    ax1.tick_params(axis='y', labelcolor=color1)
    barg = ax1.bar(labels, ngames, alpha=alpha, color=color1) 
    barw = ax1.bar(labels, nwins, alpha=alpha, color=color2)

    # ax2: win rate
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('Winrate', color=color3)  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=color3)
    dx = 0.02
    ax2.set_ylim([0-dx, 1+dx])
    ax2.plot(winrates, marker='o', linestyle='None', color=color3)
    ax2.hlines(0.5, 
               xmin=ax2.get_xlim()[0]+1, xmax=ax2.get_xlim()[1]-1,
               color=color3, linestyle=':')
    
    # i = 0
    # for rect in bar2:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width()/2.0, height, '%5.2f' % winrates[i], ha='center', va='bottom')
    #     i+=1
        
    # i = 0
    # for rect in barg:
    #     height = rect.get_height()
    #     ax1.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(scores[i]), ha='center', va='bottom')
    #     i+=1

    fig.tight_layout()
    plt.show()
    
    
    
    







