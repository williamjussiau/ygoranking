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
from math import nan

## Enum
class GameResult(Enum):
    WIN = 1
    DRAW = 0.5
    LOSE = 0

## Files name
TEST = False
if TEST:
    DECK_LIST_FILE = 'test/deck_list.csv'
    GAME_HIST_FILE = 'test/game_history.csv'
else:
    DECK_LIST_FILE = 'data/deck_list.csv'
    GAME_HIST_FILE = 'data/game_history.csv'
    


## Functions
def add_deck(deck_name, deck_owner, creation_date=None):
    """Ajoute un deck à la liste ; à utiliser avec parcimonie"""
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
        deck_data = {'n' : [n_decks+1],
                    'deck': [deck_name],
                    'owner': [deck_owner], 
                    'date': [creation_date]}
        deck_df = pd.DataFrame(data=deck_data)
        # Append
        deck_df.to_csv(f, header=f.tell()==0, index=True)
    return deck_df
    
def add_game(deck1, deck2, game_date=None):
    """Ajouter un match dans la base de données
    By default, winner=deck1"""
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
        gameData = {'n' : [n_games+1], #all_games.iloc[-1].name+1
                    'deck1': [deck1],
                    'deck2': [deck2], 
                    'date' : [game_date],
                    }
        game_df = pd.DataFrame(data=gameData)
        # Append
        game_df.to_csv(f, header=f.tell()==0, index=False)    
        
    return game_df

def find_deck(deck_name):
    all_decks = get_all_decks()
    deck = all_decks.loc[all_decks.deck == deck_name].iloc[0]
    return deck

def show_all_decks():
    all_decks = get_all_decks()
    print('Displaying all decks...')
    print(all_decks)

def show_log():
    """Affiche l'historique des matchs dans la ligne de commande"""
    all_games = get_all_games()
    print('Showing latest games...')
    print(all_games.tail())

def get_all_decks():
    '''Return a DataFrame with all decks'''
    return pd.read_csv(DECK_LIST_FILE)

def get_all_games():
    '''Return a DataFrame with all games'''
    return pd.read_csv(GAME_HIST_FILE)


