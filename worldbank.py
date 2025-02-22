from datetime import datetime

from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import pandas as pd
from pandas_datareader import wb


# dash bootstrap components = a package that makes it easier to manage the layout of the app.
# bootstrap = supplies components that allow you to do things like place app elements more precisely on a page,
# create more components like graphs and radio buttons, and style each element in very detailed ways.

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY]) # changed theme to dark


# theme = ThemeChangerAIO(aio_id="theme")


indicators = {
    "IT.NET.USER.ZS": "Individuals using the Internet (% of population)",
    "SG.GEN.PARL.ZS": "Proportion of seats held by women in national parliaments (%)",
    "EN.GHG.CO2.TR.MT.CE.AR5": "CO2 emissions (kt)", # co2 emissions from transport
}

# get country name and ISO id for mapping on choropleth
# The wb module contains functions for getting different types of data pertaining to the World Bank.
# dropna() to exclude regions by dropping all rows that don’t have a capital city
countries = wb.get_countries()
# print(countries.head(10)[['name']])
# exit()
countries["capitalCity"].replace({"": None}, inplace=True)
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries[countries["name"] != "Kosovo"]
countries = countries[countries["name"] != "Korea, Dem. People's Rep."] # filter out North Korea
countries = countries.rename(columns={"name": "country"})

# three indicators: internet usage, female politicians, and emissions data


def update_wb_data():
    # Retrieve specific world bank data from API
    df = wb.download( # retrieve data
        # indicator = which takes a list of strings that represent the indicator IDs, we assign it the keys of the indicators dictionary
        # country = takes a list of strings that represent the countries’ ISO3 codes, we assign it the iso3c column of the countries DataFrame
        # start & end = allow us to define the range of years for which we would like the data pulled.
        indicator=(list(indicators)), country=countries["iso3c"], start=2005, end=2016
    )
    print(df.to_string())

    df = df.reset_index()
    print("after resetting index")
    print(df.to_string())

    df.year = df.year.astype(int)

    # Add country ISO3 id to main df
    df = pd.merge(df, countries, on="country")
    df = df.rename(columns=indicators)
    print(df.head())
    return df


