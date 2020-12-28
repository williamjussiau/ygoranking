#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 22:46:11 2020

@author: william
"""

import ygoranking as ygor
import ygomanagement as ygom

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates


# Afficher les meilleurs/pires matchups d'un deck
# Afficher la progression de tous les decks

def get_games(deck_name):
    """Extrait les matchs du deck donné"""
    all_games = ygom.pd.read_csv(ygom.GAME_HIST_FILE)
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
    dates = ['']*ngames
    sc = ygom.pd.DataFrame(data=scores)
    for i in range(0, ngames):
        dates[i] = gm.iloc[i].date
        if(gm.deck1.iloc[i]==deck_name):
            # Deck has won this game
            sc.iloc[i].elo = gm.iloc[i].elo1
            sc.iloc[i].glicko = gm.iloc[i].gl1
            sc.iloc[i].rd = gm.iloc[i].rd1
        else:
            # Deck has lost this game
            sc.iloc[i].elo = gm.iloc[i].elo2
            sc.iloc[i].glicko = gm.iloc[i].gl2
            sc.iloc[i].rd = gm.iloc[i].rd2
    # Add dates to dataframe
    sc['date'] = dates
    # Prepend initial scores
    initial_scores = ygom.pd.DataFrame({'elo': [ygor.elo_0],
                                       'glicko': [ygor.glicko_0],
                                       'rd': [ygor.rd_0],
                                       'date': [ygom.find_deck(deck_name).date]})
    sc = ygom.pd.concat([initial_scores, sc], ignore_index=True)
    return sc

def get_win_rate(deck_name):
    """Calcule le winrate-so-far d'un deck
    C'est-à-dire pour chaque match joué, le winrate actuel en prenant tous
    les matchs précédents"""
    gm = get_games(deck_name)
    ngames = len(gm)
    dates = ['']*ngames
    win_rate = ygom.pd.DataFrame(data={'wr': np.zeros([ngames,])})
    nwins = 0
    for i in range(0, ngames):
        dates[i] = gm.iloc[i].date
        if(gm.deck1.iloc[i]==deck_name):
            # Deck has won this game
            nwins += 1
        # Else deck has lost this game
        win_rate.iloc[i].wr = nwins / (i+1)
    # Add dates to dataframe
    win_rate['date'] = dates
    # Preprend initial win rate (default: nan)
    wr_0 = ygom.pd.DataFrame({'wr': [np.nan],
                              'date':[ygom.find_deck(deck_name).date]})
    win_rate = ygom.pd.concat([wr_0, win_rate], ignore_index=True)
    return win_rate, nwins, ngames

def show_deck_stats(deck_name, fig=None, ax=None, cycler=None):  
    """
    Affiche les stats du deck donné
    Les stats comprennent : WR, progression de score...?
    """
    # Process input
    newfig = fig is None and ax is None
    
    # Scores & win rate
    scores = get_scores(deck_name)
    win_rate, nwins, ngames = get_win_rate(deck_name)

    # Formatter and locator
    dateformatter = mdates.DateFormatter("%d-%b-%y")
    datelocator = mdates.DayLocator(interval=5) ## show each day/month...

    # Plot utilities
    # xx = np.linspace(0, ngames, ngames+1)
    xx = [datetime.strptime(strdate,"%d/%m/%Y") for strdate in scores.date]
    line_elo0 = [ygor.elo_0 for d in xx]
    line_wr0 = [0.5 for d in xx]
    deck_title = 'Deck: ' + deck_name
    
    def mkdateaxis(ax, ylabel, formatter=dateformatter, locator=datelocator):
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(locator)
        ax.tick_params(axis='x', labelrotation=45)    
        ax.set_xlabel('Dates of games')
        ax.set_ylabel(ylabel)
        if newfig:
            ax.legend()
            ax.set_title(deck_title)
        ax.grid()
    
    # Plot scores
    if newfig:
        fig, ax = plt.subplots()        
        ax.plot(xx, scores.elo, color='g', label='elo', marker='.')
        ax.plot(xx, scores.glicko, color='b', label='glicko', marker='.')
        nsig = 1.96
        ax.plot(xx, scores.glicko + nsig*scores.rd, linestyle=':', color='b')
        ax.plot(xx, scores.glicko - nsig*scores.rd, linestyle=':', color='b')
        ax.fill(np.concatenate([xx, xx[::-1]]),
                 np.concatenate([scores.glicko - nsig * scores.rd,
                                 (scores.glicko + nsig * scores.rd)[::-1]]),
                 alpha=0.3, label='+-2rd')
        ax.plot(xx, line_elo0, color='r', linestyle='--')
        ax.axis([xx[0], xx[-1], 1000, 2000])
        mkdateaxis(ax, ylabel='Score')
    
    # Plot win rate
    if newfig:
        fig, ax = plt.subplots()
        ax.plot(xx, line_wr0, color='r', linestyle='--')
        ax.axis([xx[0], xx[-1], -0.05, 1.05])
    ax.plot(xx, win_rate.wr, label='Win rate', marker='o')
    mkdateaxis(ax, ylabel='Win rate')
    
def show_all_decks(up_to=None):
    """
    Affiche la progression du score elo de tous les decks au cours du temps
    Il faut itérer habilement sur show_deck_stats()
    """
    # Retrieve decks
    all_decks = ygor.get_all_decks_ranked()
    if up_to is None:
        n_decks = len(all_decks)
    else:
        n_decks = up_to
    
    decks_legend = []
    fig, ax = plt.subplots()
    default_cycler = (plt.cycler(linestyle=['-','--',':', '-.']) * plt.rcParams['axes.prop_cycle'])
    ax.set_prop_cycle(default_cycler)
    ax.grid()
    for i in range(0, n_decks):
        show_deck_stats(all_decks.deck[i], fig=fig, ax=ax, cycler=default_cycler)
        decks_legend.append(all_decks.deck[i])
    ax.grid()
    ax.legend(decks_legend, loc='best', fontsize='x-small', ncol=3)
    
def complete_ranking():
    pass
#     """Augmente le classement des decks avec quelques infos
#     Notamment : winrate, nombre de matchs"""
#     # Get decks
#     # all_decks = ygor.sort_decks()
#     # n_decks = len(all_decks)
    
