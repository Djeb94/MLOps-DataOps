import streamlit as st
import joblib


@st.cache_resource
def load_model():
    return joblib.load("regression.joblib")


model = load_model()

st.title("Estimation du prix d'une maison")

size = st.number_input("Taille", min_value=0.0, value=100.0, step=1.0)
nb_rooms = st.number_input("Nombre de chambres", min_value=0, value=3, step=1)
garden = st.number_input("Jardin (0 = non, 1 = oui)", min_value=0, max_value=1, value=0, step=1)

prediction = model.predict([[size, nb_rooms, garden]])

st.write("Prix estimé :", prediction[0])