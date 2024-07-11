"""
RandomBot -- A simple strategy: enumerates all legal moves, and picks one
uniformly at random.
"""

# Import the API objects
from api import State
from api import Deck


class Bot:

    def __init__(self):
        pass

    def get_move(self, state):
    # type: (State) -> tuple[int, int]
        """
        Function that gets called every turn. This is where to implement the strategies.
        Be sure to make a legal move. Illegal moves, like giving an index of a card you
        don't own or proposing an illegal mariage, will lose you the game.
        TODO: This bot will obey to the following play option ordered by priority:
                1) Play a card of the spades suit
                2) Play a trump suit card
                3) Play the highest rank card available
        :param State state: An object representing the gamestate. This includes a link to
            the states of all the cards, the trick and the points.
        :return: A tuple of integers or a tuple of an integer and None,
            indicating a move; the first indicates the card played in the trick, the second a
            potential spouse.
        """
        
        #All legal moves
        moves = state.moves()
        chosen_move = moves[0]

        #This bot will always firstly try to play spades, it will play the first spades card it finds on its hand
        for index, move in enumerate(moves):
            if move[0] is not None and 8 <= move[0] <= 11:
                return move


        #If playing spades is not a possibility the bot will try to play the first trump suit card it finds on its hand
        moves_trump_suit = []

        #Get all trump suit moves available
        for index, move in enumerate(moves):

            if move[0] is not None and Deck.get_suit(move[0]) == state.get_trump_suit():
                moves_trump_suit.append(move)

        if len(moves_trump_suit) > 0:
            chosen_move = moves_trump_suit[0]
            return chosen_move

        #As a last resort the bot will play the highest rank available, of any suit
        for index, move in enumerate(moves):
            if move[0] is not None and move[0] % 5 <= chosen_move[0] % 5:
                chosen_move = move
        return chosen_move