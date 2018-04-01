
"""
	Author: Janos Botyanszki

	Description:
	This file provides a few useful functions for filling in missing data in 
	time series data. I provide code for Local Regression (LOWESS), splines,
	and simpler solutions, as well as a test set to use them on.

"""
import random
import statsmodels.api as sm
import datetime as dt

from dateutil.parser import parse
from scipy.interpolate import interp1d



class Imputer(object):

	def __init__(self, x_arr, y_arr):
		if not isinstance(x_arr, list) or not isinstance(y_arr, list):
			raise ValueError('x and y arrays should be lists')

		if len(x_arr) != len(y_arr):
			raise ValueError('x and y arrays should have same length')

		self.x_arr = x_arr
		self.y_arr = y_arr


class LowessImputer(Imputer):

	def __init__(self, x_arr, y_arr):
		super().__init__(x_arr, y_arr)

		lowess = sm.nonparametric.lowess
		z = lowess(y, x, frac=0.1)
		lowess_x = z[:, 0]
		lowess_y = z[:, 1]

		self.interpolator = interp1d(lowess_x, lowess_y, bounds_error=False)

	def __call__(self, x_val):
		return self.interpolator(x)


class DataProcessor(object):

	def __init__(self, x_arr, y_arr):
		if not isinstance(x_arr, list) or not isinstance(y_arr, list):
			raise ValueError('x and y arrays should be lists')

		self.n_arr = len(x_arr)

		if len(y_arr) != self.n_arr:
			raise ValueError('x and y arrays should have same length')

		self.x_arr = x_arr
		self.y_arr = y_arr


	def convert_string_to_datetime(self, arr='x'):
		if arr == 'x':
			self.x_arr = [parse(x) for x in self.x_arr]
		elif arr == 'y':
			self.y_arr = [parse(y) for y in self.y_arr]
		else:
			raise ValueError('arr parameter should be either x or y')

	def convert_datetime_to_int(self, arr='x'):
		if arr == 'x':
			self.x_arr = [dt.datetime.timestamp(x) for x in self.x_arr]
		elif arr == 'y':
			self.y_arr = [dt.datetime.timestamp(y) for y in self.y_arr]
		else:
			raise ValueError('arr parameter should be either x or y')

	def delete_randomly(self, n=1):
		'''
			Deletes n (default=1) datapoints from the array
		'''

		rand_ix = random.sample(range(self.n_arr), self.n_arr - n)

		self.x_arr = self.x_arr(rand_ix)
		self.y_arr = self.y_arr(rand_ix)
		self.n_arr = len(x_arr)

	def find_missing_data(self, delta=None):
		'''
			Determines the indices at which data are missing, assuming that 
			the original data are equally spaced with distance delta. If 
			delta is None, this will attempt to pick the most likely spacing 
			given the data.
		'''
		pass
		