#     # # Init new variables
#     # deck_stats = np.zeros((n_decks, 4)) # winrates, ngames, nwins, nloss
#     # WINRATES = n_decks*[0]
#     # NGAMES = n_decks*[0]
#     # NWINS = n_decks*[0]
#     # NLOSS = n_decks*[0]
    
#     # # Loop on all decks
#     # for i in range(0, n_decks):
#     #     deck = all_decks.iloc[i]
#     #     deck_name = deck.deck
#     #     wr, nwins, ngames = get_win_rate(deck_name)
#     #     nloss = ngames - nwins
#     #     wr = wr.iloc[-1,0]
#     #     deck_stats[i,:] = wr, ngames, nwins, nloss
#     #     # WINRATES[i] = wr
#     #     # NGAMES[i] = ngames
#     #     # NWINS[i] = nwins
#     #     # NLOSS[i] = nloss
    
#     # # Append to all decks
#     # all_decks[['winrate','ngames','nwins','nloss']] = deck_stats
#     # # all_decks['ngames'] = NGAMES
#     # # all_decks['nwins'] = NWINS
#     # # all_decks['nloss'] = NLOSS

#     # # Log new data
#     # ygom.log_to_file(all_decks)
#     # return all_decks
#     pass
    
def show_bars(use_cm = False):
    """Affiche un graphique en barres, stylé"""
    all_decks = ygor.get_all_decks_ranked()
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
    set_color = lambda data, clr: cm.get_cmap(clr) (colors.Normalize(vmin=min(data), vmax=max(data))(data))
    
    # ax1: number of games
    ax1.set_ylabel('Number of games', color='k')
    ax1.tick_params(axis='x', labelrotation=90)
    ax1.tick_params(axis='y', labelcolor='k')

    if use_cm:
        clg = set_color(nloss, cmp[1])
        clw = set_color(nwins, cmp[0])
    else:
        clg = clr[1]
        clw = clr[0]
        
    barg = ax1.bar(labels, nloss, bottom=nwins, alpha=alpha, color=clg, edgecolor='k') 
    barw = ax1.bar(labels, nwins, alpha=alpha, color=clw, edgecolor='k')
    
    # Color labels depending on owner
    owners_clr = assign_color_per_player(labels)
    color_ticks_by_player(ax1, owners_clr, direction='x')

    # ax2: win rate
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('Winrate', color=clr[2])  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=clr[2])
    dx = 0.03
    ax2.set_ylim([0-dx, 1+dx])
    t = [i for i in range(0,n_decks)]
    ax2.plot(t, winrates, linestyle=':', marker='o', color=clr[2], drawstyle='default') # drawstyle='steps-mid'
    ax2.hlines(0.5, 
               xmin=ax2.get_xlim()[0]+1, xmax=ax2.get_xlim()[1]-1,
               color=clr[2], linestyle='--')
    
    # Add text on top of bar
    # i = 0
    # for rect in barg:
    #     height = rect.get_height()
    #     ax1.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(scores[i]), ha='center', va='bottom')
    #     i+=1

    fig.tight_layout()
    plt.show()
    
