import pandas as pd

df = pd.DataFrame({'test': [1,2,3,4,5,6,7,8,9,10],
                   'balls':[1,2,3,4,5,6,7,8,9,10]})
# print(df)
subrange = df['test'][6:9]
print(subrange)
print(subrange.loc[8])
# print(subrange[subrange > 8])
# argmin = subrange.argmin()
# index = subrange.index[argmin]
# # print(index)