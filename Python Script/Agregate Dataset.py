import pandas as pd
import ast
from sklearn.model_selection import train_test_split
# pd.set_option('display.max_rows', 14900 )
# pd.set_option('display.max_columns', 100000 )
# pd.set_option('display.width',100000)
# pd.set_option('max_colwidth', 10000)
data=pd.read_csv("Groceries.csv")
data=pd.DataFrame(data)


cekduplikat = data.duplicated(keep='first').sum()
print("Banyak Duplikat:",cekduplikat)
groceries_df_cleaned = data.copy().drop_duplicates(keep='first')

# print(groceries_df_cleaned)
#Agregasi
data_transaksi = groceries_df_cleaned.groupby(['Member_number', 'Date']).agg({'itemDescription': list}).reset_index()
data_transaksi=pd.DataFrame(data_transaksi)
print(data_transaksi)
data_transaksi.astype(str).to_csv('Dataset For Modeling.csv',index=False)
