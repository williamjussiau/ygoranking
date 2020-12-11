#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 22:46:11 2020

@author: william
"""

import ygoranking as ygo
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors
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
    win_rate, nwins, ngames = get_win_rate(deck_name)

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
    
    TODO
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
    
def show_bars(use_cm = False):
    """Affiche un graphique en barres, stylé"""
    all_decks = ygo.get_all_decks_ranked()
    n_decks = len(all_decks)
    
    ngames = all_decks.ngames.tolist()
    nwins = all_decks.nwins.tolist()
    nloss = all_decks.nloss.tolist()
    labels = all_decks.deck.tolist()
    scores = all_decks.elo.tolist()
    winrates = all_decks.winrate.tolist()
    
    # Setup
    fig, ax1 = plt.subplots()
    cmp = ['Reds', 'Blues', 'Greens_r']
    clr = ['tab:red', 'tab:blue', 'tab:green']
    alpha = 0.8
    
    # Colormap
    set_color = lambda data, clr: cm.get_cmap(clr)(colors.Normalize(vmin=min(data), vmax=max(data))(data))
    
    # ax1: number of games
    ax1.set_ylabel('Number of games', color='k')
    ax1.tick_params(axis='x', labelrotation=80)
    ax1.tick_params(axis='y', labelcolor='k')

    if use_cm:
        clg = set_color(nloss, cmp[1])
        clw = set_color(nwins, cmp[0])
    else:
        clg = clr[1]
        clw = clr[0]
        
    barg = ax1.bar(labels, nloss, bottom=nwins,
                   alpha=alpha, color=clg, edgecolor='k') 
    barw = ax1.bar(labels, nwins,
                   alpha=alpha, color=clw, edgecolor='k')

    # ax2: win rate
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('Winrate', color=clr[2])  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=clr[2])
    dx = 0.03
    ax2.set_ylim([0-dx, 1+dx])
    t = [i for i in range(0,n_decks)]
    # ax2.scatter(t, winrates, marker='o', c=t, cmap=cmp[2])
    ax2.plot(t, winrates, linestyle=':', marker='o', color=clr[2], drawstyle='default') # drawstyle='steps-mid'
    ax2.hlines(0.5, 
               xmin=ax2.get_xlim()[0]+1, xmax=ax2.get_xlim()[1]-1,
               color=clr[2], linestyle='--')
    # i = 0
    # for rect in barg:
    #     height = rect.get_height()
    #     ax1.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(scores[i]), ha='center', va='bottom')
    #     i+=1

    fig.tight_layout()
    plt.show()
    
def show_map():
    """Affiche une matrice des matchs joués et gagnés de deck à deck..."""
    all_decks = ygo.get_all_decks_ranked()
    n_decks = len(all_decks)
    labels = all_decks.deck.tolist()
    t = [i for i in range(0, n_decks)]
    all_games = ygo.get_all_games()
    n_games = len(all_games)
    
    # Initialize
    games_map = 0 * np.eye(n_decks, dtype=int)
    wins_map = 0 * np.eye(n_decks, dtype=int)
    winrate_map = 0 * np.eye(n_decks)
    # games_map = np.random.randn(n_decks, n_decks)
    
    for i in range(0, n_games):
        game_i = all_games.iloc[i]
        deck1_idx = labels.index(game_i.deck1)
        deck2_idx = labels.index(game_i.deck2)
        wins_map[deck2_idx, deck1_idx] += 1
        
    games_map = wins_map + wins_map.T;    
    games_map[games_map == 0] = -1
    winrate_map = wins_map / games_map
    winrate_map[games_map==-1] = -np.inf
    np.fill_diagonal(winrate_map, 0.5)

    # Setup figure
    fig = plt.figure()
    ax = plt.gca()
    
    # Colormap & show matrix
    normalizer = colors.DivergingNorm(vcenter=0.5, vmin=0, vmax=np.max(winrate_map))
    cax = ax.matshow(winrate_map, cmap=cm.get_cmap('RdYlGn'),
                     norm=normalizer) # coolwarm, bwr, RdYlGn
    
    # vmin = np.min(games_map), vmax=np.max(games_map)
    # Ticks
    ax.set_xlabel('Winner')
    ax.set_ylabel('Loser')
    ax.set_xticks(t)
    ax.set_yticks(t)
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.tick_params(axis='x', labelrotation=90)
    ax.tick_params(axis='y', labelrotation=0)
    # ax.grid()
    fig.colorbar(cax)
    
    # Show
    fig.tight_layout()
    plt.show()
    







