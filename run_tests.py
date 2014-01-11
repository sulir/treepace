#!/usr/bin/env python

"""Run all unit tests in the 'tests' directory and print the results."""

import unittest

def main():
    suite = unittest.TestLoader().discover('tests/', '*.py')
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()