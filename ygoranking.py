#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 16:19:07 2020

@author: william
"""
import pandas as pd
from datetime import date
from enum import Enum
from math import nan
import glicko2

## Enum
class GameResult(Enum):
    WIN = 1
    DRAW = 0.5
    LOSE = 0

## Files name
DECK_LIST_FILE = 'test_deck_list.csv' # 'deck_list.csv'
DECK_RANK_FILE = 'test_deck_ranking.csv' # 'deck_ranking.csv'
GAME_HIST_FILE = 'test_game_history.csv' # 'game_history.csv'
elo_0 = 1500
glicko_0 = 1500
rd_0 = 100

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
                    'date': [creation_date],
                    'elo' : [elo_0],
                    'glicko' : [glicko_0],
                    'rd' : [rd_0]}
        deck_df = pd.DataFrame(data=deck_data)
        # Append
        deck_df.to_csv(f, header=f.tell()==0, index=False)
    return deck_df
    
def add_game(deck1, deck2, score1=None, score2=None, game_date=None):
    """Ajouter un match dans la base de données
    By default, winner=deck1"""
    # Process input
    if game_date is None:
        game_date = date.today().strftime("%d/%m/%Y")
    if score1 is None:
        score1 = nan
    if score2 is None:
        score2 = nan
    
    # Compute new Elo & Glicko scores
    # Retrieve deck and previous ratings
    d1 = find_deck(deck1)
    d2 = find_deck(deck2)
    elo1 = d1.elo
    elo2 = d2.elo
    glicko1 = d1.glicko
    glicko2 = d2.glicko
    rd1 = d1.rd
    rd2 = d2.rd
    # Compute elo
    elo1, elo2 = compute_elo(elo1,
                             elo2,
                             result=GameResult.WIN)
    # Compute glicko
    gl1, gl2 = compute_glicko([glicko1, rd1],
                              [glicko2, rd2],
                              result=GameResult.WIN)
    glicko1 = int(gl1.rating)
    rd1 = int(gl1.rd)
    glicko2 = int(gl2.rating)
    rd2 = int(gl2.rd)
    # Log game
    with open(GAME_HIST_FILE, 'a') as f:
        # Retrieve game number
        if f.tell():
            all_games = pd.read_csv(GAME_HIST_FILE)
            n_games = len(all_games.index)
        else:
            n_games = 0
        # New deck data
        gameData = {'n' : [n_games+1],
                    'deck1': [deck1],
                    'deck2': [deck2], 
                    'score1' : [score1],
                    'score2' : [score2],
                    'date' : [game_date],
                    'elo1' : [elo1],
                    'glicko1' : [glicko1],
                    'rd1' : [rd1],
                    'elo2' : [elo2],
                    'glicko2' : [glicko2],
                    'rd2' : [rd2]}
        game_df = pd.DataFrame(data=gameData)
        # Append
        game_df.to_csv(f, header=f.tell()==0, index=False)    
        
    with open(DECK_LIST_FILE, 'a') as f:
        all_decks = pd.read_csv(DECK_LIST_FILE)
        all_decks.loc[d1.n-1, 'elo'] = elo1
        all_decks.loc[d1.n-1, 'glicko'] = glicko1
        all_decks.loc[d1.n-1, 'rd'] = rd1
        all_decks.loc[d2.n-1, 'elo'] = elo2
        all_decks.loc[d2.n-1, 'glicko'] = glicko2
        all_decks.loc[d2.n-1, 'rd'] = rd2
        all_decks.to_csv(DECK_LIST_FILE, index=False)
    
    return game_df

def find_deck(deck_name):
    all_decks = get_all_decks()
    deck = all_decks.loc[all_decks.deck == deck_name].iloc[0]
    return deck

def sort_decks():
    """Classe les decks par score (Elo ou Glicko) dans le fichier"""
    all_decks = get_all_decks()
    all_decks_sorted=all_decks.sort_values('elo', ascending=False)
    return all_decks_sorted

def rank_decks():
    """Affiche le classement de decks dans la ligne de commande"""
    all_decks_sorted = sort_decks()
    all_decks_sorted.to_csv(DECK_RANK_FILE, index=False)
    print('Ranking decks by score in file: ' + DECK_RANK_FILE)
    print(all_decks_sorted)
    
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

def compute_elo(elo1, elo2, result=GameResult.WIN):
    """Calcule le score Elo de deux decks étant donné un match
    Le joueur 1 a gagné par défaut"""
    K = 40
    W = result.value
    D = min(elo1 - elo2, 400)
    pD = lambda D: 1/(1+10**(-D/400))
    elo1 = elo1 + K * (W - pD(D))
    elo2 = elo2 + K * (1 - W - pD(-D))
    return int(elo1), int(elo2)

def compute_glicko(deck1, deck2, result=GameResult.WIN):
    """Calcule le score Glicko de deux decks étant donné un match"""
    gl1 = glicko2.Player(rating=deck1[0], rd=deck1[1])
    gl2 = glicko2.Player(rating=deck2[0], rd=deck2[1])
        
    gl1.update_player([gl2.rating], [gl2.rd], [result.value])
    gl2.update_player([gl1.rating], [gl1.rd], [1-result.value])
    
    return gl1, gl2












