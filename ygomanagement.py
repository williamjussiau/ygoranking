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


class Mode(Enum):
    PLAYER = 1
    DECK = 2


# # Files name ###############################################################

MODE = Mode.PLAYER

TEST = False
if TEST:
    DECK_LIST_FILE = 'test/deck_list.csv'
    PLAYER_LIST_FILE = 'test/player_list.csv'
    GAME_HIST_FILE_DECK = 'test/game_history_with_decks.csv'
    GAME_HIST_FILE_PLAYER = 'test/game_history_with_players.csv'
else:
    DECK_LIST_FILE = 'data/deck_list.csv'
    PLAYER_LIST_FILE = 'data/player_list.csv'
    GAME_HIST_FILE_DECK = 'data/game_history_with_decks.csv'
    GAME_HIST_FILE_PLAYER = 'data/game_history_with_players.csv'

GAME_HIST_FILE = GAME_HIST_FILE_DECK if MODE == Mode.DECK \
    else GAME_HIST_FILE_PLAYER
LIST_FILE = DECK_LIST_FILE if MODE == Mode.DECK \
    else PLAYER_LIST_FILE

# # Functions ################################################################


def add_deck(deck_name='', deck_owner='',
             creation_date=None, file=DECK_LIST_FILE):
    """Add new deck to the database"""
    # Date today
    if creation_date is None:
        creation_date = date.today().strftime("%d/%m/%Y")
    # Open or create file
    with open(file, 'a') as f:
        # Retrieve deck number
        if f.tell():
            all_decks = pd.read_csv(file)
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


def add_player(player_name, file=PLAYER_LIST_FILE):
    """Quick fix: transform deck_name to player_name in file"""
    return add_deck(deck_name=player_name, deck_owner=player_name, file=file)


def add_game(deck1, deck2,
             game_date=None,
             file=GAME_HIST_FILE_DECK):
    """Add new game to the database"""
    # Process input
    if game_date is None:
        game_date = date.today().strftime("%d/%m/%Y")

    with open(file, 'a') as f:
        # Retrieve game number
        if f.tell():
            all_games = pd.read_csv(file)
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


def add_game_player(player1, player2,
                    game_date=None,
                    file=GAME_HIST_FILE_PLAYER):
    """Add new game to the game history w players"""
    return add_game(player1, player2, file=file)


def add_game_full(deck1_player1, deck2_player2, game_date=None):
    df1 = add_game(deck1_player1[0], deck2_player2[0])
    df2 = add_game_player(deck1_player1[1], deck2_player2[1])
    return df1, df2


def remove_last_game(n=1, verbose=False):
    """Remove a number n (default 1) of the last logged games"""
    # with open(GAME_HIST_FILE_DECK, 'r+') as file:
    #     lines = file.readlines()
    #     lines_rmv = lines[:-ngames]
    all_games = get_all_games()
    if verbose:
        print('------- Warning: removing lines from file -------')
        print(all_games)
        print('Number of games logged: ' + str(len(all_games)))
        print('-------------------------------------------------')
    idxgames = len(all_games)
    all_games.drop(labels=range(idxgames-n, idxgames),
                   axis=0, inplace=True)
    if verbose:
        print('------- Deleted ' + str(n) + ' game(s) from file -------')
        print(all_games)
        print('Number of games logged: ' + str(len(all_games)))
    with open(GAME_HIST_FILE, 'w') as f:
        all_games.to_csv(f, header=f.tell() == 0, index=False)


def find_deck(deck_name):
    """Return deck as dict, based on its name"""
    all_decks = get_all_decks()
    try:
        return all_decks.loc[all_decks.deck == deck_name].iloc[0]
    except IndexError:
        return 'Error: deck not found'


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
    return pd.read_csv(LIST_FILE)


def get_all_games():
    """Return a DataFrame containing all games"""
    return pd.read_csv(GAME_HIST_FILE)


def find_owner(deck_name):
    """Return owner of a given deck"""
    return find_deck(deck_name).owner
