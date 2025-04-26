import streamlit as st
import pandas as pd
import numpy as np
#pip install openpyxl
import folium
import requests
import random
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import geopandas as gpd
from folium import Choropleth, GeoJson
from folium.plugins import HeatMap
from folium import Icon
from folium import Popup
from matplotlib.patches import Patch
import matplotlib.ticker as ticker
import unicodedata
import matplotlib.ticker as ticker
import altair as alt
import json
from dotenv import load_dotenv
import os
load_dotenv()



st.set_page_config(
    page_title="City-Fighting",
    page_icon=":student:",
    layout="wide"
)

st.markdown("<h1 style='margin-top: -50px;'>City-Fighting</h1>", unsafe_allow_html=True)


def get_commune_data(code_insee):
    url = f"https://geo.api.gouv.fr/communes?code={code_insee}&fields=code,nom,contour,centre"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            commune_data = data[0]
            contour = commune_data.get('contour', {}).get('coordinates', None)
            centre = commune_data.get('centre', {}).get('coordinates', None)
            if contour:
                if isinstance(contour[0][0][0], list):  # Vérifier si c'est un MultiPolygon
                    contour = contour[0][0]  # Prendre le premier polygone
                elif isinstance(contour[0][0], list):  # Vérifier si c'est un Polygon
                    contour = contour[0]  # Retourner directement le polygone
            return contour, centre
    return None, None


onglet1, onglet2, onglet3, onglet4, onglet5, onglet6, onglet7, onglet8, onglet9, onglet10 = st.tabs([
    "Présentation de City-Fighting",
    "Choix des Villes",
    "Données Générales",
    "Données d'Emploi",
    "Offres d'Emploi",
    "Données de Logement",
    "Données Météo",
    "Données Loisirs",
    "Données Éducation",
    "Sources et Crédits"
])











# ------------------------------------------------
# ------------- Page de Présentation -------------
# ------------------------------------------------

with onglet1:

    col1, col2, col3 = st.columns([2, 0.1, 1.5])

    with col1:
        st.markdown("", unsafe_allow_html=True)

        st.markdown("<h5>Qu'est ce que 'City-Fighting' ?</h5>", unsafe_allow_html=True)
        st.markdown("City-Fighting est une application web interactive conçue pour comparer facilement deux villes sur une variété de critères essentiels et complémentaires." \
        " Que vous soyez en pleine réflexion pour un déménagement, une opportunité professionnelle, un projet d'études ou tout simplement par curiosité, City-Fighting vous aide à visualiser les différences entre deux villes en un clin d'œil." \
        " Elle permet à l'utilisateur de comparer deux villes selon des données fiables et pertinentes, afin de l’accompagner dans ses choix de vie, de carrière ou de voyage.")


        st.markdown("", unsafe_allow_html=True)

        st.markdown("<h5>Quels types de données sont comparés ?</h5>", unsafe_allow_html=True)
        st.markdown("""
        - Données Générales : population, superficie, densité, proportions selon indicateurs, etc…
        - Données d'Emploi : taux de chômage, population active, salaire horaire médian, répartitions selon indicateurs, etc…
        - Données de Logement : nombre de logements, prix moyen au m², superficie moyenne, proportions selon indicateurs, etc…
        - Données Météo : type de climat, état du ciel, température, prévisions sur les prochains jours, etc…
        - Autres Données : données de loisirs, données d'éducation
        """)


        st.markdown("", unsafe_allow_html=True)

        st.markdown("<h5>Quelles sont les fonctionnalités principales ?</h5>", unsafe_allow_html=True)
        st.markdown("""
        - Interface intuitive avec visualisation comparative (graphiques, cartes, indicateurs dans des info-box)
        - Données récentes et mise à jour en temps réel des données météo
        - Fiches villes détaillées avec indicateurs clés  
        - Offres d'emploi en temps réel
        """)

    with col3:
        st.markdown("", unsafe_allow_html=True)
        st.markdown("", unsafe_allow_html=True)
        st.markdown('<img src="https://static.villesavivre.fr/images/c5/13/aube.jpg?format=auto" style="width: auto; height: 540px; border: 1px solid grey; border-radius: 8px;" />', unsafe_allow_html=True)

    
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)











# -------------------------------------------------
# ------------- Page Choix des Villes -------------
# -------------------------------------------------

