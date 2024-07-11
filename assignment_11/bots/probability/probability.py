"""
ProbabilityBot -- A bot that applies a very simple probabilistic strategy whenever it is our
turn to play the first card.

At each move in the first phase, the probability is calculated that the opponent has a card in his/her hand
which is in the same color as our options, but higher. This could be considered an easy win for
our opponent, and should be avoided. This means we want to play a card with the highest probability that
there is no higher card of the same color in the opponents hand.

In the second phase we simply play Minimax with Alpha-Beta pruning (as implemented in Assignment 3)

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

		# If it is not my turn, then it does not make sense to play the Probabilistic Strategy.
		# In that case,  we simply play a random move. This could be done better, but it not
		# the purpose of this bot.
		if(state.whose_turn() != state.leader()):
			chosen_move = random.choice(moves)
			#print("Played Random Move")
			return chosen_move

		# If it is my turn, and if we are in phase 1 of the game, it makes sense to apply the Probabilistic Strategy.
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
			# the variable unknowns contains all the unknowns, and u be its length (so the number of unknown cards)
			u = len(unknowns)

			# Remember
			# Suit order: CLUBS, DIAMONDS, HEARTS, SPADES
			# 0, 5, 10, 15 - Aces
			# 1, 6, 11, 16 - 10s
			# 2, 7, 12, 17 - Kings
			# 3, 8, 13, 18 - Queens
			# 4, 9, 14, 19 - Jacks

			# First let us initialise the maximal probability to 0
			maxProbability = 0

			for index, move in enumerate(moves):
				# Now we are looking for the problematic cards (problematicCards), i.e. those
				# cards that would be easy wins for the opponent, i.e. cards
				# that have the same color as the one played, but with a higher value.

				problematicCards = []
				for unknown in unknowns:
					if (move[0] is not None and (Deck.get_suit(unknown) == Deck.get_suit(move[0])) and unknown < move[0]):
						problematicCards.append(unknown)

				# Now we define pc as the number of problematic cards
				pc = len(problematicCards)

				# Calculate the probability that the opponent does not have a problemCard
				#
				# |u|-|pc|      |u-1|-|pc|   |u-2|-|pc|     |u-3|-|pc|     |u-4|-|pc|
				# --------  *   ---------  *  --------  *  ----------- * ------------
				#   |u|         |u-1|          |u-2|         |u-3|   	   |u-4|

				probability = ???

				# All that is left to do is to check whether the new probability is higher than the earlier value
				# (to calculate the maximum). If it is, we set probability to be the new maximal probability, and the
				# current move our new chosen move.
				if (move[0] is not None and probability > maxProbability):
					???
			#print("Played MaxProbability Card ", maxProbability, "played", chosen_move)
			return chosen_move
		else:
			# In phase 2 we play standard Minimax with Alpha-beta pruning.
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
