import sys
import numpy as np
from numpy import random
import functools
import heapq
from collections import deque
import datetime
import math

#--------- REPRESENTATION BEGIN --------
representation = """
        h  d  s  c
ace  [[ 0  1  2  3]  = 11pts     h = hearts
ten   [ 4  5  6  7]  = 10pts     d = diamonds
king  [ 8  9 10 11]  = 4pts      s = spades
queen [12 13 14 15]  = 3pts      c = clubs
jack  [16 17 18 19]] = 2pts
For example: '10' is 'king of spades'
"""
#--------- REPRESENTATION END   --------

#--------- HELPER FUNCTIONS BEGIN--------


def get_points(cardA):
    g = np.arange(20).reshape(5, 4) #this produces the same grid as the representation, for the purpose of checking moves
    if (np.any(g[0] == cardA)): #Ace (11)
        return 11
    elif (np.any(g[1] == cardA)): #Ten (10)
        return 10
    elif (np.any(g[2] == cardA)): #King (4)
        return 4
    elif (np.any(g[3] == cardA)): #Queen (3)
        return 3
    elif (np.any(g[4] == cardA)): #Jack (2)
        return 2

def valid_move(cardA, cardB):
    #print("validMove: comparing " + str(cardA) + " to " + str(cardB)) UNCOMMENT THIS TO SEE WHICH CARDS ARE BEING COMPARED
    g = np.arange(20).reshape(5, 4) #this produces the same grid as the representation, for the purpose of checking moves
    if check_value(cardA, cardB, g):
        return True
    elif check_suit(cardA, cardB, g):
        return True
    else:
        #print("validMove: No move found")
        return False

def check_suit(cardA, cardB, grid):
    r, c = grid.shape
    for i in range(c):
        if np.any(grid[:, i] == cardA) and np.any(grid[:, i] == cardB):
            return True

def check_value(cardA, cardB, grid):
    r, c = grid.shape
    for i in range(r):
        if np.any(grid[i] == cardA) and np.any(grid[i] == cardB):
            return True

def pick_cards(seed, size):
    random.seed(seed)
    cards = np.random.choice(20, (size*2), replace = False)
    leftHand = cards[:size]
    rightHand = cards[size:]
    return (leftHand, rightHand)

def memoize(fn, slot=None, maxsize=32):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, use lru_cache for caching the values."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)

    return memoized_fn

identity = lambda x: x
def argmin_random_tie(seq, key=identity):
    """Return an element with highest fn(seq[i]) score; break ties at random."""
    return min(shuffled(seq), key=key)

def shuffled(iterable):
    """Randomly shuffle a copy of iterable."""
    items = list(iterable)
    random.shuffle(items)
    return items



def exportToText(*args):
    with open(args[0], "w") as f:
        for argument in args:
            f.write("{}\n".format(argument))



#--------- HELPER FUNCTIONS END --------

#--------- Game State BEGIN --------
class GameState:
    """Every node in the search tree corresponds to a game state. Every edge in the search tree, represent a card played.
    In every game state there is
    - the cards from the left hand (array filled with integers that represent cards)
    - the cards from the right hand (array filled with integers that represent cards)
    Consider the stack as a literal pile of cards,
    the card on top of the stack is the one for which the card from either the left or right hand must match in either suit or value!"""
    def __init__(self, leftHand, rightHand, playLeft=True, initialStateTest=False, pointsScored = 0):
        self.leftHand = leftHand #left hand is a list
        self.rightHand = rightHand #right hand is a list
        self.playLeft = playLeft #playleft is a boolean value to (help) determine from which hand we must lay a card (More specifically, it shows wether we play from the left hand). When left has laid a card, this value will be switched to False, when right has laid a card this value will be switched to True
        self.initialStateTest = initialStateTest #this is implemented to make it easy to check if the state is the initial state (where every move is a valid move). It is used in class 'Problem', at 'actions'
        self.pointsScored = pointsScored
        self.allCards = [i for i in self.leftHand]
        self.allCards.extend([i for i in self.rightHand])
        self.allCardPoints = [get_points(i) for i in self.allCards]
        #self.printState()


    def printState(self):
        print("------")
        print("GameState: Printing state: ")
        print("Left hand: {}".format(self.leftHand))
        print("Right hand: {}".format(self.rightHand))
        print("Do we play from left hand to get to next state? {}".format(self.playLeft))
        print("Points scored: {}".format(self.pointsScored))
        print("All cards: {}".format(self.allCards))
        print("All card points: {}".format(self.allCardPoints))
        print("------")
