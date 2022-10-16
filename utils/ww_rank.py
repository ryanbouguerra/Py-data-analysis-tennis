
def winners_win(data, period, printer=False):
    """
    Function that returns the ranking for the given period based on the player's with the most wins. The ranking is an 
    ordered list of list where the first element of the inner list is the player name and the second element is his 
    associated score. The list is ordered from the highest score to the lowest score of each player.   

    Args:
        
    data: list of list, where the inner list contains each game details
    period: considered period for the ranking of type int or list
    printer: if set to True (False as default value), the function prints the top three players for the given period.

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error() and winner() should be run on the dataset before running the function.
    
    """

    if type(period) == int: # if period is only a year of type we convert it to a list
        period = [period]
    player_score = {} # dictionary where each key is a player and its associated value is the number of games won

    # building the dictionary
    for i in range(len(data)):
        if data[i][1].year in period: # considering only games in the given period
            if data[i][3] not in player_score and data[i][4] not in player_score:
                # case if both players not in dictionary
                if data[i][3] == data[i][11]: # if player1 won the game
                    player_score[data[i][3]] = 1
                    player_score[data[i][4]] = 0
                elif data[i][4] == data[i][11]: # if player2 won the game
                    player_score[data[i][3]] = 0
                    player_score[data[i][4]] = 1

            elif data[i][3] in player_score and data[i][4] not in player_score:
                # case if player1 in dictionary but player2 not in dictionary
                if data[i][3] == data[i][11]:
                    player_score[data[i][4]] = 0
                    player_score[data[i][3]] += 1

                elif data[i][4] == data[i][11]:
                    player_score[data[i][4]] = 1

            elif data[i][3] not in player_score and data[i][4] in player_score:
                # case if player1 not in dictionary but player2 in dictionary
                if data[i][3] == data[i][11]:
                    player_score[data[i][3]] = 1

                elif data[i][4] == data[i][11]:
                    player_score[data[i][3]] = 0
                    player_score[data[i][4]] += 1

            elif data[i][3] in player_score and data[i][4] in player_score:
                # case if both player in dictionary
                if data[i][3] == data[i][11]:
                    player_score[data[i][3]] += 1

                elif data[i][4] == data[i][11]:
                    player_score[data[i][4]] += 1

    # converting the dictionary into an ordered list since we can't rely on the dictionary order
    rank = sorted([[player, score] for player, score in player_score.items()], key = lambda x: -x[1])

    # if printer argument is true, the function prints the top three players with their associated scores
    if printer:
        print("\nThe top three players for the given period are:")
        for i in range(3):
            print("Player: ", rank[i][0], " Score: ", rank[i][1])
    return rank


