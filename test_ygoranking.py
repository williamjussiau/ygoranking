#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 19:12:44 2020

@author: william
"""

from ygoranking import GameResult
from ygoranking import add_deck, add_game, compute_elo, rank_decks
import glicko2

# # Add decks
# add_deck("Nordique", "Pierre")
# add_deck("ChaosMAX", "JRE")
# add_deck("Zombie", "William")

# # Add games
# add_game(deck1="Nordique", deck2="Zombie")
# add_game(deck1="ChaosMAX", deck2="Nordique")
# add_game(deck1="ChaosMAX", deck2="Zombie")
# add_game(deck1="ChaosMAX", deck2="Nordique")
# add_game(deck1="Nordique", deck2="Zombie")
# add_game(deck1="Zombie", deck2="Nordique")
# add_game(deck1="Nordique", deck2="ChaosMAX")
# add_game(deck1="Zombie", deck2="Nordique")
# add_game(deck1="Zombie", deck2="ChaosMAX")
# add_game(deck1="ChaosMAX", deck2="Nordique")
# add_game(deck1="Nordique", deck2="Zombie")
# add_game(deck1="Zombie", deck2="Nordique")
# add_game(deck1="Nordique", deck2="ChaosMAX")
# add_game(deck1="Nordique", deck2="ChaosMAX")
# add_game(deck1="Nordique", deck2="ChaosMAX")
# add_game(deck1="Nordique", deck2="ChaosMAX")
add_game(deck1='Zombie', deck2='ChaosMAX')
add_game(deck1='Zombie', deck2='Nordique')

# # Sort and output
rank_decks()

# # Test Elo
# elo1 = 1500
# elo2 = 1500
# rs = GameResult.WIN
# n1, n2 = compute_elo(elo1, elo2, result=rs)
# print(n1,  n2)

# # Test Glicko
# gl1 = glicko2.Player(rating=1500, rd=350)
# gl2 = glicko2.Player(rating=1400, rd=30)
# rs = GameResult.WIN
# gl1.update_player([gl2.rating], [gl2.rd], [rs.value])
# gl2.update_player([gl1.rating], [gl1.rd], [1-rs.value])
# print(gl1.rating, gl1.rd)
# print(gl2.rating, gl2.rd)