#--------- Game State END   --------

#--------- PROBLEM CLASS BEGIN --------
class Problem:
    """The class for a formal problem."""

    def __init__(self, initial):
        """The constructor specifies the initial state"""
        self.initial = initial
        self.winPoints = math.ceil((len(self.initial.leftHand) * 6.6)) #Win points = hand size * 6.6

    def actions(self, state, solution):
        """Return a list of actions that can be executed in the given state.
        In this case, the list of cards for which there is a legal move, is returned"""

        possibleMoves = []
        if state.initialStateTest: #By default it is set to false, therefore it is only True if we explicitly set it to be (when defining initial state). At the initial state every move is a valid move.
            return state.leftHand #All cards in the left hand are returned as valid moves (without checking, because there is nothing to check against)
        elif state.playLeft: #If it is not the initial state, we can play the game as we normally would (with checking for valid moves!). Here we check if we have to play from the left hand.
            for i in state.leftHand: #iterate through every card in left hand
                if valid_move(solution[-1], i): #check if there is a valid move for that card (i)
                    possibleMoves.append(i) #if the check passes, add the card to the list of possibly played cards.
            return possibleMoves #return the list of possible moves from left hand
        else: #If it is not the initial state, we can play the game as we normally would (with checking for valid moves!). Here we check if we have to play from the right hand.
            for i in state.rightHand: #iterate through every card in your hand
                if valid_move(solution[-1], i): #state.playedCards[-1] gets you the item on top of the stack without popping. (we want to compare the card to the last card played)
                    possibleMoves.append(i) #this adds the card for which there is a valid move to the list of cards that can be played. 'extend' is a way of appending to a list
            return possibleMoves #return the list of possible moves from right hand


    def result(self, state, action, solution):
        #in result, the state is returned that results from executing (one of the) moves from Actions (above).
        """Return the state that results from executing the given action in the given state. The 'action' is one of the cards from the list implemented above"""
        #this is the state now (originalstate), we get an action (cardPlayed), return the state how we want it to be after that action.
        #cardPlayed = 'card played in original state'

        originalState = state
        cardPlayed = action  #cardPlayed = 'card played in original state'
        lmPoints = get_points(action) #points from last move
        totalPoints = originalState.pointsScored + lmPoints #compute the amount of points so far, add points from last move to total
        newHand = [] #make a new list


        if (originalState.playLeft): #if the card played in original state was from the left hand, we know the card should be removed from that hand and placed on top of the stack of played cards.
            for i in originalState.leftHand:
                if i == cardPlayed: #if the card we're looking at is the one that should be removed
                    pass       # then don't add it to the new hand for the new state, but add it to the top of the played cards stack.
                else:
                    newHand.append(i) #add every other card (that has not been played) to the new hand for the new state
            return GameState(newHand, originalState.rightHand, False, False, totalPoints) #this returns a gamestate object with as parameters (in order): new left hand, original right hand, next move will NOT be from left hand, we are NOT in initial state, the last played card(s))


        else: #when it is not the initial state, and it is not left hand turn
            for i in originalState.rightHand:
                if i == cardPlayed:
                    pass
                else:
                    newHand.append(i)

            return GameState(originalState.leftHand, newHand, True, False, totalPoints) #this returns a gamestate object with as parameters (in order): new left hand, original right hand, next move WILL be from left hand, we are NOT in initial state, the last played card(s)


    def goal_test(self, state):
        """Return True if the state is a goal. Namely, when the points scored are more than the points needed to win"""
        #The game is defined to have left play first. If left plays first, right lays down the last card
        #if (len(state.rightHand)==0):
        #    return True

        if state.pointsScored >= self.winPoints:
            return True

        ## if points so far is more or equal to win points we're done

        #when both hands are empty the game is done.

    def path_cost(self, c, state1, action, state2, depth):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return (get_points(action) * (6-depth) + c) #COST IMPORTANT FOR BEST FIRST SEARCH
        #return c + 1 #for UNIFORM COST

    def value(self, state):
        """For optimization problems, each state has a value. Hill Climbing
        and related algorithms try to maximize this value."""
        #if state.initialStateTest:

        return (self.winPoints - state.pointsScored)

    def h(self, node):
        return  (self.winPoints - node.state.pointsScored)
