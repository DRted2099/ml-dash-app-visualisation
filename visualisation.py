import pandas as pd
import numpy as np
import os
import glob
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State, no_update
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


# df = pd.read_csv('../nodejs/stats_new/adaptive_main.csv')

## Extract path of all .csv files
f_path = glob.glob('../nodejs/stats_new/*.csv')

##Extract names of the .csv files from the path
f_names = [os.path.basename(path) for path in f_path]

label_names = [names.replace(".csv","_equipment").replace("_"," ").title() for names in f_names]



## Create a dictionary with all the dataframes
## key : value = f_names[i] : pd.read_csv(f_path[i])

df_dict = {}

for i in range(len(f_path)):
    df_name = f_names[i]
    df_content = pd.read_csv(f_path[i])
    df_dict[df_name] = df_content

# df = df_dict[f_names[0]]

## Make a list of the keys
df_keys = list(df_dict.keys())
# print(df_keys)

# col_names = df.columns.tolist()
# print(col_names)
# item_names = df['Name'].tolist()

load_figure_template("darkly")

fig = px.bar(template='darkly')

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

server = app.server

grid = dag.AgGrid(
    id="table1",
    className="ag-theme-quartz-dark",    
    dashGridOptions={"pagination": True, "paginationAutoPageSize": True}
)

app.layout = dbc.Container([
    html.H1(children = 'MLBB Equipment Dashboard', style={"font-weight": "bold"}),
    html.Br(),
    html.H6(children = 'Equipment Type', style={"font-weight": "bold"}),
    dcc.Dropdown(
        options=[{'label':labels, 'value': names} for labels, names in zip(label_names, f_names)], 
        value = df_keys[0],
        style= {"font":dbc.themes.DARKLY}, 
        id="data_frame_dd"),
    html.Br(),
    html.H6(children = 'Stat', style={"font-weight": "bold"}),
    dcc.Dropdown(id="col_dd"),
    html.Br(),
    html.Button(children="Submit", id="sub_but", n_clicks=0),
    html.Hr(),
    html.Br(),
    html.H3(children = 'Equipment Table', style={"font-weight": "bold"}),
    grid,
    html.Br(),
    html.Br(),
    html.H3(children = 'Equipment vs Stats (Dynamic)', style={"font-weight": "bold"}),
    dcc.Graph(figure=fig, id="graph1", className="dbc")
], 
className="dbc"
)

@callback(
    
    Output(component_id="table1", component_property="rowData"),
    Output(component_id="table1", component_property="columnDefs"),

    Output(component_id="col_dd", component_property="options"),
    Output(component_id="col_dd", component_property="value"),

    Input(component_id="data_frame_dd", component_property="value"),
    
)

def update_df_dd(df_dropdown):

    # print(df[dropdown_value])
    dff = df_dict[df_dropdown]

    dff_row = dff.to_dict("records")
    dff_col = [{"field":i} for i in dff.columns]

    dff_col_names = dff.columns.tolist()
    remove_item = ["Name", "status"]
    filtered_dff_col_names = [item for item in dff_col_names if item not in remove_item]

    dd_col_options = filtered_dff_col_names
    dd_col_value = filtered_dff_col_names[0]

    return dff_row, dff_col, dd_col_options, dd_col_value

@callback(
    Output(component_id="graph1", component_property="figure"),
    Input("sub_but", "n_clicks"),
    State(component_id="col_dd", component_property="value"),
    State(component_id="data_frame_dd", component_property="value")
)

def update_graph(n_clicks,col_value, df_dropdown):

    if n_clicks == 0:
        return no_update

    dff = df_dict[df_dropdown]
    fig = px.bar(dff, x="Name", y=col_value, text=dff[col_value])

    return fig

if __name__ == "__main__":
    app.run(debug = True)

