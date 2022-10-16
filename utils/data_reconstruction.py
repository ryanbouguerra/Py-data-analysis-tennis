import csv
from datetime import datetime
from glob import iglob
import pickle


def correct_error(data):
    """
    Function that corrects in place the dataset errors. For tournaments beginning at the end of a given year and ending
    the next year, the function considers those end-year games as having wrong tournament end date. It matches the
    tournament end date of those games to the tournament end date of the next year games.

    Args:

    data: list of list where the inner list contains the game's details. Data should be ordered by firstly tournament
    name and secondly by tournament start date.

    """

    # variables detecting when moving to a new tournament
    tournament_name = None
    tournament_start_date = None
    tournament_end_date = None

    for i in reversed(range(len(data))):
        # spotted error: Andrea Petkovic name not standardized for 2008 Australian Open
        if data[i][0] == "Australian Open" and data[i][1] == datetime.strptime("2008-01-14", "%Y-%m-%d").date() \
                and data[i][3] == "Chakvetadze A." and data[i][4] == "Petkovic":
            data[i][4] = "Petkovic A."
            data[i][10] = "Petkovic A. Retired"

        # modifying tournament end date of year-end games for tournaments stretching over two years
        if tournament_name is None and tournament_start_date is None and tournament_end_date is None:
            # initializing tracking variables
            tournament_name = data[i][0]
            tournament_start_date = data[i][1]
            tournament_end_date = data[i][2]

        elif data[i][0] == tournament_name and data[i][1] != tournament_start_date and abs(
                (data[i][1] - tournament_start_date).total_seconds() / (3600 * 24)) > 15:
            tournament_start_date = data[i][1]
            tournament_end_date = data[i][2]

        elif data[i][0] != tournament_name:
            tournament_name = data[i][0]
            tournament_start_date = data[i][1]
            tournament_end_date = data[i][2]

        # if iterate over the same tournament name that starts at most 15 days later, we assume that we are in fact
        # dealing with the same tournament
        elif data[i][0] == tournament_name and data[i][1] != tournament_start_date and abs(
                (data[i][1] - tournament_start_date).total_seconds() / (3600 * 24)) <= 15:
            data[i][2] = tournament_end_date


def winner(data):
    """
    Function that modifies in place the given dataset, and append the winner name to each match list.

    Args:

    data: list of list, where the inner list consists of the game details.

    Prerequisite: run correct_error() before running function

    """

    for match in data:
        if match[10] != "Completed":  # if match not completed, then find which player retired
            if match[-1].split()[-1] == "Retired":
                retired = match[10].split(". ")[0] + "." # obtaining name of player who retired
                if retired == match[3]:
                    match.append(match[4])
                elif retired == match[4]:
                    match.append(match[3])
        elif match[10] == "Completed":  # if match completed, then count who is the first to have won two sets
            player1_set_won = 0
            player2_set_won = 0
            if list(match[7])[0] > list(match[7])[2]:
                player1_set_won += 1
            else:
                player2_set_won += 1

            if list(match[8])[0] > list(match[8])[2]:
                player1_set_won += 1
            else:
                player2_set_won += 1

            if player1_set_won == player2_set_won:  # if both players one a set, then look at third set
                if list(match[9])[0] > list(match[9])[2]:
                    player1_set_won += 1
                else:
                    player2_set_won += 1

            if player1_set_won > player2_set_won:
                match.append(match[3])
            else:
                match.append(match[4])


