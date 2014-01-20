'''Run all available tests.'''
import unittest

# The modules with test suites
import fetch_test_ora as s1
#import fetch_test_plos as s2
#import fetch_test_datafinder as s3

# Define which test suites will be used.
#test_suites = [s1, s2, s3]
test_suites = [s1, ]

# Run all the suites.
def run(suites, verb=0):
    '''Run the suites with no verbosity.'''
    for suite in suites:
        log('Running: %s'%suite.SUITE_NAME)
        unittest.TextTestRunner(verbosity=verb).run(suite.suite())

def log(message):
    print
    print message
    print

log('Running all available tests. ------------------')
run(test_suites)
log('Finished all available tests. -----------------')
