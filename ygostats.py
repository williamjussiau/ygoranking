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
import matplotlib.patches as patch
from matplotlib import colors
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import time

## Getters ###################################################################
def get_games(deck_name):
    """Extract games of given deck"""
    all_games = ygom.get_all_games()
    played_games = all_games.loc[(all_games.deck1 == deck_name) |
                               (all_games.deck2 == deck_name)]
    return played_games

def get_scores(deck_name):
    """Extract deck progression (scores, winrate)"""
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
                                       'date': [ygom.find_deck(deck_name).date
                                                ]})
    sc = ygom.pd.concat([initial_scores, sc], ignore_index=True)
    return sc

def get_win_rate(deck_name):
    """Compute winrate of deck for each game they played (up-to)"""
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

## Utilities #################################################################
def convert_to_datetime(strarray):
    """Convert string to datetime"""
    return [datetime.strptime(strdate,"%d/%m/%Y") for strdate in strarray]

def convert_to_str(datearray):
    """Convert datetime to string ---"""
    return [date.strftime("%d-%b-%y") for date in datearray]

def make_date_axis(ax, ylabel, newfig=False, title=None,
                   formatter=None, locator=None,
                   dayinterval=5):
    """Set axes with dates"""
    # Formatter and locator
    if formatter is None:
        formatter = mdates.DateFormatter("%d-%b-%y")
    if locator is None:
        locator = mdates.DayLocator(interval=dayinterval)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)
    ax.tick_params(axis='x', labelrotation=45)    
    ax.set_xlabel('Dates of games')
    ax.set_ylabel(ylabel)
    if newfig:
        ax.legend()
        ax.set_title(title)
    ax.grid()
    
def assign_color_per_player(decks):
    """Assign different color to each player"""
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
    return players_baseclr[
        np.where(players[:,None]==players_base[None])[1]
        ].tolist()
    # or
    # owners_baseclr[np.argmax(owners[:,None]==owners_base[None], axis=1)]

def color_ticks_by_player(ax, color_list, direction='x'):
    """Set tick color depending on player"""
    if direction=='x':
        thoseticks = ax.get_xticklabels()
    if direction=='y':
        thoseticks = ax.get_yticklabels()
    for ticklabel, tickcolor in zip(thoseticks, color_list):
        ticklabel.set_color(tickcolor)
        
def compute_games_map():
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
    
## Display ###################################################################
def show_deck_stats(deck_name, fig=None, ax=None, cycler=None):  
    """Display stats of given deck (winrate, scores)"""
    # Process input
    newfig = fig is None and ax is None
    
    # Scores & win rate
    scores = get_scores(deck_name)
    win_rate, nwins, ngames = get_win_rate(deck_name)

    # Plot utilities
    # xx = np.linspace(0, ngames, ngames+1)
    xx = convert_to_datetime(scores.date)
    line_elo0 = [ygor.elo_0 for d in xx]
    line_wr0 = [0.5 for d in xx]
    deck_title = 'Deck: ' + deck_name
    
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
        make_date_axis(ax, ylabel='Score', newfig=newfig,
                       title=deck_title)
    
    # Plot win rate
    if newfig:
        fig, ax = plt.subplots()
        ax.plot(xx, line_wr0, color='r', linestyle='--')
        ax.axis([xx[0], xx[-1], -0.05, 1.05])
    ax.plot(xx, win_rate.wr, label='Win rate', marker='o')
    make_date_axis(ax, ylabel='Win rate', newfig=False, title=deck_title)
    
def show_all_decks(up_to=None):
    """Show progression of all decks scores through time"""
    # Retrieve decks
    all_decks = ygor.get_all_decks_ranked()
    if up_to is None:
        n_decks = len(all_decks)
    else:
        n_decks = up_to
    
    decks_legend = []
    fig, ax = plt.subplots()
    default_cycler = (plt.cycler(linestyle=['-','--',':', '-.']) 
                      * plt.rcParams['axes.prop_cycle'])
    ax.set_prop_cycle(default_cycler)
    ax.grid()
    for i in range(0, n_decks):
        show_deck_stats(all_decks.deck[i], fig=fig, ax=ax, 
                        cycler=default_cycler)
        decks_legend.append(all_decks.deck[i])
    ax.grid()
    ax.legend(decks_legend, loc='best', fontsize='x-small', ncol=3)
    
