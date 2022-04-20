import pandas as pd
import numpy as np

from funcy import pairwise
from itertools import accumulate


rng = np.random.default_rng


def split(data_frame):
    test_sample  = data_frame[    0:  100]
    test_public  = data_frame[  100:10100]
    test_private = data_frame[10100:80100]
    train        = data_frame[80100:     ]

    return test_sample, test_public, test_private, train


data_frame = pd.read_csv('rent-formatted.csv')

for name, (begin, end) in zip(('sample', 'public', 'private', 'rent'),
                              pairwise(accumulate((0, 100, 10000, 70000, len(data_frame)), lambda acc, count: acc + count))):
    result = data_frame[begin:end]
    result = result.reset_index(drop=True)

    if (name == 'rent'):
        result.to_csv(f'{name}.csv', index_label='ID')
    else:
        result.drop(columns=['家賃 + 管理費・共益費']).to_csv(f'test-{name}.csv', index_label='ID')
        result['家賃 + 管理費・共益費'].to_csv(f'predict-{name}.csv', index_label='ID')
