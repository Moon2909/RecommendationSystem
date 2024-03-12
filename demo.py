Detail see:https://drive.google.com/drive/folders/1LnoLWZ7ZPmkVIG0smIWOvvDcyLNX_gTH?usp=sharing

# Import libraries

import numpy as np
import pandas as pd
import streamlit as st

# Constant value
# THRESHOLD_RATING = 5.0 

data_base = pd.read_csv("data_for_print.csv")
list_name_food = [''] + list(data_base.name_food.unique())

# Streamlit app
st.title("WHAT SHOULD I COOK TODAY?") # Name app
st.header("Top recipe maybe you want:")

# Sidebar
st.sidebar.header("LOGO")
input_name_food = st.sidebar.selectbox('I want to make:',
                                       options=list_name_food,
                                       format_func=lambda x: 'Type name food...' if x == '' else x)
input_method = st.sidebar.radio('Choose a method:',
                                ['','Sentiment','SVD','LighFM'],
                                index=0)

# New feature: choose the number of recommendations
number_of_recommendations = st.sidebar.slider('Number of recommendations', 1, 50, 10)
st.markdown(
        """
    <style>
        div[role=radiogroup] label:first-of-type {
            visibility: hidden;
            height: 0px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


if (input_name_food!='') & (input_method!=''):
    if (input_method=='Sentiment'):
        scores = pd.read_csv('Recommendations_Sentiment.csv')
    elif (input_method=='SVD'):
        scores = pd.read_csv('Recommendations_SVD.csv')
    else:
        scores = pd.read_csv('Recommendations_LightFM.csv')
    
    # Process to get recommendations
    input_id_food = data_base[data_base['name_food']==input_name_food].itemID.iloc[0]
    list_user_rated = np.array(data_base[(data_base.itemID == input_id_food)].sort_values('rating',ascending=False).userID)
    random_userID = np.random.choice(list_user_rated[:10])
    recommendations = scores[scores.userID==random_userID].sort_values('score', ascending=False)[['recommended_itemID','score']][:number_of_recommendations]

    data_base["rn"] = data_base[['itemID','name_food','link_image_food','link_food','ingredients','nutrients']].groupby('itemID')['itemID'].rank(method='first')
    recommendations["rn"] = recommendations.groupby('recommended_itemID')['recommended_itemID'].rank(method='first')
    recommendations = recommendations.head(number_of_recommendations)




    new_df = recommendations.merge(data_base[['itemID','name_food','link_image_food','link_food','rn','ingredients','nutrients']],
                                   left_on=['recommended_itemID','rn'],
                                   right_on=['itemID','rn'], 
                                   how='left')
    
    new_df.drop(['rn','itemID'],axis=1,inplace=True)

    # Styles and scripts to improve the UI
    st.markdown("""
        <style>
            .big-font {
                font-size:26px !important;
                font-weight: bold;
            }
            .image-container {
                padding: 10px;
            }
            .info-container {
                padding: 10px;
            }
            .info-text, .score-text, .ingredients-text, .nutritional-info {
                margin-bottom: 0.25rem;
            }
            .score-text {
                font-weight: bold;
            }
            .ingredients-text {
                font-size: 16px;
            }   
            .nutritional-info {
                font-size: 16px;
            }
            .link-text {
                color: #2986cc;
                text-decoration: none;
            }
        </style>
        """, unsafe_allow_html=True)

    # Display recommendations with images, links, and scores
    for index, row in new_df.iterrows():
        col1, col2 = st.columns([1, 2])
    
        with col1:  # Image container with padding
            st.markdown(f"<div class='image-container'><img src='{row['link_image_food']}' alt='Food image' style='width: 100%; border-radius: 10px;'></div>", unsafe_allow_html=True)
    
        with col2:  # Text details with big font and proper formatting
            # Title with link
            st.markdown(f"<h2 class='big-font'>{row['name_food'].upper()}</h2>", unsafe_allow_html=True)
            # Score in bold
            st.markdown(f"<p class='score-text'><b>Score:</b> {row['score']:.2f}</p>", unsafe_allow_html=True)
            # Ingredients with smaller font size
            st.markdown(f"<p class='ingredients-text'><b>Ingredients:</b> {row['ingredients']}</p>", unsafe_allow_html=True)
        
            # Nutritional information
            nutrients = row['nutrients'].split(",")
            nutrients_info = f"Calories: {nutrients[0]}, Fat: {nutrients[1]}, Saturated Fat: {nutrients[2]}, Cholesterol: {nutrients[3]}, Sodium: {nutrients[4]}, Carbohydrate: {nutrients[5]}, Fiber: {nutrients[6]}, Sugar: {nutrients[7]}, Protein: {nutrients[8]}"
            st.markdown(f"<p class='nutritional-info'><b>Nutritional Information:</b> {nutrients_info}</p>", unsafe_allow_html=True)
        
            # Link to recipe
            st.markdown(f"<a href='{row['link_food']}' target='_blank' class='link-text'>View Recipe</a>", unsafe_allow_html=True)
    
        st.markdown("---")  # Line separation
else:
    st.warning('Hmm..... No option is selected')
