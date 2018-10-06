
import sys
sys.path.append("..\..\Game\Python")

import numpy as np
import torch

from UTTT_Logic import N, P1, P2, check3InRowAt, check3InRow
from random import shuffle
from Model import *


def board_to_input(board):
    array = np.zeros(180, dtype=np.double)

    for i in range(9):
        for j in range(9):
            spot = board[i][j]

            if spot == P1:
                array[9*i+j] = 1.
            elif spot == P2:
                array[90+9*i+j] = 1.

        quadrant = check3InRow(board[i])

        if quadrant == P1:
            array[81+i] = 1.
        elif quadrant == P2:
            array[171+i] = 1.

    return array


# array = np.zeros(180)
#
# if player == P1:
#     array[9 * g + l] = 1
# else:
#     array[90 + 9 * g + l] = 1
#
# if quadrants[g] == P1:
#     array[81 + g] = 1
# elif quadrants[g] == P2:
#     array[171 + g] = 1

with open("./Data/RecordedGames.txt") as recordedGames:

    data = []

    for recordedGame in recordedGames:

        game_data = []

        game = list(recordedGame.strip())

        board = np.zeros((9, 9))
        quadrants = np.zeros(9)

        i = 0
        player = N
        while i < len(game):

            player = P2 if player == P1 else P1

            g = int(game[i])
            l = int(game[i+1])

            board[g][l] = player
            quadrants[g] = check3InRowAt(board[g], l)

            rotated = np.copy(board)
            game_data.append((rotated, i))
            flipped = np.fliplr(board)
            game_data.append((flipped, i))
            for _ in range(3):
                rotated = np.rot90(rotated)
                game_data.append((rotated, i))
                flipped = np.rot90(flipped)
                game_data.append((flipped, i))


            i += 2

        winner = check3InRow(quadrants)

        for state, length in game_data:
            reward = 0.5+0.5*(length+1)/len(game)
            penalty = 1-reward

            data.append([board_to_input(state), np.array([reward, penalty] if winner == P1 else [penalty, reward])])




    shuffle(data)

    data = np.reshape(data, [-1, 50, 2])
    print(len(data))

    input, label = zip(*data[0])
    print(type(np.array(input)))
    print(type(np.array(label)))
    # print(data[0])

    model = UTTT_Model()
    model.load_state_dict(torch.load("./ModelInstances/uttt_model1"))
    model.eval()



    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)


    running_loss = 0.0
    for i, d in enumerate(data):
        # get the inputs
        input, label = zip(*d)

        input_tensor = torch.from_numpy(np.array(input))
        # output_tensor = torch.tensor(np.array(label)).long()
        output_tensor = torch.from_numpy(np.array(label))
        # output_tensor = torch.autograd.Variable(torch.tensor(np.array(label)).long(), requires_grad = False)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = model.forward(input_tensor)
        loss = criterion(outputs, output_tensor)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 25 == 0:  # print every 2000 mini-batches
            print('loss:  {0}'.format(running_loss / 25))
            running_loss = 0.0

    torch.save(model.state_dict(), "./ModelInstances/uttt_model1_trained")