with onglet2:

    st.markdown("", unsafe_allow_html=True)

    

    cc = pd.read_csv("communes-france-2025.csv", dtype={"code_insee": str}, low_memory=False)
    cc['nom'] = cc['nom_standard'] + ' (' + cc['dep_code'] + ')'

    cc = cc[cc['population'] >= 20000]

    regions = sorted(cc['reg_nom'].unique())

    if "region_choisie_1" not in st.session_state:
        st.session_state.region_choisie_1 = regions[0]

    if "region_choisie_2" not in st.session_state:
        st.session_state.region_choisie_2 = regions[0]

    col1, col2 = st.columns([1, 1])  

    with col1:
        col1a, col1b = st.columns(2)  

        with col1a:
            region_choisie_1 = st.selectbox("Choisissez la région de la 1ère ville :", regions, key="region_choisie_1")
            
        with col1b:
            departements_1 = cc[cc['reg_nom'] == region_choisie_1]['dep_nom'].unique()
            departement_choisi_1 = st.selectbox("Choisissez le département de la 1ère ville :", departements_1, key="departement_choisi_1")

        filtered_dep_1 = cc[cc['dep_nom'] == departement_choisi_1]['dep_code'].values[0]
            
        communes_1 = cc[(cc['reg_nom'] == region_choisie_1) & (cc['dep_nom'] == departement_choisi_1)]['nom'].unique()
        ville_choisie_1 = st.selectbox("Choisissez la 1ère ville à comparer :", communes_1, key="ville_choisie_1")

        code_insee_choisi_1 = cc[
            (cc['nom'] == ville_choisie_1) &
            (cc['dep_nom'] == departement_choisi_1) &
            (cc['reg_nom'] == region_choisie_1)
        ]['code_insee'].values[0]

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if code_insee_choisi_1:
            contour_1, centre_1 = get_commune_data(code_insee_choisi_1)
            if contour_1 and centre_1:
                m_1 = folium.Map(location=[centre_1[1], centre_1[0]], zoom_start=11)
                folium.Polygon(locations=[[coord[1], coord[0]] for coord in contour_1], color="darkred", fill=True, fill_opacity=0.2).add_to(m_1)
                folium_static(m_1, width=900, height=400)

                if filtered_dep_1 == '2A':
                    image_url = "https://www.bien-dans-ma-ville.fr/front/img/departement/2a.png"
                    image_width = "100px"
                elif filtered_dep_1 == '2B':
                    image_url = "https://www.bien-dans-ma-ville.fr/front/img/departement/2b.png"
                    image_width = "100px"
                elif filtered_dep_1 == '971':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Guadeloupe_in_France.svg/langfr-1920px-Guadeloupe_in_France.svg.png"
                    image_width = "250px"
                elif filtered_dep_1 == '972':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Martinique_in_France.svg/langfr-1920px-Martinique_in_France.svg.png"
                    image_width = "250px"
                elif filtered_dep_1 == '973':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/French_Guiana_in_France_%28special_marker%29.svg/langfr-1920px-French_Guiana_in_France_%28special_marker%29.svg.png"
                    image_width = "250px"
                elif filtered_dep_1 == '974':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Reunion_in_France.svg/langfr-1920px-Reunion_in_France.svg.png"
                    image_width = "250px"
                elif filtered_dep_1 == '976':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Mayotte_%28976%29_in_France.svg/langfr-1920px-Mayotte_%28976%29_in_France.svg.png"
                    image_width = "250px"
                else:
                    image_url = f"https://www.bien-dans-ma-ville.fr/front/img/departement/{filtered_dep_1.lower()}.png"
                    image_width = "100px"


                st.markdown(
                    f"""
                    <div style="position: relative; width: 900px;">
                        <div style="position: absolute; top: -395px; right: 30px; z-index: 1000;">
                            <img src="{image_url}"
                                style="width: {image_width}; height: auto; border: 1px solid darkgrey; border-radius: 8px; background-color: white; padding: 5px;">
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error("Contour ou centre non trouvé pour cette première commune.")






    with col2:
        col2a, col2b = st.columns(2)  

        with col2a:
            region_choisie_2 = st.selectbox("Choisissez la région de la 2nde ville :", regions, key="region_choisie_2")
            
        with col2b:
            departements_2 = cc[cc['reg_nom'] == region_choisie_2]['dep_nom'].unique()
            
            if len(cc[cc['reg_nom'] == region_choisie_1][cc['dep_nom'] == departement_choisi_1]) == 1:
                departements_2 = [d for d in departements_2 if d != departement_choisi_1]

            departement_choisi_2 = st.selectbox("Choisissez le département de la 2nde ville :", departements_2, key="departement_choisi_2")
            
        filtered_dep_2 = cc[cc['dep_nom'] == departement_choisi_2]['dep_code'].values[0]
            
        communes_2 = cc[(cc['reg_nom'] == region_choisie_2) & (cc['dep_nom'] == departement_choisi_2)]['nom'].unique()
        communes_2 = [ville for ville in communes_2 if ville != ville_choisie_1]
        ville_choisie_2 = st.selectbox("Choisissez la 2nde ville à comparer :", communes_2, key="ville_choisie_2")


        code_insee_choisi_2 = cc[
            (cc['nom'] == ville_choisie_2) &
            (cc['dep_nom'] == departement_choisi_2) &
            (cc['reg_nom'] == region_choisie_2)
        ]['code_insee'].values[0]

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if code_insee_choisi_2:
            contour_2, centre_2 = get_commune_data(code_insee_choisi_2)
            if contour_2 and centre_2:
                m_2 = folium.Map(location=[centre_2[1], centre_2[0]], zoom_start=11)
                folium.Polygon(locations=[[coord[1], coord[0]] for coord in contour_2], color="darkred", fill=True, fill_opacity=0.2).add_to(m_2)
                folium_static(m_2, width=900, height=400) 

                if filtered_dep_2 == '2A':
                    image_url = "https://www.bien-dans-ma-ville.fr/front/img/departement/2a.png"
                    image_width = "100px"
                elif filtered_dep_2 == '2B':
                    image_url = "https://www.bien-dans-ma-ville.fr/front/img/departement/2b.png"
                    image_width = "100px"
                elif filtered_dep_2 == '971':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Guadeloupe_in_France.svg/langfr-1920px-Guadeloupe_in_France.svg.png"
                    image_width = "250px"
                elif filtered_dep_2 == '972':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Martinique_in_France.svg/langfr-1920px-Martinique_in_France.svg.png"
                    image_width = "250px"
                elif filtered_dep_2 == '973':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/French_Guiana_in_France_%28special_marker%29.svg/langfr-1920px-French_Guiana_in_France_%28special_marker%29.svg.png"
                    image_width = "250px"
                elif filtered_dep_2 == '974':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Reunion_in_France.svg/langfr-1920px-Reunion_in_France.svg.png"
                    image_width = "250px"
                elif filtered_dep_2 == '976':
                    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Mayotte_%28976%29_in_France.svg/langfr-1920px-Mayotte_%28976%29_in_France.svg.png"
                    image_width = "250px"
                else:
                    image_url = f"https://www.bien-dans-ma-ville.fr/front/img/departement/{filtered_dep_2.lower()}.png"
                    image_width = "100px"


                st.markdown(
                    f"""
                    <div style="position: relative; width: 900px;">
                        <div style="position: absolute; top: -395px; right: 30px; z-index: 1000;">
                            <img src="{image_url}"
                                style="width: {image_width}; height: auto; border: 1px solid darkgrey; border-radius: 8px; background-color: white; padding: 5px;">
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error("Contour ou centre non trouvé pour cette deuxième commune.")



    def choisir_aleatoirement():
        st.session_state.region_choisie_1 = random.choice(regions)
        st.session_state.departement_choisi_1 = random.choice(cc[cc['reg_nom'] == st.session_state.region_choisie_1]['dep_nom'].unique())
        st.session_state.ville_choisie_1 = random.choice(cc[(cc['reg_nom'] == st.session_state.region_choisie_1) & (cc['dep_nom'] == st.session_state.departement_choisi_1)]['nom'].unique())

        while True:
            st.session_state.region_choisie_2 = random.choice(regions)
            st.session_state.departement_choisi_2 = random.choice(cc[cc['reg_nom'] == st.session_state.region_choisie_2]['dep_nom'].unique())
            st.session_state.ville_choisie_2 = random.choice(cc[(cc['reg_nom'] == st.session_state.region_choisie_2) & (cc['dep_nom'] == st.session_state.departement_choisi_2)]['nom'].unique())

            if (st.session_state.region_choisie_1 != st.session_state.region_choisie_2 or
                st.session_state.departement_choisi_1 != st.session_state.departement_choisi_2 or
                st.session_state.ville_choisie_1 != st.session_state.ville_choisie_2):
                break

    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 20px;'>", unsafe_allow_html=True)

            
    col1, col2 = st.columns([1, 5.5])

    with col1:
        st.button('Choisir aléatoirement les villes 🎯', on_click=choisir_aleatoirement)

    with col2:
        ville_choisie_1_formatee = f"{ville_choisie_1.split('(')[0]} ({departement_choisi_1}, {region_choisie_1})"
        ville_choisie_2_formatee = f"{ville_choisie_2.split('(')[0]} ({departement_choisi_2}, {region_choisie_2})"
        st.markdown(f"<div style='margin-top: 8px;'>La comparaison des villes se fera entre {ville_choisie_1_formatee} et {ville_choisie_2_formatee}.</div>", unsafe_allow_html=True)


    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)

    st.markdown("""
        <style>
            iframe {
                margin-bottom: -20px !important;
            }

            .block-container {
                padding-top: 6rem;
                padding-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)











# --------------------------------------------------
# ------------- Page Données Générales -------------
# --------------------------------------------------

with onglet3:

    st.markdown("", unsafe_allow_html=True)

    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Données Rapides :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un aperçu synthétique des informations essentielles dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)



    tranche = pd.read_csv("data_tranche_d-age_pourcentage.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    age_graph = pd.read_csv("data_age_graph.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    sexe = pd.read_csv("data_sexe_pourcentage.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    famille = pd.read_csv("data_famille.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    cat_socio = pd.read_csv("data_cat_socio.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    menage = pd.read_csv("data_menage_composition.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    statut_conj = pd.read_csv("data_statut_conj.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    nd = pd.read_csv("data_naissance_deces.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})



    population_1 = cc[cc['code_insee'] == code_insee_choisi_1]['population'].values[0]
    population_2 = cc[cc['code_insee'] == code_insee_choisi_2]['population'].values[0]

    densite_1 = cc[cc['code_insee'] == code_insee_choisi_1]['densite'].values[0]
    densite_2 = cc[cc['code_insee'] == code_insee_choisi_2]['densite'].values[0]

    superficie_ville_1 = cc[cc['code_insee'] == code_insee_choisi_1]['superficie_km2'].values[0]
    superficie_ville_2 = cc[cc['code_insee'] == code_insee_choisi_2]['superficie_km2'].values[0]

    altitude_1 = cc[cc['code_insee'] == code_insee_choisi_1]['altitude_moyenne'].values[0]
    altitude_2 = cc[cc['code_insee'] == code_insee_choisi_2]['altitude_moyenne'].values[0]


    
    st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Ville choisie :</p>
                <p style="font-size: 14px;">{ville_choisie_1} <br> {ville_choisie_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Région :</p>
                <p style="font-size: 14px;">{region_choisie_1} <br> {region_choisie_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Département :</p>
                <p style="font-size: 14px;">{departement_choisi_1} <br> {departement_choisi_2} </p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Nombre d'habitants :</p>
                <p style="font-size: 14px;">{f'{population_1:,}'.replace(',', ' ')} <br> {f'{population_2:,}'.replace(',', ' ')}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Densité de population :</p>
                <p style="font-size: 14px;">{f'{densite_1:,}'.replace(',', ' ')} hab/km² <br> {f'{densite_2:,}'.replace(',', ' ')} hab/km²</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Superficie :</p>
                <p style="font-size: 14px;">{f'{superficie_ville_1:,}'.replace(',', ' ')} km² <br> {f'{superficie_ville_2:,}'.replace(',', ' ')} km²</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Altitude Moyenne :</p>
                <p style="font-size: 14px;">{f'{altitude_1:,}'.replace(',', ' ')} m <br> {f'{altitude_2:,}'.replace(',', ' ')} m</p>
            </div>
            <!-- Ajoute autant de boîtes que nécessaire -->
        </div>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Graphiques :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Plusieurs visualisations des principales statistiques dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    





    # -------------------------------------
    # -------------- Ligne 1 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    colors_cat = ['#DFD4B1','#66B3FF','#99FF99','#FFCC99','#C2C2F0', '#B3FFFF', '#FFB3E6', '#FF9999']
    labels_cat = ["Agriculteurs exploitants", "Artisans, commerçants, chefs d'entreprise", "Cadres et professions intellectuelles supérieures", "Professions intermédiaires", "Employés", "Ouvriers", "Retraités", "Autres personnes sans activité professionnelle"]
    

    with cols[0]:

        cat_socio_1 = cat_socio[(cat_socio['code_insee'] == code_insee_choisi_1) & 
                                (cat_socio['Catégorie socioprofessionnelle'] != 'Ensemble')]
        cat_socio_2 = cat_socio[(cat_socio['code_insee'] == code_insee_choisi_2) & 
                                (cat_socio['Catégorie socioprofessionnelle'] != 'Ensemble')]

        if not cat_socio_1.empty and not cat_socio_2.empty:
            cat_socio_1 = cat_socio_1.set_index('Catégorie socioprofessionnelle').reindex(labels_cat)
            values_1 = cat_socio_1["%.2"].str.replace(",", ".").astype(float).values.flatten()

            cat_socio_2 = cat_socio_2.set_index('Catégorie socioprofessionnelle').reindex(labels_cat)
            values_2 = cat_socio_2["%.2"].str.replace(",", ".").astype(float).values.flatten()

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.19), sharey=True)

            bars1 = ax1.barh(labels_cat, values_1, color=colors_cat, edgecolor='white')
            ax1.set_title(f"{ville_choisie_1}", pad=20)
            ax1.invert_yaxis()
            ax1.set_yticklabels([])

            for bar in bars1:
                width = bar.get_width()
                label = f'{width:.1f}%'
                if width == max(values_1):
                    ax1.text(width - 0.2, bar.get_y() + bar.get_height() / 2, label, 
                            va='center', ha='right', fontsize=9)
                else:
                    ax1.text(width + 0.2, bar.get_y() + bar.get_height() / 2, label, 
                            va='center', ha='left', fontsize=9)

            bars2 = ax2.barh(labels_cat, values_2, color=colors_cat, edgecolor='white')
            ax2.set_title(f"{ville_choisie_2}", pad=20)
            ax2.invert_yaxis()
            ax2.set_yticklabels([])

            for bar in bars2:
                width = bar.get_width()
                label = f'{width:.1f}%'
                if width == max(values_2):
                    ax2.text(width - 0.2, bar.get_y() + bar.get_height() / 2, label, 
                            va='center', ha='right', fontsize=9)
                else:
                    ax2.text(width + 0.2, bar.get_y() + bar.get_height() / 2, label, 
                            va='center', ha='left', fontsize=9)

            fig.legend(bars1, labels_cat, loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, -0.14))
            fig.tight_layout(rect=[0, 0.1, 1, 0.95])

        else:
            fig = None


        with st.expander("📊 Répartition des catégories socioprofessionnelles :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")





    # ------------ Graphique 2 ------------

    labels_sexe = ["Femmes", "Hommes"]
    colors_sexe = ['#FF9999', '#66B3FF']

    with cols[2]:

        sexe_1 = sexe[sexe['code_insee'] == code_insee_choisi_1]
        if not sexe_1.empty:
            values_3 = sexe_1[labels_sexe].values.flatten()
            fig3, ax3 = plt.subplots(figsize=(5, 5))
            wedges_3, _, _ = ax3.pie(values_3, autopct='%1.1f%%', startangle=140, colors=colors_sexe, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax3.axis('equal')
            plt.title(f"{ville_choisie_1}")
        else:
            fig3 = None

        sexe_2 = sexe[sexe['code_insee'] == code_insee_choisi_2]
        if not sexe_2.empty:
            values_4 = sexe_2[labels_sexe].values.flatten()
            fig4, ax4 = plt.subplots(figsize=(5, 5))
            wedges_4, _, _ = ax4.pie(values_4, autopct='%1.1f%%', startangle=140, colors=colors_sexe, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax4.axis('equal')
            ax4.legend(wedges_4, labels_sexe, loc="center left", bbox_to_anchor=(1, 0.5))
            plt.title(f"{ville_choisie_2}")
        else:
            fig4 = None

        if fig3 is not None and fig4 is not None:
            fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(10, 5))

            wedges3, _, _ = ax3.pie(values_3, autopct='%1.1f%%', startangle=140, colors=colors_sexe, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax3.axis('equal')
            ax3.set_title(f"{ville_choisie_1}", fontsize=10)

            wedges4, _, _ = ax4.pie(values_4, autopct='%1.1f%%', startangle=140, colors=colors_sexe, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax4.axis('equal')
            ax4.set_title(f"{ville_choisie_2}", fontsize=10)

            fig.legend(wedges4, labels_sexe, loc='lower center', ncol=2, fontsize=10, frameon=False)
            fig.tight_layout(rect=[0, 0.1, 1, 0.95])

        else:
            fig = None


        with st.expander("📈 Proportion de la population par sexe :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")
    

    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)







    # -------------------------------------
    # -------------- Ligne 2 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    colors_menage = ['#FF9999','#66B3FF','#99FF99','#FFCC99','#C2C2F0']
    labels_menage = ["Ménages d'une personne", "Autres ménages sans famille", "Couples sans enfant", "Couples avec enfant(s)", "Familles monoparentales"]

    with cols[0]:

        menage_1 = menage[(menage['code_insee'] == code_insee_choisi_1)]
        if not menage_1.empty:
            menage_1 = menage_1.set_index('Type de ménages').reindex(labels_menage)
            values_3 = menage_1["%3"].str.replace(",", ".").astype(float).values.flatten()
            fig3, ax3 = plt.subplots(figsize=(5, 5))
            wedges_3, _, _ = ax3.pie(values_3, autopct='%1.1f%%', startangle=140, colors=colors_menage, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax3.axis('equal')
            plt.title(f"{ville_choisie_1}")
        else:
            fig3 = None

        menage_2 = menage[(menage['code_insee'] == code_insee_choisi_2)]
        if not menage_2.empty:
            menage_2 = menage_2.set_index('Type de ménages').reindex(labels_menage)
            values_4 = menage_2["%3"].str.replace(",", ".").astype(float).values.flatten()
            fig4, ax4 = plt.subplots(figsize=(5, 5))
            wedges_4, _, _ = ax4.pie(values_4, autopct='%1.1f%%', startangle=140, colors=colors_menage, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax4.axis('equal')
            ax4.legend(wedges_4, labels_menage, loc="center left", bbox_to_anchor=(1, 0.5))
            plt.title(f"{ville_choisie_2}")
        else:
            fig4 = None

        if fig3 is not None and fig4 is not None:
            fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(10, 5))

            wedges3, _, _ = ax3.pie(values_3, autopct='%1.1f%%', startangle=140, colors=colors_menage, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax3.axis('equal')
            ax3.set_title(f"{ville_choisie_1}", fontsize=10)

            wedges4, _, _ = ax4.pie(values_4, autopct='%1.1f%%', startangle=140, colors=colors_menage, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax4.axis('equal')
            ax4.set_title(f"{ville_choisie_2}", fontsize=10)

            fig.legend(wedges4, labels_menage, loc='lower center', ncol=2, fontsize=10, frameon=False)
            fig.tight_layout(rect=[0, 0.1, 1, 0.95])

        else:
            fig = None


        with st.expander("📈 Proportion de la composition des ménages :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")






    # ------------ Graphique 2 ------------

    colors_conj = ['#FF9999','#66B3FF','#99FF99','#FFCC99','#C2C2F0','#FFB3E6']
    labels_conj = ["Marié(e)", "Pacsé(e)", "En concubinage ou union libre", "Veuf, veuve", "Divorcé(e)", "Célibataire"]

    with cols[2]:

        statut_conj_1 = statut_conj[statut_conj['code_insee'] == code_insee_choisi_1]
        if not statut_conj_1.empty:
            statut_conj_1 = statut_conj_1.set_index('Statut').reindex(labels_conj)
            values_1 = statut_conj_1["%"].str.replace(",", ".").astype(float).values.flatten()
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            wedges_1, _, _ = ax1.pie(values_1, autopct='%1.1f%%', startangle=140, colors=colors_conj, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax1.axis('equal')
            plt.title(f"{ville_choisie_1}")
        else:
            fig1 = None

        statut_conj_2 = statut_conj[statut_conj['code_insee'] == code_insee_choisi_2]
        if not statut_conj_2.empty:
            statut_conj_2 = statut_conj_2.set_index('Statut').reindex(labels_conj)
            values_2 = statut_conj_2["%"].str.replace(",", ".").astype(float).values.flatten()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            wedges_2, _, _ = ax2.pie(values_2, autopct='%1.1f%%', startangle=140, colors=colors_conj, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax2.axis('equal')
            ax2.legend(wedges_2, labels_conj, loc="center left", bbox_to_anchor=(1, 0.5))
            plt.title(f"{ville_choisie_2}")
        else:
            fig2 = None

        if fig1 is not None and fig2 is not None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

            wedges1, _, _ = ax1.pie(values_1, autopct='%1.1f%%', startangle=140, colors=colors_conj, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax1.axis('equal')
            ax1.set_title(f"{ville_choisie_1}", fontsize=10)

            wedges2, _, _ = ax2.pie(values_2, autopct='%1.1f%%', startangle=140, colors=colors_conj, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax2.axis('equal')
            ax2.set_title(f"{ville_choisie_2}", fontsize=10)

            fig.legend(wedges2, labels_conj, loc='lower center', ncol=2, fontsize=10, frameon=False)
            fig.tight_layout(rect=[0, 0.1, 1, 0.95])

        else:
            fig = None


        with st.expander("📈 Proportion de la population par statut conjugal :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")
    


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    






    # -------------------------------------
    # -------------- Ligne 3 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    with cols[2]:

        modalites_enfants = ["Aucun enfant", "1 enfant", "2 enfants", "3 enfants", "4 enfants ou plus"]

        # Filtrer les données
        famille_1 = famille[(famille['code_insee'] == code_insee_choisi_1) & 
                        (famille['Nombre d\'enfants'].isin(modalites_enfants))]

        famille_2 = famille[(famille['code_insee'] == code_insee_choisi_2) & 
                        (famille['Nombre d\'enfants'].isin(modalites_enfants))]

        try:
            valeurs_1 = famille_1.set_index("Nombre d'enfants").loc[modalites_enfants]["%.2"].str.replace(",", ".").astype(float).values
            valeurs_2 = famille_2.set_index("Nombre d'enfants").loc[modalites_enfants]["%.2"].str.replace(",", ".").astype(float).values

            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(modalites_enfants)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color='#FF9999')
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color='#66B3FF')

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(modalites_enfants)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f} %',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Proportion du nombre d'enfant(s) par famille :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")



            



    # ------------ Graphique 2 ------------

    with cols[0]:

        tranches_age = ["0-14 ans", "15-29 ans", "30-44 ans", "45-59 ans", "60-74 ans", "75-+ ans"]

        age_1 = tranche[tranche['code_insee'] == code_insee_choisi_1]
        age_2 = tranche[tranche['code_insee'] == code_insee_choisi_2]

        try:
            valeurs_age_1 = age_1[tranches_age].values.flatten().astype(float)
            valeurs_age_2 = age_2[tranches_age].values.flatten().astype(float)

            if np.any(np.isnan(valeurs_age_1)) or np.any(np.isnan(valeurs_age_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(tranches_age)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_age_1, width, label=ville_choisie_1, color='#FF9999')
            bars2 = ax.bar(x + offset, valeurs_age_2, width, label=ville_choisie_2, color='#66B3FF')

            max_val = max(max(valeurs_age_1), max(valeurs_age_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(tranches_age)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f}%',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Proportion de la population par tranches d'âge :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)








    # -------------------------------------
    # -------------- Ligne 4 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    with cols[0]:
        df_long = age_graph.melt(id_vars=["Ville", "code_insee"], 
                                var_name="Année", 
                                value_name="Population")
        df_long["Année"] = df_long["Année"].astype(int)

        age_graph_1 = df_long[df_long['code_insee'] == code_insee_choisi_1]
        age_graph_2 = df_long[df_long['code_insee'] == code_insee_choisi_2]

        with st.expander("📈 Évolution du nombre d'habitants par année :", expanded=True):

            option1 = st.selectbox(
                "🎛️ Options d'affichage",
                options=[
                    "Afficher les deux villes choisies",
                    f"Afficher uniquement {ville_choisie_1}",
                    f"Afficher uniquement {ville_choisie_2}"
                ],
                index=0,
                key="unique_key_option1",
                label_visibility="collapsed"
            )

            st.markdown("", unsafe_allow_html=True)

            figx, ax = plt.subplots(figsize=(11.1, 5))

            max_population = 0

            if option1 == f"Afficher uniquement {ville_choisie_1}" or option1 == "Afficher les deux villes choisies":
                ax.plot(age_graph_1["Année"], age_graph_1["Population"], 
                        marker='o', markersize=6, linewidth=2.5, color='#FF9999', label=ville_choisie_1)
                ax.fill_between(age_graph_1["Année"], age_graph_1["Population"], 
                                color='#FF9999', alpha=0.1)
                max_population = max(max_population, age_graph_1["Population"].max())

            if option1 == f"Afficher uniquement {ville_choisie_2}" or option1 == "Afficher les deux villes choisies":
                ax.plot(age_graph_2["Année"], age_graph_2["Population"], 
                        marker='s', markersize=6, linewidth=2.5, color='#66B3FF', label=ville_choisie_2)
                ax.fill_between(age_graph_2["Année"], age_graph_2["Population"], 
                                color='#66B3FF', alpha=0.1)
                max_population = max(max_population, age_graph_2["Population"].max())

            ax.set_xticks(age_graph_1["Année"])
            ax.set_ylim(0, max_population * 1.1)
            ax.grid(True, linestyle='--', alpha=0.5)

            ax.yaxis.set_major_formatter(ticker.FuncFormatter(
                lambda x, _: f'{x/1e6:,.1f}M' if x >= 1e6 else f'{x/1e3:,.1f}K'))

            legend = ax.legend(
                loc="lower center",
                bbox_to_anchor=(0.5, -0.3),
                ncol=2,
                fontsize=10,
                frameon=False
            )
            
            figx.tight_layout(rect=[0, 0.05, 1, 1])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            st.pyplot(figx)




    # ------------ Graphique 2 ------------

    with cols[2]:

        df_nd = nd.melt(
            id_vars=["code_insee", "Ville", "Unnamed: 0"],
            var_name="Année",
            value_name="Valeur"
        )

        df_nd["Année"] = df_nd["Année"].astype(int)
        df_nd["Valeur"] = (
            df_nd["Valeur"]
            .astype(str)
            .str.replace(r"\xa0", "", regex=True)
            .str.replace(" ", "")
            .str.replace(",", "")
            .astype(int)
        )

        nd_1 = df_nd[df_nd['code_insee'] == code_insee_choisi_1]
        nd_2 = df_nd[df_nd['code_insee'] == code_insee_choisi_2]

        with st.expander("📈 Évolution des naissances et décès de la population :", expanded=True):
            col1, col2 = st.columns([3, 2])

            with col1:
                option2 = st.selectbox(
                    "🎛️ Ville(s) à afficher",
                    options=[
                        "Afficher les deux villes choisies",
                        f"Afficher uniquement {ville_choisie_1}",
                        f"Afficher uniquement {ville_choisie_2}"
                    ],
                    index=0,
                    key="unique_key_option2",
                    label_visibility="collapsed"
                )

            with col2:
                nd_choix = st.selectbox(
                    "📊 Naissance ou Décès",
                    options=["Naissances", "Décès"],
                    index=0,
                    key="unique_key_type_affichage",
                    label_visibility="collapsed"
                )

            st.markdown("", unsafe_allow_html=True)
            
            figx, ax = plt.subplots(figsize=(11.1, 5))

            max_population = 0

            if (option2 == f"Afficher uniquement {ville_choisie_1}" or option2 == "Afficher les deux villes choisies") and nd_choix == "Naissances":
                nd_1 = nd_1[nd_1["Unnamed: 0"] == "Naissances domiciliées"]
                ax.plot(nd_1["Année"], nd_1["Valeur"], 
                        marker='o', markersize=6, linewidth=2.5, color='#FF9999', label=ville_choisie_1)
                ax.fill_between(nd_1["Année"], nd_1["Valeur"], 
                                color='#FF9999', alpha=0.1)
                max_population = max(max_population, nd_1["Valeur"].max())

            if (option2 == f"Afficher uniquement {ville_choisie_1}" or option2 == "Afficher les deux villes choisies") and nd_choix == "Décès":
                nd_1 = nd_1[nd_1["Unnamed: 0"] == "Décès domiciliés"]
                ax.plot(nd_1["Année"], nd_1["Valeur"], 
                        marker='s', markersize=6, linewidth=2.5, color='#FF9999', label=ville_choisie_1)
                ax.fill_between(nd_1["Année"], nd_1["Valeur"], 
                                color='#FF9999', alpha=0.1)
                max_population = max(max_population, nd_1["Valeur"].max())

            if (option2 == f"Afficher uniquement {ville_choisie_2}" or option2 == "Afficher les deux villes choisies") and nd_choix == "Naissances":
                nd_2 = nd_2[nd_2["Unnamed: 0"] == "Naissances domiciliées"]
                ax.plot(nd_2["Année"], nd_2["Valeur"], 
                        marker='o', markersize=6, linewidth=2.5, color='#66B3FF', label=ville_choisie_2)
                ax.fill_between(nd_2["Année"], nd_2["Valeur"], 
                                color='#66B3FF', alpha=0.1)
                max_population = max(max_population, nd_2["Valeur"].max())

            if (option2 == f"Afficher uniquement {ville_choisie_2}" or option2 == "Afficher les deux villes choisies") and nd_choix == "Décès":
                nd_2 = nd_2[nd_2["Unnamed: 0"] == "Décès domiciliés"]
                ax.plot(nd_2["Année"], nd_2["Valeur"], 
                        marker='s', markersize=6, linewidth=2.5, color='#66B3FF', label=ville_choisie_2)
                ax.fill_between(nd_2["Année"], nd_2["Valeur"], 
                                color='#66B3FF', alpha=0.1)
                max_population = max(max_population, nd_2["Valeur"].max())


            ax.set_xticks(nd_1["Année"])
            ax.set_ylim(0, max_population * 1.1)
            ax.grid(True, linestyle='--', alpha=0.5)
            legend = ax.legend(
                loc="lower center",
                bbox_to_anchor=(0.5, -0.3),
                ncol=2,
                fontsize=10,
                frameon=False
            )
            figx.tight_layout(rect=[0, 0.05, 1, 1])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

            st.pyplot(figx)

    

    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)


    st.markdown("", unsafe_allow_html=True)











# -------------------------------------------------
# ------------- Page Données d'Emploi -------------
# -------------------------------------------------

with onglet4:

    st.markdown("", unsafe_allow_html=True)


    df_statut_pro = pd.read_csv("data_stat_pro_annee.csv")
    df_salaire_horaire = pd.read_csv("data_salaire_genre_categ_pro.csv", sep=",")

    def enlever_accents(texte):
            return ''.join(
                c for c in unicodedata.normalize('NFD', texte)
                if unicodedata.category(c) != 'Mn'
            )

    ville_choisie_1_nom = ville_choisie_1.split(' (')[0]
    ville_choisie_1_nom = enlever_accents(ville_choisie_1_nom).replace(' ', '-')

    ville_choisie_2_nom = ville_choisie_2.split(' (')[0]
    ville_choisie_2_nom = enlever_accents(ville_choisie_2_nom).replace(' ', '-')


    def get_population_data(token, code_dep):
        url = "https://api.francetravail.io/partenaire/stats-informations-territoire/v1/indicateur/stat-population-active"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "codeTypeTerritoire": "DEP",
            "codeTerritoire": f"{code_dep}",
            "codeTypeActivite": "CUMUL",
            "codeActivite": "CUMUL",
            "codeTypePeriode": "ANNEE"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()


    def affichage_pourcentage(df, symbole=""):
        return df.apply(
        lambda x: f"{symbole}{x:.2f} %" if pd.notnull(x) and x > 0 else (f"{x:.2f} %" if pd.notnull(x) else "")
        )


    def affichage_population(data):
        df = pd.DataFrame([{
            "Année": int(item["codePeriode"]),
            "Population Active": item["valeurPrincipaleNombre"],
            "% Population Active / Totale": item["valeurSecondaireTaux"]
        } for item in data])
        
        df = df.sort_values("Année")
        
        df["Évolution (%)"] = df["Population Active"].pct_change() * 100
        df["% Population Active / Totale"] = affichage_pourcentage(df["% Population Active / Totale"])
        max_year = df["Année"].max()
        return df[df["Année"] == max_year]["% Population Active / Totale"].values[0]


    def evolution_pop_active(data):
        df = pd.DataFrame([{
            "Année": int(item["codePeriode"]),
            "Population Active": item["valeurPrincipaleNombre"],
            "% Population Active / Totale": item["valeurSecondaireTaux"]
        } for item in data])
        
        df = df.sort_values("Année")
        
        df["Évolution (%)"] = df["Population Active"].pct_change() * 100
        df["Évolution (%)"] = affichage_pourcentage(df["Évolution (%)"], "+")
        max_year = df["Année"].max()
        return df[df["Année"] == max_year]["Évolution (%)"].values[0]


    def prop_genre_actif(data):
        df = pd.DataFrame([{
                "Année": int(item["codePeriode"]),
                "Genre": caract["libCaract"],
                "Population Active": caract["nombre"],
                "% Population Active / Totale": caract["pourcentage"]
            } for item in data for caract in item["listeValeurParCaract"] if caract["codeTypeCaract"] == "GENRE"])

        df["% Population Active / Totale"] = affichage_pourcentage(df["% Population Active / Totale"])
        max_year = df["Année"].max()
        return df[df["Année"] == max_year]["% Population Active / Totale"].values[:2]


    def prop_chomage(df, ville):
        # Nettoyage et conversion des valeurs de pourcentage
        df["Chômeurs en %"] = df["Chômeurs en %"].astype(str).str.replace(",", ".").astype(float)
        df["Chômeurs en % (2)"] = affichage_pourcentage(df["Chômeurs en %"])
        
        # Filtrage de la bonne ville et année
        resultat = df[(df["Année"] == 2021) & (df["Ville"].str.lower() == ville.lower())]["Chômeurs en % (2)"]
        return resultat.values[0]


    def secteur_act(data):
        df = pd.DataFrame([{
            "Année": int(item["codePeriode"]),
            "Statut socio-professionnel": caract["libCaract"],
            "Pourcentage": caract["pourcentage"]
        } for item in data for caract in item["listeValeurParCaract"] if caract["codeTypeCaract"] == "GRSEC"])
        
        df = df.sort_values("Année")
        return df


    def salaire_hor_moy(df, ville):
        df["Ensemble"] = df["Ensemble"].astype(str).str.replace(",", ".").astype(float)
        salaire = df[(df["Ville"].str.lower() == ville.lower())]["Ensemble"][1:]
        return salaire.median()


    def tranches_age(data):
        df = pd.DataFrame([{
            "Année": int(item["codePeriode"]),
            "Tranche âge": caract["libCaract"],
            "Pourcentage": caract["pourcentage"]
        } for item in data for caract in item["listeValeurParCaract"] if caract["codeTypeCaract"] == "AGE"])
        
        df = df.sort_values("Année")
        return df
    

    def authenticate(scope):
        url = 'https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {
            'grant_type': 'client_credentials',
            'scope': scope,
            'client_id': os.getenv("API_CLIENT_ID"),
            'client_secret': os.getenv("API_CLIENT_SECRET")
        }
        response = requests.post(url, data=params, headers=headers)
        return json.loads(response.text)['access_token']




    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Données Rapides :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un aperçu synthétique des informations sur l'emploi dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)



    tranche = pd.read_csv("data_tranche_d-age_pourcentage.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})



    try:
        token = authenticate("infosterritoire api_stats-informations-territoirev1")
        population_data1 = get_population_data(token, filtered_dep_1)
        population_data2 = get_population_data(token, filtered_dep_2)
        data1 = population_data1.get("listeValeursParPeriode", [])
        data2 = population_data2.get("listeValeursParPeriode", [])

        try:
            pop_active1 = affichage_population(data1)
        except:
            pop_active1 = "Pas de données"

        try:
            pop_active2 = affichage_population(data2)
        except:
            pop_active2 = "Pas de données"

        try:
            evo_pop_active1 = evolution_pop_active(data1)
        except:
            evo_pop_active1 = "Pas de données"

        try:
            evo_pop_active2 = evolution_pop_active(data2)
        except:
            evo_pop_active2 = "Pas de données"

        try:
            genre_actif1 = prop_genre_actif(data1)
        except:
            genre_actif1 = "Pas de données"

        try:
            genre_actif2 = prop_genre_actif(data2)
        except:
            genre_actif2 = "Pas de données"

        try:
            chomage1 = prop_chomage(df_statut_pro, ville_choisie_1_nom)
        except:
            chomage1 = "Pas de données"

        try:
            chomage2 = prop_chomage(df_statut_pro, ville_choisie_2_nom)
        except:
            chomage2 = "Pas de données"

        try:
            secteur1 = secteur_act(data1)
        except:
            secteur1 = pd.DataFrame()

        try:
            secteur2 = secteur_act(data2)
        except:
            secteur2 = pd.DataFrame()

        try:
            salaire_horaire1 = round(salaire_hor_moy(df_salaire_horaire, ville_choisie_1_nom), 2)
        except:
            salaire_horaire1 = "Pas de données"

        try:
            salaire_horaire2 = round(salaire_hor_moy(df_salaire_horaire, ville_choisie_2_nom), 2)
        except:
            salaire_horaire2 = "Pas de données"

        try:
            age1 = tranches_age(data1)
        except:
            age1 = pd.DataFrame()

        try:
            age2 = tranches_age(data2)
        except:
            age2 = pd.DataFrame()

    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")


    # st.write("genre_actif1:", genre_actif1)
    # st.write("type(genre_actif1):", type(genre_actif1))

    # st.write("genre_actif2:", genre_actif2)
    # st.write("type(genre_actif2):", type(genre_actif2))


    femmes_actives1 = "Pas de données" if isinstance(genre_actif1, str) and genre_actif1 == "Pas de données" else (genre_actif1[1] if isinstance(genre_actif1, np.ndarray) and genre_actif1.size > 1 else "Pas de données")
    femmes_actives2 = "Pas de données" if isinstance(genre_actif2, str) and genre_actif2 == "Pas de données" else (genre_actif2[1] if isinstance(genre_actif2, np.ndarray) and genre_actif2.size > 1 else "Pas de données")

    hommes_actives1 = "Pas de données" if isinstance(genre_actif1, str) and genre_actif1 == "Pas de données" else (genre_actif1[0] if isinstance(genre_actif1, np.ndarray) and genre_actif1.size > 0 else "Pas de données")
    hommes_actives2 = "Pas de données" if isinstance(genre_actif2, str) and genre_actif2 == "Pas de données" else (genre_actif2[0] if isinstance(genre_actif2, np.ndarray) and genre_actif2.size > 0 else "Pas de données")

    salaire1_affichage = f"{salaire_horaire1} €" if isinstance(salaire_horaire1, (int, float)) and not np.isnan(salaire_horaire1) else "Pas de données"
    salaire2_affichage = f"{salaire_horaire2} €" if isinstance(salaire_horaire2, (int, float)) and not np.isnan(salaire_horaire2) else "Pas de données"



    st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Ville choisie :</p>
                <p style="font-size: 14px;">{ville_choisie_1} <br> {ville_choisie_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Population active (%) :</p>
                <p style="font-size: 14px;">{pop_active1} <br> {pop_active2} </p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Évolution des actifs :</p>
                <p style="font-size: 14px;"> {evo_pop_active1} <br> {evo_pop_active2} </p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Part des femmes actives :</p>
                <p style="font-size: 14px;"> {femmes_actives1} <br> {femmes_actives2} </p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Part des hommes actifs :</p>
                <p style="font-size: 14px;"> {hommes_actives1} <br> {hommes_actives2} </p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Taux de chômeurs :</p>
                <p style="font-size: 14px;"> {chomage1} <br> {chomage2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Salaire horaire médian :</p>
                <p style="font-size: 14px;"> {salaire1_affichage} <br> {salaire2_affichage}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Graphiques :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Plusieurs visualisations d'indicateurs d'emploi dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)


    col1, colbis, col2 = st.columns([1, 0.1, 1])
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    col3, colbis2, col4 = st.columns([1, 0.1, 1])
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)        
    
    col5, colbis3, col6 = st.columns([1, 0.1, 1])

    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)


    # Nettoyage des données
    df_statut_pro["Chômeurs en %"] = df_statut_pro["Chômeurs en %"].astype(str).str.replace(",", ".").astype(float)
    df_statut_pro["Actifs ayant un emploi en %"] = df_statut_pro["Actifs ayant un emploi en %"].astype(str).str.replace(",", ".").astype(float)

    # Récupérer les noms des villes depuis les sélections
    ville1 = ville_choisie_1_nom.lower()
    ville2 = ville_choisie_2_nom.lower()

    # Filtrer les données pour les deux villes
    df_filtered_statut_pro = df_statut_pro[df_statut_pro["Ville"].str.lower().isin([ville1, ville2])]

    # Créer le graphique à barres groupées avec Altair
    df_filtered_statut_pro["Année"] = df_filtered_statut_pro["Année"].astype(str)

    # Graphique à barres groupées (pas empilées)
    chart_chomeur = alt.Chart(df_filtered_statut_pro).mark_bar().encode(
        x=alt.X("Année:N", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Chômeurs en %:Q", title="Taux de chômage (%)"),
        color=alt.Color("Ville:N", 
                        title="Ville",
                        scale=alt.Scale(
                            range=["#FF9999", "#66B3FF"]
                        )),
        xOffset="Ville:N",
        tooltip=["Ville", "Année", "Chômeurs en %"]
    ).properties(
        width=500,
        height=350
    )


    chart_actifs_emploi = alt.Chart(df_filtered_statut_pro).mark_bar().encode(
        x=alt.X("Année:N", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Actifs ayant un emploi en %:Q", title="Actifs ayant un emploi (%)"),
        color=alt.Color("Ville:N", 
                        title="Ville",
                        scale=alt.Scale(
                            range=["#FF9999", "#66B3FF"]
                        )),
        xOffset="Ville:N",  # << CLÉ POUR LES BARRES CÔTE À CÔTE
        tooltip=["Ville", "Année", "Actifs ayant un emploi en %"]
    ).properties(
        width=500,
        height=350
    )


    chart_statut_pro1 = alt.Chart(secteur1).mark_bar().encode(
        x=alt.X("Année:N", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Pourcentage:Q", title="Population active (%)"),
        color=alt.Color("Statut socio-professionnel:N", 
                        title="Statut socio-professionnel",
                        scale=alt.Scale(
                            range=["#FF9999", "#66B3FF", "#99FF99", "#FFCC99", "#C2C2F0"]
                        )),
        tooltip=["Statut socio-professionnel", "Pourcentage", "Année"]
    ).properties(
        title=f"{ville_choisie_1}",
        width=500,
        height=350
    ).configure_title(
        fontSize=14,
        anchor='middle',
        fontWeight='normal'
    )


    chart_statut_pro2 = alt.Chart(secteur2).mark_bar().encode(
        x=alt.X("Année:N", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Pourcentage:Q", title="Population active (%)"),
        color=alt.Color("Statut socio-professionnel:N", 
                        title="Statut socio-professionnel",
                        scale=alt.Scale(
                            range=["#FF9999", "#66B3FF", "#99FF99", "#FFCC99", "#C2C2F0"]
                        )),
        tooltip=["Statut socio-professionnel", "Pourcentage", "Année"]
    ).properties(
        title=f"{ville_choisie_2}",
        width=500,
        height=350
    ).configure_title(
        fontSize=14,
        anchor='middle',
        fontWeight='normal'
    )


    chart_age1 = alt.Chart(age1).mark_bar().encode(
        x=alt.X("Année:N", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Pourcentage:Q", title="population active (%)"),
        color=alt.Color("Tranche âge:N", 
                        title="Tranche âge",
                        scale=alt.Scale(
                            range=["#FF9999", "#66B3FF", "#99FF99"]
                        )),
        tooltip=["Tranche âge", "Pourcentage", "Année"]
    ).properties(
        title=f"{ville_choisie_1}",
        width=500,
        height=350
    ).configure_title(
        fontSize=14,
        anchor='middle',
        fontWeight='normal'
    )


    chart_age2 = alt.Chart(age2).mark_bar().encode(
        x=alt.X("Année:N", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Pourcentage:Q", title="population active (%)"),
        color=alt.Color("Tranche âge:N", 
                        title="Tranche âge",
                        scale=alt.Scale(
                            range=["#FF9999", "#66B3FF", "#99FF99"]
                        )),
        tooltip=["Tranche âge", "Pourcentage", "Année"]
    ).properties(
        title=f"{ville_choisie_2}",
        width=500,
        height=350
    ).configure_title(
        fontSize=14,
        anchor='middle',
        fontWeight='normal'
    )


    # Affichage dans les colonnes Streamlit
    # Graphique à barres groupées - Actifs ayant un emploi
    with col1:
        with st.expander("📊 Répartition de la part d'actifs ayant un emploi par ville et par année :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if df_filtered_statut_pro.empty:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")
            else:
                st.altair_chart(chart_actifs_emploi, use_container_width=True)

    # Graphique à barres groupées - Taux de chômage
    with col2:
        with st.expander("📊 Taux de chômage par ville et par année :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if df_filtered_statut_pro.empty:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")
            else:
                st.altair_chart(chart_chomeur, use_container_width=True)

    # Graphique - Répartition population active par secteur d'activité (ville 1)
    with col3:
        with st.expander("📊 Répartition de la population active par secteur d'activité et par année :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if secteur1.empty:
                st.write("Aucune donnée trouvée pour la ville sélectionnée.")
            else:
                st.altair_chart(chart_statut_pro1, use_container_width=True)

    # Graphique - Répartition population active par secteur d'activité (ville 2)
    with col4:
        with st.expander("📊 Répartition de la population active par secteur d'activité et par année :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if secteur2.empty:
                st.write("Aucune donnée trouvée pour la ville sélectionnée.")
            else:
                st.altair_chart(chart_statut_pro2, use_container_width=True)

    # Graphique - Répartition population active par tranche d'âge (ville 1)
    with col5:
        with st.expander("📊 Répartition de la population active par tranche d'âge et par année :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if age1.empty:
                st.write("Aucune donnée trouvée pour la ville sélectionnée.")
            else:
                st.altair_chart(chart_age1, use_container_width=True)

    # Graphique - Répartition population active par tranche d'âge (ville 2)
    with col6:
        with st.expander("📊 Répartition de la population active par tranche d'âge et par année :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if age2.empty:
                st.write("Aucune donnée trouvée pour la ville sélectionnée.")
            else:
                st.altair_chart(chart_age2, use_container_width=True)









# ------------------------------------------------
# ------------- Page Offres d'Emploi -------------
# ------------------------------------------------

with onglet5:

    st.markdown("", unsafe_allow_html=True)

    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Recherche d'offres d'emploi :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un aperçu des offres d'emploi actuelles dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)
    
    

    def authenticate(scope):
        url = 'https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {
            'grant_type': 'client_credentials',
            'scope': scope,
            'client_id': os.getenv("API_CLIENT_ID"),
            'client_secret': os.getenv("API_CLIENT_SECRET")
        }
        response = requests.post(url, data=params, headers=headers)
        return json.loads(response.text)['access_token']


    def liste_metier(code_dep, mots_cles, access_token):
        url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
        querystring = {"departement": f"{code_dep}", "motsCles": f"{mots_cles}"}
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        response = requests.get(url, headers=headers, params=querystring)

        try:
            return response.json()
        except json.JSONDecodeError:
            return {}

    

    def enlever_accents(texte):
            return ''.join(
                c for c in unicodedata.normalize('NFD', texte)
                if unicodedata.category(c) != 'Mn'
            )


    ville_choisie_1_nom = ville_choisie_1.split(' (')[0]
    ville_choisie_1_nom = enlever_accents(ville_choisie_1_nom).replace(' ', '-')

    ville_choisie_2_nom = ville_choisie_2.split(' (')[0]
    ville_choisie_2_nom = enlever_accents(ville_choisie_2_nom).replace(' ', '-')
    


    mot_cle = st.text_input("🔍 Mot-clé métier (ex : data, développeur)", value="data")
    nb_offres = st.selectbox("🔢 Nombre d'offres à afficher", ["5", "10", "50", "100", "Toutes"])

    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)



    try:
        token = authenticate("api_offresdemploiv2 o2dsoffre")

        col_ville1, spacer_middle, col_ville2 = st.columns([1, 0.1, 1])

        with col_ville1:
            st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
            st.subheader(f"🔍 Offres pour {ville_choisie_1} :")
            st.markdown("", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)
            recherche_data1 = liste_metier(filtered_dep_1, mot_cle + " " + ville_choisie_1_nom, token)
            offres1 = recherche_data1.get("resultats", [])

            if offres1:
                if nb_offres != "Toutes":
                    offres1 = offres1[:int(nb_offres)]
                for offre in offres1:
                    st.markdown(f"### {offre['intitule']}")
                    st.write(f"📍 Lieu : {offre.get('lieuTravail', {}).get('libelle', 'Inconnu')}")
                    st.write(f"📝 {offre.get('description', 'Pas de description.')[:300]}...")
                    st.write(f"[🔗 Voir l'offre]({offre.get('origineOffre', {}).get('urlOrigine', '#')})")
                    st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
            else:
                st.warning("Aucune offre trouvée pour cette ville.")

        with col_ville2:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.subheader(f"🔍 Offres pour {ville_choisie_2} :")
            st.markdown("", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)
            recherche_data2 = liste_metier(filtered_dep_2, mot_cle + " " + ville_choisie_2_nom, token)
            offres2 = recherche_data2.get("resultats", [])

            if offres2:
                if nb_offres != "Toutes":
                    offres2 = offres2[:int(nb_offres)]
                for offre in offres2:
                    st.markdown(f"### {offre['intitule']}")
                    st.write(f"📍 Lieu : {offre.get('lieuTravail', {}).get('libelle', 'Inconnu')}")
                    st.write(f"📝 {offre.get('description', 'Pas de description.')[:300]}...")
                    st.write(f"[🔗 Voir l'offre]({offre.get('origineOffre', {}).get('urlOrigine', '#')})")
                    st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
            else:
                st.warning("Aucune offre trouvée pour cette ville.")

    except Exception as e:
        st.error(f"Erreur lors de la recherche : {e}")


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)


    st.markdown("", unsafe_allow_html=True)









# ----------------------------------------------------
# ------------- Page Données de Logement -------------
# ----------------------------------------------------

with onglet6:

    st.markdown("", unsafe_allow_html=True)

    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Données Rapides :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un aperçu synthétique des informations sur le logement dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)



    tranche = pd.read_csv("data_tranche_d-age_pourcentage.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    maison = pd.read_csv("data_maisons_appartements.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    dfv = pd.read_csv("data_dfv_2019-2023_reduit.csv", sep=",", encoding="utf-8", dtype={"INSEE_COM": str})
    piece = pd.read_csv("data_piece_moy.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    nb_piece_moyen = pd.read_csv("data_nb_moyen_hab_log.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    emmenagement = pd.read_csv("data_anciennete_emmenagement.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    statut_occ = pd.read_csv("data_statut_occupation.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    superficie = pd.read_csv("data_superficie_log.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    type_log = pd.read_csv("data_log_T2.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    nb_piece = pd.read_csv("data_nbr_pcs_logement.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})
    date = pd.read_csv("data_date_log.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})



    maison_1 = maison[maison['code_insee'] == code_insee_choisi_1]['Maisons'].values
    maison_2 = maison[maison['code_insee'] == code_insee_choisi_2]['Maisons'].values
    maison_1 = maison_1[0] if maison_1.size > 0 else "Pas de données"
    maison_2 = maison_2[0] if maison_2.size > 0 else "Pas de données"

    appart_1 = maison[maison['code_insee'] == code_insee_choisi_1]['Appartements'].values
    appart_2 = maison[maison['code_insee'] == code_insee_choisi_2]['Appartements'].values
    appart_1 = appart_1[0] if appart_1.size > 0 else "Pas de données"
    appart_2 = appart_2[0] if appart_2.size > 0 else "Pas de données"

    surface_1 = dfv[(dfv['INSEE_COM'] == code_insee_choisi_1) & (dfv['Annee'] == 2023)]['SurfaceMoy'].values
    surface_2 = dfv[(dfv['INSEE_COM'] == code_insee_choisi_2) & (dfv['Annee'] == 2023)]['SurfaceMoy'].values
    surface_1 = surface_1[0] if surface_1.size > 0 else "Pas de données"
    surface_2 = surface_2[0] if surface_2.size > 0 else "Pas de données"

    prixm2_1 = dfv[(dfv['INSEE_COM'] == code_insee_choisi_1) & (dfv['Annee'] == 2023)]['Prixm2Moyen'].values
    prixm2_2 = dfv[(dfv['INSEE_COM'] == code_insee_choisi_2) & (dfv['Annee'] == 2023)]['Prixm2Moyen'].values
    prixm2_1 = prixm2_1[0] if prixm2_1.size > 0 else "Pas de données"
    prixm2_2 = prixm2_2[0] if prixm2_2.size > 0 else "Pas de données"

    piece_moy_1 = piece[(piece['code_insee'] == code_insee_choisi_1) & (piece['Type de résidence principale'] == "Ensemble des résidences principales")]['2021'].values
    piece_moy_2 = piece[(piece['code_insee'] == code_insee_choisi_2) & (piece['Type de résidence principale'] == "Ensemble des résidences principales")]['2021'].values
    piece_moy_1 = piece_moy_1[0] if piece_moy_1.size > 0 else "Pas de données"
    piece_moy_2 = piece_moy_2[0] if piece_moy_2.size > 0 else "Pas de données"

    nb_piece_moyen_1 = nb_piece_moyen[(nb_piece_moyen['code_insee'] == code_insee_choisi_1)]['1'].values
    nb_piece_moyen_2 = nb_piece_moyen[(nb_piece_moyen['code_insee'] == code_insee_choisi_2)]['1'].values
    nb_piece_moyen_1 = nb_piece_moyen_1[0] if nb_piece_moyen_1.size > 0 else "Pas de données"
    nb_piece_moyen_2 = nb_piece_moyen_2[0] if nb_piece_moyen_2.size > 0 else "Pas de données"



    def formater_donnees(valeur, type_valeur=""):
        if valeur == "Pas de données":
            return valeur
        try:
            formatted_value = f'{float(valeur):,.0f}'.replace(',', ' ')
            if type_valeur == "surface":
                return f'{formatted_value} m²'
            elif type_valeur == "prix":
                return f'{formatted_value} €'
            else:
                return formatted_value
        except ValueError:
            return valeur


    maison_1 = formater_donnees(maison_1)
    maison_2 = formater_donnees(maison_2)

    appart_1 = formater_donnees(appart_1)
    appart_2 = formater_donnees(appart_2)

    surface_1 = formater_donnees(surface_1, type_valeur="surface")
    surface_2 = formater_donnees(surface_2, type_valeur="surface")

    prixm2_1 = formater_donnees(prixm2_1, type_valeur="prix")
    prixm2_2 = formater_donnees(prixm2_2, type_valeur="prix")

    piece_moy_1 = formater_donnees(piece_moy_1)
    piece_moy_2 = formater_donnees(piece_moy_2)

    nb_piece_moyen_1 = formater_donnees(nb_piece_moyen_1)
    nb_piece_moyen_2 = formater_donnees(nb_piece_moyen_2)


    st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Ville choisie :</p>
                <p style="font-size: 14px;">{ville_choisie_1} <br> {ville_choisie_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Nombre de maisons :</p>
                <p style="font-size: 14px;">{maison_1} <br> {maison_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Nombre d'appartements :</p>
                <p style="font-size: 14px;">{appart_1} <br> {appart_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Superficie moyenne :</p>
                <p style="font-size: 14px;">{surface_1}<br> {surface_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Prix moyen au m² :</p>
                <p style="font-size: 14px;">{prixm2_1}<br> {prixm2_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Nombre de pièces moyen :</p>
                <p style="font-size: 14px;">{piece_moy_1} <br> {piece_moy_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Nombre d'hab/log moyen :</p>
                <p style="font-size: 14px;">{nb_piece_moyen_1} <br> {nb_piece_moyen_2}</p>
            </div>
            <!-- Ajoute autant de boîtes que nécessaire -->
        </div>
    """, unsafe_allow_html=True)



    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Graphiques :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Plusieurs visualisations d'indicateurs de logement dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)








    # -------------------------------------
    # -------------- Ligne 1 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    with cols[0]:

        modalites_piece = ["1 pièce", "2 pièces", "3 pièces", "4 pièces", "5 pièces ou plus"]

        # Filtrer les données
        piece_1 = nb_piece[
            (nb_piece['code_insee'] == code_insee_choisi_1) &
            (nb_piece['Nombre de pièces'].isin(modalites_piece)) &
            (nb_piece['Nombre de pièces'] != 'Ensemble')
        ]
        piece_1.rename(columns={piece_1.columns[6]: 'Pourcentage'}, inplace=True)

        piece_2 = nb_piece[
            (nb_piece['code_insee'] == code_insee_choisi_2) &
            (nb_piece['Nombre de pièces'].isin(modalites_piece)) &
            (nb_piece['Nombre de pièces'] != 'Ensemble')
        ]
        piece_2.rename(columns={piece_2.columns[6]: 'Pourcentage'}, inplace=True)

        try:
            valeurs_1 = piece_1.iloc[:, 6].apply(lambda x: float(str(x).replace(',', '.'))).values.flatten()
            valeurs_2 = piece_2.iloc[:, 6].apply(lambda x: float(str(x).replace(',', '.'))).values.flatten()
            
            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(modalites_piece)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color='#FF9999')
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color='#66B3FF')

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(modalites_piece)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f} %',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Proportion des logements par nombre de pièces :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")

    






    # ------------ Graphique 2 ------------

    with cols[2]:

        labels_superficie = [
            "Moins de 30 m²", 
            "Entre 30 et 40 m²", 
            "Entre 40 et 60 m²", 
            "Entre 60 et 80 m²", 
            "Entre 80 et 100 m²", 
            "Entre 100 et 120 m²", 
            "Plus de 120 m²"
        ]
        
        labels_affichage = [
            "Moins de 30 m²", 
            "30 à 40 m²", 
            "40 à 60 m²", 
            "60 à 80 m²", 
            "80 à 100 m²", 
            "100 à 120 m²", 
            "Plus de 120 m²"
        ]
        
        superficie_1 = superficie[
            (superficie['code_insee'] == code_insee_choisi_1) &
            (superficie['X0'].isin(labels_superficie))
        ]

        superficie_2 = superficie[
            (superficie['code_insee'] == code_insee_choisi_2) &
            (superficie['X0'].isin(labels_superficie))
        ]

        try:
            valeurs_1 = superficie_1["X2"].astype(str).str.replace(",", ".").astype(float).values.flatten()
            valeurs_2 = superficie_2["X2"].astype(str).str.replace(",", ".").astype(float).values.flatten()
            
            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(labels_superficie)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color='#FF9999')
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color='#66B3FF')

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(labels_affichage)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f} %',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Répartition des logements par surface (en m²) :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    





    # -------------------------------------
    # -------------- Ligne 2 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    colors_log = ['#FF9999','#66B3FF','#99FF99']
    labels_log = ["Résidences principales", "Résidences secondaires et logements occasionnels", "Logements vacants"]

    with cols[0]:

        log_1 = type_log[
            (type_log['code_insee'] == code_insee_choisi_1) &
            (type_log['Catégorie ou type de logement'].isin([
                "Résidences principales",
                "Résidences secondaires et logements occasionnels",
                "Logements vacants"
            ]))
        ]
        if not log_1.empty:
            values_1 = log_1.iloc[:, 6].apply(lambda x: float(str(x).replace(',', '.'))).values.flatten()
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            wedges_1, _, _ = ax1.pie(values_1, autopct='%1.1f%%', startangle=140, colors=colors_log, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax1.axis('equal')
            plt.title(f"{ville_choisie_1}")
        else:
            fig1 = None

        log_2 = type_log[
            (type_log['code_insee'] == code_insee_choisi_2) &
            (type_log['Catégorie ou type de logement'].isin([
                "Résidences principales",
                "Résidences secondaires et logements occasionnels",
                "Logements vacants"
            ]))
        ]
        if not log_2.empty:
            values_2 = log_2.iloc[:, 6].apply(lambda x: float(str(x).replace(',', '.'))).values.flatten()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            wedges_2, _, _ = ax2.pie(values_2, autopct='%1.1f%%', startangle=140, colors=colors_log, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax2.axis('equal')
            ax2.legend(wedges_2, labels_log, loc="center left", bbox_to_anchor=(1, 0.5))
            plt.title(f"{ville_choisie_2}")
        else:
            fig2 = None

        if fig1 is not None and fig2 is not None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

            wedges1, _, _ = ax1.pie(values_1, autopct='%1.1f%%', startangle=140, colors=colors_log, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax1.axis('equal')
            ax1.set_title(f"{ville_choisie_1}", fontsize=10)

            wedges2, _, _ = ax2.pie(values_2, autopct='%1.1f%%', startangle=140, colors=colors_log, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax2.axis('equal')
            ax2.set_title(f"{ville_choisie_2}", fontsize=10)

            fig.legend(wedges2, labels_log, loc='lower center', ncol=2, fontsize=10, frameon=False)
            fig.tight_layout(rect=[0, 0.1, 1, 0.95])

        else:
            fig = None


        with st.expander("📈 Proportion des logements par type :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")





    # ------------ Graphique 2 ------------

    labels_statut_occ = ["Propriétaires", "Locataires", "Logés gratuitement"]
    colors_statut_occ = ['#FF9999', '#66B3FF','#99FF99']

    with cols[2]:

        statut_occ_1 = statut_occ[statut_occ['code_insee'] == code_insee_choisi_1]
        if not statut_occ_1.empty:
            values_3 = statut_occ_1[labels_statut_occ].values.flatten()
            fig3, ax3 = plt.subplots(figsize=(5, 5))
            wedges_3, _, _ = ax3.pie(values_3, autopct='%1.1f%%', startangle=140, colors=colors_statut_occ, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax3.axis('equal')
            plt.title(f"{ville_choisie_1}")
        else:
            fig3 = None

        statut_occ_2 = statut_occ[statut_occ['code_insee'] == code_insee_choisi_2]
        if not statut_occ_2.empty:
            values_4 = statut_occ_2[labels_statut_occ].values.flatten()
            fig4, ax4 = plt.subplots(figsize=(5, 5))
            wedges_4, _, _ = ax4.pie(values_4, autopct='%1.1f%%', startangle=140, colors=colors_statut_occ, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax4.axis('equal')
            ax4.legend(wedges_4, labels_statut_occ, loc="center left", bbox_to_anchor=(1, 0.5))
            plt.title(f"{ville_choisie_2}")
        else:
            fig4 = None

        if fig3 is not None and fig4 is not None:
            fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(10, 5))

            wedges3, _, _ = ax3.pie(values_3, autopct='%1.1f%%', startangle=140, colors=colors_statut_occ, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax3.axis('equal')
            ax3.set_title(f"{ville_choisie_1}", fontsize=10)

            wedges4, _, _ = ax4.pie(values_4, autopct='%1.1f%%', startangle=140, colors=colors_statut_occ, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax4.axis('equal')
            ax4.set_title(f"{ville_choisie_2}", fontsize=10)

            fig.legend(wedges4, labels_statut_occ, loc='lower center', ncol=2, fontsize=10, frameon=False)
            fig.tight_layout(rect=[0, 0.1, 1, 0.95])

        else:
            fig = None


        with st.expander("📈 Proportion des logements par statut d'occupation :", expanded=True):
            st.markdown("", unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée trouvée pour l'une des deux villes sélectionnées.")


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)







    # -------------------------------------
    # -------------- Ligne 3 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    with cols[2]:

        labels_date = ["Avant 1919", "De 1919 à 1945", "De 1946 à 1970", "De 1971 à 1990", "De 1991 à 2005", "Après 2005"]

        # Filtrer les données
        date_1 = date[
            (date['code_insee'] == code_insee_choisi_1) &
            (date['0'].isin(labels_date))
        ]

        date_2 = date[
            (date['code_insee'] == code_insee_choisi_2) &
            (date['0'].isin(labels_date))
        ]

        try:
            valeurs_1 = date_1["2"].astype(str).str.replace(",", ".").astype(float).values.flatten()
            valeurs_2 = date_2["2"].astype(str).str.replace(",", ".").astype(float).values.flatten()
            
            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(labels_date)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color='#FF9999')
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color='#66B3FF')

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(labels_date)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f} %',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Proportion des logements par date de construction :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")






    # ------------ Graphique 2 ------------

    with cols[0]:

        labels_emmenagement = ["Depuis moins de 2 ans", "De 2 à 4 ans", "De 5 à 9 ans", "De 10 à 19 ans", "De 20 à 29 ans", "30 ans ou plus"]

        # Filtrer les données
        emmenagement_1 = emmenagement[
            (emmenagement['code_insee'] == code_insee_choisi_1) &
            (emmenagement['Unnamed: 0'].isin(labels_emmenagement))
        ]

        emmenagement_2 = emmenagement[
            (emmenagement['code_insee'] == code_insee_choisi_2) &
            (emmenagement['Unnamed: 0'].isin(labels_emmenagement))
        ]

        try:
            valeurs_1 = emmenagement_1["Part des ménages en %"].astype(str).str.replace(",", ".").astype(float).values.flatten()
            valeurs_2 = emmenagement_2["Part des ménages en %"].astype(str).str.replace(",", ".").astype(float).values.flatten()
            
            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(labels_emmenagement)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color='#FF9999')
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color='#66B3FF')

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(labels_emmenagement)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f} %',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Proportion des logements par ancienneté d'emménagement :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)










    # -------------------------------------
    # -------------- Ligne 4 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    with cols[0]:
        dfv["Annee"] = dfv["Annee"].astype(int)

        prix_moyen_1 = dfv[dfv['INSEE_COM'] == code_insee_choisi_1]
        prix_moyen_2 = dfv[dfv['INSEE_COM'] == code_insee_choisi_2]

        with st.expander("📈 Évolution du prix moyen d'un logement (en €) :", expanded=True):

            option3 = st.selectbox(
                "🎛️ Options d'affichage",
                options=[
                    "Afficher les deux villes choisies",
                    f"Afficher uniquement {ville_choisie_1}",
                    f"Afficher uniquement {ville_choisie_2}"
                ],
                index=0,
                key="unique_key_option3",
                label_visibility="collapsed"
            )

            st.markdown("", unsafe_allow_html=True)

            figx, ax = plt.subplots(figsize=(11.1, 5))

            max_population = 0

            if option3 == f"Afficher uniquement {ville_choisie_1}" or option3 == "Afficher les deux villes choisies":
                ax.plot(prix_moyen_1["Annee"], prix_moyen_1["PrixMoyen"], 
                        marker='o', markersize=6, linewidth=2.5, color='#FF9999', label=ville_choisie_1)
                ax.fill_between(prix_moyen_1["Annee"], prix_moyen_1["PrixMoyen"],
                                color='#FF9999', alpha=0.1)
                max_population = max(max_population, prix_moyen_1["PrixMoyen"].max())

            if option3 == f"Afficher uniquement {ville_choisie_2}" or option3 == "Afficher les deux villes choisies":
                ax.plot(prix_moyen_2["Annee"], prix_moyen_2["PrixMoyen"], 
                        marker='s', markersize=6, linewidth=2.5, color='#66B3FF', label=ville_choisie_2)
                ax.fill_between(prix_moyen_2["Annee"], prix_moyen_2["PrixMoyen"], 
                                color='#66B3FF', alpha=0.1)
                max_population = max(max_population, prix_moyen_2["PrixMoyen"].max())

            ax.set_xticks(prix_moyen_1["Annee"])
            ax.set_ylim(0, max_population * 1.1)
            ax.grid(True, linestyle='--', alpha=0.5)

            ax.yaxis.set_major_formatter(ticker.FuncFormatter(
                lambda x, _: f'{x/1e6:,.1f}M' if x >= 1e6 else f'{x/1e3:,.1f}K'))
            
            legend = ax.legend(
                loc="lower center",
                bbox_to_anchor=(0.5, -0.3),
                ncol=2,
                fontsize=10,
                frameon=False
            )
            figx.tight_layout(rect=[0, 0.05, 1, 1])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            st.pyplot(figx)





    # ------------ Graphique 2 ------------

    with cols[2]:
        dfv["Annee"] = dfv["Annee"].astype(int)

        prix_m2_1 = dfv[dfv['INSEE_COM'] == code_insee_choisi_1]
        prix_m2_2 = dfv[dfv['INSEE_COM'] == code_insee_choisi_2]

        with st.expander("📈 Évolution du prix moyen au m² d'un logement (en €) :", expanded=True):

            option4 = st.selectbox(
                "🎛️ Options d'affichage",
                options=[
                    "Afficher les deux villes choisies",
                    f"Afficher uniquement {ville_choisie_1}",
                    f"Afficher uniquement {ville_choisie_2}"
                ],
                index=0,
                key="unique_key_option4",
                label_visibility="collapsed"
            )

            st.markdown("", unsafe_allow_html=True)

            figx, ax = plt.subplots(figsize=(11.1, 5))

            max_population = 0

            if option4 == f"Afficher uniquement {ville_choisie_1}" or option4 == "Afficher les deux villes choisies":
                ax.plot(prix_m2_1["Annee"], prix_m2_1["Prixm2Moyen"], 
                        marker='o', markersize=6, linewidth=2.5, color='#FF9999', label=ville_choisie_1)
                ax.fill_between(prix_m2_1["Annee"], prix_m2_1["Prixm2Moyen"],
                                color='#FF9999', alpha=0.1)
                max_population = max(max_population, prix_m2_1["Prixm2Moyen"].max())

            if option4 == f"Afficher uniquement {ville_choisie_2}" or option4 == "Afficher les deux villes choisies":
                ax.plot(prix_m2_2["Annee"], prix_m2_2["Prixm2Moyen"], 
                        marker='s', markersize=6, linewidth=2.5, color='#66B3FF', label=ville_choisie_2)
                ax.fill_between(prix_m2_2["Annee"], prix_m2_2["Prixm2Moyen"], 
                                color='#66B3FF', alpha=0.1)
                max_population = max(max_population, prix_m2_2["Prixm2Moyen"].max())

            ax.set_xticks(prix_m2_1["Annee"])
            ax.set_ylim(0, max_population * 1.1)
            ax.grid(True, linestyle='--', alpha=0.5)
            legend = ax.legend(
                loc="lower center",
                bbox_to_anchor=(0.5, -0.3),
                ncol=2,
                fontsize=10,
                frameon=False
            )
            figx.tight_layout(rect=[0, 0.05, 1, 1])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

            st.pyplot(figx)


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)


    st.markdown("", unsafe_allow_html=True)










