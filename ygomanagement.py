#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 23:40:26 2020

@author: william

All utilitary functions: manage decks, find deck, get games...
"""

from enum import Enum
import pandas as pd
from datetime import date
# from math import nan

# # Enum #####################################################################


class GameResult(Enum):
    WIN = 1
    DRAW = 0.5
    LOSE = 0


# # Files name ###############################################################


TEST = False
if TEST:
    DECK_LIST_FILE = 'test/deck_list.csv'
    GAME_HIST_FILE = 'test/game_history.csv'
else:
    DECK_LIST_FILE = 'data/deck_list.csv'
    GAME_HIST_FILE = 'data/game_history.csv'

# # Functions ################################################################


def add_deck(deck_name, deck_owner, creation_date=None):
    """Add new deck to the database"""
    # Date today
    if creation_date is None:
        creation_date = date.today().strftime("%d/%m/%Y")
    # Open or create file
    with open(DECK_LIST_FILE, 'a') as f:
        # Retrieve deck number
        if f.tell():
            all_decks = pd.read_csv(DECK_LIST_FILE)
            n_decks = len(all_decks.index)
        else:
            n_decks = 0
        # New deck data
        deck_data = {'n': [n_decks+1],
                     'deck': [deck_name],
                     'owner': [deck_owner],
                     'date': [creation_date]}
        deck_df = pd.DataFrame(data=deck_data)
        # Append
        deck_df.to_csv(f, header=f.tell() == 0, index=False)
    return deck_df


def add_game(deck1, deck2, game_date=None):
    """Add new game to the database"""
    # Process input
    if game_date is None:
        game_date = date.today().strftime("%d/%m/%Y")

    with open(GAME_HIST_FILE, 'a') as f:
        # Retrieve game number
        if f.tell():
            all_games = pd.read_csv(GAME_HIST_FILE)
            n_games = len(all_games.index)
        else:
            n_games = 0
        # New deck data
        gameData = {'n': [n_games+1],  # all_games.iloc[-1].name+1
                    'deck1': [deck1],
                    'deck2': [deck2],
                    'date': [game_date]}
        game_df = pd.DataFrame(data=gameData)
        # Append
        game_df.to_csv(f, header=f.tell() == 0, index=False)
    return game_df


def remove_last_game(nremov=1, verbose=False):
    """Remove a number n (default 1) of the last logged games"""
    # with open(GAME_HIST_FILE, 'r+') as file:
    #     lines = file.readlines()
    #     lines_rmv = lines[:-ngames]
    all_games = get_all_games()
    if verbose:
        print('------- Warning: removing lines from file -------')
        print(all_games)
        print('Number of games logged: ' + str(len(all_games)))
        print('-------------------------------------------------')
    idxgames = len(all_games)
    all_games.drop(labels=range(idxgames-nremov, idxgames),
                   axis=0, inplace=True)
    if verbose:
        print('------- Deleted ' + str(nremov) + ' game(s) from file -------')
        print(all_games)
        print('Number of games logged: ' + str(len(all_games)))
    with open(GAME_HIST_FILE, 'w') as f:
        all_games.to_csv(f, header=f.tell() == 0, index=False)


def find_deck(deck_name):
    """Return deck as dict, based on its name"""
    all_decks = get_all_decks()
    deck = all_decks.loc[all_decks.deck == deck_name].iloc[0]
    return deck


def show_all_decks_log():
    """Print all decks"""
    all_decks = get_all_decks()
    print('Displaying all decks...')
    print(all_decks)


def show_log():
    """Print last games played"""
    all_games = get_all_games()
    print('Showing latest games...')
    print(all_games.tail(15))


def get_all_decks():
    """"Return a DataFrame containing all decks"""
    return pd.read_csv(DECK_LIST_FILE)


def get_all_games():
    """Return a DataFrame containing all games"""
    return pd.read_csv(GAME_HIST_FILE)


def find_owner(deck_name):
    """Return owner of a given deck"""
    return find_deck(deck_name).owner
