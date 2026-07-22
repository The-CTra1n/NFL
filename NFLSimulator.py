import pandas as pd
import random
import math

def main():
    matchesData = pd.read_csv("GameResults.csv").values.tolist()
    teamsData = pd.read_csv("TeamPayouts.csv").values.tolist()

    teams = [teamsData[i][0] for i in range(0, 32)]

    numMatches = len(matchesData)
    matchesTeams = [[matchesData[i][1], matchesData[i][0]] for i in range(0, numMatches)]
    homeWinProbs = [float(matchesData[i][2]) for i in range(0, numMatches)]

    divisions = ['AFC East', 'AFC North', 'AFC South', 'AFC West', 'NFC East', 'NFC North', 'NFC South', 'NFC West']
    conferences = ["AFC", "NFC"]

    teamDivision = {div: [] for div in divisions}
    divisionTeam = {teamsData[i][0]: teamsData[i][1] for i in range(0, 32)}

    for i in range(0, 32):
        teamDivision[teamsData[i][1]].append(teamsData[i][0])

    teamELOs = {teamsData[i][0]: teamsData[i][3] for i in range(0, 32)}

    # Determine which games are already played (none are played in the sample, but keeping logic)
    currentGame = 0
    while currentGame < numMatches and homeWinProbs[currentGame] % 1 == 0:
        currentGame += 1

    for i in range(0, currentGame):
        homeWinProbs[i] = (homeWinProbs[i] + 1) % 2

    for i in range(currentGame, numMatches):
        elo1 = teamELOs[matchesTeams[i][0]]
        elo2 = teamELOs[matchesTeams[i][1]]
        homeWinProbs[i] = 1 / (math.pow(10, (elo2 - (elo1 + 55)) / 400) + 1)

    def sim_match_playoff(team1, team2):
        elo1 = teamELOs[team1]
        elo2 = teamELOs[team2]
        if random.random() < 1 / (math.pow(10, (elo2 - (elo1 + 55)) / 400) + 1):
            return team1
        return team2

    def sim_match_superbowl(team1, team2):
        elo1 = teamELOs[team1]
        elo2 = teamELOs[team2]
        if random.random() < 1 / (math.pow(10, (elo2 - elo1) / 400) + 1):
            return team1
        return team2

    rounds = 10000

    teamDivisionWins = {t: 0 for t in teams}
    teamGameWins = {t: 0.0 for t in teams}
    superbowlCounts = {t: 0 for t in teams}
    winCounts = {t: 0 for t in teams}

    for r in range(rounds):
        teamCounts = {t: 0 for t in teams}
        teamConference = {"AFC": [], "NFC": []}

        for i in range(0, 32):
            teamConference[teamsData[i][2]].append(teamsData[i][0])

        for i in range(0, numMatches):
            if random.random() < homeWinProbs[i]:
                teamCounts[matchesTeams[i][0]] += 1
            else:
                teamCounts[matchesTeams[i][1]] += 1

        for i in range(0, 32):
            teamGameWins[teams[i]] += teamCounts[teams[i]]

        # AFC Bye
        byeAFC = teamConference["AFC"][0]
        for i in teamConference["AFC"]:
            if teamCounts[i] > teamCounts[byeAFC]:
                byeAFC = i
            elif teamCounts[i] == teamCounts[byeAFC]:
                if random.random() > 0.5:
                    byeAFC = i

        semis = []
        semis.append(byeAFC)
        teamCounts.pop(byeAFC)
        divChampAFC = divisionTeam[byeAFC]
        teamConference["AFC"].remove(byeAFC)

        # NFC Bye
        byeNFC = teamConference["NFC"][0]
        for i in teamConference["NFC"]:
            if teamCounts[i] > teamCounts[byeNFC]:
                byeNFC = i
            elif teamCounts[i] == teamCounts[byeNFC]:
                if random.random() > 0.5:
                    byeNFC = i

        semis.append(byeNFC)
        teamCounts.pop(byeNFC)
        divChampNFC = divisionTeam[byeNFC]
        teamConference["NFC"].remove(byeNFC)

        teamDivisionWins[byeNFC] += 1
        teamDivisionWins[byeAFC] += 1

        playoffs = [""] * 12
        place = 0

        for k in divisions:
            if k != divChampNFC and k != divChampAFC:
                winner = teamDivision[k][0]
                for l in teamDivision[k]:
                    if l in teamCounts and teamCounts[l] > teamCounts[winner]:
                        winner = l
                    elif l in teamCounts and teamCounts[l] == teamCounts[winner]:
                        if random.random() > 0.5:
                            winner = l
                teamDivisionWins[winner] += 1
                teamCounts.pop(winner)

                if winner not in semis:
                    playoffs[place] = winner
                    place += 1

                conf = k[:3]
                teamConference[conf].remove(winner)

        for k in conferences:
            for i in range(0, 3):
                winner = teamConference[k][0]
                for l in teamConference[k]:
                    if teamCounts[l] > teamCounts[winner]:
                        winner = l
                    elif teamCounts[l] == teamCounts[winner]:
                        if random.random() > 0.5:
                            winner = l
                teamCounts.pop(winner)
                playoffs[place] = winner
                place += 1
                teamConference[k].remove(winner)

        # Wildcard round
        for i in range(0, 6):
            if i < 3:
                semis.append(sim_match_playoff(playoffs[i], playoffs[8-i]))
            else:
                semis.append(sim_match_playoff(playoffs[i], playoffs[14-i]))

        # Divisional round
        confFinals = []
        confFinals.append(sim_match_playoff(semis[0], semis[4]))
        confFinals.append(sim_match_playoff(semis[2], semis[3]))
        confFinals.append(sim_match_playoff(semis[1], semis[7]))
        confFinals.append(sim_match_playoff(semis[5], semis[6]))

        # Conference Championship
        superbowl = []
        superbowl.append(sim_match_playoff(confFinals[0], confFinals[1]))
        superbowl.append(sim_match_playoff(confFinals[2], confFinals[3]))

        for i in superbowl:
            superbowlCounts[i] += 1

        winner = sim_match_superbowl(superbowl[0], superbowl[1])
        winCounts[winner] += 1

    # Output results
    print(f"{'Team':<15} {'Win Superbowl':>15} {'Reach Superbowl':>17} {'Win Division':>15} {'Expected Wins':>15}")
    print("-" * 81)

    # Sort teams by Win Superbowl descending
    teams_sorted = sorted(teams, key=lambda t: winCounts[t], reverse=True)

    for team in teams_sorted:
        win_sb_prob = winCounts[team] / rounds
        reach_sb_prob = superbowlCounts[team] / rounds
        win_div_prob = teamDivisionWins[team] / rounds
        expected_wins = teamGameWins[team] / rounds
        print(f"{team:<15} {win_sb_prob:>15.4f} {reach_sb_prob:>17.4f} {win_div_prob:>15.4f} {expected_wins:>15.2f}")

if __name__ == "__main__":
    main()