# -------------------------------------------------
# ------------- Page Données de Météo -------------
# -------------------------------------------------

with onglet7 :


    st.markdown("", unsafe_allow_html=True)

    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Données Rapides :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un aperçu synthétique des conditions météo actuelles dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)


    communes = gpd.read_file("Communes.geojson")
    climat_df = pd.read_excel('climat.xlsx')
    climat_saison = pd.read_csv("data_climat_saison.csv", sep=",", encoding="utf-8", dtype={"code_insee": str})



    def enlever_accents(texte):
            return ''.join(
                c for c in unicodedata.normalize('NFD', texte)
                if unicodedata.category(c) != 'Mn'
            )

    ville_choisie_1_nom = ville_choisie_1.split(' (')[0]
    ville_choisie_1_nom = enlever_accents(ville_choisie_1_nom).replace(' ', '-')

    ville_choisie_2_nom = ville_choisie_2.split(' (')[0]
    ville_choisie_2_nom = enlever_accents(ville_choisie_2_nom).replace(' ', '-')


    heure_1 = "Pas de données"
    heure_2 = "Pas de données"
    date_1 = "Pas de données"
    date_2 = "Pas de données"
    temperature_1 = "Pas de données"
    temperature_2 = "Pas de données"
    condition_1 = "Pas de données"
    condition_2 = "Pas de données"
    vent_vitesse_1 = "Pas de données"
    vent_vitesse_2 = "Pas de données"
    vent_direction_1 = "Pas de données"
    vent_direction_2 = "Pas de données"
    sunrise_1 = "Pas de données"
    sunset_1 = "Pas de données"
    sunrise_2 = "Pas de données"
    sunset_2 = "Pas de données"
    icone_url_1 = "Pas de données"
    icone_url_2 = "Pas de données"
    conditions_jours_1 = []
    conditions_jours_2 = []


    if ville_choisie_1_nom:
        url = f"https://prevision-meteo.ch/services/json/{ville_choisie_1_nom}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "current_condition" in data:
                current_1 = data['current_condition']
                ville_1 = data['city_info']['name']
                sunrise_1 = data['city_info']['sunrise']
                sunset_1 = data['city_info']['sunset']
                temperature_1 = current_1['tmp']
                condition_1 = current_1['condition']
                vent_vitesse_1 = current_1['wnd_spd']
                vent_direction_1 = current_1['wnd_dir']
                date_1 = current_1['date'].replace('.', '-')
                heure_1 = current_1['hour']
                icone_url_1 = current_1['icon']

                for i in range(1, 3):
                    day = data.get(f'fcst_day_{i}')
                    if day:
                        conditions_jours_1.append({
                            "date": day['date'],
                            "jour": day['day_long'],
                            "condition": day['condition'],
                            "tmin": day['tmin'],
                            "tmax": day['tmax'],
                            "icone": day['icon']
                        })

        else:
            st.warning("Aucune donnée météo disponible pour cette ville.")



    if ville_choisie_2_nom:
        url = f"https://prevision-meteo.ch/services/json/{ville_choisie_2_nom}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "current_condition" in data:
                current_2 = data['current_condition']
                ville_2 = data['city_info']['name']
                sunrise_2 = data['city_info']['sunrise']
                sunset_2 = data['city_info']['sunset']
                temperature_2 = current_2['tmp']
                condition_2 = current_2['condition']
                vent_vitesse_2 = current_2['wnd_spd']
                vent_direction_2 = current_2['wnd_dir']
                date_2 = current_2['date'].replace('.', '-')
                heure_2 = current_2['hour']
                icone_url_2 = current_2['icon']

                for i in range(1, 3):
                    day = data.get(f'fcst_day_{i}')
                    if day:
                        conditions_jours_2.append({
                            "date": day['date'],
                            "jour": day['day_long'],
                            "condition": day['condition'],
                            "tmin": day['tmin'],
                            "tmax": day['tmax'],
                            "icone": day['icon']
                        })

        else:
            st.warning("Aucune donnée météo disponible pour cette ville.")


    latitude_centre_1 = cc[cc['nom'] == ville_choisie_1]['latitude_mairie'].values[0] if ville_choisie_1 in cc['nom'].values else "Pas de données"
    longitude_centre_1 = cc[cc['nom'] == ville_choisie_1]['longitude_mairie'].values[0] if ville_choisie_1 in cc['nom'].values else "Pas de données"
    climat_1 = climat_df[climat_df['code_insee'] == code_insee_choisi_1]['nom_type'].values[0] if code_insee_choisi_1 else "Pas de données"

    latitude_centre_2 = cc[cc['nom'] == ville_choisie_2]['latitude_mairie'].values[0] if ville_choisie_2 in cc['nom'].values else "Pas de données"
    longitude_centre_2 = cc[cc['nom'] == ville_choisie_2]['longitude_mairie'].values[0] if ville_choisie_2 in cc['nom'].values else "Pas de données"
    climat_2 = climat_df[climat_df['code_insee'] == code_insee_choisi_2]['nom_type'].values[0] if code_insee_choisi_2 else "Pas de données"

    
    

    def formater_donnees(valeur, heure=None, sunset=None, vent_direction=None, type_valeur=""):
        if valeur == "Pas de données":
            return valeur
        try:
            if type_valeur == "date" and heure is not None:
                return f"{valeur} | {heure}"
            elif type_valeur == "sunrise" and sunset is not None:
                return f"{valeur} ↗︎ | {sunset} ↘︎"
            elif type_valeur == "vent_vitesse" and vent_direction is not None:
                return f"{valeur}km/h {vent_direction}"
            elif type_valeur == "temperature":
                return f"{valeur}°C"
            else:
                return valeur
        except ValueError:
            return valeur



    date_1 = formater_donnees(date_1, heure=heure_1, type_valeur="date")
    date_2 = formater_donnees(date_2, heure=heure_2, type_valeur="date")

    sunrise_1 = formater_donnees(sunrise_1, sunset=sunset_1, type_valeur="sunrise")
    sunrise_2 = formater_donnees(sunrise_2, sunset=sunset_2, type_valeur="sunrise")

    vent_vitesse_1 = formater_donnees(vent_vitesse_1, vent_direction=vent_direction_1, type_valeur="vent_vitesse")
    vent_vitesse_2 = formater_donnees(vent_vitesse_2, vent_direction=vent_direction_2, type_valeur="vent_vitesse")

    temperature_1 = formater_donnees(temperature_1, type_valeur="temperature")
    temperature_2 = formater_donnees(temperature_2, type_valeur="temperature")



    st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Ville choisie :</p>
                <p style="font-size: 14px;">{ville_choisie_1} <br> {ville_choisie_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Type de climat :</p>
                <p style="font-size: 14px;">{climat_1} <br> {climat_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Date courante :</p>
                <p style="font-size: 14px;">{date_1} <br> {date_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Horaires du soleil :</p>
                <p style="font-size: 14px;">{sunrise_1}<br> {sunrise_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center; height: 146px;">
                <p style="font-size: 16px; font-weight: bold;">État du ciel :</p>
                <p style="font-size: 14px;">
                    <img src="{icone_url_1}" width="20" /> {condition_1} <br> 
                    <img src="{icone_url_2}" width="20" /> {condition_2}
                </p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Vent et orientation :</p>
                <p style="font-size: 14px;">{vent_vitesse_1}<br> {vent_vitesse_2}</p>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 234px; text-align: center;">
                <p style="font-size: 16px; font-weight: bold;">Température :</p>
                <p style="font-size: 14px;">{temperature_1} <br> {temperature_2}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)

    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Carte des Climats :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Une visualisation détaillée des différents types de climat dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)



    couleurs = {
        "8": "#CD5C5C",  # firebrick3
        "7": "#FF8C00",  # darkorange
        "6": "#B3E59A",  # darkolivegreen2
        "5": "#4E9F3D",  # chartreuse4
        "4": "#66CDAA",  # aquamarine3
        "3": "#97FFFF",  # darkslategray1
        "2": "#00BFFF",  # deepskyblue
        "1": "#00008B"   # blue4
    }


    type_labels = {
        "1": "Montagne",
        "2": "Semi-continental",
        "3": "Océanique dégradé",
        "4": "Océanique altéré",
        "5": "Océanique",
        "6": "Méditerranéen altéré",
        "7": "Bassin du Sud-Ouest",
        "8": "Méditerranéen"
    }




    cols = st.columns([1, 1])


    with cols[0]:
        if 'zoom_start' not in st.session_state:
            st.session_state.zoom_start = 5

        def toggle_zoom():
            st.session_state.zoom_start = 11 if st.session_state.zoom_start == 5 else 5

        m = folium.Map(location=[latitude_centre_1, longitude_centre_1], zoom_start=st.session_state.zoom_start)

        folium.GeoJson(
            communes,
            style_function=lambda feature: {
                'fillColor': couleurs.get(str(feature['properties']['Type']), '#ffffff'),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.4
            }
        ).add_to(m)


        popup_text = f"<b>Ville :</b> {ville_choisie_1}<br><b>Climat :</b> {climat_1}"
        popup_custom = Popup(popup_text, max_width=300)

        folium.Marker(
            [latitude_centre_1, longitude_centre_1],
            popup=popup_custom,
            icon=Icon(color='darkred', icon="cloud")
        ).add_to(m)


        st.components.v1.html(f"""
            <style>
                .folium-map {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                #map {{
                    margin: 0 auto;
                }}
            </style>
            {m.get_root().render()}
        """, width=900, height=410)


    with cols[1]:
        if 'zoom_start' not in st.session_state:
            st.session_state.zoom_start = 5

        def toggle_zoom():
            st.session_state.zoom_start = 11 if st.session_state.zoom_start == 5 else 5

        m = folium.Map(location=[latitude_centre_2, longitude_centre_2], zoom_start=st.session_state.zoom_start)

        folium.GeoJson(
            communes,
            style_function=lambda feature: {
                'fillColor': couleurs.get(str(feature['properties']['Type']), '#ffffff'),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.4
            }
        ).add_to(m)


        popup_text = f"<b>Ville :</b> {ville_choisie_2}<br><b>Climat :</b> {climat_2}"
        popup_custom = Popup(popup_text, max_width=300)

        folium.Marker(
            [latitude_centre_2, longitude_centre_2],
            popup=popup_custom,
            icon=Icon(color='darkred', icon="cloud")
        ).add_to(m)


        st.components.v1.html(f"""
            <style>
                .folium-map {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                #map {{
                    margin: 0 auto;
                }}
            </style>
            {m.get_root().render()}
        """, width=900, height=410)



    st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)

            
    col1, col2 = st.columns([1, 5.5])

    with col1:
        st.button("Changer le zoom des villes 🔎", on_click=toggle_zoom)

    with col2:
        st.markdown(f"<div style='margin-top: 8px; margin-left: -25px;'>Seule la représentation cartographique des climats de la France Métropolitaine peut être visible. Les climats de la Corse et des DOM-TOM ne peuvent être affichés sur la carte.</div>", unsafe_allow_html=True)


    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)






    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Graphiques :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Plusieurs visualisations d'indicateurs de la météo dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)








    # -------------------------------------
    # -------------- Ligne 1 --------------
    # -------------------------------------

    cols = st.columns([1, 0.1, 1])


    # ------------ Graphique 1 ------------

    with cols[0]:

        climat_saison = climat_saison.rename(columns={"Eté": "Été"})
        saisons = ["Hiver", "Printemps", "Été", "Automne"]

        saison_1 = climat_saison[(climat_saison['code_insee'] == code_insee_choisi_1) & 
                                (climat_saison['X'] == "Heures d'ensoleillement")]

        saison_2 = climat_saison[(climat_saison['code_insee'] == code_insee_choisi_2) & 
                                (climat_saison['X'] == "Heures d'ensoleillement")]

        try:
            valeurs_1 = saison_1[saisons].values.flatten().astype(float)
            valeurs_2 = saison_2[saisons].values.flatten().astype(float)

            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(saisons)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color="#F4A261")
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color="#EAC199")

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(saisons)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Heures d’ensoleillement par saison :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")





    # ------------ Graphique 2 ------------

    with cols[2]:

        climat_saison = climat_saison.rename(columns={"Eté": "Été"})
        saisons = ["Hiver", "Printemps", "Été", "Automne"]

        saison_1 = climat_saison[(climat_saison['code_insee'] == code_insee_choisi_1) & 
                                (climat_saison['X'] == "Hauteur de pluie")]

        saison_2 = climat_saison[(climat_saison['code_insee'] == code_insee_choisi_2) & 
                                (climat_saison['X'] == "Hauteur de pluie")]

        try:
            valeurs_1 = saison_1[saisons].values.flatten().astype(float)
            valeurs_2 = saison_2[saisons].values.flatten().astype(float)

            if np.any(np.isnan(valeurs_1)) or np.any(np.isnan(valeurs_2)):
                raise ValueError("Présence de NaN dans les données")

            width = 0.35
            offset = width / 1.75
            x = np.arange(len(saisons)) * (width * 3)

            fig, ax = plt.subplots(figsize=(10, 5))

            bars1 = ax.bar(x - offset, valeurs_1, width, label=ville_choisie_1, color="#66B3FF")
            bars2 = ax.bar(x + offset, valeurs_2, width, label=ville_choisie_2, color="#3F81C3")

            max_val = max(max(valeurs_1), max(valeurs_2))
            ax.set_ylim(0, max_val * 1.15)

            ax.set_xticks(x)
            ax.set_xticklabels(saisons)

            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

            fig.legend([bars1, bars2], [ville_choisie_1, ville_choisie_2],
                    loc='lower center', ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.01))

            fig.tight_layout(rect=[0, 0.1, 1, 1])

        except:
            fig = None

        with st.expander("📊 Hauteur de pluie par saison (en mm) :", expanded=True):
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.write("Aucune donnée disponible pour l'une des deux villes sélectionnées.")


    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)








    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Prévisions Météo :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un aperçu des prévisions météo pour les deux prochains jours dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)
    


    st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 104px;">
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 827px; text-align: center;">
                <p style="font-size: 14px;">{ville_choisie_1}</p>
                <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                    {''.join([f'<div style="text-align: center; margin: 10px; width: 250px; font-size: 14px;">'
                            f'<img src="{jour["icone"]}" width="50" /><br>{jour["jour"]} ({jour["date"].replace(".", "-")})<br>'
                            f'☀️ {jour["condition"]}<br>🌡️ {jour["tmin"]}°C ➝ {jour["tmax"]}°C</div>' 
                            for jour in conditions_jours_1]) if conditions_jours_1 else '<p>Pas de données disponibles</p>'}
                </div>
            </div>
            <div style="border: 2px solid #ddd; padding: 20px; border-radius: 10px; width: 827px; text-align: center;">
                <p style="font-size: 14px;">{ville_choisie_2}</p>
                <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                    {''.join([f'<div style="text-align: center; margin: 10px; width: 250px; font-size: 14px;">'
                            f'<img src="{jour["icone"]}" width="50" /><br>{jour["jour"]} ({jour["date"].replace(".", "-")})<br>'
                            f'☀️ {jour["condition"]}<br>🌡️ {jour["tmin"]}°C ➝ {jour["tmax"]}°C</div>' 
                            for jour in conditions_jours_2]) if conditions_jours_2 else '<p>Pas de données disponibles</p>'}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)



    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)


    st.markdown("", unsafe_allow_html=True)


            
        
    # show_map = st.button("Afficher la carte des types de climat", key="climat_map_button")

    # def plot_map():
    #     fig, ax = plt.subplots(figsize=(10, 10))

    #     # Tracer la géométrie avec les couleurs de remplissage et de bordure
    #     communes.plot(ax=ax, column='Type', cmap='tab20c', legend=False,
    #                 edgecolor='black', linewidth=0.5)

    #     # Appliquer les couleurs personnalisées aux types
    #     for type_val, color in couleurs.items():
    #         communes[communes['Type'] == type_val].plot(ax=ax, color=color)

    #     # Créer la légende personnalisée avec les bons noms
    #     legend_labels = [Patch(color=color, label=type_labels[type_val]) for type_val, color in couleurs.items()]
    #     ax.legend(handles=legend_labels, bbox_to_anchor=(1, 1), loc="upper left")

    #     # Supprimer les axes
    #     ax.set_axis_off()

    #     # Afficher la carte dans Streamlit
    #     st.pyplot(fig)


    # cols = st.columns([1, 1, 1])

    # # Ajouter un bouton dans Streamlit pour afficher la carte
    # with cols[0]:
    #     if show_map:
    #         plot_map()









