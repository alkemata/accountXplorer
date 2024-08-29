from dash.dependencies import Input, Output, State
from FinanceX import functions as functions
from FinanceX import appedit
from FinanceX.ui.edit_ui import layout_categories

import pandas as pd
from dash import no_update

app=appedit

@app.callback(
        Output('detail-table', 'data'),
        [Input('pivot-table', 'active_cell')]
    )
def display_details(active_cell):
        if active_cell:
            row = active_cell['row']
            col = active_cell['column_id']
            category = pivot_table.index[row]
            month = pd.Period(col, freq='M')  # Convert string back to Period
            # Filter the dataframe based on the selected category and month
            filtered_df = df[(df['Kategorie'] == category) & (df['Month'] == month)]
            filtered_df = filtered_df.drop(columns=['Month'])
            filtered_df['Buchungsdatum'] = filtered_df['Buchungsdatum'].astype(str)
            return filtered_df.to_dict('records')
        return no_update


@app.callback(
        [Output('pivot-table', 'data'),
        Output('shared-dataframe','df_cat')],
        [Input('update-button', 'n_clicks')],
        [State('detail-table', 'selected_rows'),
         State('detail-table', 'data'),
         State('category-dropdown', 'value'),
         State('shared-dataframe','data')
         ]
    )
def update_category(n_clicks, selected_rows, detail_data, selected_category,df):
        if n_clicks > 0 and selected_rows and selected_category:
            detail_df = pd.DataFrame(detail_data)
            selected_indices = detail_df.iloc[selected_rows].index
            
            # Update the original dataframe
            for index in selected_indices:
                df.loc[index, 'Kategorie'] = selected_category
            
            # Recreate pivot table
            new_pivot_table = functions.create_pivot_table(df)
            
            # Update data tables
            return new_pivot_table.reset_index().to_dict('records')
        return no_update, new_pivot_table

@app.callback(
        Output('save-button', 'n_clicks'),
        Input('save-button', 'n_clicks'),
        State('shared-dataframe','data')
    )
def save_dataframe(n_clicks,df):
        if n_clicks > 0:
            functions.save_df(df)
        return 0

@app.callback(
    [Output('log', 'value'),
    Output('shared-dataframe','data'),
    Output('categories','children'),
    Output('shared-categories','data')
    ],
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
            return "",None,None,None  # No clicks yet
        log_message=''
    #merge new data
        res=functions.merge_new_data(file1, file2)
        if res.code==1:
            df=res.data
        else:
            log_message=res.msg
            return log_message, None, None,None
        log_message += res.msg+'\n'
        account_data=functions.load_account_data(file3)
        log_message += 'Accounts configuration file loaded.'
        categories=functions.pivot_table(file4)
        category_order=functions.load_categories(file4)
        layout2=layout_categories(categories,account_data,category_order)
        return log_message, account_data.to_dict('records'), layout2,categories.to_dict('records')