def round(data, robin_tourn = None):
    """
    Function that modifies in place the given dataset to identify the different rounds of non round robin
    tournaments. The function appends n to the match list for the game taking place at the n round.
    It works by appending a list containing the players that played in previous games of the same tournament.
    When iterating, if one of the player is already in the list, it implies that we moved to the next round and the list
    is reinitialized.

    Args:

    data: list of list, where the inner list consists of the game details.
    robin_tourn: list of round robin tournaments (string) where each tournament within the list never changes to knockout
    tournament over the considered period. If "robin_tourn" not specified, the function uses the list of round robin
    tournaments for single women over the 2007-2021 period (current dataset).

    Prerequisite: the dataset should be ordered by firstly tournament name and secondly by tournament start date.

    """
    if not robin_tourn:
        robin_tourn = ["BNP Paribas WTA Finals", "WTA Finals", "Sony Ericsson Championships",
                      "Qatar Airways Tournament of Champions Sofia", "Garanti Koza WTA Tournament of Champions",
                      "WTA Elite Trophy"]
    robin_excpt = "Commonwealth Bank Tournament of Champions"
    robin_excpt_date = 2009

    # variable keeping track of the tournament
    tournament_name = data[0][0]
    tournament_end_date = data[0][2]
    track_lst = []

    round_counter = 1
    for match in data:
        if (match[3] not in track_lst and match[4] not in track_lst) and match[0] == tournament_name and match[
            2] == tournament_end_date and match[0] not in robin_tourn \
                and (match[0] != robin_excpt or (match[0] == robin_excpt and match[1].year != robin_excpt_date)):
            # still in the same round of the same tournament, just append each player to the list and the round number
            # to the dataset
            track_lst.append(match[3])
            track_lst.append(match[4])
            match.append(round_counter)

        elif (match[3] in track_lst or match[4] in track_lst) and match[0] == tournament_name and match[
            2] == tournament_end_date and match[0] not in robin_tourn \
                and (match[0] != robin_excpt or (match[0] == robin_excpt and match[1].year != robin_excpt_date)):
            # still in the same tournament, but one of the player is already in the list meaning that we moved to the next
            # round
            round_counter += 1  # increment the round
            track_lst = [match[3], match[4]]  # reinitialise list
            match.append(round_counter)

        elif (match[0] != tournament_name or (match[0] == tournament_name and match[2] != tournament_end_date)) and \
                match[0] not in robin_tourn and (
                match[0] != robin_excpt or (match[0] == robin_excpt and match[1].year != robin_excpt_date)):
            # new tournament: updating all variables
            tournament_name = match[0]
            tournament_end_date = match[2]
            round_counter = 1
            track_lst = [match[3], match[4]]
            match.append(round_counter)