# ------------------------------------------------
# ------------- Page Données Loisirs -------------
# ------------------------------------------------

with onglet8:

    def enlever_accents(texte):
            return ''.join(
                c for c in unicodedata.normalize('NFD', texte)
                if unicodedata.category(c) != 'Mn'
            )


    ville_choisie_1_nom = ville_choisie_1.split(' (')[0]
    ville_choisie_1_nom = enlever_accents(ville_choisie_1_nom).replace(' ', '-')
    ville_choisie_1_nom = ville_choisie_1_nom.lower()

    ville_choisie_2_nom = ville_choisie_2.split(' (')[0]
    ville_choisie_2_nom = enlever_accents(ville_choisie_2_nom).replace(' ', '-')
    ville_choisie_2_nom = ville_choisie_2_nom.lower()


    df_loisirs = pd.read_csv("loisirs.csv")

    def decoupage_loisir(df, ville, categorie):
        if categorie != "Hôtels":
            return df[
                (df["Ville"] == ville) &
                (df["catégorie"] == categorie)
            ].iloc[:, :-3].rename(columns={"Label": f"Etablissements culturels ({ville})", "Value": f"Nombre ({ville})"})
        else:
            subset = df[
                (df["Ville"] == ville) &
                (df["catégorie"] == categorie)
            ].iloc[:, :-3].rename(columns={"Label": f"Etablissements culturels ({ville})", "Value": f"Nombre ({ville})"})
            return pd.concat([
                subset[1:2],
                subset[3:4],
                subset[5:]
            ])
        
    def fusionner_comparaison(df_ville1, df_ville2, nom_ville1, nom_ville2, categorie):
        df1 = df_ville1.rename(columns={
            df_ville1.columns[0]: f"{categorie}",
            df_ville1.columns[1]: f"Nombre à {nom_ville1}"
        })

        df2 = df_ville2.rename(columns={
            df_ville2.columns[0]: f"{categorie}",
            df_ville2.columns[1]: f"Nombre à {nom_ville2}"
        })

        return pd.merge(df1, df2, on=f"{categorie}", how="outer")

    df_culture_ville1 = decoupage_loisir(df_loisirs, ville_choisie_1_nom, "Culture")
    df_sport_ville1 = decoupage_loisir(df_loisirs, ville_choisie_1_nom, "Sports")
    df_hotel_ville1 = decoupage_loisir(df_loisirs, ville_choisie_1_nom, "Hôtels")

    df_culture_ville2 = decoupage_loisir(df_loisirs, ville_choisie_2_nom, "Culture")
    df_sport_ville2 = decoupage_loisir(df_loisirs, ville_choisie_2_nom, "Sports")
    df_hotel_ville2 = decoupage_loisir(df_loisirs, ville_choisie_2_nom, "Hôtels")

    df_culture_final = fusionner_comparaison(df_culture_ville1, df_culture_ville2, ville_choisie_1, ville_choisie_2, "Culture")
    df_sport_final = fusionner_comparaison(df_sport_ville1, df_sport_ville2, ville_choisie_1, ville_choisie_2, "Sports")
    df_hotel_final = fusionner_comparaison(df_hotel_ville1, df_hotel_ville2, ville_choisie_1, ville_choisie_2, "Hôtels")

    df_culture_final.index = [""] * len(df_culture_final)
    df_sport_final.index = [""] * len(df_sport_final)
    df_hotel_final.index = [""] * len(df_hotel_final)




    st.markdown("", unsafe_allow_html=True)
    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Tableau Culture :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un descriptif des informations culturelles dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.dataframe(df_culture_final)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Tableau Sport :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un descriptif des informations sportives dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.dataframe(df_sport_final)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Tableau Hôtel :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un descriptif des informations hôtelières dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.dataframe(df_hotel_final)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)













