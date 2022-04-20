import pandas as pd
import numpy as np


rng = np.random.default_rng(0)


def format(data_frame):
    result = data_frame

    result = result.drop_duplicates(subset=['URL'])
    result = result.drop(columns=['Unnamed: 0', 'URL', '取り扱い店舗物件コード', 'SUUMO物件コード'])
    result = result.sample(frac=1, random_state=rng)
    result = result.reset_index(drop=True)

    return result


data_frame = format(pd.read_csv('data/rent-raw.csv'))
data_frame.to_csv('data/rent-formatted.csv', index=False)
