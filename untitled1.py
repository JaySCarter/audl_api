# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 21:59:09 2022

@author: JaysC
"""
import os

import numpy as np
import pandas as pd

import janitor


scores = ['GOAL', 'SCORED_ON', 'CALLAHAN', 'CALLAHAN_THROWN']
we_score = ['GOAL', 'CALLAHAN']
they_score = ['SCORED_ON', 'CALLAHAN_THROWN']

turnovers = ['THROWAWAY', 'DROP', 'STALL', 'CALLAHAN_THROWN']
takeaways = ['BLOCK', 'CALLAHAN', 'STALL_CAUSED', 'THROWAWAY_CAUSED']

pulls = ['PULL_OUT_OF_BOUNDS', 'PULL_INBOUNDS']

pens = ['D_PENALTY_ON_THEM', 'D_PENALTY_ON_US', 'O_PENALTY_ON_THEM', 'O_PENALTY_ON_US']

quarter_ends = ['START_OF_GAME', 'END_OF_Q1', 'HALFTIME', 'END_OF_Q3', 'GAME_OVER']

line_sets = ['SET_D_LINE', 'SET_O_LINE', 'SET_D_LINE_NO_PULL', 'SET_O_LINE_NO_PULL']
o_lines = ['SET_O_LINE', 'SET_O_LINE_NO_PULL']
d_lines = ['SET_D_LINE', 'SET_D_LINE_NO_PULL']

timeouts = ['THEIR_MIDPOINT_TIMEOUT', 'OUR_MIDPOINT_TIMEOUT']

other = ['REF_TIMEOUT_DISCUSSION???', 'INJURY_ON_O', 'INJURY_ON_D']

def column_cleaning(df):
    
    df['is_home'] = df['home_team'] == df['team_id']
    df['is_away'] = df['away_team'] == df['team_id']
    
    df["game_point_id"] = df["game_id"]*1000 + df["point_id"]
    
    df['player'] = np.where(df['event_type'].isin(line_sets), df['player'], "")
    
    df['home_score']  = np.where((df['is_home']) & (df['event_type'].isin(we_score)), 1, 0)
    df['away_score']  = np.where((df['is_away']) & (df['event_type'].isin(we_score)), 1, 0)
    
    
df = pd.read_csv("Flyers_Games.csv").rename({"Unnamed: 0" : "event_index"}, axis=1)

    