def round_robin(data, robin_tourn = None):
    """
    Function that modifies in place the given dataset to identify the different rounds of round robin tournaments.
    For round robin rounds, the function appends the number 1 and "Round robin" to the list of match. For rounds above
    round robins, the function appends the number 2 for the next round, etc. The function is based on the assumption that
    each round robin tournament either consists of two or four round robin groups. In addition, it assumes that the first
    eight games are round robin rounds. Indeed, this functionworks by firstly identifying the different group
    distributions by looking at the first eight games, and then can "safely" recognize whether a game is played at the
    round robin stage or at a later stage.

    Args:

    data: list of list, where the inner list consists of the game details.
    robin_tourn: list of round robin tournaments (string) where each tournament within the list never changes to knockout
    tournament over the considered period. If "robin_tourn" not specified, the function uses the list of round robin
    tournaments for single women over the 2007-2021 period (current dataset).

    Prerequisite: the dataset should be ordered by first tournament name and secondly by tournament start date.

    """

    # variable used for identifying round robin tournament
    if not robin_tourn:
        robin_tourn = ["BNP Paribas WTA Finals", "WTA Finals", "Sony Ericsson Championships",
                      "Qatar Airways Tournament of Champions Sofia", "Garanti Koza WTA Tournament of Champions",
                      "WTA Elite Trophy"]
    robin_excpt = "Commonwealth Bank Tournament of Champions"
    robin_excpt_date = 2009
    tournament_end_date = None

    # variable used for establishing groups
    group_established = False
    first_eight_games = []
    group1, group2, group3, group4 = set(), set(), set(), set()
    unique_player = set()

    # variable used for identifying rounds above round robin round
    round_robin_passed = False
    round_count = 1
    lst_tracker = [] # list that tracks player for next round

    for i in range(len(data)):
        if (data[i][0] in robin_tourn or (data[i][0] == robin_excpt and data[i][1].year ==  robin_excpt_date)) and \
                tournament_end_date is None: # find first round robin tournament
            # update tracking variables
            round_count = 1
            data[i].append(round_count)
            data[i].append("Round robin")
            tournament_end_date = data[i][2]
            first_eight_games = [[data[i][3], data[i][4]]]

        elif (data[i][0] in robin_tourn or (data[i][0] == robin_excpt and data[i][1].year == robin_excpt_date)) \
                and tournament_end_date != data[i][2]: # iterated over a new tournament
            round_count = 1
            data[i].append(round_count)
            data[i].append("Round robin")
            # update tracking variables
            tournament_end_date = data[i][2]
            group_established = False
            round_robin_passed = False
            first_eight_games = [[data[i][3], data[i][4]]]
            lst_tracker = []
            group1, group2, group3, group4, unique_player = set(), set(), set(), set(), set()

        elif (data[i][0] in robin_tourn or (data[i][0] == robin_excpt and data[i][1].year == robin_excpt_date)) \
                and tournament_end_date == data[i][2]:
            # obtaining the first 8 round robin matches to identify groups attribution
            if len(first_eight_games) < 8:
                first_eight_games.append([data[i][3], data[i][4]])
                data[i].append(round_count)
                data[i].append("Round robin")
                unique_player.add(data[i][3])
                unique_player.add(data[i][4])

            # once first 8 matches collected, the groups are established
            elif len(first_eight_games) == 8 and not group_established:
                group_established = True
                data[i].append(round_count)
                data[i].append("Round robin")
                group1.add(first_eight_games[0][0])
                group1.add(first_eight_games[0][1])
                rep = 0 # variable controlling the while loop

                # establishing the first group
                while rep < 2:
                    for k in range(len(first_eight_games)):
                        if first_eight_games[k][0] in group1 or first_eight_games[k][1] in group1:
                            group1.add(first_eight_games[k][0])
                            group1.add(first_eight_games[k][1])
                    rep += 1

                # establishing the second group
                rep = 0
                base_case = 0 # variable that enables the one-time initialization of the second group
                while rep < 2:
                    for k in range(len(first_eight_games)):
                        if first_eight_games[k][0] not in group1 and first_eight_games[k][1] not in group1:
                            if base_case == 0: # initialize second group
                                group2.add(first_eight_games[k][0])
                                group2.add(first_eight_games[k][1])
                                base_case += 1
                            elif first_eight_games[k][0] in group2 or first_eight_games[k][1] in group2:
                                # constructing second group
                                group2.add(first_eight_games[k][0])
                                group2.add(first_eight_games[k][1])
                    rep += 1

                # case if more than two round robin groups
                if (len(group1) + len(group2)) != len(unique_player):
                    rep = 0
                    base_case = 0
                    # establishing the third group
                    while rep < 2:
                        for k in range(len(first_eight_games)):
                            if first_eight_games[k][0] not in group1 and first_eight_games[k][1] not in group1 and \
                                    first_eight_games[k][0] not in group2 and first_eight_games[k][1] not in group2:
                                if base_case == 0: # initialize third group
                                    group3.add(first_eight_games[k][0])
                                    group3.add(first_eight_games[k][1])
                                    base_case += 1
                                elif first_eight_games[k][0] in group3 or first_eight_games[k][1] in group3:
                                    # constructing third group
                                    group3.add(first_eight_games[k][0])
                                    group3.add(first_eight_games[k][1])
                        rep += 1

                    # establishing the fourth group which is assumed to consist of the remaining players
                    for k in range(len(first_eight_games)):
                        if first_eight_games[k][0] not in group1 and first_eight_games[k][1] not in group1 and \
                                first_eight_games[k][0] not in group2 and first_eight_games[k][1] not in group2 and \
                                first_eight_games[k][0] not in group3 and first_eight_games[k][1] not in group3:
                            group4.add(first_eight_games[k][0])
                            group4.add(first_eight_games[k][1])

            # now that groups established, we can safely recognize round robin rounds over next iterations
            elif not round_robin_passed:
                if group3: # if tournament consists of 4 round robin groups

                    if (data[i][3] in group1 and data[i][4] in group1) or (data[i][3] in group2 and data[i][4] in group2) \
                            or (data[i][3] in group3 and data[i][4] in group3) or (data[i][3] in group4 and data[i][4] in group4):
                        data[i].append(round_count)
                        data[i].append("Round robin")

                    elif data[i][4] not in unique_player: # case if player2 replaced by another new player
                        unique_player.add(data[i][4])
                        data[i].append(round_count)
                        data[i].append("Round robin")
                        # finding the group of the new added player
                        if data[i][3] in group1:
                            group1.add(data[i][4])
                        elif data[i][3] in group2:
                            group2.add(data[i][4])
                        elif data[i][3] in group3:
                            group3.add(data[i][4])
                        elif data[i][3] in group4:
                            group4.add(data[i][4])

                    elif data[i][3] not in unique_player: # case if player1 replaced by another new player
                        unique_player.add(data[i][3])
                        data[i].append(round_count)
                        data[i].append("Round robin")
                        # finding the group of the new added player
                        if data[i][4] in group1:
                            group1.add(data[i][3])
                        elif data[i][4] in group2:
                            group2.add(data[i][3])
                        elif data[i][4] in group3:
                            group3.add(data[i][3])
                        elif data[i][4] in group4:
                            group4.add(data[i][3])

                elif not group3: # if tournament consists of 2 round robin groups
                    if (data[i][3] in group1 and data[i][4] in group1) or (data[i][3] in group2 and data[i][4] in group2):
                        data[i].append(round_count)
                        data[i].append("Round robin")

                    elif data[i][4] not in unique_player: # case if player2 replaced by another new player
                        unique_player.add(data[i][4])
                        data[i].append(round_count)
                        data[i].append("Round robin")
                        if data[i][3] in group1:
                            group1.add(data[i][4])
                        elif data[i][3] in group2:
                            group2.add(data[i][4])

                    elif data[i][3] not in unique_player: # case if player1 replaced by another new player
                        unique_player.add(data[i][3])
                        data[i].append(round_count)
                        data[i].append("Round robin")
                        if data[i][4] in group1:
                            group1.add(data[i][3])
                        elif data[i][4] in group2:
                            group2.add(data[i][3])

            # following statements try to figure out if we passed round robin rounds by checking if two players
            # of different groups played against each other

            # case for tournament with 4 round robin groups
            if group3 and data[i][3] in unique_player and data[i][4] in unique_player and ((data[i][3] in group1 and data[i][4] not in group1) or (data[i][3] in group2 and data[i][4] not in group2) or (data[i][3] in group3 and data[i][4] not in group3) or (data[i][3] in group4 and data[i][4] not in group4)):
                if data[i][3] not in lst_tracker and data[i][4] not in lst_tracker and not round_robin_passed:
                    # updating variables to inform the algorithm that round robin stage have been passed
                    round_robin_passed = True
                    round_count += 1
                    lst_tracker.append(data[i][3])
                    lst_tracker.append(data[i][4])
                    data[i].append(round_count)

            # case for tournament with 2 round robin groups
            elif not group3 and data[i][3] in unique_player and data[i][4] in unique_player and ((data[i][3] in group1 and data[i][4] not in group1) or (data[i][3] in group2 and data[i][4] not in group2)):
                if data[i][3] not in lst_tracker and data[i][4] not in lst_tracker and not round_robin_passed:
                    round_robin_passed = True
                    round_count += 1
                    lst_tracker.append(data[i][3])
                    lst_tracker.append(data[i][4])
                    data[i].append(round_count)

            # now that round robin stages have been passed, the method of direct elimination is used to keep track
            # of the different rounds

            # if both players are not in lst_tracker, it means that we are still at the same round
            if round_robin_passed and data[i][3] not in lst_tracker and data[i][4] not in lst_tracker:
                lst_tracker.append(data[i][3])
                lst_tracker.append(data[i][4])
                data[i].append(round_count)

            # when one of the player is already in lst_tracker, it means that we moved to the next round
            elif round_robin_passed and (data[i][3] in lst_tracker or data[i][4] in lst_tracker) and \
                    lst_tracker != [data[i][3], data[i][4]]: # to avoid double initialization
                lst_tracker = [data[i][3], data[i][4]]
                round_count += 1
                data[i].append(round_count)


