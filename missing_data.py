
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
import numpy as np

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

		self.interpolator = None


class LowessImputer(Imputer):

	def __init__(self, x_arr, y_arr):
		super().__init__(x_arr, y_arr)

		lowess = sm.nonparametric.lowess
		z = lowess(y_arr, x_arr, frac=0.1)
		lowess_x = z[:, 0]
		lowess_y = z[:, 1]

		self.interpolator = interp1d(lowess_x, lowess_y, bounds_error=False)

	def __call__(self, x_val):
		return self.interpolator(x)

imputers = {
	'lowess': LowessImputer
}

class DataProcessor(object):

	def __init__(self, x_arr, y_arr):
		if not isinstance(x_arr, list) or not isinstance(y_arr, list):
			raise ValueError('x and y arrays should be lists')

		self.n_arr = len(x_arr)

		if len(y_arr) != self.n_arr:
			raise ValueError('x and y arrays should have same length')

		if not self.n_arr:
			raise ValueError('x and y found to be empty lists')

		self.x_arr = x_arr
		self.y_arr = y_arr

		if isinstance(x_arr[0], np.datetime64):
			self.convert_datetime_to_int('x')

		if isinstance(y_arr[0], np.datetime64):
			self.convert_datetime_to_int('y')

		self.sort_x_values()
		self.delta = None
		self.imputer = None
		self.missing_x_arr = []

	def sort_x_values(self):
		x_y = sorted(zip(self.x_arr, self.y_arr), key=lambda tup: tup[0])
		self.x_arr, self.y_arr = [list(tup) for tup in zip(*x_y)]

	def infer_delta(self):
		'''
			Try to infer the most likely spacing for the data

		'''

		diff_arr = [(self.x_arr[j+1] - self.x_arr[j]) for j in range(self.n_arr-1)]
		freq, delta = np.histogram(diff_arr)
		self.delta = delta[np.argmax(freq)]
		return self.delta

	def set_imputer(self, imputer_name):
		if imputer_name in imputers.keys():
			self.imputer = imputers[imputer_name](self.x_arr, self.y_arr)

		else:
			raise KeyError('imputer type not supported: %s' % imputer_name)

	def convert_string_to_datetime(self, arr='x'):
		if arr == 'x':
			self.x_arr = [parse(x) for x in self.x_arr]
		elif arr == 'y':
			self.y_arr = [parse(y) for y in self.y_arr]
		else:
			raise ValueError('arr parameter should be either x or y')

	def convert_datetime_to_int(self, arr='x'):
		if arr == 'x':
			minx = min(self.x_arr)
			self.x_arr = [dt.datetime.timestamp(x) - minx for x in self.x_arr]
		elif arr == 'y':
			miny = min(self.y_arr)
			self.y_arr = [dt.datetime.timestamp(y) - miny for y in self.y_arr]
		else:
			raise ValueError('arr parameter should be either x or y')

	def delete_randomly(self, n=1):
		'''
			Deletes n (default=1) datapoints from the array
		'''

		rand_ix = random.sample(range(self.n_arr), self.n_arr - n)

		self.x_arr = list(np.array(self.x_arr)[rand_ix])
		self.y_arr = list(np.array(self.y_arr)[rand_ix])
		self.n_arr = len(self.x_arr)
		self.sort_x_values()

	def find_missing_data(self, delta=None):
		'''
			Determines the indices at which data are missing, assuming that 
			the original data are equally spaced with distance delta. If 
			delta is None, this will use the known value of delta or attempt 
			to pick the most likely spacing given the data.
		'''
		if not delta:
			delta = self.delta if self.delta else self.infer_delta()
		print('inferred delta (sec) =', delta)
		missing_data_ix = [i for i in range(self.n_arr-1) if 
							(self.x_arr[i+1] - self.x_arr[i]) > delta]

		for i in sorted(missing_data_ix, reverse=True):
			x_added = self.x_arr[i] + delta
			self.x_arr.insert(i+1, x_added)
			self.y_arr.insert(i+1, np.nan)
			self.missing_x_arr.append((i+1, x_added))

	def impute_all(self):
		if not self.imputer:
			raise ValueError('No imputer set')

		if self.missing_x_arr:
			for i, x in sorted(self.missing_x_arr, key=lambda x: -x[0]):
				print(i, self.y_arr[i])


if __name__=='__main__':
	import pandas as pd 

	data = pd.read_csv('govtraffic2.csv', parse_dates=['Time'])
	data.dropna(inplace=True)
	data.set_index('Unnamed: 0', inplace=True)
	data.index.rename('ID', inplace=True)
	data = data.iloc[49:200,:]
	time_int = data.Time.apply(dt.datetime.timestamp)



	dp = DataProcessor(list(time_int.values), list(data['cdc.gov/']))
	dp.set_imputer('lowess')
	dp.delete_randomly(10)
	dp.find_missing_data()
	dp.impute_all()




