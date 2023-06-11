
"""
Created on Fri Jun 9 15:46:07 2023

@author: Conor McMenamin
"""

import pandas as pd 
import random
import math
import csv

import itertools
# Read data from file 'filename.csv' 
# (in the same directory that your python process is based)
# Control delimiters, rows, column names with read_csv (see later) 

   
            
matchesData = pd.read_csv("GameResults.csv").values.tolist()
teamsData=pd.read_csv("TeamPayouts.csv").values.tolist()

teams=[teamsData[i][0] for i in range(0,32)]

numMatches=len(matchesData)
matchesTeams=[[matchesData[i][1],matchesData[i][0]] for i in range(0,numMatches)]
homeWinProbs=[float(matchesData[i][2]) for i in range(0,numMatches)]

teamDivisionWins=dict([(teams[i]+'' ,0 ) for i in range(0,32)])
teamMadePlayoffs=dict([(teams[i]+'' ,0 ) for i in range(0,32)])
teamConference=dict([(teams[i]+'' ,teamsData[i][2] ) for i in range(0,32)])
teamGameWins=dict([(teams[i]+'' ,0 ) for i in range(0,32)])

divisions=['AFC East','AFC North', 'AFC South', 'AFC West', 'NFC East', 'NFC North', 'NFC South','NFC West' ]
conferences=["AFC", "NFC"]


teamDivision=dict([(divisions[i] ,[] ) for i in range(0,len(divisions))])
divisionTeam=dict([(teams[i]+'' ,teamsData[i][1] ) for i in range(0,32)])
for i in range(0,32):
    teamDivision[teamsData[i][1]].append(teamsData[i][0])
    
teamELOs=dict([(teams[i]+'' ,teamsData[i][3] ) for i in range(0,32)])

mult=1
rounds=25000
numberOfGameSims=0

def sim_match(team1,team2):
    elo1=teamELOs[team1]
    elo2=teamELOs[team2]
    if (random.random()<1/(math.pow(10,mult*(elo2-(elo1+55))/400)+1)):
        return(team1)
    return team2

def sim_match_playoff(team1,team2):
    elo1=teamELOs[team1]
    elo2=teamELOs[team2]
    if (random.random()<1/(math.pow(10,mult*(1.25*(elo2-(elo1+55)))/400)+1)):
        return(team1)
    return team2

def sim_match_superbowl(team1,team2):
    elo1=teamELOs[team1]
    elo2=teamELOs[team2]
    if (random.random()<1/(math.pow(10,mult*(1.25*(elo2-(elo1)))/400)+1)):
        return(team1)
    return team2

def sim_match_home_win_probs(team1,team2):
    elo1=teamELOs[team1]
    elo2=teamELOs[team2]
    return(1/(math.pow(10,mult*(elo2-(elo1+55))/400)+1))
  
playoffCounts=dict([(teams[i]+'' ,0 ) for i in range(0,32)])
divisionWinCounts=dict([(teams[i]+'' ,0 ) for i in range(0,32)])
winCounts=dict([(teams[i]+'' ,0 ) for i in range(0,32)])
superbowlCounts=dict([(teams[i]+'' ,0 ) for i in range(0,32)])



teamPayoffs=dict([(teams[i]+'' ,[max(teamsData[i][5],0), teamsData[i][6] ,teamsData[i][7] ,teamsData[i][8] ] ) for i in range(0,32)])
notPlayoffs=[]
for i in range(0,32):
    if teamsData[i][4]>0:
        notPlayoffs.append(i)
notPlayoffPayoffs=dict([(teams[i]+'' ,teamsData[i][4] ) for i in notPlayoffs])
results=[]
pnL=[]
totalROI=0

lst = list(itertools.product([0, 1], repeat=numberOfGameSims))


#for simulating games

standard=0
home=0
currentGame=0
while homeWinProbs[currentGame] % 1==0:
    currentGame+=1
startingGame=currentGame+0
for i in range(0,currentGame):
    homeWinProbs[i]=(homeWinProbs[i]+1)%2
for i in range(currentGame,numMatches):
    homeWinProbs[i]=sim_match_home_win_probs(matchesTeams[i][0],matchesTeams[i][1])



