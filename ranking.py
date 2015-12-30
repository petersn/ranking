#!/usr/bin/python
"""
Here
"""

import math
#from matplotlib import pyplot as plt

UPSET_THRESHOLD = 0.25

class Player:
	def __init__(self, mean, variance):
		self.mean, self.variance = float(mean), float(variance)

	@staticmethod
	def produce_aggregate_player(self, team):
		return Player(sum(p.mean for p in team), sum(p.variance for p in team))

def phi(x):
	return math.erfc(-x / 2**0.5) / 2

def normal(x, mu, sigma):
	return math.exp(- (x - mu)**2 / (2.0 * sigma**2)) / (sigma * (2 * math.pi)**0.5)

def objective(x, mu1, sigma1, mu2, sigma2):
	return (normal(x, mu2, sigma2) - (x - mu1) / sigma1**2.0 * phi((x - mu2) / float(sigma2))) * normal(x, mu1, sigma1)

def _ddx_objective(x, mu1, sigma1, mu2, sigma2):
	z2 = (x - mu2) / float(sigma2)
	normal_z2 = normal(z2, mu2, sigma2)
	result = (mu2 - x)/sigma2**2 * normal(x, mu2, sigma2)
	result += - phi(z2) / sigma1**2.0
	result += (mu1 - x) * normal_z2 / (sigma1**2 * sigma2)
	return result

def ddx_objective(x, mu1, sigma1, mu2, sigma2):
	left = _ddx_objective(x, mu1, sigma1, mu2, sigma2)
	result = left * normal(x, mu1, sigma1)
	result += (x - mu1)/sigma1**2 * objective(x, mu1, sigma1, mu2, sigma2)
	return result

def root_find(x, mu1, sigma1, mu2, sigma2):
	for _ in xrange(32):
		slope = ddx_objective(x, mu1, sigma1, mu2, sigma2)
		if slope == 0.0:
			# We have no hope of convergence, return any garbage.
			return 0.0
		x -= objective(x, mu1, sigma1, mu2, sigma2) / slope
	return x

def performance_mle(player1, player2, outcome):
	"""performance_mle(player1, player2, outcome) -> x

	Does MLE on the performance of player 1, to find the performance x
	that is most likely given that player 1 had a given performance relative
	to player 2. If outcome == "win", then it assumes player 1 beat player 2,
	and likewise for "loss" or "draw".
	"""
	assert outcome in ("win", "loss", "draw"), "Invalid outcome: %r" % outcome
	DEBUG = True
	if outcome in ("win", "loss"):
		solutions = []
		mu1, sigma1, mu2, sigma2 = player1.mean, player1.variance**0.5, player2.mean, player2.variance**0.5
		# If the game is a loss, we just say that player1 won on the negative version of the game.
		if outcome == "loss":
			mu1, mu2 = -mu1, -mu2
		if DEBUG:
			xs = []
			score1 = []
			score2 = []
			score3 = []
		for i in xrange(2006):
			lerp_coef = -2 + i / 500.0
			starting_x = lerp_coef * player2.mean + (1 - lerp_coef) * player1.mean
			if DEBUG:
				xs.append(starting_x)
				score1.append(phi((starting_x - mu2) / sigma2) * normal(starting_x, mu1, sigma1) * 4e2) # Blue
				score2.append(objective(starting_x, mu1, sigma1, mu2, sigma2) * 0.5 * 1e3) # Green
				score3.append(ddx_objective(starting_x, mu1, sigma1, mu2, sigma2) * 100.0) # Red
			solution = root_find(starting_x, mu1, sigma1, mu2, sigma2)
			# We only allow a solution if it has negative slope where it's being solved.
			if ddx_objective(solution, mu1, sigma1, mu2, sigma2) < 0:
				solutions.append(solution)
		if DEBUG:
			plt.hold(True)
			plt.plot(xs, score1)
			plt.plot(xs, score2)
			plt.plot(xs, score3)
			plt.show()
		assert len(solutions), "Strangely, couldn't find any roots without multiplicity."
		curried_objective = lambda x: abs(objective(x, mu1, sigma1, mu2, sigma2))
#		curried_objective = lambda x: phi((x - mu2) / sigma2) * normal(x, mu1, sigma1)
		result = min(solutions, key=curried_objective)
#		print "The value:", ddx_objective(result, mu1, sigma1, mu2, sigma2)
		debug_info = {"mu1": mu1, "mu2": mu2, "sigma1": sigma1, "sigma2": sigma2, "outcome": outcome, "result": result, "objective": curried_objective(result)}
		assert curried_objective(result) < 1e-5, "Newton's method failed to converge from any of the starting points!\n%r" % debug_info
		# If we're playing for a loss, then negate the position found.
		if outcome == "loss":
			result = -result
		return result
	elif outcome == "draw":
		# Here we're attempting to find
		# \[ \argmax_x \mathcal{N}_{\mu_1, \sigma_1)(x) \mathcal{N}_{\mu_2, \sigma_2}(x), \]
		# which thankfully has a fully analytic solution.
		# See: http://www.johndcook.com/blog/2012/10/29/product-of-normal-pdfs/
		result = (player1.mean / player1.variance + player2.mean / player2.variance) / (1.0/player1.variance + 1.0 / player2.variance)
		return result

def probability_of_win(player1, player2):
	winning_z_score = (player2.mean - player1.mean) / (player1.variance + player2.variance)**0.5
	prob = 0.5 * math.erfc(winning_z_score / 2**0.5)
	return prob

def most_likely_given_(player1, player2):
	pass

def compute_new_scores(teams, team_rankings, player_params):
#	# First, normalize the outcomes to be a partition of unity.
#	norm = float(sum(outcomes))
#	outcomes = [o/norm for o in outcomes]
	# We now update for all pairs of teams.
	aggregates = {i: Player.produce_aggregate_player(map(player_params.__getitem__, team)) for i, team in enumerate(teams)}
	print aggregates
	team_totals = {i: 0 for i, team in enumerate(teams)}
	for i, t1 in enumerate(teams):
		for j, t2 in enumerate(teams):
			# Find all pairs where t1 beat t2.
			if not (team_rankings[i] > team_rankings[j]):
				continue
			# Compute the probability of this victory.
			prob = probability_of_win(aggregates[i], aggregates[j])
			# Exchanged points.
#			team_totals[
			# If the probability of a win is

