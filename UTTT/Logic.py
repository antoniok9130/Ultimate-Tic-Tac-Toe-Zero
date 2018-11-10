#cython: language_level=3, boundscheck=False
import sys

import numpy as np

P1 = 1
P2 = 2
N = 0
T = -1
B = (P1 | P2) # Note that (P1 | P2) == B

if B == P1 or B == P2:
    raise Exception("B == P1 or B == P2")

triple0 = ((1, 2), (3, 6))
triple4 = ((3, 5), (1, 7), (0, 8), (2, 6))
triple8 = ((6, 7), (2, 5))

pairs = (((1, 2), (3, 6), (4, 8)),
        ((0, 2), (4, 7)),
        ((0, 1), (5, 8), (4, 6)),
        ((0, 6), (4, 5)),
        ((0, 8), (1, 7), (2, 6), (3, 5)),
        ((2, 8), (3, 4)),
        ((0, 3), (2, 4), (7, 8)),
        ((1, 4), (6, 8)),
        ((6, 7), (2, 5), (0, 4)))

def check3InRow(array): # , position = -1
    # if (position > -1):
    #     for pair in pairs[position]:
    #         if (array[position] == array[pair[0]] and array[pair[0]] == array[pair[1]]):
    #             return True
    #
    #     return False

    checkTie = 1
    if (array[0] != N):
        for triple in triple0:
            if (array[0] == array[triple[0]] and array[triple[0]] == array[triple[1]]):
                return array[0]
    else:
        checkTie = 0

    if (array[4] != N):
        for triple in triple4:
            if (array[4] == array[triple[0]] and array[triple[0]] == array[triple[1]]):
                return array[4]
    else:
        checkTie = 0

    if (array[8] != N):
        for triple in triple8:
            if (array[8] == array[triple[0]] and array[triple[0]] == array[triple[1]]):
                return array[8]
    else:
        checkTie = 0

    return T if (checkTie == 1 and array[1] != N and array[2] != N and array[3] != N and
                                   array[5] != N and array[6] != N and array[7] != N) \
             else N

def checkTie(array):
    for i in array:
        if (i == N):
            return False

    return True

    
def check3InRowAt(array, position):    
    for p0, p1 in pairs[position]:
        if (array[position] == array[p0] and array[p0] == array[p1]):
            return True

    return False


def potential3inRow(array, position, player = None):
    if player is None:
        potential = N
        for p0, p1 in pairs[position]:
            if array[p0] != N and \
                    array[p0] == array[p1]:
                if potential != N and potential != array[p0]:
                    return B

                potential = array[p0]

        return potential

    else:
        for p0, p1 in pairs[position]:
            if array[p0] == player and \
                    array[p0] == array[p1]:
                return True

        return False


def updatePotential3inRow(potential, array, position):
    player = array[position]
    if player != N:
        for pair in pairs[position]:
            if player == array[pair[0]]:
                potential[pair[1]] |= player
            elif player == array[pair[1]]:
                potential[pair[0]] |= player




def getBoardSymbol(value, simple = True):
    if (value == P1):
        return "X"
    if (value == P2):
        return "O"
    if (value == T):
        return "T"

    return "_" if simple else " "


def getRandomRemaining(quadrant):
    for r in np.random.randint(low=0, high=9, size=25):
        if (quadrant[r] == N):
            return r

    print("Could not find Random Remaining for: ", quadrant)
    print(quadrant[0] == N)
    raise Exception("")


def checkInstantWin(potentialQuadrants, quadrants, board, g, player):
    if quadrants[g] == N and potentialQuadrants[g] == player or potentialQuadrants[g] == B:
        for l in range(9):
            if board[g][l] == N and check3InRowAt(board[g], l):
                return True

    return False


def simulation(state, policy):
    """
    Parameters
    ----------
    state : UTTT_Node
        The game state
    """
    winner = state.winner

    quadrants = state.buildQuadrant()
    board     = state.buildBoard2D()

    numRemainingQuadrants = 0
    numRemainingBoard = np.zeros(9, dtype=int)
    potentialQuadrants = np.zeros(9, dtype=int)

    for i, quadrant in enumerate(quadrants):
        if quadrant == N:
            numRemainingQuadrants += 1
            potentialQuadrants[i] = potential3inRow(quadrants, i)
            numRemainingBoard[i] += sum([1 for j in board[i] if j == N])

    move = state.move
    player = state.getPlayer()

    length = -1

    while winner == N:
        length += 1

        if move is not None and quadrants[move[1]] == N:
            if checkInstantWin(potentialQuadrants, quadrants, board, move[1], player):
                winner = player
                break
        
        else:
            for g in range(9):
                if checkInstantWin(potentialQuadrants, quadrants, board, g, player):
                    winner = player
                    break

            if winner != N:
                break

        try:
            g, l = policy(move, quadrants, board)
        except:
            print(move)
            print(quadrants)
            print(numRemainingBoard)
            printBoard(board, quadrants)
            raise Exception("Exception was thrown")

        board[g][l] = player
        numRemainingBoard[g] -= 1

        move = (g, l)

        if check3InRowAt(board[g], l):
            quadrants[g] = player
            numRemainingQuadrants -= 1

            updatePotential3inRow(potentialQuadrants, quadrants, g)

            if check3InRowAt(quadrants, g):
                winner = player
                break

            elif numRemainingQuadrants == 0:
                winner = T
                break

        elif numRemainingBoard[g] <= 0:
            quadrants[g] = T
            numRemainingQuadrants -= 1

            if numRemainingQuadrants == 0:
                winner = T
                break


        player = P2 if player == P1 else P1

    return winner, length



verticalSpace = "     │   │    ║    │   │    ║    │   │    "
verticalDivide = "  ───┼───┼─── ║ ───┼───┼─── ║ ───┼───┼─── "
bigVerticalDivide = " ═════════════╬═════════════╬═════════════"

def printBoard(board, quadrant, simple = False):
    if simple:
        for a in range(3) :
            for b in range(3) :
                for c in range(3) :
                    for d in range(3):
                        print(getBoardSymbol(board[3 * a + c][3 * b + d], simple), end="")

                    print("  ", end="")

                if (a == 0) :
                    print("   ", end="")
                    for d in range(3):
                        print(getBoardSymbol(quadrant[3 * b + d], simple))

                print()

            print()

    else :
        print()
        for a in range(3):
            if (a != 0):
                print(bigVerticalDivide)

            print(verticalSpace)
            for b in range(3):
                if (b != 0):
                    print(verticalDivide)

                print("  ", end="")
                for c in range(3):
                    if (c != 0):
                        print(" ║ ", end="")

                    for d in range(3):
                        if (d != 0):
                            print("│", end="")

                        print(" "+getBoardSymbol(board[3 * a + c][3 * b + d], simple)+" ", end="")


                print(" ")

            print(verticalSpace)

        print()