def show_games_frequency(mode=None):
    """Plot Github-like table of games frequency"""
    all_games = ygom.get_all_games()
    dates, uidx = np.unique(all_games.date, return_index=True)
    uidx = np.sort(uidx)
    dates = np.array(all_games.date[uidx])
    games_per_date = np.zeros(shape=dates.shape, dtype=int)
    jdate = 0
    # Loop on games
    for i in range(0, len(all_games)):
        game_i = all_games.iloc[i]
        # If dates do not correspond, increment date counter
        if game_i.date != dates[jdate]:
            jdate += 1
        # Note: this works when dates are sorted
        games_per_date[jdate] += 1
    dates = convert_to_datetime(dates)
        
    # Display
    ndpw = int(7) # number of days per week
    if mode=='':
        fig, ax = plt.subplots()
        ax.bar(dates, games_per_date, color='g',
               label='Game count')
        make_date_axis(ax, newfig=True, 
                       ylabel='Number of games', title='Games frequency',
                       dayinterval=7)
    else:
        first_day = dates[0]
        prev_monday = first_day - timedelta(days=first_day.weekday())
        
        last_day = dates[-1]
        next_monday = last_day + timedelta(days=7-last_day.weekday())
        
        ndays = next_monday - prev_monday
        nweeks = int(np.ceil(ndays.days / ndpw)) # should be an int already
        
        # 1 column = 1 week, 1 row = 1 weekday
        gf_map = np.zeros(shape=(ndpw, nweeks), dtype=int)
        for i in range(0, len(dates)):
            date_idx = (dates[i] - prev_monday).days
            date_sub = np.unravel_index(date_idx, gf_map.shape, order='F') #FC
            gf_map[date_sub] = games_per_date[i]
        fig, ax = plt.subplots()
        # cax = ax.matshow(gf_map, cmap=cm.get_cmap('Greens'))
        cax = plt.pcolormesh(gf_map, 
                             edgecolors='w', cmap=cm.get_cmap('Greens'))
        ax.set_aspect('equal')
        ax.invert_yaxis()
        # Label days (y)
        ax.set_ylabel('Days')
        ax.set_yticks([i+0.5 for i in range(0, ndpw)])
        ax.set_yticklabels(['Monday',
                            'Tuesday',
                            'Wednesday',
                            'Thurdsay',
                            'Friday',
                            'Saturday',
                            'Sunday']);
        # Label weeks with date (x)
        ax.set_xlabel('Weeks')
        ax.set_xticks([i+0.5 for i in range(0, nweeks)])
        mondays_dates = convert_to_str([prev_monday + i*timedelta(days=ndpw) 
                                        for i in range(0, nweeks)])
        ax.set_xticklabels(mondays_dates)
        ax.tick_params(axis='x', labelrotation=45, 
                       bottom=True, top=False, labelbottom=True, labeltop=False)
        ax.set_title('Games frequency')
        fig.colorbar(cax)
    
