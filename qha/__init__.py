#!/usr/bin/env python3

import sys

if sys.version_info < (3, 5):  # In case of user who does not have ``pip`` above version 9.0.0
    raise EnvironmentError('Please use Python version higher than 3.5!')

__author__ = {'Tian Qin': 'qinxx197@umn.edu', 'Qi Zhang': 'qz2280@columbia.edu'}
__copyright__ = 'Copyright (c) 2018, Renata group'
__credits__ = {'Renata M. M. Wentzcovitch': 'rmw2150@columbia.edu'}
__date__ = 'Feb 17, 2018'
__maintainer__ = 'Tian Qin, Qi Zhang'
__version__ = '1.0.20'