count=0
awayWin=0
simGameROI=0
weekEV=0
preGameHome=0
for r in range(0,rounds*((2*numberOfGameSims)+1)+1):
    
    if r % rounds==0 and r>rounds:
        
        if not(r % (2*rounds))==0:
            homeWinProbs[currentGame]=sim_match_home_win_probs(matchesTeams[currentGame][0],matchesTeams[currentGame][1])
            gameEV=int((homeWinProbs[currentGame]*(simGameROI-standard)/rounds)+((1-homeWinProbs[currentGame])*(awayWin-standard)/rounds))
            weekEV+=gameEV
            print(matchesTeams[currentGame][1]+" win:",int((awayWin-standard)/rounds),"@ " + matchesTeams[currentGame][0]+" win:",int((simGameROI-standard)/rounds), "Expectancy:",gameEV )
            currentGame+=1
            
        awayWin=simGameROI
        simGameROI=0
        home=(home+1)%2
        if home == 1:
            teamELOs=dict([(teams[i]+'' ,teamsData[i][3] ) for i in range(0,32)])
            teamELOs[matchesTeams[currentGame][1]]+=20
            teamELOs[matchesTeams[currentGame][0]]-=20
            for i in range(startingGame,numMatches):
                homeWinProbs[i]=sim_match_home_win_probs(matchesTeams[i][0],matchesTeams[i][1])
        if home == 0:
            teamELOs=dict([(teams[i]+'' ,teamsData[i][3] ) for i in range(0,32)])
            teamELOs[matchesTeams[currentGame][1]]-=20
            teamELOs[matchesTeams[currentGame][0]]+=20
            for i in range(startingGame,numMatches):
                homeWinProbs[i]=sim_match_home_win_probs(matchesTeams[i][0],matchesTeams[i][1])

        homeWinProbs[currentGame]=home
    
        
    
    rOI=0
    teamCounts=dict([(teams[i]+'' ,0 ) for i in range(0,32)])   
    teamConference=dict([("AFC",[]),("NFC",[])])
    for i in range(0,32):
        teamConference[teamsData[i][2]].append(teamsData[i][0])
        
    for i in range(0, numMatches):
        #print(matchesTeams[i][0],homeWinProbs[i])
        if random.random()<homeWinProbs[i]:
            teamCounts[matchesTeams[i][0]]+=1
        else:
            teamCounts[matchesTeams[i][1]]+=1
            
    for i in range(0, 32):
        teamGameWins[teams[i]]=(teamGameWins[teams[i]]*r+teamCounts[teams[i]])/(r+1)
        
    playoffTeams=dict([("AFC",[]),("NFC",[])])
    byeAFC=teamConference["AFC"][0]
    for i in teamConference["AFC"]:
        if teamCounts[i]>teamCounts[byeAFC]:
            byeAFC=i
        if teamCounts[i]==teamCounts[byeAFC]:
            if random.random()>0.5:
                byeAFC=i
    semis=[] 
                   
    semis.append(byeAFC)
    teamCounts.pop(byeAFC)
    divChampAFC=divisionTeam[byeAFC]
    teamConference[divChampAFC[:3]].pop(teamConference[divChampAFC[:3]].index(byeAFC))
    playoffs=["" for i in range(0,12)]
    byeNFC=teamConference["NFC"][0]
    
    for i in teamConference["NFC"]:
        
        if teamCounts[i]>teamCounts[byeNFC]:
            byeNFC=i
        if teamCounts[i]==teamCounts[byeNFC]:
            if random.random()>0.5:
                byeNFC=i
    semis.append(byeNFC)
    teamCounts.pop(byeNFC)
    
    divChampNFC=divisionTeam[byeNFC]
    teamConference[divChampNFC[:3]].pop(teamConference[divChampNFC[:3]].index(byeNFC))
    place=0
    teamDivisionWins[byeNFC]+=1
    teamDivisionWins[byeAFC]+=1
    for i in semis:
        rOI+=(teamPayoffs[i][0]+teamPayoffs[i][1])
    for k in divisions:
        if k != divChampNFC and  k != divChampAFC:
            winner=teamDivision[k][0]
            for l in teamDivision[k]:
                if teamCounts[l]>teamCounts[winner]:
                    winner=l
                if teamCounts[l]==teamCounts[winner]:
                    if random.random()>0.5:
                        winner=l
            teamDivisionWins[winner]+=1
            teamMadePlayoffs[winner]+=1
        
            teamCounts.pop(winner)
            if(not(winner in semis)):
                playoffs[place]=winner
                place+=1
                rOI+=(teamPayoffs[winner][0]+teamPayoffs[winner][1])
            teamConference[k[:3]].pop(teamConference[k[:3]].index(winner))
    
    for k in conferences:
        for i in range(0,3):
            winner=teamConference[k][0]
        
            for l in teamConference[k]:
                if teamCounts[l]>teamCounts[winner]:
                    winner=l
                if teamCounts[l]==teamCounts[winner]:
                    if random.random()>0.5:
                        winner=l
            teamMadePlayoffs[winner]+=1
            teamCounts.pop(winner)
            playoffs[place]=winner
            rOI+=(teamPayoffs[winner][0])
            place+=1
            teamConference[k].pop(teamConference[k].index(winner))
    
    for key in notPlayoffPayoffs.keys():
        if( not( key in playoffs or key in semis)):
            rOI+=notPlayoffPayoffs[key]
    
    
    
    
        
    
    
    for i in range(0,6):
        if(i<3):
            semis.append(sim_match_playoff(playoffs[i], playoffs[8-i]))
        else:
            semis.append(sim_match_playoff(playoffs[i], playoffs[14-i]))
    confFinals=[]
    confFinals.append(sim_match_playoff(semis[0],semis[4]))
    confFinals.append(sim_match_playoff(semis[2],semis[3]))
    confFinals.append(sim_match_playoff(semis[1],semis[7]))
    confFinals.append(sim_match_playoff(semis[5],semis[6]))    
    superbowl=[]
    superbowl.append(sim_match_playoff(confFinals[0],confFinals[1]))
    superbowl.append(sim_match_playoff(confFinals[2],confFinals[3]))
    for i in superbowl:
        rOI+=(teamPayoffs[i][2])
    
    winner=sim_match_superbowl(superbowl[0],superbowl[1])
    rOI+=(teamPayoffs[winner][3])
    totalROI+=rOI
    simGameROI+=rOI
    
    """
    results.append([])
    results[r].append(byeAFC)
    for i in [0,1,2,6,7,8]:
        results[r].append(playoffs[i])
    results[r].append(byeNFC)
    for i in [3,4,5,9,10,11]:
        results[r].append(playoffs[i])
    for i in confFinals:
        results[r].append(i)
    for i in superbowl:
        results[r].append(i)    
    results[r].append(winner)
    results[r].append(rOI)
    """
    
    if (r+1)<=rounds:
        for i in playoffs:
            playoffCounts[i]+=1
        for i in superbowl:
            superbowlCounts[i]+=1
        playoffCounts[byeAFC]+=1
        playoffCounts[byeNFC]+=1
        winCounts[winner]+=1
        pnL.append([rOI])
        if (r+1)==rounds:
            print(count/rounds)
            """with open("SimulatedPnL.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(pnL)"""
            standard=simGameROI
            simGameROI=0
            """if home == 0:
                k=20
                teamELOs=dict([(teams[i]+'' ,teamsData[i][3] ) for i in range(0,32)])
                teamELOs[matchesTeams[currentGame][1]]-=20
                teamELOs[matchesTeams[currentGame][0]]+=20
                for i in range(startingGame,numMatches):
                    homeWinProbs[i]=sim_match_home_win_probs(matchesTeams[i][0],matchesTeams[i][1])
            """
            homeWinProbs[currentGame]=home
            print("Book Value", int(standard/rounds))
            for i in teams:
                print(i,playoffCounts[i]/rounds,teamDivisionWins[i]/rounds,superbowlCounts[i]/rounds,winCounts[i]/rounds,int(teamGameWins[i]*100)/100)


        
print("Week Expectancy:", weekEV)
print("Book Value", int(standard/rounds))
