import os
import re

import pandas as pd
import datetime
import matplotlib.pyplot as mp


def add_div_val_column(data, val_1, val_2):
    x = []
    for a, b in zip(data[val_1].values, data[val_2].values):
        if isinstance(a, float) and isinstance(b, float):
            x.append(a / b)
    data[f'{val_1} / {val_2}'] = x


def renamer_func(col_name: str):
    if col_name in CHECK_LIST:
        return 'DATA'
    elif re.match(r'[A-Z]{3}', col_name):
        count = COUNTS.get(col_name, 1)
        return f'{count} {col_name}'
    else:
        return col_name


def filter_frame(datafr):
    for column in datafr:
        if not column.startswith('1') and column != 'DATA':
            datafr.drop(columns=column, inplace=True)
    return datafr


def remove_strings(x):
    if isinstance(x, float):
        return x
    elif isinstance(x, datetime.datetime):
        return x
    else:
        return None


def find_min_or_max(data, column, maximum=True):
    if maximum:
        value = data[column].max()
    else:

        value = data[column].min()
    row = data.loc[data[column] == value]
    val_date = row.iloc[0]['DATA']
    return value, val_date


# list of different names for columns with dates
CHECK_LIST = ['KURS ŚREDNI', 'data',  'Unnamed: 0', 'Data']
# currency list with not standard exchange rate
COUNTS = {
    'HUF': 100,
    'JPY': 100,
    'ISK': 100,
    'IDR': 10000,
    'KRW': 100
}
'''
you can choose pairs of columns that you want to find div values for and create columns with them
also dates of minimum and maximum difference would be printed
leave empty if you only want to integrate tables  
'''
RATIO_PAIRS = ['1 GBP / 1 EUR', '1 BRL / 1 TRY']
# path to data
PATH = './data'


files = os.listdir(PATH)
frames = (pd.read_excel(f'{PATH}/{file}') for file in files if file.endswith('.xls'))
int_frame = None
for frame in frames:
    clean_frame = frame.rename(columns=renamer_func)
    clean_frame = filter_frame(clean_frame)
    clean_frame = clean_frame.applymap(remove_strings)
    if int_frame is None:
        int_frame = clean_frame
    else:
        int_frame = pd.concat([int_frame, clean_frame], ignore_index=True)
    int_frame.drop_duplicates(keep='last', inplace=True, subset=['DATA'])
if any(RATIO_PAIRS):
    for pair in RATIO_PAIRS:
        vals = pair.split(' / ')
        add_div_val_column(int_frame, vals[0], vals[1])
        for prefix, max_flag in (('Maximum', True), ('Minimum', False)):
            val, date = find_min_or_max(int_frame, pair, maximum=max_flag)
            print(f'{prefix} of {pair} and date: {val}, {date}')
    int_frame.plot(x='DATA', y=RATIO_PAIRS, kind='line', figsize=(6, 6))
    mp.show()

# uncomment print to show result data frame in output or .to_excel to create new integrated .xls file
# print(int_frame)
# int_frame.to_excel('./results/result.xls')
