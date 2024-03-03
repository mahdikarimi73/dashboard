import pandas as pd
import random
import dash
from dash import dcc , html , Dash, html , Input, Output , State , dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import jalali_pandas
import arrow
import jdatetime


########################################## خواندن داده ها #######################################

global saved_df
global plan_df
global structure_df

saved_df = pd.read_excel("C:\\Users\\Mahdi Karimi\\Desktop\\saved_data2.xlsx")
plan_df = pd.read_excel("C:\\Users\\Mahdi Karimi\\Desktop\\plans.xlsx")
structure_df = pd.read_excel("C:\\Users\\Mahdi Karimi\\Desktop\\organ_structure.xlsx")


######################################## تابع جلالی #######################################
def jalali(data):
    year , month , date = map(int, data.split("-"))
    jalali_date = jdatetime.date(year , month , date)
    return jalali_date

##################################    تابع محاسبه ماه ###################################

def months_between(start_date, end_date):
    # Calculate the difference in years and convert to months
    year_diff = end_date.year - start_date.year
    months_from_years = year_diff * 12
    
    # Calculate the difference in months
    month_diff = end_date.month - start_date.month
    
    # Combine the two differences to get total months difference
    total_months_diff = months_from_years + month_diff
    
    return total_months_diff + 1


######################################### توابع ساختن نمودار ###################################

def generate_random_color():
    return f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}'

def bar_with_line(data_frame, x, y, title=None):                       # Visualization function

    if y == "تعداد":
        y2 = "تعداد حدانتظار"
    elif y == "درصد":
        y2 = "درصد حدانتظار"
    
    unique_combinations = data_frame[['خانه بهداشت', 'خدمت']]
    color_map = {f"{row['خانه بهداشت']}_{row['خدمت']}": generate_random_color() for index, row in unique_combinations.iterrows()}

    fig = go.Figure()

    for index, row in unique_combinations.iterrows():
        place_service_key = f"{row['خانه بهداشت']}_{row['خدمت']}"
        place_color = color_map[place_service_key]
        
        place_service_data = data_frame[(data_frame['خانه بهداشت'] == row['خانه بهداشت']) & (data_frame['خدمت'] == row['خدمت'])]

    place_service_data[x] = place_service_data[x].apply(jalali)

        
    fig.add_trace(go.Bar(x=place_service_data[x], y=place_service_data[y], name=f"{row['خانه بهداشت']} - {row['خدمت']} - {y}", marker_color=place_color))
    fig.add_trace(go.Scatter(x=place_service_data[x], y=place_service_data[y2], mode='markers+lines', name=f"{row['خانه بهداشت']} - {row['خدمت']} - {y2}", marker_color=place_color, line=dict(color=place_color)))

    fig.update_layout(xaxis_title=x,
                      yaxis_title=y,
                      legend_title="خانه بهداشت - خدمت")

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 ماه", step="month", stepmode="backward"),
                    dict(count=3, label="3 ماه", step="month", stepmode="backward"),
                    dict(count=6, label="6 ماه", step="month", stepmode="backward"),
                    dict(count=1, label="1 سال", step="year", stepmode="backward"),
                    dict(step="all", label="تمام")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    # Update layout to show all date marks on the x-axis
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(data_frame[x]),
            ticktext=list(data_frame[x])
        )
        )
    fig.update_layout(template='seaborn')


    return fig




###################################### لایه های اپلیکیشن ########################################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)
server = app.server
CONTENT_STYLE = {
    "margin-right": "2rem",
    "margin-left": "2rem",
    "padding": "2rem 1rem",
}

app.layout = html.Div([
    dbc.Row([
        dbc.Tabs(
            [
                dbc.Tab(label="شاخص های مراقبتی", tab_id="tab-1"),
                dbc.Tab(label="اطلاعات تندرستی", tab_id="tab-2"),
                dbc.Tab(label="ورود اطلاعات", tab_id="tab-3"),
            ],
            id="tabs",
            active_tab="tab-1",
        ),
    ]),
    html.Div(id='tab-content')  # Placeholder for dynamic content based on active tab
], style=CONTENT_STYLE)


