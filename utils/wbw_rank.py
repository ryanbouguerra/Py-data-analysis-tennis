from collections import OrderedDict

# I used the OrderedDict data type to avoid the repetitive conversion of rank and updated_rank variables
# to an ordered list. Indeed, the algorithm only relies on two variables instead of four, for each iteration.
# After having taken the mean running time for 1000 calls of the function without OrderedDict and with OrderedDict,
# I found that the function using OrderedDict is slightly slower (~0.01 second), but I believe that the function with
# OrederedDict has a better space-complexity.

def wbw_ranking(data, period, adjust_max=10, iteration_max =500,printer=False):
    """
    Function that returns the ranking for the given period based on the "Winners beat other Winners" technique. The
    ranking is an ordered list of list where the first element of the inner list is the player name and the second
    element is his associated score. The list is ordered from the highest score to the lowest score of each player.

    Args:

    data: list of list, where the inner list contains each game details
    period: considered period for the ranking of type int or list
    adjust_max: sets the maximum number of allowed adjustments for convergence (type int and default value 10)
    iteration_max: sets the maximum number of allowed iterations (integer greater than 0 and default value 500). If the
    number of iterations before convergence exceeds iterations_max, the algorithm stops.
    printer: if set to True (False as default value), the function prints the top three players for the given period.

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error() and winner() should be run on the dataset before running the function.

    """

    if type(period) == int: # if given period is a single year of type int
        period = [period]

    updated_rank = OrderedDict() # OrderedDict where key is a player with its associated score
    defeated_dic = {} # dictionary where each key is a player and its value is the list of players against whom he lost

    # building updated_rank and defeated_dic variables
    for i in range(len(data)):
        if data[i][1].year in period: # focusing on games played in the given year
            if data[i][3] not in updated_rank and data[i][4] not in updated_rank:
                updated_rank[data[i][3]] = 0
                updated_rank[data[i][4]] = 0
                if data[i][3] == data[i][11]:
                    defeated_dic[data[i][3]] = []
                    defeated_dic[data[i][4]] = [data[i][3]]
                elif data[i][4] == data[i][11]:
                    defeated_dic[data[i][4]] = []
                    defeated_dic[data[i][3]] = [data[i][4]]

            elif data[i][3] in updated_rank and data[i][4] not in updated_rank:
                updated_rank[data[i][4]] = 0
                if data[i][3] == data[i][11]:
                    defeated_dic[data[i][4]] = [data[i][3]]
                elif data[i][4] == data[i][11]:
                    defeated_dic[data[i][4]] = []
                    defeated_dic[data[i][3]].append(data[i][4])

            elif data[i][3] not in updated_rank and data[i][4] in updated_rank:
                updated_rank[data[i][3]] = 0
                if data[i][3] == data[i][11]:
                    defeated_dic[data[i][3]] = []
                    defeated_dic[data[i][4]].append(data[i][3])

                elif data[i][4] == data[i][11]:
                    defeated_dic[data[i][3]] = [data[i][4]]

            elif data[i][3] in updated_rank and data[i][4] in updated_rank:
                if data[i][3] == data[i][11]:
                    defeated_dic[data[i][4]].append(data[i][3])

                elif data[i][4] == data[i][11]:
                    defeated_dic[data[i][3]].append(data[i][4])

    total_players = len(updated_rank) # number of unique players
    rank = OrderedDict((key, 1/total_players) for key in updated_rank) # initializing scores of each player

    if adjust_max is None:
        adjust_max = 15

    iteration = 0 # iteration counter
    adjust_count = adjust_max + 1 # counts the number of adjustments made before next iteration

    while adjust_count > adjust_max: # while loop that stops when adjustment made is lower or equal to adjust max
        # updating variables
        adjust_count = 0
        iteration += 1

        # Distributing shares among players
        for player, lost_against in defeated_dic.items():
            loss_count = len(lost_against) # number of players he lost against

            if loss_count > 0:
                share_to_give = rank[player] / loss_count
                for item in lost_against:
                    updated_rank[item] += share_to_give

            elif loss_count == 0: # case if player never lost
                updated_rank[player] = rank[player]

        # Rescaling scores
        for item in updated_rank:
            updated_rank[item] = updated_rank[item]*0.85 + 0.15/total_players

        # Ordering the OrderedDict according to each player's score
        updated_rank = OrderedDict(sorted(updated_rank.items(), key=lambda item: -item[1]))
        rank = OrderedDict(sorted(rank.items(), key=lambda item: -item[1]))

        # Obtaining the number of adjustments made between the iterations
        for u, j in zip(rank.items(), updated_rank.items()): # iterating over dictionary elements
            if u[0] != j[0]:
                adjust_count += 1

        # Updating the dictionaries for the next iteration
        if adjust_count > adjust_max:
            rank = updated_rank
            updated_rank = OrderedDict((key, 0) for key in rank)

        elif adjust_count <= adjust_max: # if algorithm converged returns list
            updated_rank = list(updated_rank.items())
            if printer:
                print("\nThe top three players for the given period are:")
                for i in range(3):
                    print("Player: ", updated_rank[i][0], " Score: ", updated_rank[i][1])
            return updated_rank

        if iteration == iteration_max: # if algorithm didn't converge after maximum number of iterations
            print("The algorithm couldn't converge, please modify inputted arguments.")
            break

