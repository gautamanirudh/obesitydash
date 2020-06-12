import plotly.graph_objects as go
import pandas as pd
import plotly.express as px 

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

df = pd.read_csv("obesity-cleaned.csv")

df["Percentage"] = df["Obesity (%)"].str.split().str[0]
df.Percentage = df.Percentage.str.replace("No", '0')
df["Range"] = df["Obesity (%)"].str.split().str[1]
df["Range"] = df["Range"].str.replace("]", "")
df["Range"] = df["Range"].str.replace("[", "")
df["Range"] = df["Range"].str.replace("data", "0")

df["Min"] = df["Range"].str.split("-").str[0]
df["Max"] = df["Range"].str.split("-").str[1]
df.drop(["Unnamed: 0", "Obesity (%)"], axis=1, inplace=True)
df["Percentage"] = df.Percentage.astype("float")

df["Min"] = df["Min"].str.replace("data", '0')
df["Min"] = df["Min"].astype("float")
df["Max"] = df["Max"].astype("float")

yeardf = df.loc[:, ['Year', 'Percentage']]
yeardf = yeardf.groupby("Year").mean()

fig1 = px.line(yeardf, x=yeardf.index, y="Percentage", labels={
    "x": "Year"}, title='Worlds average obesity Percentage')


# ----------------------------------------------------------------------------

data = df.copy()
dff = data[data.Country.isin(
    ['India', 'China', 'Japan', 'Bangladesh', 'Sri Lanka', 'Pakistan', 'Afghanistan'])]
dff[dff["Sex"] == "Both sexes"]
fig2 = px.bar(dff, x="Country", y="Percentage", animation_frame="Year",
              animation_group="Country", hover_name="Country", range_y=[0, 12])
fig2.update_layout(
    title='Comparing Average obesity percentages in Asian Countries')
#--------------------------------------------------------------------------------
data = df.copy()
dff = data[data.Country.isin(
    ['India', 'China', 'Japan', 'Bangladesh', 'Sri Lanka', 'Pakistan', 'Afghanistan'])]
dff = dff[dff.Sex.isin(['Male', 'Female'])]
dff = dff[dff.Year > 1990.0]
fig3 = px.bar(dff, x="Country", y="Percentage", color='Sex', barmode='group', animation_frame="Year",
              animation_group="Country", hover_name="Country", range_y=[0, 12])
fig3.update_layout(
    title='Comparing male and female obesity percentages in Asian Countries')

# -------------------------------------------------------------------------------------


dff = data[data.Country.isin(
    ['India', 'China', 'Japan', 'Bangladesh', 'Sri Lanka', 'Pakistan', 'Afghanistan'])]
dff[dff["Sex"] == "Both sexes"]
# df = px.data.gapminder().query("continent=='Oceania'")
fig4 = px.line(dff, x="Country", y="Percentage", animation_frame="Year", line_dash="Sex",
               animation_group="Country", hover_name="Country", range_y=[0, 12])
# fig = px.line(dff, x="Year", y="Max", color='Country')


#--------------------------------------------------------------------------------------------


dff5 = data[data["Sex"] == "Both sexes"]
dff5 = data.groupby("Country").mean().sort_values(
    by="Percentage", ascending=False).head(15)
fig5 = px.bar(dff5, x=dff5.index, y="Percentage")
fig5.update_layout(title='Countries with high Average obesity percentages')

# ------------------------------------------------------------------------------
most_obese = list(dff5.index)
data = df.copy()
dff5 = data[data.Country.isin(most_obese)]
dff5 = dff5[dff5.Sex.isin(['Male', 'Female'])]

fig6 = px.bar(dff5, x="Country", y="Percentage", color='Sex', barmode='group', animation_frame="Year",
              animation_group="Country", hover_name="Country", range_y=[0, 80])
fig6.update_layout(
    title='Comparing male and female obesity percentages in Most obese Countries')

#-------------------------------------------------------------------------------
countries_options = []
countries = data.Country.unique()
for i in list(countries):
    temp_dic = {}
    temp_dic.update({"label": i})
    temp_dic.update({"value": i})
    countries_options.append(temp_dic)


# clist = ["India","Japan"]



# App layout
app.layout = html.Div([

    html.H1("Obesity Percentage of Countries(1975 -2016)",
            style={'text-align': 'center'}),
    html.Div(children=[html.H4("Total number of countries"),
                       html.Div(len(countries))],
             style={
        "width": "200px",
        "margin": "0 auto",
        "border": "solid #E5ECF6 3px",
        "border-radius": "20px",
        "display": "flex",
        "flex-direction": "column",
        "justify-content": "center",
        "background-color": "#E5ECF6",
        "align-items": "center",


    }),


    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='fig1', figure=fig1),
    dcc.Graph(id='fig2', figure=fig2),
    html.Div([
        dcc.Graph(id='fig3', figure=fig3),

        dcc.Graph(id='fig4', figure=fig4),
    ],
        style={
        "display": "flex",

    }),

    dcc.Graph(id='fig5', figure=fig5),
    dcc.Graph(id='fig6', figure=fig6),

    dcc.Dropdown(id="slct_year",
                 options=countries_options,
                 multi=True,
                 value=["India"],
                 style={'width': "100%"}
                 ),


    dcc.Graph(id='fig7', figure={}),

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='fig7', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    # container = "The year chosen by user was: {}".format(option_slctd)

    # dff = df.copy()
    # dff = dff[dff["Year"] == option_slctd]
    # dff = dff[dff["Affected by"] == "Varroa_mites"]
    clist = option_slctd

    fig7 = go.Figure()
    for i in clist:
        Countrydata = data[(data["Country"] == i) &
                           (data["Sex"] == "Both sexes")]
        Countryseries = Countrydata["Percentage"].diff().div(
            Countrydata["Percentage"].shift(1))*100

# fig = px.line( x=Countrydata[1:].Year, y=Countryseries[1:],labels={"x":"Year","y":"Growth Percentage"},title='Growth rate')
# fig.show()

        fig7.add_trace(go.Scatter(x=Countrydata[1:].Year, y=Countryseries[1:],
                                  mode='lines+markers',
                                  name=i))

    fig7.update_layout(title="Growth Rate in years",
                       xaxis_title="Countries", yaxis_title="Growth rate (%)")

    return [fig7]


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