################################# کال بک تغییر تب ها ###########################################
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab')]
)
def render_tab_content(active_tab):
    if active_tab == "tab-1":        
        return html.Div([
            dbc.Row([
            dbc.Col([
                html.Label("واحد", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='unit-dropdown',
                    options=[{'label': unit, 'value': unit} for unit in plan_df['واحد'].unique()],
                    placeholder="انتخاب واحد",
                )
            ], width=2),
            dbc.Col([
                html.Label("خدمت", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='service-dropdown',
                    placeholder="انتخاب خدمت",
                )
            ], width=4),
            dbc.Col([
                html.Label("خانه بهداشت", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='health-house-dropdown',
                    options=[{'label': hh, 'value': hh} for hh in structure_df['خانه بهداشت'].unique()],
                    placeholder="انتخاب خانه بهداشت",
                    multi=True
                )
            ], width=4),
            dbc.Col([
            html.Label("نمایش اطلاعات بر اساس ", style={'text-align': 'right'}),
            dcc.RadioItems(
                id='data-type-selection',
                options=[
                    {'label': 'درصد', 'value': 'درصد'},
                    {'label': 'تعداد', 'value': 'تعداد'},
                ],
                value='درصد',  # Default value
                style={'text-align': 'right', 'color': 'white'}
            )], width=2)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(id='graph-container')
                ])])
        ]),
    elif active_tab == "tab-2":
        return html.Div([
            dbc.Row([
            dbc.Col([
                html.Label("گروه شاخص", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='index-group-dropdown',
                    options=[{'label': unit, 'value': unit} for unit in plan_df['واحد'].unique()],
                    placeholder="انتخاب گروه شاخص",
                )
            ], width=2),
            dbc.Col([
                html.Label("شاخص", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='index-dropdown',
                    placeholder="انتخاب شاخص",
                )
            ], width=4),
            dbc.Col([
                html.Label("خانه بهداشت", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='health-house-dropdown',
                    options=[{'label': hh, 'value': hh} for hh in structure_df['خانه بهداشت'].unique()],
                    placeholder="انتخاب خانه بهداشت",
                    multi=True
                )
            ], width=4),
            dbc.Row([
                dbc.Col([
                    html.Div(id='table-container')
                ])])
        ]),
            # Adapt and place here the content for tab-2
        ])
    elif active_tab == "tab-3":
        return html.Div([
            dbc.Row([
            dbc.Col([
                html.Label("واحد/گروه شاخص", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='unit-index-group-dropdown-input',
                    options=[{'label': unit, 'value': unit} for unit in plan_df['واحد'].unique()],
                    placeholder="انتخاب واحد/گروه شاخص",
                )
            ], width=2),
            dbc.Col([
                html.Label("خدمت/شاخص", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='service-index-dropdown-input',
                    placeholder="انتخاب خدمت/شاخص",
                )
            ], width=4),
            dbc.Col([
                html.Label("خانه بهداشت", style={'text-align': 'right'}),
                dcc.Dropdown(
                    id='health-house-dropdown-input',
                    options=[{'label': hh, 'value': hh} for hh in structure_df['خانه بهداشت'].unique()],
                    placeholder="انتخاب خانه بهداشت"
                )
            ], width=4)]),
            dbc.Row([html.Div(id='table-container')]),
            dbc.Row([
            dbc.Col(dcc.Input(id='date-text-input', type='text', placeholder='تاریخ را به صورت 01-01-1400 وارد کنید')),
            dbc.Col(dcc.Input(id='population-input', type='number', placeholder="جمعیت")),
            dbc.Col(dcc.Input(id='quantity-input', type='number', placeholder="تعداد")),
            dbc.Col(dbc.Button("اضافه کردن", id='add-button', n_clicks=0, className="mt-2"))]),
        ]),



############################# کال بک آپدیت خدمت بر اساس واحد ##################################
@app.callback(
    Output('service-dropdown', 'options'),
    [Input('unit-dropdown', 'value')]
)
def set_service_options(selected_unit):
    if not selected_unit:
        return []
    filtered_services = plan_df[plan_df['واحد'] == selected_unit]['خدمت'].unique()
    return [{'label': service, 'value': service} for service in filtered_services]



@app.callback(
    Output('service-index-dropdown-input', 'options'),
    [Input('unit-index-group-dropdown-input', 'value')]
)
def set_service_options(selected_unit):
    if not selected_unit:
        return []
    filtered_services = plan_df[plan_df['واحد'] == selected_unit]['خدمت'].unique()
    return [{'label': service, 'value': service} for service in filtered_services]



#################################### کال بک آپدیت گراف #########################################
@app.callback(
    Output('graph-container', 'children'),
    [Input('unit-dropdown', 'value'),
     Input('service-dropdown', 'value'),
     Input('health-house-dropdown', 'value'),
     Input("data-type-selection", "value")]
)
def update_graph(selected_unit, selected_service, selected_houses, selected_datatype):
    if not selected_unit or not selected_service or not selected_houses:
        return html.Div("لطفا واحد، خدمت، و خانه بهداشت را برای نمایش نمودار انتخاب کنید.")

    filtered_df = saved_df[(saved_df['واحد'] == selected_unit) & 
                     (saved_df['خدمت'] == selected_service) & 
                     (saved_df['خانه بهداشت'].isin(selected_houses))]

    if selected_datatype == "تعداد":                 
        fig = bar_with_line(filtered_df, 'تاریخ شمسی', 'تعداد', f"نمودار مراقبت انجام شده نسبت به حد انتظار {selected_service} در خانه بهداشت {' و '.join(selected_houses)}")
    else:
        fig = bar_with_line(filtered_df, 'تاریخ شمسی', 'درصد', f"نمودار مراقبت انجام شده نسبت به حد انتظار {selected_service} در خانه بهداشت {' و '.join(selected_houses)}")

    return dcc.Graph(figure=fig)