def show_bars(use_cm = False, sort_by='elo'):
    """Show stylish bar graph with scores"""
    all_decks = ygor.get_all_decks_ranked()
    n_decks = len(all_decks)
    
    ngames = all_decks.ngames.tolist()
    nwins = all_decks.nwins.tolist()
    nloss = all_decks.nloss.tolist()
    labels = all_decks.deck.tolist()
    scores_elo = all_decks.elo.tolist()
    scores_glicko = all_decks.glicko.tolist()
    scores_glickord = all_decks.rd.tolist()
    winrates = all_decks.winrate.tolist()
        
    # Setup
    fig, ax1 = plt.subplots()
    cmp = ['Reds', 'Blues', 'Greens_r']
    clr = ['tab:red', 'tab:blue', 'tab:green']
    alpha = 0.8
    
    # ax1: number of games
    ax1.set_ylabel('Number of games', color='k')
    ax1.tick_params(axis='x', labelrotation=90)
    ax1.tick_params(axis='y', labelcolor='k')

    if use_cm:
        set_color = lambda data, clr: cm.get_cmap(clr) (colors.Normalize(
        vmin=min(data), vmax=max(data))(data))
        clg = set_color(nloss, cmp[1])
        clw = set_color(nwins, cmp[0])
    else:
        clg = clr[1]
        clw = clr[0]
        
    barg = ax1.bar(labels, nloss, bottom=nwins, alpha=alpha, color=clg, 
                   edgecolor='k') 
    barw = ax1.bar(labels, nwins, alpha=alpha, color=clw, 
                   edgecolor='k')
        
    # Color labels depending on owner
    owners_clr = assign_color_per_player(labels)
    color_ticks_by_player(ax1, owners_clr, direction='x')

    # ax2: win rate
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('Winrate', color=clr[2])  # already handled xlabel ax1
    ax2.tick_params(axis='y', labelcolor=clr[2])
    dx = 0.03
    ax2.set_ylim([0-dx, 1+dx])
    t = [i for i in range(0,n_decks)]
    ax2.plot(t, winrates, linestyle=':', marker='o', color=clr[2], 
             drawstyle='default') # drawstyle='steps-mid'
    ax2.hlines(0.5, 
               xmin=ax2.get_xlim()[0]+1, xmax=ax2.get_xlim()[1]-1,
               color=clr[2], linestyle='--')

    
    # Add text on top of bar
    for i, rect in enumerate(barg):
        height = max(ngames)*1.07
        if sort_by is 'elo':
            txt = str(scores_elo[i])
        else:
            txt = str(scores_glicko[i]) #+ ' ' + '(' + str(scores_glickord[i]) + ')'
        #rect.get_height() + barw.get_children()[i].get_height()
        ax1.text(rect.get_x() + rect.get_width()/2.0, 
                 height, '%s' % txt, ha='center', va='bottom',
                 fontsize=8, rotation=45, verticalalignment='center')

    fig.tight_layout()
    plt.show()
    
def show_scores(boxplot=True, step=False):
    """Show scores graph with different options (box, whiskers...)"""
    all_decks = ygor.get_all_decks_ranked()
    n_decks = len(all_decks)
    
    # ngames = all_decks.ngames.tolist()
    # nwins = all_decks.nwins.tolist()
    # nloss = all_decks.nloss.tolist()
    labels = all_decks.deck.tolist()
    scores_elo = all_decks.elo
    scores_glicko = all_decks.glicko
    scores_rd = all_decks.rd
    # winrates = all_decks.winrate.tolist()
    xx = list(range(0, n_decks))
        
    # Setup
    fig, ax1 = plt.subplots()
    clr = ['tab:red', 'tab:blue', 'tab:green']
    alpha = 0.8
    
    # ax1: number of games
    ax1.set_ylabel('Elo score', color=clr[1])
    ax1.tick_params(axis='x', labelrotation=90)
    ax1.tick_params(axis='y', labelcolor=clr[1])
    
    ax1.scatter(labels, scores_elo, alpha=alpha, color=clr[1], edgecolor='k') 

    clg = clr[1]
    clw = clr[0]
        
    # Color labels depending on owner
    owners_clr = assign_color_per_player(labels)
    color_ticks_by_player(ax1, owners_clr, direction='x')

    # ax2: glicko
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel('Glicko score', color=clw)  # already handled xlabel ax1
    ax2.tick_params(axis='y', labelcolor=clw)
    
    if boxplot:
        n_sample = 10000
        # randvec = np.random.randn(n_sample, n_decks)
        # scores_samples = np.zeros(shape=(n_sample, n_decks))
        # for i in range(0, n_decks):
        #     scores_samples[:,i] = scores_glicko[i] 
        #     + scores_rd[i] * np.random.randn(n_sample,)
        scores_samples = np.tile(scores_glicko, [n_sample, 1]) + \
            np.multiply(np.tile(scores_rd, [n_sample, 1]), \
                        np.random.randn(n_sample, n_decks))
        
        # patch_artist = patch.Patch(edgecolor=None, facecolor=None, 
        #                            color='k', 
        #                            linewidth=None, linestyle='--', 
        #                            antialiased=None, 
        #                            hatch=None, 
        #                            fill=True, 
        #                            capstyle=None, 
        #                            joinstyle=None)
        bplt = ax2.boxplot(scores_samples,
                           labels=labels,
                           notch=False, 
                           meanline=True,
                           positions=range(0, n_decks),
                           showmeans=True,
                           showcaps=True, 
                           showbox=True, 
                           showfliers=False, 
                           manage_ticks=False,
                           patch_artist=True, 
                           boxprops=dict(facecolor=clw, color='k',
                                         alpha=0.5),
                           capprops=dict(color=clw, alpha=0.5),
                           whiskerprops=dict(color=clw, alpha=0.5),
                           meanprops=dict(color=clw, linestyle='-')
                           )
        
    else:
        nsig = 1
        ax2.scatter(labels, scores_glicko, alpha=alpha, 
                    color=clw, edgecolor='k')
        if not step:
            ax2.plot(labels, scores_glicko+nsig*scores_rd, 
                 color=clw, linestyle='--', linewidth=0.5)
            ax2.plot(labels, scores_glicko-nsig*scores_rd, 
                   color=clw, linestyle='--', linewidth=0.5)
            ax2.fill(np.concatenate([xx, xx[::-1]]),
                      np.concatenate([scores_glicko - nsig * scores_rd,
                                    (scores_glicko + nsig * scores_rd)[::-1]]),
                          alpha=0.2, label='+-2rd', color=clw)
        else:
            ax2.step(labels, scores_glicko+nsig*scores_rd, 
                 color=clw, linestyle='--', linewidth=0.5,
                 where='mid')
            ax2.step(labels, scores_glicko-nsig*scores_rd, 
                   color=clw, linestyle='--', linewidth=0.5,
                   where='mid')
            ax2.fill_between(xx, scores_glicko - nsig * scores_rd, 
                             scores_glicko + nsig * scores_rd, step='mid',
                             alpha=0.2, label='+-2rd', color=clw)
    
    ax2.hlines(ygor.elo_0,
               xmin=ax2.get_xlim()[0]+1, xmax=ax2.get_xlim()[1]-1,
               color=clr[2], linestyle='--', linewidth=0.5)
    
    ax1.set_ylim([ax2.get_ylim()[0], ax2.get_ylim()[1]])
    
    fig.tight_layout()
    plt.show()

