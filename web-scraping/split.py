import pandas as pd
import numpy as np

from funcy import pairwise
from itertools import accumulate


rng = np.random.default_rng

data_frame = pd.read_csv('data/rent-formatted.csv')

for name, (begin, end) in zip(('sample', 'public', 'private', 'rent'),
                              pairwise(accumulate((0, 100, 10000, 70000, len(data_frame)), lambda acc, count: acc + count))):
    result = data_frame[begin:end]
    result = result.reset_index(drop=True)

    print(name, len(result))

    if (name == 'rent'):
        result.to_csv(f'data/{name}.csv', index_label='ID')
    else:
        result.drop(columns=['家賃 + 管理費・共益費']).to_csv(f'data/test-{name}.csv', index_label='ID')
        result['家賃 + 管理費・共益費'].to_csv(f'data/predict-{name}.csv', index_label='ID')