def compute_map():
    """Compute games map"""
    all_decks = ygor.get_all_decks_ranked()
    n_decks = len(all_decks)
    labels = all_decks.deck.tolist()
    all_games = ygom.get_all_games()
    n_games = len(all_games)
    
    # Initialize
    games_map = 0 * np.eye(n_decks, dtype=int)
    wins_map = 0 * np.eye(n_decks, dtype=int)
    winrate_map = 0 * np.eye(n_decks)
    
    # Compute number of games per pair of decks
    for i in range(0, n_games):
        game_i = all_games.iloc[i]
        wins_map[labels.index(game_i.deck1), labels.index(game_i.deck2)] += 1
    # Symmetrize
    games_map = wins_map + wins_map.T
    # Cancel no-match-ups (avoid division by 0 at next step)
    games_map[games_map == 0] = -1
    # Compute winrate : number of wins on number of games
    winrate_map = wins_map / games_map
    winrate_map[games_map==-1] = -np.inf
    
    # Grey out decks with same owner (including diagonal)
    game_is_impossible = np.zeros((n_decks, n_decks), dtype=int)
    for i in range(0, n_decks):
        owner_i = ygom.find_owner(labels[i])
        for j in range(0, i):
            owner_j = ygom.find_owner(labels[j])
            if owner_i==owner_j:
                game_is_impossible[i, j] = 1
    game_is_impossible = game_is_impossible + game_is_impossible.T
    np.fill_diagonal(game_is_impossible, 1)
    return winrate_map, game_is_impossible

def show_this_map(this_map=None, cmap=None):
    """Display games map"""
    if this_map is None:
        winrate_map, game_is_impossible = compute_map()
        show_winrate = True
    else:
        winrate_map=this_map
        show_winrate = False
    
    all_decks = ygor.get_all_decks_ranked()
    labels = all_decks.deck.tolist()
    n_decks = len(labels)
    t = [i for i in range(0, n_decks)]

    # Setup figure
    fig = plt.figure()
    ax = plt.gca()
    
    # Colormap & overlay matrices (genuine games & impossible games greyed out)
    normalizer = colors.DivergingNorm(vcenter=0.5, vmin=0, vmax=np.max(winrate_map))
    if cmap is None:
        cmap = 'RdYlGn' # coolwarm, bwr, RdYlGn
    cax = ax.matshow(winrate_map, cmap=cm.get_cmap(cmap),
                     norm=normalizer, alpha=1) 
    if show_winrate:
        ax.matshow(game_is_impossible, alpha=0.1, cmap=cm.get_cmap('binary'))

    # Ticks
    ax.set_xlabel('Loser')
    ax.set_ylabel('Winner')
    ax.set_xticks(t)
    ax.set_yticks(t)
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.tick_params(axis='x', labelrotation=90)
    ax.tick_params(axis='y', labelrotation=0)
    fig.colorbar(cax)
    
    # Color labels depending on owner
    owners_clr = assign_color_per_player(labels)
    color_ticks_by_player(ax, owners_clr, direction='x')
    color_ticks_by_player(ax, owners_clr, direction='y')
    
    # Show
    # fig.tight_layout()
    plt.show()
        
