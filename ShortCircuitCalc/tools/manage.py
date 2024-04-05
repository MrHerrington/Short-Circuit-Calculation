import csv
import pandas as pd
from ShortCircuitCalc.config import ROOT_DIR
from ShortCircuitCalc.config import DATA_DIR


# with open('C:/Users/ib225/Desktop/СН_v4 вспом. зд.txt', 'r', encoding='UTF-8') as file:
#     data = file.readlines()
#     for i in range(len(data)):
#         data[i] = data[i].strip('\n')
#         data[i] = data[i].replace(',', '.')
#         data[i] = data[i].replace('\t', ',')
#         data[i] = data[i].split(',')
#     df = pd.DataFrame(data)
#     df.to_csv(path_or_buf=ROOT_DIR / 'data/other_resistance_catalog', index=False,encoding='UTF-8', sep=',',
#               header=df.iloc[0].name, escapechar=' ', quoting=csv.QUOTE_NONE)