#--------- PROBLEM CLASS END   --------

#--------- NODE CLASS BEGIN --------
class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state. Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node. Other functions
    may add an f and h value;"""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        self.nodeName = np.array_str(np.array(self.state.leftHand)) + np.array_str(np.array(self.state.rightHand))
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.nodeName) #self.state by default

    def __lt__(self, node):
        #return self.state < node.state
        return False

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state, self.solution())]


    def child_node(self, problem, action):
        next_state = problem.result(self.state, action, self.solution())
        next_node = Node(next_state, self, action, problem.path_cost(self.path_cost, self.state, action, next_state, self.depth))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def pointsSoFar(self):
        """Return the amount of points obtained so far"""
        movesByPoints = [get_points(node.action) for node in self.path()[1:]]
        sum = 0
        for i in movesByPoints:
            sum += i
        return sum

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(self.state)
#--------- NODE CLASS END   --------

#-------- PRIORITY QUEUE CLASS BEGIN -----
class PriorityQueue:
    """A Queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first.
    If order is 'min', the item with minimum f(x) is
    returned first; if order is 'max', then it is the item with maximum f(x).
    Also supports dict-like lookup."""

    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':  # now item with max f(x)
            self.f = lambda x: -f(x)  # will be popped first
        else:
            raise ValueError("Order must be either 'min' or 'max'.")

    def append(self, item):
        """Insert item at its correct position."""
        heapq.heappush(self.heap, (self.f(item), item))

    def extend(self, items):
        """Insert each item in items at its correct position."""
        for item in items:
            self.append(item)

    def pop(self):
        """Pop and return the item (with min or max f(x) value)
        depending on the order."""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    def __len__(self):
        """Return current capacity of PriorityQueue."""
        return len(self.heap)

    def __contains__(self, key):
        """Return True if the key is in PriorityQueue."""
        return any([item == key for _, item in self.heap])

    def __getitem__(self, key):
        """Returns the first value associated with key in PriorityQueue.
        Raises KeyError if key is not present."""
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")

    def __delitem__(self, key):
        """Delete the first occurrence of key."""
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)
#-------- PRIORITY QUEUE CLASS END -----

#-------- HILL CLIMB SEARCH BEGIN -----
def hill_climbing(problem):
    """
    From the initial node, keep choosing the neighbor with highest value,
    stopping when no neighbor is better.
    """
    current = Node(problem.initial)
    while True:
        neighbors = current.expand(problem)
        if not neighbors:
            break
        neighbor = argmin_random_tie(neighbors, key=lambda node:problem.value(node.state)) #we are using argmin and not argmax because we are looking for the node with the CLOSEST distance to goal
        if (problem.value(neighbor.state) <= problem.value(current.state) and not problem.value(current.state) != 0):
            break
        current = neighbor
    print("PC: {}".format(current.path_cost))
    print("HC solutionL {}".format(current.solution()))
    return current
#-------- HILL CLIMB SEARCH END -------





HOWTOSETCUSTOMHEURISTIC =""" 
leftThree = [3,11,19]
rightThree = [7,15,18]

print("Left: {}".format(leftThree))
print("Right: {}".format(rightThree))
initialState = GameState(leftThree, rightThree, True, True)

p = Problem(initialState)
def customH(n=lambda n:n):
    print("custom H")
    #20 is points to win, it depends on the hand size
    return(20- n.state.pointsScored)
p.h = customH

print("Astar")
astar_search(p)"""