#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2019-2020 Ralf Weber
#
# This file is part of MetaboVerse.
#
# MetaboVerse is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MetaboVerse is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MetaboVerse.  If not, see <https://www.gnu.org/licenses/>.
#


import os
import sys
import unittest
from pathlib import Path

from . import test_databases
from . import test_isomorphism_database
from . import test_substructure_database

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))


if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_databases))
    suite.addTest(unittest.findTestCases(test_isomorphism_database))
    suite.addTest(unittest.findTestCases(test_substructure_database))

    report = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), 'results', 'results_test_suite_databases')
    runTestSuite(suite, report, title='Process Test Suite Report', verbosity=2)
