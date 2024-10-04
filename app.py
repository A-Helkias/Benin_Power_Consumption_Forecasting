import joblib
from tensorflow.keras.models import load_model
import streamlit as st
import pandas as pd
import datetime
import numpy as np
import plotly.graph_objects as go

# Load the images from the specified paths
left_image_path = "left.png"
right_image_path = "right.png"

# Use columns to place images in the top corners
col1, col2, col3 = st.columns([1, 6, 1])  # Adjust column sizes as needed

with col1:
    # Display the left image at the top-left corner
    st.image(left_image_path, width=100)  # Adjust the width as necessary

with col3:
    # Display the right image at the top-right corner
    st.image(right_image_path, width=200)  # Adjust the width as necessary

# Title of the app (centered and on a single line)
st.markdown("<h1 style='text-align: center; font-size: 24px;'>Prévision de la consommation horaire d'énergie électrique du Bénin</h1>", unsafe_allow_html=True)

# Sidebar Navigation - Numbered format with added space between options
st.sidebar.markdown(
    """
    <style>
    div[role="radiogroup"] > label > div {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.sidebar.title("Menu")
selected_option = st.sidebar.radio(
    "Select a page:",
    ("1 - Electricity Consumption Forecasting", 
     "2 - Documentation", 
     "3 - Model Reliability", 
     "4 - Builder Contact Informations")
)

# Main page content based on sidebar selection
if selected_option == "1 - Electricity Consumption Forecasting":
    start_date = datetime.date(2024, 1, 1)  # Date de début fixe
    end_date = st.date_input('Sélectionnez une date :', value=start_date + datetime.timedelta(days=1))

    if st.button('Effectuer la prévision'):
        # Générer DataFrame pour la plage de dates
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        date_df = pd.DataFrame({"Date": date_range, "Power": 0})
        try:
            # Import des prédictions déjà réalisées
            result_date_range = pd.date_range(start=start_date, end=end_date, freq="H")
            pred_data_2024 = pd.read_csv("data/pred_data_2024.csv", parse_dates=['Date'])
            date_df = pred_data_2024[pred_data_2024['Date'].isin(result_date_range)]

            st.write("Prévisions futures :")
            st.write(date_df)

            # Plot the main animated chart (restored to previous format)
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=date_df['Date'], 
                y=date_df['Power'], 
                mode='lines', 
                name='Prévisions', 
                line=dict(color="firebrick", width=2.5),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 0, 0.2)'
            ))

            # Add animation to the chart
            frames = [go.Frame(
                data=[go.Scatter(
                    x=date_df['Date'][:i+1], 
                    y=date_df['Power'][:i+1], 
                    mode='lines', 
                    fill='tozeroy',
                    fillcolor='rgba(255, 0, 0, 0.05)'
                )],
                name=str(i)
            ) for i in range(len(date_df))]

            fig.frames = frames

            fig.update_layout(
                updatemenus=[{
                    'buttons': [
                        {
                            'args': [None, {'frame': {'duration': 1, 'redraw': True}, 'fromcurrent': True}],
                            'label': 'Play',
                            'method': 'animate'
                        },
                        {
                            'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                            'label': 'Pause',
                            'method': 'animate'
                        }
                    ],
                    'direction': 'left',
                    'pad': {'r': 10, 't': 87},
                    'showactive': True,
                    'type': 'buttons',
                    'x': 0.1,
                    'xanchor': 'right',
                    'y': 0,
                    'yanchor': 'top'
                }]
            )

            fig.update_layout(
                title="Prévisions de la consommation horaire",
                xaxis_title='Date',
                yaxis_title='Consommation (MW)',
                hovermode="x unified"
            )

            st.plotly_chart(fig)

            # Daily, Weekly, and Monthly Consumption (sum for each period)
            daily_sum = date_df.groupby(date_df['Date'].dt.date)['Power'].sum()
            weekly_sum = date_df.groupby(date_df['Date'].dt.isocalendar().week)['Power'].sum()
            monthly_sum = date_df.groupby(date_df['Date'].dt.month)['Power'].sum()

            # Display Daily and Weekly Consumption on the first line
            col1, col2 = st.columns(2)

            with col1:
                daily_fig = go.Figure()
                daily_fig.add_trace(go.Scatter(
                    x=daily_sum.index, 
                    y=daily_sum, 
                    mode='lines+markers', 
                    name='Consommation quotidienne', 
                    line=dict(color="firebrick", width=2.5),
                    marker=dict(size=5)
                ))
                daily_fig.update_layout(
                    xaxis=dict(showticklabels=True, title="Jour"),
                    yaxis=dict(showticklabels=True, title="Consommation (MW)"),
                    height=250,
                    title="Daily Consumption",
                    title_pad=dict(b=0, l=0, t=100),  # Adjusted title padding
                    hovermode="x unified"
                )
                st.plotly_chart(daily_fig)

            with col2:
                weekly_fig = go.Figure()
                weekly_fig.add_trace(go.Scatter(
                    x=weekly_sum.index, 
                    y=weekly_sum, 
                    mode='lines+markers', 
                    name='Consommation hebdomadaire', 
                    line=dict(color="firebrick", width=2.5),
                    marker=dict(size=5)
                ))
                weekly_fig.update_layout(
                    xaxis=dict(showticklabels=True, title="Semaine"),
                    yaxis=dict(showticklabels=True, title="Consommation (MW)"),
                    height=250,
                    title="Weekly Consumption",
                    title_pad=dict(b=0, l=0, t=30),  # Adjusted title padding
                    hovermode="x unified"
                )
                st.plotly_chart(weekly_fig)

            # Display Monthly Sum and Mean Consumption per Day (histogram) on the second line
            col3, col4 = st.columns(2)

            with col3:
                monthly_fig = go.Figure()
                monthly_fig.add_trace(go.Scatter(
                    x=monthly_sum.index, 
                    y=monthly_sum, 
                    mode='lines+markers', 
                    name='Consommation mensuelle', 
                    line=dict(color="firebrick", width=2.5),
                    marker=dict(size=5)
                ))
                monthly_fig.update_layout(
                    xaxis=dict(showticklabels=True, title="Mois"),
                    yaxis=dict(showticklabels=True, title="Consommation (MW)"),
                    height=250,
                    title="Monthly Consumption",
                    title_pad=dict(b=0, l=0, t=30),  # Adjusted title padding
                    hovermode="x unified"
                )
                st.plotly_chart(monthly_fig)

            # Mean consumption per day (Monday to Sunday)
            date_df['Day of Week'] = date_df['Date'].dt.day_name()
            mean_consumption_per_day = date_df.groupby('Day of Week')['Power'].mean()
            mean_consumption_per_day = mean_consumption_per_day.reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

            with col4:
                mean_day_fig = go.Figure()
                mean_day_fig.add_trace(go.Bar(
                    x=mean_consumption_per_day.index, 
                    y=mean_consumption_per_day, 
                    name='Moyenne de consommation par jour', 
                    marker=dict(color='firebrick')
                ))
                mean_day_fig.update_layout(
                    xaxis=dict(showticklabels=True, title="Jour de la semaine"),
                    yaxis=dict(showticklabels=True, title="Consommation (kW)"),
                    height=250,
                    title="Consumption per Day",
                    title_pad=dict(b=0, l=0, t=30),  # Adjusted title padding
                    hovermode="x unified"
                )
                st.plotly_chart(mean_day_fig)

        except Exception as e:
            st.write(f"Une erreur s'est produite : {e}")
            
elif selected_option == "2 - Documentation":
    
    # Loop through the 18 outputs
    for i in range(1, 19):
        # Section title and description input
        st.markdown(f"### Titre de la cellule {i}")
        description = st.text_area("Description de la cellule à compléter après validation...")

        # Display the output image
        image_path = f"images/output_{i}.png"
        st.image(image_path, caption=f"Output {i}", use_column_width=True) 
