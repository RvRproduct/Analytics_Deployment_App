from re import M
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

header = st.beta_container()
dataset = st.beta_container()
features = st.beta_container()
charts = st.beta_container()


@st.cache
def get_data(filename):
    story_data = pd.read_csv(filename)
    return story_data


states = alt.topo_feature(data.us_10m.url, feature='states')


def filter_rank_option(rank, brand, year, month):
    story_filter = get_data("data/analytics_deployment_app.csv")
    story_filter = story_filter.loc[(story_filter['rank'] == rank) & (
        story_filter['brand'].isin([f'rsd: {brand}', f'rsm: {brand}'])) & (story_filter['year'] == year) & (story_filter['month'] == month)]
    return story_filter


def get_max_rows(rank, brand, year, month):
    story_filter = get_data("data/analytics_deployment_app.csv")
    story_filter = story_filter.loc[(story_filter['rank'] == rank) & (
        story_filter['brand'].isin([f'rsd: {brand}', f'rsm: {brand}'])) & (story_filter['year'] == year) & (story_filter['month'] == month)]
    story_filter = story_filter.sort_values(by=['placekey', 'brand_v'])
    story_filter = story_filter.head(2)
    return story_filter


with header:
    st.title("Analytics Deployment App")
    st.text("""App By: Roberto Reynoso, This App allows you to compared Related Same Day and Month Visit
Scores based on the number of visits for other brands, from those that had made a visit to Chipotle,
within the same day or month.""")

with dataset:
    st.header("Chipotle Dataset")
    st.text("This is My DataSet, which I used Databricks/Pyspark to develop.")

    story_data = get_data("data/analytics_deployment_app.csv")
    st.write(story_data.head())

with features:
    st.header("Features Created")
    my_features = story_data[["rank", "year", "month", "brand", "brand_v"]]
    st.write(my_features.head())


with charts:
    st.header("Charts")
    st.text("Choose Different Parameters to Change the Visualizations")

    sel_col, disp_col = st.beta_columns(2)

    max_depth = int(sel_col.slider(
        "Choose Rank", min_value=0, max_value=19, value=0, step=1))
    year_choice = sel_col.slider(
        "Choose Year", min_value=2019, max_value=2022, value=2019, step=1)

    month_choice = sel_col.slider(
        "Choose Month", min_value=1, max_value=12, value=1, step=1)

    sel_col.text("List of The Brands:")
    sel_col.write(story_data["brand"])

    input_feature = str(sel_col.text_input(
        "Choose Brand (Just Enter Brand Not 'rsm or rsd')", "Walmart"))

    max_choice = sel_col.selectbox(
        "Max Compare", options=["no", "yes"])

    if max_choice != "yes":
        st.text(
            "Spatial Map")
        plot = filter_rank_option(
            max_depth, input_feature, year_choice, month_choice)
        background = alt.Chart(states).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).project('albersUsa').properties(
            width=500,
            height=300
        )

        points = alt.Chart(plot).mark_circle().encode(
            longitude='longitude:Q',
            latitude='latitude:Q',
            size=alt.value(50),
            tooltip=['placekey', 'brand', 'brand_v', 'year', 'month']
        )
        st.altair_chart(background + points)

    else:
        st.text(
            "Bar Chart")
        plot = get_max_rows(
            max_depth, input_feature, year_choice, month_choice)

        points = alt.Chart(plot).mark_circle(size=0).encode(color='placekey:N')
        bar = alt.Chart(plot, title='rsd vs rsm'.upper()).mark_bar().encode(
            x=alt.X('brand', axis=alt.Axis(
                title=f'Year: {year_choice} Month: {month_choice}'.upper())),
            y=alt.Y('brand_v:Q', axis=alt.Axis(title='Visit Count'.upper())),
            color=alt.Color('placekey:N', legend=alt.Legend(title='Legend')),
        ).interactive()
        st.altair_chart(bar + points)
