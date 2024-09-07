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
file7='new_categories.txt'

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
rows = pd.read_csv(os.path.join(ressources_dir,file1),header=0,sep=';').to_dict(orient='records')
rows= pd.read_csv('your_data_file.csv')
# Ensure that the 'date' column is in datetime format (if not already)
rows['date'] = pd.to_datetime(rows['date'])
# Create a dictionary in the desired format
account_dict = {
    row['account']: {'date': row['date'], 'saldo': row['saldo']}
    for _, row in rows.iterrows()
}


initial_date=date = account_dict[account]['date']
df_calc=df[df['Buchungsdatum']>=initial_date]

def calculate_saldo(group, initial_saldo):
    group['Saldo'] = initial_saldo + group['Betrag'].cumsum()
    return group

df = df_calc[].groupby('Konto', group_keys=False).apply(lambda g: calculate_saldo(g, initial_saldo[g.name]['saldo']))
print(df)

print('4 - Calculating occurences')
data=functions.load_budget(file5).to_dict('records')
occurrences = []
for row in data:
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


print('4 - New categorizing')
file7_path=os.path.join(ressources_dir,file7)

with open(file7_path, 'r') as file:
    keywords = {}
    for line in file:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if line.startswith(' '):  # Assuming sub-categories are indented
            if current_category:
                        # Split the line into category and keywords
                category, kw = stripped_line.split(':')
                # Strip whitespace and split keywords by comma
                keywords[category.strip()] = [k.strip().lower() for k in kw.split(',')]
                categories[current_category].append(category.strip())
        else:
            current_category = stripped_line
            categories[current_category] = []
keywords={k: v for k, v in keywords.items() if v != ['']}


def categorize_spending(receiver, description, categories):
    # Combine receiver and description for keyword search
    combined_text = f"{receiver.lower()} {description.lower()}"

    # Iterate through categories and their keywords
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in combined_text:
                return category
    
    # Default category if no keywords match
    return 'Uncategorized'

df['Category'] = df.apply(lambda x: categorize_spending(str(x['Empfaenger']), str(x['Verwendungszweck']), keywords), axis=1)
print('Total number of elements: '+str(df.shape[0]))
print('Uncategorized: '+str(df[df['Category']=='Uncategorized'].shape[0]))

df['Buchungsdatum'] = pd.to_datetime(df['Buchungsdatum'])
df['Buchungsdatum']=df['Buchungsdatum'].dt.strftime('%d-%m-%Y')
df.to_csv(os.path.join(ressources_dir,file2),index=False)