def assign_color_per_player(decks):
    players = np.array([ygom.find_deck(dk).owner for dk in decks])
    players_base = np.array(['Pierre', 'JRE', 'William'])
    players_baseclr = np.array(['tab:cyan','tab:green','tab:orange'])
    # owners_clr = [0]*len(owners)
    # for i in range(0, len(owners)):
    #     for j in range(0, len(owners_base)):
    #         if owners[i]==owners_base[j]:
    #             owners_clr[i] = owners_baseclr[j]
    # return owners_clr
    # or with np.array:
    return players_baseclr[np.where(players[:,None]==players_base[None])[1]].tolist()
    # or
    # owners_baseclr[np.argmax(owners[:,None]==owners_base[None], axis=1)]

def color_ticks_by_player(ax, color_list, direction='x'):
    if direction=='x':
        thoseticks = ax.get_xticklabels()
    if direction=='y':
        thoseticks = ax.get_yticklabels()
    for ticklabel, tickcolor in zip(thoseticks, color_list):
        ticklabel.set_color(tickcolor)

def show_players():
    """Affiche les stats d'un joueur : nombre de matchs joués,
    gagnés/perdus, nombre de decks"""
    all_decks = ygor.get_all_decks_ranked()
    all_players = np.unique(np.array(all_decks.owner))
    players = ygom.pd.DataFrame()
    for i in range(0, len(all_players)):
        player_i = all_decks[all_decks.owner == all_players[i]]
        player_dict = dict({'name': all_players[i],
                            'ndecks': len(player_i),
                            'ngames': sum(player_i.ngames),
                            'nwins': sum(player_i.nwins),
                            'nloss': sum(player_i.nloss),
                            # 'maxelo': max(player_i.elo),
                            # 'minelo': min(player_i.elo),
                            # 'maxglicko': max(player_i.glicko),
                            # 'minglicko': min(player_i.glicko),
                            'avgwinrate': sum(player_i.nwins)/sum(player_i.ngames)})
        players = players.append(ygom.pd.DataFrame(data=[player_dict]))
    players.reset_index(drop=True, inplace=True)
    return players

def suggest_new_matchup(player1=None, player2=None):
    all_decks = ygor.get_all_decks_ranked()
    labels = all_decks.deck.tolist()
    
    winrate_map, game_is_impossible = compute_map()
    game_is_possible = 1-game_is_impossible
    matchup_undone = np.zeros(winrate_map.shape, dtype=int)
    matchup_undone[np.isinf(winrate_map)] = 1
    # matchup_undone[winrate_map>=0] = 0
    
    free_matchups = matchup_undone * game_is_possible
    # show_this_map(free_matchups)
    
    if player1 is None and player2 is None:
        filter_by_player = np.ones(winrate_map.shape, dtype=int)
    else:
        filter_by_player = np.zeros(winrate_map.shape, dtype=int)
        for i in range(0, len(winrate_map)):
            for j in range(0, i):
                deck1_owner = ygom.find_owner(labels[i])
                deck2_owner = ygom.find_owner(labels[j])
                if ((deck1_owner==player1 or deck1_owner==player2) 
                    and (deck2_owner==player1 or deck2_owner==player2)):
                        filter_by_player[i,j] = 1
                    
    # show_this_map(filter_by_player)
    new_matchup_between = free_matchups * filter_by_player
    show_this_map(new_matchup_between)
    
    
    
    
    






