from dash.dependencies import Input, Output, State
from FinanceX import functions as functions
from FinanceX import appedit
from FinanceX.ui.edit_ui import layout_categories

import pandas as pd
from dash import no_update

app=appedit

@app.callback(
        Output('detail-table', 'data'),
        [Input('pivot-table', 'active_cell'),
        Input('pivot-table','data'),
        Input('table-global','data'),
        ]
    )
def display_details(active_cell,pivot, datafrme):
        if active_cell:
            row = active_cell['row']
            col = active_cell['column_id']
            pivot_table=pd.DataFrame(pivot)
            df=pd.DataFrame(dataFrame)
            category = pivot_table.index[row]
            month = pd.Period(col, freq='M')  # Convert string back to Period
            # Filter the dataframe based on the selected category and month
            filtered_df = df[(df['Kategorie'] == category) & (df['Month'] == month)]
            filtered_df = filtered_df.drop(columns=['Month'])
            filtered_df['Buchungsdatum'] = filtered_df['Buchungsdatum'].astype(str)
            return filtered_df.to_dict('records')
        return no_update


@app.callback(
        [
        Output('data_table','data'),
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
    [Output('log', 'value'),
    Output('pivot-table','data'),
    Output('pivot-table','columns'),
    Output('table-global','data'),
    Output('table-global','columns')
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
            return "",no_update,no_update  # No clicks yet
        log_message=''
    #merge new data
        res=functions.merge_new_data(file1, file2)
        if res['code']==1:
            df=res['data']
        else:
            log_message=res['msg']
            return log_message, no_update, no_update
        log_message += res['msg']+'\n'
        account_data=df
        log_message += 'Accounts configuration file loaded - '+str(categories.columns)
        categories=functions.pivot_table(file4,df)
        category_order=functions.load_categories(file4)
        #layout2=layout_categories(categories,account_data,category_order)
        return log_message, categories.reset_index().to_dict('records'), categories.reset_index().columns,account_data.to_dict('records'),account_data.columns