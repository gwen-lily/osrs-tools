from bedevere import *


def is_stochastic(P: np.ndarray, precision: float = arithmetic_precision, stochastic_type: str = 'right') -> bool:
	"""Checks that a given matrix is square and probability-complete or a vector is probability-complete

	Square means that a matrix is n x n, probability complete means that all of the elements of a row, column,
	row & column, or vector sum to 1, i.e. that they fully describe a probability space.

	Parameters:
		P (np.ndarray): A vector or square matrix with slices that meet the probability complete description.
		precision (float): Arithmetic precision required when analyzing slice sums. If the sum value is within the
			precision value, the slice is evaluated to meet the probability complete description.
		stochastic_type (str): One of three descriptions for matrices:
			right: Rows sum to 1
			left: Columns sum to 1
			doubly: Rows and columns each sum to 1

	Returns:
		bool: True if P is stochastic, False otherwise
	"""

	try:
		m, n = P.shape

	except ValueError as E:
		m, n = (P.shape[0], 1)

	if (m == 1 and n > 1) or (m > 1 and n == 1):
		max_dimension = max([m, n])
		return math.fabs(sum(P.reshape((max_dimension,))) - 1) < precision

	elif m == n:
		if stochastic_type == 'right':
			return all([math.fabs(sum(P[i, :]) - 1) < precision for i in range(m)])

		elif stochastic_type == 'left':
			return all([math.fabs(sum(P[:, i]) - 1) < precision for i in range(n)])

		elif stochastic_type == 'doubly':
			return all([math.fabs(sum(P[i, :]) - 1) < precision for i in range(m)]) and \
			       all([math.fabs(sum(P[:, i]) - 1) < precision for i in range(n)])

	return False


def is_triangular(P: np.ndarray, direction: str) -> bool:
	"""Checks that a given matrix is triangular according to the given type

	A matrix is upper-triangular if all of the entries below the main diagonal are zero and lower-triangular if all of
	the entries above the main diagonal are zero.

	Parameters:
		P (np.ndarray): Square matrix
		direction (str): Indicates the type of triangularity
			upper: Upper triangular
			lower: Lower triangular

	Returns:
		bool: True if the given matrix meets the given triangular condition
	"""

	m, n = P.shape

	if m == n:
		if direction == 'upper':
			return all(b == True for b in (P == np.triu(P)).reshape(m*n,))

		elif direction == 'lower':
			return all(b == True for b in (P == np.tril(P)).reshape(m*n,))

	return False


def is_unitriangular(P: np.ndarray, direction: str) -> bool:
	"""Checks that a given matrix is unitriangular according to the given type

	A unitriangular matrix is a triangular matrix whose diagonal entries are all equal to 1.

	Parameters:
		P (np.ndarray): Square matrix
		direction (str): Indicates the type of triangularity
			upper: Upper triangular
			lower: Lower triangular

	Returns:
		bool: True if the given matrix meets the unitriangular condition
	"""

	return all(d == 1 for d in np.diag(P)) and is_triangular(P, direction)


def is_strictly_triangular(P: np.ndarray, direction: str) -> bool:
	"""Checks that a given matrix is strictly triangular according to the given type

	A strictly triangular matrix is a triangular matrix whose diagonal entries are all equal to 0.

	Parameters:
		P (np.ndarray): Square matrix
		direction (str): Indicates the type of triangularity
			upper: Upper triangular
			lower: Lower triangular

	Returns:
		bool: True if the given matrix meets the unitriangular condition
	"""

	return all(d == 0 for d in np.diag(P)) and is_triangular(P, direction)


def is_atomic(P: np.ndarray, direction: str) -> bool:
	"""Checks that a given matrix is atomic according to the given type

	An atomic matrix is a unitriangular matrix where all off-diagonal elements are zero, except for the entries in a
	single column.

	Parameters:
		P (np.ndarray): Square matrix
		direction (str): Indicates the type of triangularity
			upper: Upper triangular
			lower: Lower triangular

	Returns:
		bool: True if the given matrix meets the atomic condition
	"""

	if is_unitriangular(P, direction):

		m, n = P.shape
		column_slices = [P[:i, i] for i in range(n)]
		nonzero_column_slices = []

		for cs in column_slices:
			if any(not e == 0 for e in cs):
				nonzero_column_slices.append(cs)

		return len(nonzero_column_slices) == 1

	return False


def is_unidirectional_matrix(P: np.ndarray, precision: float = arithmetic_precision,
                                     stochastic_type: str = 'right') -> bool:
	"""Checks that a given matrix is unidirectional and stochastic

	Depending on the stochastic type, the matrix must either be upper- (right) or lower- (left) diagonal, implying
	an ordering of states such that direction in only a single direction is possible. See is_stochastic for more detail
	on the features of stochastic matrices.

	Parameters:
		P (np.ndarray): A vector or square matrix with slices that meet the probability complete description.
		precision (float): Arithmetic precision required when analyzing slice sums. If the sum value is within the
			precision value, the slice is evaluated to meet the probability complete description.
		stochastic_type (str): One of three descriptions for matrices:
			right: Rows sum to 1
			left: Columns sum to 1
			doubly: Rows and columns each sum to 1

	Returns:
		bool: True if P is stochastic and conditionally-diagonal, depending on the type of stochasticism.
	"""

	if stochastic_type == 'right':
		direction = 'upper'

	elif stochastic_type == 'left':
		direction = 'lower'

	else:
		raise RuntimeError(r"I haven't implemented that yet chief, for I am but a humble lad")

	return is_stochastic(P, precision, stochastic_type) and is_triangular(P, direction=direction)


def test_stochastic():
	# stochastic test
	tests = 1e3
	max_dimension = 10

	for test in range(int(tests)):
		test_dimension = random.choice(np.arange(1, max_dimension))

		right = np.asarray(np.random.dirichlet(np.ones(test_dimension), test_dimension))
		left = np.transpose(np.asarray(np.random.dirichlet(np.ones(test_dimension), test_dimension)))

		row = np.asarray(np.random.dirichlet(np.ones(test_dimension), 1)).reshape(1, test_dimension)
		column = np.asarray(np.random.dirichlet(np.ones(test_dimension), 1).reshape(test_dimension, 1))

		assert is_stochastic(right, stochastic_type='right')
		assert is_stochastic(left, stochastic_type='left')
		assert is_stochastic(row)
		assert is_stochastic(column)


if __name__ == '__main__':
	test_stochastic()