from datetime import timedelta
from collections import OrderedDict

def modif_start_date(data):
    """ 
    Auxiliary function that modifies in place the tournament start date of games that started at the beginning of the 
    year but where the tournament has already started last year. Indeed, the question is based on tournament and not 
    games anymore, therefore, we harmonize the tournaments start date, before answering the question. 
    
    Args: 
    
    data: list of list where the inner list contains the game's details
        
    Prerequisite: 
    The dataset should be ordered by firstly tournament name and secondly by tournament start date.
    
    """

    # variables detecting when moving to a new tournament
    tourn = None
    tourn_start_date = None

    for i in range(len(data)):
        if tourn == None and tourn_start_date == None: # initializing tracking variables
            tourn = data[i][0]
            tourn_start_date = data[i][1]

        elif data[i][0] == tourn and data[i][1] != tourn_start_date and abs((data[i][1] - tourn_start_date).total_seconds() / (3600 * 24)) > 30:
            tourn_start_date = data[i][1]

        elif data[i][0] != tourn:
            tourn = data[i][0]
            tourn_start_date = data[i][1]

        # if we iterate over the same tournament name that starts at most 15 days later, we assume that we are in fact
        # dealing with the same tournament
        elif data[i][0] == tourn and data[i][1] != tourn_start_date and abs((data[i][1] - tourn_start_date).total_seconds() / (3600 * 24)) <= 30:
            data[i][1] = tourn_start_date


