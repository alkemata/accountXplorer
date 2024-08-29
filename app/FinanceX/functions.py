import pandas as pd
import os
from flask import current_app
ressources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'resources')

def load_categories(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    categories = {}
    current_category = None

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if line.startswith(' '):  # Assuming sub-categories are indented
            if current_category:
                categories[current_category].append(stripped_line)
        else:
            current_category = stripped_line
            categories[current_category] = []
    return categories

def save_df(dataframe): #TODO remove duplicate functions with overview
    dataframe.to_csv('saved_dataframe.csv', index=False)

def load_data(file1):
    if os.path.exists(os.path.join(ressources_dir,file1)):
        df = pd.read_csv(os.path.join(ressources_dir,file1), sep=',') #TO>DO put file in ressources directory. See in edit as well
        df['Buchungsdatum'] = pd.to_datetime(df['Buchungsdatum'], format='%Y-%m-%d')
    return df

def load_account_data(file3):
    account_data = {}
    with open(filename, mode='r') as file:
        reader = csv.reader(os.path.join(ressources_dir,file3),delimiter=';')
        #next(reader)  # Skip the header row if there is one
        for row in reader:
            account_code = row[0]
            account_name = row[1]
            account_value = float(row[2])  # Assuming the value column contains numeric data
            account_data[account_code] = {'name': account_name, 'value': account_value}
    return account_data

def detect_transfers(row):
    if row['Konto']=='DE39360100430206819439':
        if row['Kategorie']=='PayPal':
            row['Kategorie']='Umbuchung'
        if row['Umbuchung']=='0-Euro-Konto':
            row['Kategorie']='Umbuchung'
        if row['Buchungstext']=='LASTSCHRIFT':      
            row['Kategorie']='Umbuchung' 
    if row['Konto']=='DE47700400480857576300':
        if row['Umbuchung']=='Postbank Giro extra plus':
            row['Kategorie']='Umbuchung'
    if row['Konto']=='PayPal (albanatita@gmail.com)':
        if row['Kategorie']=='Sonstige Einnahmen':
            row['Kategorie']='Umbuchung'
    return row['Kategorie']

    df['Month'] = df['Buchungsdatum'].dt.to_period('M')
    return df

def merge_new_data(file1, file2):
    try:
        df_existing = pd.read_csv(os.path.join(ressources_dir,file2))
    except Exception as e:
        print('File note found')
        return {'code': 0, 'msg':  str(e) + ' - '+os.path.join(ressources_dir,file2)}
   # Load the CSV with additional rows-
    try:
        df_new = pd.read_csv(os.path.join(ressources_dir,file1))
    except FileNotFoundError as e:
        return {'code': 1, 'msg': 'No update of transactions found, just loading existing file', 'data':df_existing}
    df_new['Betrag'] = pd.to_numeric(df_new['Betrag'].replace(',','.',regex=True), errors='coerce')
    df_new = df_new.drop(columns=['Wertstellungsdatum', 'BIC', 'Notiz','Schlagworte','SteuerKategorie','ParentKategorie','Splitbuchung','AbweichenderEmpfaenger'])
    df_new['Buchungsdatum'] = pd.to_datetime(df['Buchungsdatum'], format='%d.%m.%Y')
    df_new['Kategorie'] = df.apply(detect_transfers, axis=1)  
    # Concatenate the existing DataFrame and new data
    df_combined = pd.concat([df_existing, df_new])
    # Drop duplicates based on only three columns (replace 'column1', 'column2', 'column3' with actual column names)
    df_combined = df_combined.drop_duplicates(subset=['Buchungsdatum', 'Verwendungszweck', 'Empfaenger','IBAN','Konto'])
    # Save the updated DataFrame (if needed)
    df_combined.to_csv(os.path.join(ressources_dir,file2))
    return {'code':1,'msg':'Account data file update', 'data': df_combined}


 
def pivot_table(file4):
    # Predefined list of categories
    categories = load_categories(os.path.join(ressources_dir,file4))
    category_order = []
    for sublist in categories.values():
        category_order.extend(sublist)

    # Set the category order
    df['Kategorie'] = pd.Categorical(df['Kategorie'], categories=category_order, ordered=True)
    pivot_table = df.pivot_table(values='Betrag', index='Kategorie', columns='Month', aggfunc='sum', fill_value=0)
    pivot_table.columns = pivot_table.columns.astype(str)  # Convert Period to str
    pivot_table = pivot_table.reindex(category_order)  # Reindex to enforce the order
    for col in pivot_table.select_dtypes(include=['float', 'int']).columns:
        pivot_table[col] = pivot_table[col].map('{:.2f}'.format)
    return pivot_table


def calculate_saldo():
    accounts=df['Konto'].unique()
    dfs = {k: v for k, v in df.groupby('Konto')}
    for k,v in dfs.items():
            initial_value = account_data[k[0:3]]['value']
            dfs[k] = calculate_differences(initial_value, v)
    merged_df = pd.concat(dfs.values(), axis=0, ignore_index=True)
    merged_df = merged_df.sort_values(by='Buchungsdatum').reset_index(drop=True)