def proper_round(data):
    """
    Function that modifies in place the given dataset to give appropriate name to each tournament rounds. This
    function is extremely useful for functions such as who_won_final, since it allows them to be straightforward and
    have a linear running time. Moreover, it doesn't modify the 12th element of each list, so it can be used to directly
    answer question 3, while the 13th element of each list will be used for functions answering questions on the
    dataset (who_won_final, which_round...).

    Arg:

    data: list of list, where the inner list consists of the game details.

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error(), winner(), round() and round_robin() should be run on the dataset before running the function.

    """

    # variables used for detecting when moving to a new tournament
    tournament_name = data[-1][0]
    tournament_end_date = data[-1][2]
    round_count = data[-1][12]

    # Assuming data is sorted
    data[-1].append("Final")
    for i in reversed(range(len(data) - 1)):

        # detecting third place match
        if abs((data[i + 1][12] - data[i][12])) > 1 and data[i - 1][12] == data[i][12]:
            data[i - 1].append("Third place match")

        # moving to a new tournament
        if data[i][0] != tournament_name or (data[i][0] == tournament_name and data[i][2] != tournament_end_date):
            tournament_name = data[i][0]
            tournament_end_date = data[i][2]
            round_count = data[i][12]
            data[i].append("Final")

        # iterating over same tournament
        elif data[i][0] == tournament_name and data[i][2] == tournament_end_date:
            if data[i][12] == round_count - 1 and (round_count - 1) > 0 and data[i][-1] != "Round robin" and data[i][-1] != "Third place match":
                data[i].append("Semifinals")

            elif data[i][12] == round_count - 2 and (round_count - 2) > 0 and data[i][-1] != "Round robin" and data[i][-1] != "Third place match":
                data[i].append("Quarterfinals")

            elif data[i][-1] != "Round robin" and data[i][-1] != "Third place match":
                data[i].append(data[i][12])