def show_this_map(this_map=None, cmap=None):
    """Display given map"""
    if this_map is None:
        winrate_map, game_is_impossible = compute_games_map()
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
    normalizer = colors.DivergingNorm(vcenter=0.5, 
                                      vmin=0, 
                                      vmax=np.max(winrate_map))
    if cmap is None:
        cmap = 'RdYlGn' # coolwarm, bwr, RdYlGn
    cax = ax.matshow(winrate_map, cmap=cm.get_cmap(cmap),
                      norm=normalizer, alpha=1) 
    # cax = plt.pcolormesh(winrate_map, 
    #                      edgecolors='k', cmap=cm.get_cmap(cmap),
    #                      norm=normalizer, alpha=1)
    # ax.set_aspect('equal')
    # ax.invert_yaxis()
    
    if show_winrate:
        ax.matshow(game_is_impossible, alpha=0.1, cmap=cm.get_cmap('binary'))
        # plt.pcolormesh(game_is_impossible, 
        #                alpha=0.1, cmap=cm.get_cmap('binary'))
        
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

def show_players():
    """Show stats of all players: played gamed, win/loss, nr of decks"""
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
                            'avgwinrate': sum(player_i.nwins)/
                            sum(player_i.ngames)})
        players = players.append(ygom.pd.DataFrame(data=[player_dict]))
    players.reset_index(drop=True, inplace=True)
    return players

def suggest_new_matchup(player1=None, player2=None):
    all_decks = ygor.get_all_decks_ranked()
    labels = all_decks.deck.tolist()
    
    winrate_map, game_is_impossible = compute_games_map()
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
            deck1_owner = ygom.find_owner(labels[i])
            for j in range(0, i):
                deck2_owner = ygom.find_owner(labels[j])
                if ((deck1_owner==player1 or deck1_owner==player2) 
                    and (deck2_owner==player1 or deck2_owner==player2)):
                        filter_by_player[i,j] = 1
                    
    # show_this_map(filter_by_player)
    new_matchup_between = free_matchups * filter_by_player
    new_matchup_between = new_matchup_between + new_matchup_between.T
    show_this_map(new_matchup_between)
    
    
    






