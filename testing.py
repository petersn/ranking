#!/usr/bin/python

import math
import random

mu1    = 0.0
sigma1 = 25.0
mu2    = 20.0
sigma2 = 25.0

def probability_of_acceptability(mu1, sigma1, mu2, sigma2):
	arg = (mu1 - mu2) / (sigma1**2 + sigma2**2)**0.5
	return math.erfc(-arg/2**0.5)/2

def OLD_expected_acceptable(mu1, sigma1, mu2, sigma2):
	# Compute the integral of the likelihood function.
	total_variance = sigma1**2 + sigma2**2
	value = sigma1**2 * math.exp(-(mu1 - mu2)**2 / (2 * total_variance)) / (2 * math.pi * total_variance)**0.5
	# Now we normalize by the probability.
	v = probability_of_acceptability(mu1, sigma1, mu2, sigma2)
	value /= v
	# Correct for our our u-substitution.
	value += mu1
	return value

def expected_acceptable(mu1, sigma1, mu2, sigma2):
	var = sigma1**2.0 + sigma2**2.0
	coef1 = 2 / (math.erfc((mu2 - mu1)/(2 * var)**0.5))
	coef2 = sigma1**2 / (2 * math.pi * var)**0.5
	coef3 = math.exp(-(mu1 - mu2)**2/(2*var))
	return mu1 + coef1 * coef2 * coef3

acceptable = []
count = 1000000
for _ in xrange(count):
	p1 = random.normalvariate(mu1, sigma1)
	p2 = random.normalvariate(mu2, sigma2)
	if p1 > p2:
		acceptable.append(p1)

print "Empirical values:"
print "P(p1 > p2) =", len(acceptable) / float(count)
print "E[p1 | p1 > p2] =", sum(acceptable) / max(1.0, float(len(acceptable)))
print "Theoretical values:"
print "P(p1 > p2) =", probability_of_acceptability(mu1, sigma1, mu2, sigma2)
print "E[p1 | p1 > p2] =", expected_acceptable(mu1, sigma1, mu2, sigma2)
print "E[p1 | p1 > p2] =", OLD_expected_acceptable(mu1, sigma1, mu2, sigma2)

