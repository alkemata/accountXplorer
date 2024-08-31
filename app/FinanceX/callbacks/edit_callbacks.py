from dash.dependencies import Input, Output, State
from FinanceX import functions as functions
from FinanceX import appedit
from FinanceX.ui.edit_ui import layout_categories, layout_list_global, layout_saldo, layout_planning

import pandas as pd
from dash import no_update, callback_context

app=appedit

@app.callback(
        [Output('detail-table', 'data'),
        Output('log2','value')],
        [Input('pivot-table', 'active_cell'),
        Input('pivot-table','data'),
        Input('table-global','data'),
        ]
    )
def display_details(active_cell,pivot, dataframe):
        if active_cell:
            row = active_cell['row']
            col = active_cell['column_id']
            pivot_table=pd.DataFrame(pivot).reset_index()
            df=pd.DataFrame(dataframe)
            category = pivot_table.iloc[row]['Kategorie']
            month=col
            #month = pd.Period(col, freq='M')  # Convert string back to Period
            # Filter the dataframe based on the selected category and month
            filtered_df = df[(df['Kategorie'] == category) & (df['Month'] == int(month))]
            filtered_df = filtered_df.drop(columns=['Month'])
             #filtered_df['Buchungsdatum'] = filtered_df['Buchungsdatum'].astype(str)
            return filtered_df.to_dict('records'),str(row)+' - '+category
        return no_update,''


@app.callback(
        [Output('data_table','data'),
        Output('data_table','columns'),
        ],
        [Input('update-button-2', 'n_clicks')],
        [State('table-global', 'data'),
        State('detail-table', 'selected_rows'),
         State('detail-table', 'data'),
         State('category-dropdown', 'value'),
         ]
    )
def update_category(n_clicks, df_data,selected_rows, detail_data, selected_category):
        if n_clicks > 0 and selected_rows and selected_category:
            df=pd.DataFrame(df_data)
            detail_df = pd.DataFrame(detail_data)
            selected_indices = detail_df.iloc[selected_rows].index
            # Update the original dataframe
            for index in selected_indices:
                df.loc[index, 'Kategorie'] = selected_category
            
            # Recreate pivot table
            new_pivot_table = functions.create_pivot_table(df)
            
            # Update data tables
            return df.reset_index().to_dict('records'),df.reset_index().column.to_dict('records')
        return no_update, no_update

@app.callback(
        Output('save-button', 'n_clicks'),
        Input('save-button', 'n_clicks'),
    )
def save_dataframe(n_clicks):
        if n_clicks > 0:
            print('toto')
          #  functions.save_df()
        return 0

@app.callback(
    [Output('log','value'),
    Output('part-list-global','children'),
    Output('part-pivottable','children'),
    Output('part-saldo','children'),
    Output('part-planning','children')
    ] ,
    Input('update-button', 'n_clicks'),
    State('file1', 'value'),
    State('file2', 'value'),
    State('file3', 'value'),
    State('file4', 'value')
    )

def update_file_account(n_clicks, file1, file2, file3, file4):
        with open('log', 'a') as file:
            file.write("Callback activated\n")
        if n_clicks is None:
            return "",no_update,no_update, no_update,no_update # No clicks yet
        log_message=''
    #merge new data
        res=functions.merge_new_data(file1, file2)
        if res['code']==1:
            df=res['data']
        else:
            log_message=res['msg']
            return log_message, no_update, no_update,no_update,no_update
        log_message += res['msg']+'\n'
        categories=functions.pivot_table(file4,df)
        log_message += 'Accounts configuration file loaded - '+str(categories.columns)
        unique_accounts = df['Konto'].unique()
        category_order=functions.load_categories(file4)
        layout1=layout_list_global(df)
        layout2=layout_categories(categories,df,category_order)
        layout3=layout_saldo(unique_accounts)
        data=functions.load_budget('budget.txt') #todo put in ui
        print('test?')
        if data is not None:
            layout4=layout_planning(data.to_dict('records'))        
        else:
            layout4=layout_planning([])
        return log_message,layout1, layout2,layout3,layout4

@app.callback(
    Output('table-global', 'data'),
    [Input('filter-button', 'n_clicks'),
    Input('filter-input','value'),
    Input('calculate-button', 'n_clicks')],
    [State('table-global','data'),
    State('saldo-input-table', 'data')]
)
def update_global_table(n_clicks,filter_value,n_clicks2,data,saldo_input_data):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'filter-input':
        data2=update_table(n_clicks,filter_value,data)
    if button_id=='calculate-button':
        data2=calculate_saldo(n_clicks2, saldo_input_data, data)
    return data2

def update_table(n_clicks,filter_value,data):
    if n_clicks == 0:
        return no_update
    df=pd.DataFrame(data)
    if not filter_value:
        # Return the original data if no filter is provided
        return df.to_dict('records')

    try:
        # Parse the filter input
        col_name, filter_val = filter_value.split(':')
        # Filter the dataframe
        filtered_df = df[df[col_name].str.contains(filter_val, case=False, na=False)]
        return filtered_df.to_dict('records')
    except Exception as e:
        # Return an empty table or handle errors if the input format is wrong
        return df.to_dict('records')

def calculate_saldo(n_clicks, saldo_input_data, transaction_data):
    if n_clicks == 0:
        return no_update

    # Convert transaction data to DataFrame
    transactions_df = pd.DataFrame(transaction_data)
    transactions_df['Buchungsdatum'] = pd.to_datetime(transactions_df['Buchungsdatum'])
    transactions_df['Betrag']=transactions_df['Betrag'].astype(float)
    
    # Initialize list to hold calculated saldo for each account
    calculated_saldos = []
    merged_data = []

    # Calculate saldo for each account
    for row in saldo_input_data:
        account = row['Account']
        start_date = pd.to_datetime(row['Date']) 
        initial_saldo = float(row['Saldo'])

        before_start_date = transactions_df[
            (transactions_df['Konto'] == account) & 
            (transactions_df['Buchungsdatum'] < start_date)
        ]
        
        after_start_date = transactions_df[
            (transactions_df['Konto'] == account) & 
            (transactions_df['Buchungsdatum'] >= start_date)
        ].copy()  # Make a copy to avoid modifying the original DataFrame

        # Calculate the saldo for the transactions after the start date
        after_start_date['Saldo'] = initial_saldo + after_start_date['Betrag'].cumsum()

        # Combine before and after DataFrames
        account_merged = pd.concat([before_start_date, after_start_date])

        merged_data.append(account_merged)
    merged_df = pd.concat(merged_data)
    merged_df = merged_df.sort_values(by='Buchungsdatum', ascending=False)
    return merged_df.to_dict('records')

@app.callback(
    Output('output-table', 'data'),
    Input('update-button', 'n_clicks'),
    State('input-table', 'data')
)
def update_occurrences(n_clicks, rows):
    if n_clicks > 0:
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
        #occ.columns=['Date','Amount','Description', 'Account']
        return occ.to_dict('records')
    return no_update

# Callback to add a row to the input table
@app.callback(
    Output('input-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('input-table', 'data'),
    State('input-table', 'columns')
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows