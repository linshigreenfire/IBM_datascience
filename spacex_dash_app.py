"""Interactive SpaceX launch analytics dashboard.
Run with: python spacex_dash_app.py
The dashboard reads the IBM Skills Network course dataset at startup.
"""
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

DATA_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv"
df = pd.read_csv(DATA_URL)
df["Year"] = pd.to_datetime(df["Date"]).dt.year
sites = ["All sites", *sorted(df["LaunchSite"].dropna().unique())]

app = Dash(__name__)
app.title = "SpaceX Launch Analytics"
app.layout = html.Main([
    html.H1("Falcon 9 launch analytics"),
    html.P("Explore landing outcomes across launch sites, payloads, orbits, and time."),
    html.Label("Launch site"),
    dcc.Dropdown(id="site-filter", options=[{"label": x, "value": x} for x in sites], value="All sites", clearable=False),
    html.Div([
        dcc.Graph(id="site-success"),
        dcc.Graph(id="payload-outcome"),
    ], style={"display":"grid", "gridTemplateColumns":"1fr 1fr", "gap":"20px"}),
    dcc.Graph(id="yearly-success"),
], style={"maxWidth":"1200px", "margin":"32px auto", "fontFamily":"Arial", "color":"#142A3A"})

@app.callback(
    Output("site-success", "figure"), Output("payload-outcome", "figure"), Output("yearly-success", "figure"),
    Input("site-filter", "value"),
)
def update_charts(selected_site):
    view = df if selected_site == "All sites" else df[df["LaunchSite"] == selected_site]
    site_rates = view.groupby("LaunchSite", as_index=False).agg(success_rate=("Class", "mean"), launches=("Class", "size"))
    f1 = px.bar(site_rates, x="LaunchSite", y="success_rate", color="success_rate", range_y=[0,1],
                hover_data={"launches":True,"success_rate":".1%"}, color_continuous_scale=["#D95F59","#14857F"],
                title="Observed landing success by site")
    f1.update_layout(yaxis_title="Landing success rate", xaxis_title="", coloraxis_showscale=False)
    f2 = px.scatter(view, x="PayloadMass", y="FlightNumber", color=view["Class"].map({0:"Unsuccessful",1:"Successful"}),
                    hover_data=["Orbit","LaunchSite"], color_discrete_map={"Successful":"#14857F","Unsuccessful":"#D95F59"},
                    title="Payload mass and flight number")
    f2.update_layout(xaxis_title="Payload mass (kg)", yaxis_title="Flight number", legend_title="Landing")
    yearly = view.groupby("Year", as_index=False).agg(success_rate=("Class", "mean"), launches=("Class", "size"))
    f3 = px.line(yearly, x="Year", y="success_rate", markers=True, hover_data={"launches":True},
                 title="Landing success by year", color_discrete_sequence=["#14857F"])
    f3.update_layout(yaxis_title="Landing success rate", xaxis_title="Year", yaxis_range=[0,1])
    return f1, f2, f3

if __name__ == "__main__":
    app.run(debug=False)
