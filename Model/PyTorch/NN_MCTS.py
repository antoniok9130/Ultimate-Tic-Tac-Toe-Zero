import time

import numpy as np
import torch

import sys
sys.path.append("..\..\Game\Python")

from UTTT_Logic import *
from MCTS_Logic import *
from NN_MCTS_Node import *


def board_to_input(board):
    array = np.zeros(81, dtype=np.double)

    for i in range(9):
        for j in range(9):
            spot = board[i][j]

            if spot == P1:
                array[9*i+j] = 1.
            elif spot == P2:
                array[9*i+j] = -1.

    return np.reshape(array, (-1, 1, 9, 9))

class NN_MCTS:
    def __init__(self, model1=None, model2=None):
        self.model1 = model1
        self.model2 = model2

        if self.model1 is None:
            self.model1 = UTTT_Model()
            self.model1.load_state_dict(torch.load("./ModelInstances/uttt_genetic_model1"))
            self.model1.eval()

        if self.model2 is None:
            self.model2 = UTTT_Model()
            self.model2.load_state_dict(torch.load("./ModelInstances/uttt_genetic_model2"))
            self.model2.eval()

        self.player = None

    def getMove(self, node, iterations=3200):
        AIPlayer = P2 if node.getPlayer() == P1 else P1
        self.player = AIPlayer
        quadrants = np.zeros(9, dtype=int)
        node.buildQuadrant(quadrants)
        if node.getNextQuadrant() != -1:
            if potential3inRow(quadrants, node.getNextQuadrant(), AIPlayer):
                quadrant = np.zeros(9, dtype=int)
                node.buildQuadrant(quadrant, node.getNextQuadrant())
                for i, q in enumerate(quadrant):
                    if q == N and potential3inRow(quadrant, i, AIPlayer):
                        return [node.getNextQuadrant(), i]

        else:
            for i, q in enumerate(quadrants):
                if q == N and potential3inRow(quadrants, i, AIPlayer):
                    quadrant = np.zeros(9, dtype=int)
                    node.buildQuadrant(quadrant, i)
                    for j, q1 in enumerate(quadrant):
                        if q1 == N and potential3inRow(quadrant, j, AIPlayer):
                            return [i, j]


        # thinkingTime *= 1000
        # end = time.time()+thinkingTime

        # print("{0} + {1} = {2}".format(time.time(), thinkingTime, end))
        i = 0
        while (i < iterations):
            self.select(node)
            i += 1

        if node.getNumVisits() == 0:
            raise Exception("No Move found...")

        # print("Search Space Size:  {0}".format(node.getNumVisits()))
        return self.getChildVisitedMost(node).getMove()


    def getChildVisitedMost(self, node):
        mostVisited = 0
        index = -1
        for i, child in enumerate(node.getChildren()):
            if child.getNumVisits() > mostVisited or \
                    (child.getNumVisits() == mostVisited and np.random.rand(1) > 0.5):
                mostVisited = child.getNumVisits()
                index = i

        return node.getChild(index)


    def getChildHighestUCT(self, node):
        highestUCT = 0
        index = -1
        for i, child in enumerate(node.getChildren()):
            if child.getUCT() > highestUCT or \
                    (child.getUCT() == highestUCT and np.random.rand(1) > 0.5):
                highestUCT = child.getUCT()
                index = i

        return node.getChild(index)


    def select(self, node):
        if not node.hasChildren():
            node.init()

            if node.getWinner() != N:
                self.backpropogate(node, [1, 0] if node.getWinner() == P1 else [0, 1])

            elif node.hasMove() and node.getNumVisits() == 0:
                self.backpropogate(node, self.runSimulation(node))

            else:
                self.expand(node)

        else:
            self.select(self.getChildHighestUCT(node))



    def expand(self, node):
        if not node.hasChildren():
            numChildren = 0
            legalMoves = []
            allQuadrants = np.zeros(9, dtype=int)
            node.buildQuadrant(allQuadrants)

            if node.hasMove() and allQuadrants[node.getLocal()] == N:
                nextQuadrant = np.zeros(9, dtype=int)
                node.buildQuadrant(nextQuadrant, node.getLocal())
                for i, q in enumerate(nextQuadrant):
                    if q == N:
                        legalMoves.append((node.getLocal(), i))

            else:
                board = np.zeros((9, 9))
                node.buildBoard2D(board)
                for i, aQ in enumerate(allQuadrants):
                    if aQ == N:
                        for j in range(9):
                            if board[i][j] == 0:
                                legalMoves.append([i, j])

            if len(legalMoves) > 0:
                node.initChildren()

                for i, legalMove in enumerate(legalMoves):
                    node.addChild(NN_MCTS_Node(legalMove, node, False))

                random = node.getChild(np.random.choice(len(node.getChildren()), size=1)[0])
                self.backpropogate(random, self.runSimulation(random))



    def runSimulation(self, node):
        node.init()
        board = np.zeros((9, 9))
        node.buildBoard2D(board)
        
        input_tensor = torch.from_numpy(board_to_input(board))

        if self.player == P1:
            return list(self.model1.predict(input_tensor))

        else:
            return list(self.model2.predict(input_tensor))



    def backpropogate(self, node, probabilities):

        if node.getParent() is not None:
            self.backpropogate(node.getParent(), probabilities)

        node.updateUCT(probabilities)