app.layout = dbc.Container(
    [
        # theme,
        # 1.) The first row has a column component that stretches 12 columns wide and contains
        # the H1 heading and Graph visualization components. These correspond to the title and the
        # choropleth map in the app
            dbc.Row(
                dbc.Col(
                [
                    html.H1(
                        "Comparison of World Bank Country Data",
                        style={"textAlign": "center"},
                    ),
                    html.H3(
                        f"Data last fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        style={"textAlign": "center", "color": "#888"},
                    ),
                    dcc.Graph(id="my-choropleth", figure={}),
                ],
                width=12,
                )
            ),
        # 2.) second row we place a column component that stretches only four columns wide,
        # inside which we place the Label and RadioItems. These correspond to the “Select Data Set”
        # subtitle and the three radio buttons beneath it in the app.
        dbc.Row([
            dbc.Col(
                [
                    dbc.Label(
                        "Select Data Set:",
                        className="fw-bold",
                        style={"textDecoration": "underline", "fontSize": 20},
                    ),
                    dcc.Dropdown( # radio items = small circles or boxes next to a label that can be clicked.
                        # A radio button is similar to a checkbox except that, while the checkbox allows the user to choose multiple labels, the radio button only allows one label to be chosen at a time.
                        id="my-dropdown", # id name
                        # options = responsible for displaying the labels. We pass it a list of dictionaries, each of which represents a label; we use list comprehension to
                        # loop over all the indicators and create a label for each item.
                        options=[{"label": i, "value": i} for i in indicators.values()],
                        # value = registers the value selected by the user, depending on which radio button the user clicks; the object assigned to the value prop in Listing 5-9 represents the value chosen
                        # by default as the app loads for the first time.
                        value=list(indicators.values())[0],
                        # inputClassName = style the radio button; in this case, we assign it the Bootstrap class me-2 to set the circle two units of space to the left of the label
                        className="me-2",
                    ),
                ],
                width=4,
            ),


        # 3.) The last row contains the Label, RangeSlider, and Button, all of which are wrapped in
        # a column component that is six columns wide.

                dbc.Col(
                    [
                        dbc.Label(
                            "Select Years:",
                            className="fw-bold",
                            style={"textDecoration": "underline", "fontSize": 20},
                        ),
                        dcc.RangeSlider(
                            # commonly used when we want to present a wide range of values to select from or when the
                            # user can select a range rather than discrete values.
                            # in this case, we’ll use it to allow the user
                            # to select a single year or a range of years
                            id="years-range",
                            # min and max props define the lowest and highest values on the RangeSlider, usually from left to right
                            min=2005,
                            max=2016,
                            step=1,
                            # step prop determines the increment to make when the slider is moved.
                            value=[2005, 2006],
                            # value = determines the initial range that’s selected by default when the app loads; it will also detect the range of years selected by the app user.
                            marks={
                                # labels the marks. We assign it a dictionary: the key determines the position of the year on the slider,
                                # while the value indicates the text to display in that position on the app.
                                2005: "2005",
                                2006: "'06",
                                2007: "'07",
                                2008: "'08",
                                2009: "'09",
                                2010: "'10",
                                2011: "'11",
                                2012: "'12",
                                2013: "'13",
                                2014: "'14",
                                2015: "'15",
                                2016: "2016",
                            },
                            # not listed: allowCross, which allows the RangeSlider handles (the blue circles you see above 2005 and ’06 in Figure 5-4) to cross each other when set to True. By default, allowCross=False, but if you changed that to True, you would be able to pull the 2005 handle to the right and over the ’06 handle.
                        ),
                        ],
                        width=6,
                )]),

                dbc.Col(
                    [
                        html.Div(
                            id="clicker-counter",
                            children=f"Button clicked 0 times",
                            style={"textAlign": "left", "fontSize": "18"},
                                ),
                            ],
                width=6,
                ),


        dbc.Row(
                dbc.Col(
                        dbc.Button(
                            id="my-button",
                            children="Submit", # prop represents the text displayed on the button
                            n_clicks=0, # prop counts the number of times the button has been clicked by the user, so we initialize it at 0
                            color="primary", # prop sets the color of the button background.
                            className="mb-2",
                        ),
                    width=6,
                    className="d-flex justify-content-end",
                ),
            justify="end",
        ),
        # dcc.store = used to save dashboard data in memory on the user’s web browser so that the data can be called and recalled quickly and efficiently.
        # The store is invisible and does not appear on the user’s page, though we must still declare it in the layout section
        dcc.Store(id="storage", storage_type="session", data={}),
        dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    ]
)

@app.callback(
    Output("clicker-counter", "children"),
    Input("my-button", "n_clicks"),
)

def update_click_count(n_clicks):
    return f"Button clicked {n_clicks} times"

@app.callback(Output("storage", "data"), Input("timer", "n_intervals"))
# our app uses 2 callbacks: 1. data from world bank and 2 creating and displaying the choropleth map on the app.
def store_data(n_time):
    dataframe = update_wb_data()
    return dataframe.to_dict("records")


@app.callback(
    Output("my-choropleth", "figure"),
    Input("my-button", "n_clicks"),
    Input("storage", "data"),
    # Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    State("years-range", "value"),
    State("my-dropdown", "value"),
)
def update_graph(n_clicks, stored_dataframe, years_chosen, indct_chosen):
    dff = pd.DataFrame.from_records(stored_dataframe)
    print(years_chosen)

    if years_chosen[0] != years_chosen[1]:
        dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]
        dff = dff.groupby(["iso3c", "country"])[indct_chosen].mean()
        dff = dff.reset_index()

        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="world",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["SG.GEN.PARL.ZS"]: "% parliament women",
                indicators["IT.NET.USER.ZS"]: "pop % using internet",
            },
            # template=template_from_url(theme)
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig

    if years_chosen[0] == years_chosen[1]:
        dff = dff[dff["year"].isin(years_chosen)]
        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="world",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["SG.GEN.PARL.ZS"]: "% parliament women",
                indicators["IT.NET.USER.ZS"]: "pop % using internet",
            },
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig




if __name__ == "__main__":
    app.run_server(debug=True)
