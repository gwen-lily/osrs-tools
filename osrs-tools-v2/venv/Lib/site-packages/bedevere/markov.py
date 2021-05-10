from bedevere import *
from bedevere.matrix import *


class MarkovChain:

	def __init__(self, transition_matrix: np.ndarray, states: np.ndarray):
		"""Initializes a MarkovChain class given transition matrix: Q and states: t"""

		self.transition_matrix = np.atleast_2d(transition_matrix)
		self.states = np.array(states, copy=True)

		assert len(self.states) == len(np.unique(self.states))  	# assert uniqueness of all states

		self.states_dict = {}

		for i, e in enumerate(self.states):
			self.states_dict[e] = i

		# if n-step transition matrices are calculated they get stored here for future reference
		self.transition_matrices_dict = {
			0: np.eye(self.transition_matrix.shape[0]),
			1: self.transition_matrix
		}

	# Analytical Methods

	def step_transition_matrix(self, steps: int):
		"""Return the transition matrix representing n steps"""
		assert steps >= 0

		if steps not in self.transition_matrices_dict:
			self.step_transition_matrix_generator(steps)

		return self.transition_matrices_dict[steps]

	def step_transition_matrix_generator(self, max_steps: int):
		"""Generate the transition matrix representing n steps"""
		start_point = max(self.transition_matrices_dict.keys())
		assert start_point < max_steps  	# since we store every intermediary, this should never happen
		step_matrix = np.array(self.transition_matrices_dict[start_point], copy=True)

		for i in range(start_point + 1, max_steps + 1):
			step_matrix = np.dot(step_matrix, self.transition_matrix)
			self.transition_matrices_dict[i] = np.array(step_matrix, copy=True)

	def probability_distribution(self, current_distribution: np.array, number_of_steps: Union[int, np.array])\
			-> np.array:
		"""Return the state distribution given current distribution of length m and number of steps

		If an array of steps of length n is given, return an m x n matrix where the jth column is the state distribution
		 after (the jth element of number of steps) steps """
		assert current_distribution.shape == self.states.shape
		assert math.fabs(sum(current_distribution) - 1) < arithmetic_precision

		if type(number_of_steps) == int:
			return np.dot(current_distribution, self.step_transition_matrix(number_of_steps))

		else:

			distributions = np.ndarray(shape=(self.states.shape[0], number_of_steps.shape[0]))

			for i, step in enumerate(number_of_steps):
				try:
					assert step < number_of_steps[i + 1]

				except IndexError:
					pass

				distributions[:, i] = np.dot(current_distribution, self.step_transition_matrix(step))

			return distributions

	def mean_state(self, current_distribution: np.array) -> np.array:
		"""Return the weighted mean of all states, with the current distribution as probability weights"""
		assert current_distribution.shape == self.states.shape
		mean_state = np.dot(current_distribution, self.states)
		return mean_state

	# Statistical Methods / Monte-Carlo

	def monte_carlo(self, starting_state, steps: int):
		"""Return a state after n steps in a Markov Chain, with each step chosen randomly"""

		assert starting_state in self.states
		current_state = starting_state

		for step in range(steps):
			i = self.states_dict[current_state]
			transition_probabilities = self.transition_matrix[i, :]
			current_state = random.choices(self.states, transition_probabilities)[0]

		return current_state


class AbsorbingMarkovChain(MarkovChain):

	def __init__(self, Q: np.ndarray, R: np.ndarray, states: np.ndarray):
		t, r = R.shape
		assert Q.shape == (t, t)
		assert states.size == t + r

		self.transient_states = states[:t]
		self.absorbing_states = states[-r:]

		P = np.empty((r+t, r+t))
		P[:t, :t] = Q
		P[:t, t:] = R
		P[t:, :t] = np.zeros((r, t))
		P[t:, t:] = np.eye(r)

		self.fundamental_matrix = np.linalg.inv(np.eye(t) - Q)
		self.expected_steps = np.dot(self.fundamental_matrix, np.ones((t, 1)))

		super().__init__(P, states)

	def monte_carlo_absorbing(self, starting_state) -> np.array:
		"""Returns the state arrived at after a number of steps and the amount it took to get there"""
		assert starting_state in self.states

		current_state = starting_state
		steps = 0

		while current_state in self.transient_states:
			steps += 1

			i = self.states_dict[current_state]
			transition_probabilities = self.transition_matrix[i, :]
			current_state = random.choices(self.states, transition_probabilities)[0]

		return current_state, steps


def test_mc():
	pass


if __name__ == '__main__':
	pass
	# test = np.asarray([[0.1, 0.9], [0, 1]])
	# is_unidirectional_matrix(test, 1e-5)
