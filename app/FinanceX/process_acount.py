import functions
import pandas as pd
import os
import csv
ressources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'resources')


file0='non_processed.csv'
file1='accounts.txt'
file2='processed.csv'
file3='config.txt'
file4='categories.txt'
file5='budget.txt'
file6='occurences.csv'

print('1 - Loading data')
df_existing = pd.read_csv(os.path.join(ressources_dir,file0),sep=';') #todo merge with load_data
df_existing['Buchungsdatum'] = pd.to_datetime(df_existing['Buchungsdatum'], format='%d.%m.%Y')
df_existing['Betrag'] = pd.to_numeric(df_existing['Betrag'].replace(',','.',regex=True), errors='coerce')
df_existing['Betrag']=df_existing['Betrag'].astype(float)
df_existing=df_existing[['Buchungsdatum','Empfaenger','Verwendungszweck','Buchungstext','Betrag','IBAN','Kategorie','Konto','Umbuchung','Notiz','Schlagworte']]
df_existing['Kategorie'] = df_existing.apply(functions.detect_transfers, axis=1) 
df_existing['Month']=0
df_existing['Saldo']=0
df=df_existing

print('2 - creating pivot table for categories')
categories = functions.load_categories(os.path.join(ressources_dir,file4))
category_order = []
for sublist in categories.values():
    category_order.extend(sublist)
df['Buchungsdatum'] = pd.to_datetime(df['Buchungsdatum'], format='%d-%m-%Y')
df['Month']=df['Buchungsdatum'].dt.month
#df['Betrag'] = pd.to_numeric(df['Betrag'].str.replace(',', '.'))
# Set the category order
df['Kategorie'] = pd.Categorical(df['Kategorie'], categories=category_order, ordered=True)
pivot_table = df.pivot_table(values='Betrag', index='Kategorie', columns='Month', aggfunc='sum', fill_value=0)
pivot_table.columns = pivot_table.columns.astype(str)  # Convert Period to str
pivot_table = pivot_table.reindex(category_order)  # Reindex to enforce the order
#    for col in pivot_table.select_dtypes(include=['float', 'int']).columns:
#        pivot_table[col] = pivot_table[col].map('{:.2f}'.format)


print('3- Calculating saldo')
rows = pd.read_csv(os.path.join(ressources_dir,file1), parse_dates=['Date']).to_dict(orient='records')

for row in rows:
    account = row['Account']
    start_date = pd.to_datetime(row['Date']) 
    initial_saldo = float(row['Saldo'])

    before_start_date = df[
        (df['Konto'] == account) & 
        (df['Buchungsdatum'] < start_date)
    ]

    after_start_date = df[
        (df['Konto'] == account) & 
        (df['Buchungsdatum'] >= start_date)
    ].sort_values(by='Buchungsdatum',ascending=True)# Make a copy to avoid modifying the original DataFrame

    # Calculate the saldo for the transactions after the start date
    after_start_date['Saldo'] = initial_saldo + after_start_date['Betrag'].cumsum()

    # Combine before and after DataFrames
    account_merged = pd.concat([before_start_date, after_start_date])

    merged_data.append(account_merged)
merged_df = pd.concat(merged_data)
merged_df = merged_df.sort_values(by='Buchungsdatum', ascending=False)
df=merged_df

df.to_csv(s.path.join(ressources_dir,file2))

print('4 - Claculating occurences')
data=functions.load_budget(file5).to_dict('records')
occurrences = []
for row in rows:
    type_ = int(row['type'])
    datetype = pd.to_datetime(row['datetype'],dayfirst=True)
    description = row['description']
    amount = row['amount']
    account = row['account']

    if type_ == 0:
        occurrences.append({
            'date': datetype.strftime('%d-%m-%Y'),
            'amount': str(amount),
            'description': description,
            'account': account
        })
    elif type_ == 1:
        for i in range(12):
            new_date = (datetype + pd.DateOffset(months=i)).strftime('%d-%m-%Y')
            occurrences.append({
                'date': new_date,
                'amount': str(amount),
                'description': description,
                'account': account
            })
    elif type_ == 2:

        for i in range(0, 12, 3):
            new_date = (datetype + pd.DateOffset(months=i)).strftime('%d-%m-%Y')
            occurrences.append({
                'date': new_date,
                'amount': str(amount),
                'description': description,
                'account': account
            })
    elif type_ == 3:
        new_date = datetype
        occurrences.append({
            'date': new_date.strftime('%d-%m-%Y'),
            'amount': str(amount),
            'description': description,
            'account': account
        })
occ= pd.DataFrame(occurrences)
file2_path=os.path.join(ressources_dir,file6)
occ.to_csv(file2_path, index=False)

