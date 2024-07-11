"""
Utilitybot -- A bot that combines our  simple probabilistic strategy with a notion of utility.
The idea is that our probabilistic strategy favours Aces and tens (as there are fewer higher cards available.
In this bot we combine the probability of a card having a higher card with its costs by simply multiplying the
probability and the cost value.
"""

# Import the API objects
from api import State, Deck, util
import random

class Bot:
	__randomize = True

	def __init__(self, randomize=True, depth=5):
		self.__max_depth = depth


	def get_move(self, state):
		# type: (State) -> tuple[int, int]
		"""
		Function that gets called every turn. This is where to implement the strategies.
		Be sure to make a legal move. Illegal moves, like giving an index of a card you
		don't own or proposing an illegal mariage, will lose you the game.
		:param State state: An object representing the gamestate. This includes a link to
			the states of all the cards, the trick and the points.
		:return: A tuple of integers or a tuple of an integer and None,
			indicating a move; the first indicates the card played in the trick, the second a
			potential spouse.
		"""
		# All legal moves
		moves = state.moves()

		# If it is not my turn, the following will be executed as my idea
		if(state.whose_turn() != state.leader()):		

			# Check whether the opponent has made a legal move
			if state.get_opponents_played_card() is not None:

				# Initializing the lists that are going to store, one the first one, the problematic cards we possess towards our opponent,
				# that means, the cards of the same suit as the played card but with higher rank, and on the second one, the cards we possess 
				# of the trump suit that will come in handy later on 
				problematic_cards_for_the_opponent = []
				moves_trump_suit = []

				# Appending the cards on our hand that match the problematic card condition stated above into the first list
				for index, move in enumerate(moves):
					if move[0] is not None and Deck.get_suit(move[0]) == Deck.get_suit(state.get_opponents_played_card()) and Deck.get_rank(move[0]) > Deck.get_rank(state.get_opponents_played_card()):
						problematic_cards_for_the_opponent.append(move)

				# If there are any moves matching the condition above we play the first one to be found
				if len(problematic_cards_for_the_opponent) > 0:
					chosen_move = problematic_cards_for_the_opponent[0]
					return chosen_move

				# If the problematic card strategy is not possible to execute, we will now append all the moves matching the trump suit
				# into the second list 
			for index, move in enumerate(moves):
				if move[0] is not None and Deck.get_suit(move[0]) == state.get_trump_suit():
					moves_trump_suit.append(move)

			# If there are any moves matching the above condition we will play the first one to be found
			if len(moves_trump_suit) > 0:
				chosen_move = moves_trump_suit[0]
				return chosen_move

			# In case it is, firstly, impossible to apply the problematic card strategy and, secondly, impossible to play a trump suit card
			# this bot will simply play randomly
			chosen_move = random.choice(moves)
			return chosen_move

		# If it is my turn, and if we are in phase 1 of the game, it makes sense to apply the Utility value Strategy.
		if state.get_phase() == 1:
			chosen_move = moves[0]

			# The following method enumerates all cards and what is known about them for this player.
			# This is called the perspective, which is an array of 20 entries, one per card.
			# The values can be U for unknown, P1H for Player 1 Hand, etc. Print the perspective if you
			# are unsure what this does.
			perspective = state.get_perspective()

			# First, let us extract all the unknown cards. These are the cards
			# in the talon (except for the card that determines trump) and the opponents hand.

			# Let unknowns be an array containing all the unknown cards
			unknowns = []
			# Enumerate over all the cards in the perspective
			for index, card in enumerate(perspective):
				search_term = 'U'
				if card == search_term:
					# If a card has a U value, it is is added to the list of unknowns.
					unknowns.append(index)
			# the variable unknowns contains all the unknowns, so let u be its length
			u = len(unknowns)

			# Remember
			# Suit order: CLUBS, DIAMONDS, HEARTS, SPADES
			# 0, 5, 10, 15 - Aces
			# 1, 6, 11, 16 - 10s
			# 2, 7, 12, 17 - Kings
			# 3, 8, 13, 18 - Queens
			# 4, 9, 14, 19 - Jacks

			# First let us initialise the maximal Utility to 0
			maxUtility = 0

			for index, move in enumerate(moves):
				# Now we are looking for the problematic cards (problematicCards), i.e. those
				# cards that would be easy wins for the opponent, i.e. cards
				# that have the same color as the one played, but with a higher value.

				problematicCards = []
				for unknown in unknowns:
					if (move[0] is not None and (Deck.get_suit(unknown) == Deck.get_suit(move[0])) and unknown < move[
0]):
						problematicCards.append(unknown)

				# Now we define pc as the number of problematic cards
				pc = len(problematicCards)

				# Calculate the probability that the opponent does not have a problemCard
				#
				# |u|-|pc|      |u-1|-|pc|   |u-2|-|pc|     |u-3|-|pc|     |u-4|-|pc|
				# --------  *   ---------  *  --------  *  ----------- * ------------
				#   |u|         |u-1|          |u-2|         |u-3|   	   |u-4|

				probability = ((u - pc) / u) * ((u-1 - pc) / (u-1)) * ((u-2 - pc) / (u-2)) * ((u-3 - pc) / (u-3)) * ((u-4 - pc) / (u-4))

				# Now we have the probability, but still want to normalise it with the costs of losing the card.
				# E.g. playing a 10 is a higher risk of loosing points as compared with playing a Jack.

				# Let score be an array with values for the various cards. The modulo method will assign a rank to each
				# card, and each of these ranks is given a value from the score array.
				score = [11, 10, 4, 3, 2]
				if (move[0] is not None):
					rank = move[0] % 5
					points = score[rank]
					utility = probability / points
				else:
					utility = 0.0

				# Now we check if the utility of the current option (move) is higher than the highest of the previous
				# options. If so, we choose this as our new maximal utility, and this move the chosen move.
				if (move[0] is not None and utility > maxUtility):
					maxUtility = utility
					chosen_move = move
			# print("Played MaxUtility Move: ", maxUtility, "played", chosen_move)
			return chosen_move
		else:
			# In phase 2 we play a simple Minimax with Alpha-beta pruning as of Assignment 3, which should be an optimal game.
			val, move = self.value(state)
			# print("Played MinimaxMove")
			return move


	# A helper function for Minimax
	def value(self, state, alpha=float('-inf'), beta=float('inf'), depth=0):
				"""
                Return the value of this state and the associated move
                :param State state:
                :param float alpha: The highest score that the maximizing player can guarantee given current knowledge
                :param float beta: The lowest score that the minimizing player can guarantee given current knowledge
                :param int depth: How deep we are in the tree
                :return val, move: the value of the state, and the best move.
                """

				if state.finished():
					winner, points = state.winner()
					return (points, None) if winner == 1 else (-points, None)

				if depth == self.__max_depth:
					return heuristic(state)

				best_value = float('-inf') if maximizing(state) else float('inf')
				best_move = None

				moves = state.moves()

				if self.__randomize:
					random.shuffle(moves)

				for move in moves:

					next_state = state.next(move)
					value, _ = self.value(next_state)

					if maximizing(state):
						if value > best_value:
							best_value = value
							best_move = move
							alpha = best_value
					else:
						if value < best_value:
							best_value = value
							best_move = move
							beta = best_value

					# Prune the search tree
					# We know this state will never be chosen, so we stop evaluating its children
					if alpha > beta:
						break

				return best_value, best_move

# A helper function for Minimax
def maximizing(state):
	# type: (State) -> bool
	"""
    Whether we're the maximizing player (1) or the minimizing player (2).

    :param state:
    :return:
    """
	return state.whose_turn() == 1
# A helper function for Minimax
def heuristic(state):
	# type: (State) -> float
	"""
    Estimate the value of this state: -1.0 is a certain win for player 2, 1.0 is a certain win for player 1
	:param state:
    :return: A heuristic evaluation for the given state (between -1.0 and 1.0)
    """
	return util.ratio_points(state, 1) * 2.0 - 1.0, None