def who_won_final(data, tournament_name, tournament_year, printer=True):
    """
    Function that returns the winner of the considered tournament.

    Args:

    data: list of list, where the inner list consists of the game details
    tournament_name: the considered tournament name (string)
    tournament_year: the given year when the tournament took place (string or int)
    printer: if set to True (default value), the function prints the winner of the given tournament.

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error(), winner(), round(), round_robin() and proper_round() should be run on the dataset before running the
    function.

    """

    found = False # determines whether the winner has been found
    for i in range(len(data)):
        if data[i][0] == tournament_name and data[i][2].year == tournament_year and data[i][13] == "Final":
            if printer == True:
                print("The winner of the", tournament_year, tournament_name, "is", data[i][11])
            return data[i][11]

    if not found:
        if printer == True:
            print("The algorithm didn't find the winner. Please check the given year, tournament name and round.")



def who_played_who(data, tournament_name, tournament_year, round):
    """
    The function prints the different confrontations for the given tournament round.

    Args:

    data: list of list, where the inner list consists of the game details.
    tournament_name: the considered tournament name (string)
    tournament_year: the given year when the tournament took place (string or int)
    round: the considered round of type int or string which can be "Quarterfinals, Semifinals, Final"

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error(), winner(), round(), round_robin() and proper_round() should be run on the dataset before running the
    function.

    """

    found = False
    if type(tournament_year) == str:
        tournament_year = int(tournament_year)

    if type(round) == int:
        print("\nThe confrontations for the round", round, "of the", tournament_year, tournament_name, "are:")
    elif type(round) == str and round != "Final" and round != "Third place match":
        print("\nThe confrontations for the", round, "of the", tournament_year, tournament_name, "are:")
    if round == "Final" or round == "Third place match":
        print("\nThe confrontation for the", round, "of the", tournament_year, tournament_name, "is:")

    for i in range(len(data)):
        if data[i][0] == tournament_name and data[i][2].year == tournament_year and data[i][13] == round:
            found = True
            print([data[i][3], data[i][4]])

    # case when confrontations are quarterfinals, or semifinals or final and the inserted round is of type int
    if not found:
        for i in range(len(data)):
            if data[i][0] == tournament_name and data[i][2].year == tournament_year and data[i][12] == round:
                found = True
                print([data[i][3], data[i][4]])
        if not found:
            print("The algorithm didn't find the required confrontations. Please check the given year, tournament name and round.")