# --------------------------------------------------
# ------------- Page Données Éducation -------------
# --------------------------------------------------

with onglet9:

    df_education = pd.read_csv("education1.csv", sep=";")
    df_ecole = pd.read_csv("ecole.csv", sep=";")

    def decoupage_education(df, ville, categorie):
        if categorie != "Non scolarisés":
            return df[
                (df["Ville"] == ville) &
                (df["type"] == categorie)
            ].iloc[:, :-3].rename(columns={"Label": f"Distribution de la population ({ville})", "Value": f"Nombre ({ville})"})
        else:
            subset = df[
                (df["Ville"] == ville) &
                (df["type"] == categorie)
            ].iloc[:, :-3].rename(columns={"Label": f"Distribution de la population ({ville})", "Value": f"Nombre ({ville})"})
            return subset
        
    def fusionner_comparaison(df_ville1, df_ville2, nom_ville1, nom_ville2, texte, categorie=""):
        df1 = df_ville1.rename(columns={
            df_ville1.columns[0]: f"{categorie}",
            df_ville1.columns[1]: f"{texte} à {nom_ville1}"
        })

        df2 = df_ville2.rename(columns={
            df_ville2.columns[0]: f"{categorie}",
            df_ville2.columns[1]: f"{texte} à {nom_ville2}"
        })

        return pd.merge(df1, df2, on=f"{categorie}", how="outer")

    df_scolarises_ville1 = decoupage_education(df_education, ville_choisie_1_nom, "Scolarisés")
    df_non_scolarises_ville1 = decoupage_education(df_education, ville_choisie_1_nom, "Non scolarisés")

    df_scolarises_ville2 = decoupage_education(df_education, ville_choisie_2_nom, "Scolarisés")
    df_non_scolarises_ville2 = decoupage_education(df_education, ville_choisie_2_nom, "Non scolarisés")

    df_ecole_ville1 = df_ecole[df_ecole["Ville"] == ville_choisie_1_nom]
    df_ecole_ville2 = df_ecole[df_ecole["Ville"] == ville_choisie_2_nom]

    df_scolarises_final = fusionner_comparaison(df_scolarises_ville1, df_scolarises_ville2, ville_choisie_1, ville_choisie_2, "Nombre de personnes scolarisées", "Scolarisés")
    df_scolarises_final.columns = df_scolarises_final.columns.str.strip().str.replace('\u00A0', ' ')
    df_scolarises_final = df_scolarises_final.rename(columns={
        "% de la population scolarisée_x": f"Population scolarisée à {ville_choisie_1} (en %)",
        "% de la population scolarisée_y": f"Population scolarisée à {ville_choisie_2} (en %)"
    })
    df_scolarises_final = df_scolarises_final.drop(columns=["Moyenne des villes_x", "Moyenne des villes_y"])

    df_non_scolarises_final = fusionner_comparaison(df_non_scolarises_ville1, df_non_scolarises_ville2, ville_choisie_1, ville_choisie_2, "Nombre de diplômes", "Niveau de diplôme")
    df_non_scolarises_final.columns = df_non_scolarises_final.columns.str.strip().str.replace('\u00A0', ' ')
    df_non_scolarises_final = df_non_scolarises_final.rename(columns={
        "% de la population scolarisée_x": f"Diplômes à {ville_choisie_1} (en %)",
        "% de la population scolarisée_y": f"Diplômes à {ville_choisie_2} (en %)"
    })
    df_non_scolarises_final = df_non_scolarises_final.drop(columns=["Moyenne des villes_x", "Moyenne des villes_y"])
    
    df_ecole_final = fusionner_comparaison(df_ecole_ville1, df_ecole_ville2, ville_choisie_1, ville_choisie_2, "Nombre d'établissements scolaires", "")
    df_ecole_final = df_ecole_final.drop(columns=["code_insee_x", "code_insee_y", "Ville_x", "Ville_y"])

    df_scolarises_final.index = [""] * len(df_scolarises_final)
    df_non_scolarises_final.index = [""] * len(df_non_scolarises_final)
    df_ecole_final.index = [""] * len(df_ecole_final)






    ordre_scolarises = [
    "2 - 5 ans", "6 - 10 ans", 
    "11 - 14 ans", "15 - 17 ans",
    "18 - 24 ans", "25 - 29 ans",
    "30 ans et plus"
    ]

    df_scolarises_final["Scolarisés"] = pd.Categorical(
        df_scolarises_final["Scolarisés"], 
        categories=ordre_scolarises, 
        ordered=True
    )

    df_scolarises_final = df_scolarises_final.sort_values("Scolarisés")






    ordre_diplomes = [
        "Aucun diplôme",
        "Brevet des collèges",
        "CAP / BEP",
        "Baccalauréat / brevet professionnel",
        "De Bac +2 à Bac +4",
        "Bac +5 et plus"
    ]

    df_non_scolarises_final["Niveau de diplôme"] = pd.Categorical(
        df_non_scolarises_final["Niveau de diplôme"],
        categories=ordre_diplomes,
        ordered=True
    )

    df_non_scolarises_final = df_non_scolarises_final.sort_values("Niveau de diplôme")






    types_etablissements = [
        "Ecoles maternelles",
        "Ecoles élémentaires",
        "Collèges",
        "Lycées généraux",
        "Lycées professionnels",
        "Lycées agricoles",
        "Etablissements avec classes préparatoires aux grandes écoles",
        "Ecoles de formation sanitaire et sociale",
        "Ecoles de commerce, gestion, administration d'entreprises, comptabilité, vente",
        "Unités de formation et de recherche (UFR)",
        "Instituts universitaires (IUP, IUT et IUFM)",
        "Ecoles d'ingénieurs",
        "Etablissements de formation aux métiers du sport",
        "Centres de formation d'apprentis (hors agricoles)",
        "Centres de formation d'apprentis agricoles",
        "Autres écoles d'enseignement supérieur",
        "Autres formations post-bac non universitaire"
    ]

    df_ecole_final = df_ecole_final.rename(columns={df_ecole_final.columns[0]: "Type d'établissement"})

    df_ecole_final["Type d'établissement"] = pd.Categorical(
        df_ecole_final["Type d'établissement"],
        categories=types_etablissements,
        ordered=True
    )

    df_ecole_final = df_ecole_final.sort_values("Type d'établissement")








    st.markdown("", unsafe_allow_html=True)
    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Tableau Scolarisation :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un descriptif des informations de scolarisation dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.dataframe(df_scolarises_final)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Tableau Niveaux de Diplôme :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un descriptif des niveaux de diplôme dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.dataframe(df_non_scolarises_final)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)


    st.markdown("""
    <p style="display: inline-block;">
        <span style="font-size: 18px; font-weight: bold; border-bottom: 1px solid black; padding-bottom: 2px;">
            Tableau Établissements Scolaires :
        </span>
        <span style="font-size: 15px; font-weight: normal; margin-left: 15px;">
            Un descriptif des établissements scolaires dans les villes choisies
        </span>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    st.dataframe(df_ecole_final)
    st.markdown("", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)










# -------------------------------------------------
# ------------ Page Sources et Crédits ------------
# -------------------------------------------------

with onglet10:

    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 10px;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5.5])

    with col1:
        with open("Sources.pdf", "rb") as file:
            st.download_button(
                label="Choix des sources de données 🔎",
                data=file,
                file_name="Sources.pdf",
                mime="application/pdf"
            )

    with col2:
        st.markdown(f"<div style='margin-top: 8px; margin-left: -5px;'>Un rapport présentant les sources utilisées pour l'application, leur origine ainsi que la manière d'extraction</div>", unsafe_allow_html=True)


    st.markdown("<hr style='border: 1px solid #ddd; margin-top: 15px;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center;">
        <p style="display: inline-block;">
            <span style="font-size: 15px; font-weight: normal;">
                Patrick CHEN <a href="https://www.linkedin.com/in/patrick-chen2/" target="_blank">
                    <img src="https://static.vecteezy.com/system/resources/previews/023/986/926/non_2x/linkedin-logo-linkedin-logo-transparent-linkedin-icon-transparent-free-free-png.png" alt="LinkedIn Patrick CHEN" style="width: 20px; height: 20px; vertical-align: middle;">
                </a> <br> 
                Baptiste TIVRIER <a href="https://www.linkedin.com/in/baptiste-tivrier/" target="_blank">
                    <img src="https://static.vecteezy.com/system/resources/previews/023/986/926/non_2x/linkedin-logo-linkedin-logo-transparent-linkedin-icon-transparent-free-free-png.png" alt="LinkedIn Baptiste TIVRIER" style="width: 20px; height: 20px; vertical-align: middle;">
                </a> <br> (© 2025)
            </span>
        </p>
    </div>
""", unsafe_allow_html=True)