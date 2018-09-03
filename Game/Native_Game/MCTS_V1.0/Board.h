//
// Created by Antonio on 2018-04-18.
//

#ifndef ULTIMATE_TIC_TAC_TOE_ZERO_BOARD_H
#define ULTIMATE_TIC_TAC_TOE_ZERO_BOARD_H

#include <array>
#include <iostream>
#include <list>
#include <memory>
#include <string>
#include <vector>

#define For(a, b) for (int i = a; i < b; ++i)
#define Forj(a, b) for (int j = a; j < b; ++j)

extern const int P1;
extern const int P2;
extern const int N;
extern const int T;

typedef std::array<int, 9> Quadrant;
typedef std::array<Quadrant, 9> Board2D;
typedef unsigned int uint;

struct Move {
    int first;
    int second;

    Move(int first, int second);
    Move(const Move& other);
    Move(Move&& other);
};

// class Board {
// public:
//     int length;
//     explicit Board(int length = 0);
// };

std::string getBoardSymbol(const int& value);

int check3InRow(const Quadrant& quadrant);

void getRemaining(Quadrant& quadrant, std::vector<int>& remaining);
int& getRandomRemaining(std::vector<int>& remaining);
bool remainingContains(std::vector<int>& remaining, const int& q);
void removeFromRemaining(std::vector<int>& remaining, const int& n);

std::unique_ptr<Quadrant> make_Quadrant();
std::unique_ptr<Board2D> make_Board2D();
Quadrant make_Quadrant(Quadrant& quadrant);
Board2D make_Board2D(Board2D& board);

std::ostream& operator<<(std::ostream& out, Board2D& board);

std::ostream& operator<<(std::ostream& out, std::vector<size_t>& v);
template <typename T>
std::ostream& operator<<(std::ostream& out, std::list<T>& l);

#endif  // ULTIMATE_TIC_TAC_TOE_ZERO_BOARD_H
