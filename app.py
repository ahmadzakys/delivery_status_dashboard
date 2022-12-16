######-----Import Dash-----#####
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px

#####-----Create a Dash app instance-----#####
app = dash.Dash(
    external_stylesheets=[dbc.themes.LITERA],
    name = 'Delivery Status'
    )
app.title = 'Delivery Status Evaluation Dashboard'

##-----Navbar
navbar = dbc.NavbarSimple(
    brand="Delivery Status Evaluation Dashboard",
    brand_href="#",
    color="#242947",
    dark=True,
)


##----- Import DataCoSupplyChain
df=pd.read_csv('DataCoSupplyChainDataset.csv', encoding='ISO-8859-1')
df['order date (DateOrders)']=df['order date (DateOrders)'].astype('datetime64')
df.rename(columns={'order date (DateOrders)':'order date'}, inplace=True)
df['Year']=df['order date'].dt.year

##----- Pie Chart
data_Customer_Segment=df.groupby(['Customer Segment'])['Order Id'].count().reset_index(
    name='Number of Orders').sort_values(
        by= 'Number of Orders',
        ascending= False)

plot_pie = px.pie(data_Customer_Segment, 
            values='Number of Orders', 
            names='Customer Segment', 
            title='Number of Orders of Different Customer Segments', 
            width=450, 
            height=450,
            color_discrete_sequence = ['#242947', '#b8c1ec', '#eebbc2'])

##----- Choropleth
df['Days Shipment Difference']=df['Days for shipping (real)']-df['Days for shipment (scheduled)']
df_geo=df.groupby(['Order Country'])['Days Shipment Difference'].mean().reset_index(
    name='Number of Days').sort_values(
        by= 'Number of Days', 
        ascending= False)

plot_map = px.choropleth(df_geo,
                    locationmode='country names',
                    locations='Order Country',
                    title='Number of Days Difference Between Shipping Real and Scheduled',
                    color='Number of Days', # lifeExp is a column of data
                    hover_name='Order Country', 
                    #hover_data ='Order City',
                    color_continuous_scale=px.colors.sequential.ice)
plot_map.update_layout(title_x=0.5)
plot_map.add_annotation(dict(x=0.2,
                             y=-0.12),
                             showarrow=False,
                             text='Number of Days : Avg(Real Shipping Days - Scheduled Shipping Days)',
                             textangle=0,
                             xanchor='left')
plot_map.add_annotation(dict(x=0.2,
                             y=-0.17),
                             showarrow=False,
                             text='+ : Late Delivery',
                             textangle=0,
                             xanchor='left')
plot_map.add_annotation(dict(x=0.2,
                             y=-0.22),
                             showarrow=False,
                             text='-  : Advanced Delivery',
                             textangle=0,
                             xanchor='left')


## -----LAYOUT-----
app.layout = html.Div(children=[
    navbar,
    
    html.Br(),

    ## --Component Main Page--
    html.Div([
        ## --ROW1--
        dbc.Row([
            ### --COLUMN1--
            dbc.Col([
                dcc.Graph(figure=plot_pie),  
            ],width=4),

            ### --COLUMN2--
            dbc.Col([
                dcc.Graph(figure=plot_map),
            ],
            width=8,
            ),
        ]),

        html.H1('Evaluation by Country',
            style={'textAlign': 'center', 
                   'fontSize': 35, 
                   'background-color':'#242947',
                   'color':'white'}
            ),
        html.Br(),
        ## --ROW2--
        dbc.Row([
            ### --COLUMN1--
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=df['Order Country'].sort_values().unique(),
                            value='Indonesia',
                            style={'font-size' : '100%'},
                        ),
                    ),
            ]),
            ]),
            
            ### --COLUMN2--
            dbc.Col([
                dbc.Card(id='mean_scheduled',color='#b8c1ec',className='text-center',inverse=True),
            ],width=3),
            
            ### --COLUMN3--
            dbc.Col([
                dbc.Card(id='mean_real',color='#b8c1ec',className='text-center',inverse=True),
            ],width=3),
        ]),
        html.Br(),
        ## --ROW3--
        dbc.Row([
            ### --COLUMN1--
            dbc.Col([
                dcc.RangeSlider(
                        df['Year'].min(),
                        df['Year'].max(),
                        step=None,
                        id='year_slider',
                        value=[df['Year'].min(), df['Year'].max()],
                        marks={str(year): str(year) for year in df['Year'].unique()}
                ),
                dcc.Graph(
                    id='plot_hist',
                ),
            ],width=6),
            
            ### --COLUMN2--
            dbc.Col([
                dbc.Tabs([
                    ## --Delivery Status--
                    dbc.Tab(
                        dcc.Graph(
                            id='plot_status',
                        ),
                        label='Status'
                    ),

                    ## --Shipping Mode--
                    dbc.Tab(
                        dcc.Graph(
                            id='plot_mode',
                        ),
                        label='Mode'
                    ),

                    ## --Type
                    dbc.Tab(
                        dcc.Graph(
                            id='plot_type',
                        ),
                        label='Type'
                    ),
                ]),
            ],width=6),
        ])  
    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px',
    }),
    html.Footer('By : Ahmad Zaky Said',
            style={'textAlign': 'center', 
                   'fontSize': 20, 
                   'background-color':'#242947',
                   'color':'white'})
])