def which_round(data, player, tournament_name, tournament_year):
    """
    Function that prints the round in which the player has been eliminated from the given tournament.

    Args:

    data: list of list, where the inner list consists of the game details
    player: considered player of type string=
    tournament_name: the considered tournament name (string)
    tournament_year: the given year when the tournament took place (string or int)

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error(), winner(), round(), round_robin() and proper_round() should be run on the dataset before running the
    function.
    """
    print("\n")
    if type(tournament_year) == str:
        tournament_year = int(tournament_year)
    for i in reversed(range(len(data))):
        if data[i][0] == tournament_name and data[i][2].year == tournament_year:
            if (data[i][3] == player or data[i][4] == player) and data[i][11] != player:
                if data[i][13] != "Round robin":
                    if type(data[i][13]) == int:
                        print(player, "was eliminated from the", tournament_year, tournament_name, "at the round",
                              data[i][13])
                        break
                    elif type(data[i][13]) == str:
                        print(player, "was eliminated from the", tournament_year, tournament_name, "at the",
                              data[i][13])
                        break
                elif data[i][13] == "Round robin":
                    # avoiding case where winner of the tournament lost a game in the robin rounds
                    if who_won_final(data, tournament_name, tournament_year, False) == player:
                        print(player, "won the", tournament_year, tournament_name)
                        break
                    else:
                        print(player, "was eliminated from the", tournament_year, tournament_name, "at the round robin stage.")
                        break

            # moving to the next tournament after having iterated through all possible games either player all games
            elif data[i-1][0] != tournament_name or (data[i-1][0] == tournament_name and data[i-1][2].year != tournament_year):
                # case where player won all of his games
                if who_won_final(data, tournament_name, tournament_year, False) == player:
                    print(player, "won the", tournament_year, tournament_name)
                    break

                else:
                    print("The algorithm didn't find the round. Please check the given year, tournament name and player name.")
                    break

def round_played(data, player, round):
    """
    Function that prints the number of time a given player played in a given round.

    Args:

    data: list of list, where the inner list consists of the game details
    player: considered player of type string
    round: the considered round of type int or string which can be "Quarterfinals, Semifinals, Final"

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error(), winner(), round(), round_robin() and proper_round() should be run on the dataset before running the
    function.

    """

    round_counter = 0
    print("\n")
    if type(round) == str:
        for i in range(len(data)):
            if (data[i][3] == player or data[i][4] == player) and round == data[i][13]:
                round_counter += 1
        print(player, "played", round_counter, round)
    elif type(round) == int:
        for i in range(len(data)):
            if (data[i][3] == player or data[i][4] == player) and round == data[i][12]:
                round_counter += 1
        print(player, "played", round_counter, "round", round)

def two_players_games(data, player1, player2):
    """
    Function that prints how many games player1 played against player2, and how many times player1 won and player 2 won.

    Args:
    data: list of list, where the inner list consists of the game details
    player1, player2: considered players of type string

    Prerequisite:
    The dataset should be ordered by first tournament name and secondly by tournament start date.
    correct_error(), winner(), round(), round_robin() and proper_round() should be run on the dataset before running the
    function.
    """
    total_games = 0
    player1_count = 0
    print("\n")
    for i in range(len(data)):
        if (data[i][3] == player1 and data[i][4] == player2) or (data[i][3] == player2 and data[i][4] == player1) :
            total_games += 1
            if data[i][11] == player1:
                player1_count += 1
    if total_games != 0:
        print(player1, "played against", player2, total_games, "times and", player1, "won",
              player1_count, "of these games and", player2, "won", (total_games-player1_count), "of these games.")
    elif total_games == 0:
        print(player1, "never played against", player2)


# Building dataset
file_path = '../assignment-final-data/*.csv'
dataset = [] # dataset that will store each tennis game details

for file in iglob(file_path): # iterating over the different csv files in the folder
    with open(file, "r") as f:
        csvreader = csv.reader(f) # reading the csv files
        header = next(csvreader) # skipping the headers
        for row in csvreader:
            tournament, start, end, bestOf, player1, player2, rank1, rank2, set1, set2, set3, comment = row
            dataset.append([tournament.strip(), datetime.strptime(start, "%Y-%m-%d").date(),
                         datetime.strptime(end, "%Y-%m-%d").date(), player1.strip(), player2.strip(), rank1, rank2,
                         set1.strip(), set2.strip(), set3.strip(), comment.strip()]) # appending the dataset

dataset.sort(key=lambda x: (x[0], x[1]))  # sorting the data by tournament and date
correct_error(dataset) # correcting dataset errors
winner(dataset)  # determine each winner for each game
round(dataset)  # determining the round of the match being played
round_robin(dataset)  # determining the round of round robin tournament
proper_round(dataset) # setting proper name for tournaments

# Converting dataset into pickle object
with open('dataset', 'wb') as fw:
    pickle.dump(dataset, fw)