#################################### کال بک آپدیت جدول ########################################
@app.callback(
    Output('table-container', 'children'),
    [Input('unit-index-group-dropdown-input', 'value'),
     Input('service-index-dropdown-input', 'value'),
     Input('health-house-dropdown-input', 'value')]
)
def update_table(selected_unit_group_index ,selected_service_index, selected_house):
    filtered_df = saved_df[(saved_df['واحد'] == selected_unit_group_index) & 
                     (saved_df['خدمت'] == selected_service_index) & 
                     (saved_df['خانه بهداشت'] == selected_house)]
    table = dbc.Table.from_dataframe(filtered_df, striped=True, bordered=True, hover=True)
    return table



###################################### کال بک ورود اطلاعات #####################################
@app.callback(
    Output('table-container', 'children', allow_duplicate=True),
    [Input('add-button', 'n_clicks')],
    [State('date-text-input', 'value'),
     State('population-input', 'value'),
     State('quantity-input', 'value'),
     State('unit-index-group-dropdown-input', 'value'),
     State('service-index-dropdown-input', 'value'),
     State('health-house-dropdown-input', 'value')],
     prevent_initial_call=True
)
def save_table(n_clicks, date, population, quantity, unit, service, house):
    
    global saved_df

    if n_clicks > 0:
        # Ensure that 'index' is properly managed for new row entries
        pass
    
    date = jalali(date)
    # Filtering structure_df for the selected houses
    filter_structure_df = structure_df[structure_df["خانه بهداشت"] == house ]
    headquarter = filter_structure_df["ستاد شهرستان"].iloc[0] if not filter_structure_df.empty else None
    center = filter_structure_df["مرکز خدمات جامع سلامت"].iloc[0] if not filter_structure_df.empty else None

    # Filtering plan_df for the selected service
    filter_plan_df = plan_df[plan_df["خدمت"] == service]
    age_group = filter_plan_df["گروه سنی"].iloc[0] if not filter_plan_df.empty else None
    service_package = filter_plan_df["بسته خدمتی"].iloc[0] if not filter_plan_df.empty else None
    start_date = filter_plan_df["تاریخ شروع"].iloc[0] if not filter_plan_df.empty else None
    start_date = jalali(start_date)
    end_date = filter_plan_df["تاریخ پایان"].iloc[0] if not filter_plan_df.empty else None
    end_date = jalali(end_date)
    duration = filter_plan_df["مدت ماهانه"].iloc[0] if not filter_plan_df.empty else None
    expect_rate = filter_plan_df["درصد حد انتظار ماهانه"].iloc[0] if not filter_plan_df.empty else 0
    between_month = months_between(start_date, date)
    print(between_month)
    expect_percent = expect_rate *  between_month
    expect_number = expect_percent * population / 100
    percent = (quantity/population) * 100

    # Add new row to saved_df
    new_row_df = pd.DataFrame([{
        'تاریخ شمسی': date,
        'جمعیت': population,
        'تعداد': quantity,
        'درصد' : percent,
        'واحد': unit,
        'خدمت': service,
        'ستاد شهرستان': headquarter,
        'مرکز خدمات جامع سلامت': center,
        'گروه سنی': age_group,
        'بسته خدمتی': service_package,
        'تاریخ شروع': start_date,
        'تاریخ پایان': end_date,
        'مدت ماهانه': duration,
        'تعداد حدانتظار': expect_number,
        'درصد حدانتظار': expect_percent,
        'درصد حد انتظار ماهانه' : expect_rate , 
        'خانه بهداشت': house
    }])

    # Append the new row to the DataFrame
    saved_df = pd.concat([saved_df, new_row_df], ignore_index=True)

    # Regenerate the table with the updated DataFrame
    table = dbc.Table.from_dataframe(saved_df, striped=True, bordered=True, hover=True)
    
    saved_df.to_excel("C:\\Users\\Mahdi Karimi\\Desktop\\saved_data2.xlsx", index=False)
    return table




if __name__ == "__main__":
    app.run_server(debug=True)