### Callback Mean(Scheduled)
@app.callback(
    Output(component_id='mean_scheduled', component_property='children'),
    Input(component_id='choose_country', component_property='value')
)

def update_card1(country_name):
    mean_scheduled = [
        dbc.CardHeader(f'Average days for shipment (scheduled) in {country_name}'),
        dbc.CardBody([
            html.H1(round(df[df['Order Country']==country_name]['Days for shipment (scheduled)'].mean(),2))
            ]),
    ]
    return mean_scheduled

### Callback Mean(Real)
@app.callback(
    Output(component_id='mean_real', component_property='children'),
    Input(component_id='choose_country', component_property='value')
)

def update_card2(country_name):
    mean_real = [
        dbc.CardHeader(f'Average days for shipping (real) in {country_name}'),
        dbc.CardBody([
            html.H1(round(df[df['Order Country']==country_name]['Days for shipping (real)'].mean(),2))
            ]),
    ]
    return mean_real

##-- Callback Plot Histogram
@app.callback(
    Output(component_id='plot_hist', component_property='figure'),
    Input(component_id='choose_country', component_property='value'),
    Input(component_id='year_slider', component_property='value')
)

def update_plot_hist(country_name, year_value):
    # Data aggregation
    data_year=df[df['Year'].isin(year_value)]
    data_country=data_year[data_year['Order Country']==country_name]
    data_days=data_country[['Days for shipment (scheduled)','Days for shipping (real)']]
    data_days.rename(columns={'Days for shipment (scheduled)':'Scheduled','Days for shipping (real)':'Real'}, inplace=True)
    days_melt=pd.melt(data_days, 
                    value_vars=['Scheduled','Real'],
                    value_name='Days',
                    var_name='Shipment Status')
    # Visualize
    plot_hist=px.histogram(days_melt,
                        x="Days", 
                        color="Shipment Status", 
                        nbins=10,
                        title=f'Distribution of Days Shipping Real and Scheduled in {country_name}',
                        template = 'ggplot2',
                        labels = {'count': 'Number of Orders', 'Days': 'Number of Days'},
                        color_discrete_sequence = ['#242947', '#b8c1ec'])
    plot_hist.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01),
                        title_x=0.5,
                        )
    plot_hist.update_layout({'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
   
    return plot_hist


##-- Callback Plot Status
@app.callback(
    Output(component_id='plot_status', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot1(country_name):
    # Data aggregation
    data_delivery_status=df[df['Order Country']==country_name].groupby(
        ['Delivery Status'])['Order Id'].count().reset_index(
            name='Number of Orders').sort_values(
                by= 'Number of Orders',
                ascending= False)

    # Visualize
    plot_status = px.bar(
        data_delivery_status, 
        x='Delivery Status',  
        y='Number of Orders', 
        color='Delivery Status',
        labels = {'Delivery Status': 'Delivery Status', 'Number of Orders': 'Number of Orders'},
        color_discrete_sequence = ['#242947', '#b8c1ec', '#eebbc2', '#D2B48C'],
        template = 'ggplot2',
        title = f'Delivery Status in {country_name}')
    plot_status.update_layout(showlegend=False)
    
    return plot_status

##-- Callback Plot Mode
@app.callback(
    Output(component_id='plot_mode', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot2(country_name):
    # Data aggregation
    data_shipping_mode=df[df['Order Country']==country_name].groupby(
        ['Shipping Mode', 'Delivery Status'])['Order Id'].count().reset_index(
            name='Number of Orders').sort_values(
                by='Number of Orders', 
                ascending=False)
    
    # Visualize
    plot_mode = px.bar(
        data_shipping_mode, 
        x='Shipping Mode',  
        y='Number of Orders', 
        color='Delivery Status',
        category_orders={"Delivery Status": ["Late delivery", "Advance shipping", "Shipping on time", "Shipping canceled"]},
        color_discrete_sequence = ['#242947', '#b8c1ec', '#eebbc2', '#D2B48C'],
        template = 'ggplot2',
        title = f'Shipping Mode Based on Delivery Status in {country_name}')
    plot_mode.update_layout(showlegend=False)
    
    return plot_mode


##-- Callback Plot Type
@app.callback(
    Output(component_id='plot_type', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot3(country_name):
    # Data aggregation
    data_transaction_type=df[df['Order Country']==country_name].groupby(
        ['Type', 'Delivery Status'])['Order Id'].count().reset_index(
            name='Number of Orders').sort_values(
                by='Number of Orders', 
                ascending=False)
    
    # Visualize
    plot_type = px.bar(
        data_transaction_type, 
        x='Type',  
        y='Number of Orders', 
        color='Delivery Status',
        category_orders={"Delivery Status": ["Late delivery", "Advance shipping", "Shipping on time", "Shipping canceled"]},
        color_discrete_sequence = ['#242947', '#b8c1ec', '#eebbc2', '#D2B48C'],
        template = 'ggplot2',
        title = f'Transaction Type Based on Delivery Status in {country_name}')
    plot_type.update_layout(showlegend=False)
    
    return plot_type
######-----Start the Dash server-----#####
if __name__ == "__main__":
    app.run_server()