def wbw_ranking_tourn(data, period, adjust_max=10, iteration_max=100):
    """
    Auxiliary function that will help initialize our WbW ranking for the year 2007. The function returns the ranking
    for a year according to completed tournaments that took place in that given year. The ranking is a list of list where
    the inner list first element consists of the player name and the second element is the player's position within the
    ranking.

    Args:

    data: list of list, where the inner list contains each game details
    period: considered period for the ranking of type int or list
    adjust_max: sets the maximum number of allowed adjustments for convergence (type int and default value 10)
    iteration_max: sets the maximum number of allowed iterations (integer greater than 0 and default value 100). If the
    number of iterations before convergence exceeds iterations_max, the algorithm stops.

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
        if data[i][2].year in period: # focusing on tournaments that ended in the given year
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

    iteration = 0 # iteration counter
    adjust_count = adjust_max + 1 # counts the number of adjustments made before next iteration

    # while loop that stops when the number of adjustment made is lower or equal to the limit
    while adjust_count > adjust_max:

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

        # Obtaining the number of adjustments made over the iteration
        for u, j in zip(rank.items(), updated_rank.items()):
            if u[0] != j[0]:
                adjust_count += 1

        # Updating the dictionaries for the next iteration
        if adjust_count > adjust_max:
            rank = updated_rank
            updated_rank = OrderedDict((key, 0) for key in rank)

        elif adjust_count <= adjust_max: # if algorithm converged returns ranking list
            final_rank = []
            position = 0 # rank counter
            for item in updated_rank:
                position += 1
                final_rank.append([item, position])
            return final_rank

        if iteration == iteration_max: # if algorithm didn't converge after maximum number of iterations
            print("Initializer algorithm couldn't converge, please modify inputted arguments.")
            break


def wbw_ranking_past(data, past_period, days_before, adjust_max=10, iteration_max=100):
    """
    Auxiliary function that returns the WbW ranking of each player based only on tournament that took place before a
    specified date. The ranking is a list of list where the inner list first element consists of the player name
    and the second element is the player's position within the ranking.

    Args:

    data: list of list, where the inner list contains each game details
    past_period: looking at tournaments that occurred before the past_period date (datetime object)
    days_before: controls the window time length for including completed past tournaments (timedelta object)
    adjust_max: sets the maximum number of allowed adjustments for convergence (type int and default value 10)
    iteration_max: sets the maximum number of allowed iterations (integer greater than 0 and default value 100). If the
    number of iterations before convergence exceeds iterations_max, the algorithm stops.

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error() and winner() should be run on the dataset before running the function.

    """

    updated_rank = OrderedDict() # OrderedDict where key is a player with its associated score
    defeated_dic = {} # dictionary where each key is a player and its value is the list of players against whom he lost

    # building updated_rank and defeated_dic variables
    for i in range(len(data)):

        # finding tournaments that occurred before the specified date
        if days_before >= (past_period - data[i][2]) > timedelta(days=0):
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

        # Obtaining the number of adjustments made over the iteration
        for u, j in zip(rank.items(), updated_rank.items()): # iterating over dictionary elements
            if u[0] != j[0]:
                adjust_count += 1

        # Updating the dictionaries for the next iteration
        if adjust_count > adjust_max:
            rank = updated_rank
            updated_rank = OrderedDict((key, 0) for key in rank)

        # if algorithm converged returns list
        elif adjust_count <= adjust_max:
            final_rank = []
            position = 0 # rank counter
            for item in updated_rank:
                position += 1
                final_rank.append([item, position])
            return final_rank

        # if algorithm didn't converge after maximum number of iterations
        if iteration == iteration_max:
            print("The algorithm for the WbW ranking based on the 52 weeks past tournaments couldn't converge, please modify inputted arguments.")
            break


def wbw_comparison(data, adjust_max=10, iteration_max=100, window_time=timedelta(days=364), initializing_year=2007):
    """
    Function that computes the WbW ranking at the start of each tournament based on the tournament that occurred in
    the past 52 weeks by default. Then returns a list of list, where the first element of the list is the calculated WbW
    ranking and its associated WTA ranking. Note that player having not played in the past 52 weeks completed tournaments
    or with unknown WTA ranking are not included in the list of points.

    Args:
    data: list of list, where the inner list contains each game details
    adjust_max: sets the maximum number of allowed adjustments for convergence (type int and default value 10)
    iteration_max: sets the maximum number of allowed iterations (integer greater than 0 and default value 100). If the
    number of iterations before convergence exceeds iterations_max, the algorithm stops.
    window_time: used for establishing the WbW ranking of each player before each tournament (timedelta object)
    initializing_year: considered year for initializing first WbW ranking (type int)

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error() and winner() should be run on the dataset before running the function.

    """

    modif_start_date(data)  # modifying start date of special case tournament
    data.sort(key=lambda x: x[1])  # sorting the data by tournaments start date

    wta_rank = {} # dictionary of players with their associated WTA rank for each tournament
    points = [] # list of points to be returned

    ranking_initialized = False # variable that determines whether the first WbW ranking has been initialized

    # variables detecting when moving to a new tournament
    tournament_name = None
    tournament_start_date = None
    tournament_end_date = None

    # obtaining the WTA ranking for players of the same tournament
    for i in range(len(data)):
        if data[i][2].year > initializing_year:

            # initializing variables
            if tournament_end_date is None and tournament_name is None:
                tournament_name = data[i][0]
                tournament_start_date = data[i][1]
                tournament_end_date = data[i][2]
                wta_rank[data[i][3]] = data[i][5]
                wta_rank[data[i][4]] = data[i][6]

            # constructing wta_rank dictionary
            elif data[i][2] == tournament_end_date and data[i][0] == tournament_name:
                if data[i][3] not in wta_rank and data[i][4] not in wta_rank:
                    wta_rank[data[i][3]] = data[i][5]
                    wta_rank[data[i][4]] = data[i][6]

                elif data[i][3] in wta_rank and data[i][4] not in wta_rank:
                    wta_rank[data[i][4]] = data[i][6]

                elif data[i][3] not in wta_rank and data[i][4] in wta_rank:
                    wta_rank[data[i][3]] = data[i][5]

            # moved to a new tournament
            elif data[i][0] != tournament_name or (data[i][0] == tournament_name and data[i][2] != tournament_end_date):

                # initializing first WbW ranking only once
                if not ranking_initialized:
                    ranking_initialized = True
                    wbw_rank = wbw_ranking_tourn(data, initializing_year, adjust_max, iteration_max)

                    # appending points list
                    for item in wbw_rank:
                        if item[0] in wta_rank and wta_rank[item[0]]: # removing missing values
                            points.append([float(wta_rank[item[0]]), item[1]]) # converts WTA rank to float

                else:
                    # WbW ranking based on completed tournament occurred before tournament start date
                    wbw_rank = wbw_ranking_past(data, tournament_start_date, window_time, adjust_max, iteration_max)

                    # appending points list
                    for item in wbw_rank:
                        if item[0] in wta_rank and wta_rank[item[0]]: # removing missing values
                            points.append([float(wta_rank[item[0]]), item[1]]) # converts WTA rank to float

                # updating variables for next tournament
                wta_rank = {data[i][3]: data[i][5], data[i][4]: data[i][6]}
                tournament_name = data[i][0]
                tournament_start_date = data[i][1]
                tournament_end_date = data[i][2]

    return points
























