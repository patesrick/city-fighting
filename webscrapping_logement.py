import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_logement_2021(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"id": "produit-tableau-LOG_T7"})
    if table is None:
        print(f"[⚠️] Aucun tableau trouvé à l’URL : {url}")
        return None

    rows = table.find_all("tr")
    data = []

    for row in rows:
        cells = row.find_all(["th", "td"])
        row_data = [cell.get_text(strip=True).replace("\xa0", " ") for cell in cells]
        if row_data:
            data.append(row_data)


    for i, ligne in enumerate(data[:3]):
        if i == 0:  # Ajouter les deux chaînes vides uniquement sur la première ligne
            ligne_correcte = ['""', '""'] + [f'"{cell}"' for cell in ligne]
        else:
            ligne_correcte = [f'"{cell}"' for cell in ligne]


    if len(data) < 3:
        print("⚠️ Pas assez de lignes pour construire le DataFrame")
        return None

    header1 = data[0]
    header2 = data[1]

    # Fusionner les deux niveaux d'en-tête
    full_columns = []
    for i in range(len(header2)):
        h1 = header1[i] if i < len(header1) else ""
        h2 = header2[i]
        if h1 and h2:
            full_columns.append(f"{h1} - {h2}")
        else:
            full_columns.append(h1 or h2)

    df = pd.DataFrame(data[2:], columns=full_columns)

    # Garder uniquement les colonnes liées à 2021
    colonnes_2021 = [col for col in df.columns if col == "Nombre" or "Statut" in col]
    df_2021 = df[colonnes_2021].copy()

    return df_2021.set_index("Statut d'occupation").T

# Lire par chunks
chunksize = 50
reader = pd.read_csv("communes-france-2025.csv", dtype={"code_insee": str}, low_memory=False, chunksize=chunksize)

data_concat = []

for chunk_index, df_chunk in enumerate(reader):
    # Supprimer première colonne si elle est inutile
    if df_chunk.columns[0].startswith("Unnamed"):
        df_chunk = df_chunk.drop(df_chunk.columns[0], axis=1)

    # Filtrer les villes > 20k habitants
    filtered_source = df_chunk[df_chunk["population"] >= 20000]

    for i in range(filtered_source.shape[0]):
        code_insee = filtered_source["code_insee"].iloc[i]
        ville = filtered_source["nom_sans_accent"].iloc[i]

        url = f"https://www.insee.fr/fr/statistiques/2011101?geo=COM-{code_insee}"
        print(f"[{chunk_index+1}] étape : {i+1}/{filtered_source.shape[0]} - {ville} ({code_insee})")

        recherche = get_logement_2021(url)
        if recherche is not None:
            recherche["code_insee"] = code_insee
            recherche["Ville"] = ville
            data_concat.append(recherche)

            print("✅ Ligne ajoutée au DataFrame :")
            print(recherche)
            print("------------------------------------------------------------")



# Concat final
df_final = pd.concat(data_concat, ignore_index=True)
df_final.to_csv("data_statut_occupation.csv", index=False, encoding="utf-8-sig")

df = pd.read_csv("data_statut_occupation.csv")

colonnes_a_convertir = [
    "Ensemble",
    "Propriétaire",
    "Locataire",
    "dont d'un logement HLM loué vide",
    "Logé gratuitement"
]

for col in colonnes_a_convertir:
    df[col] = df[col].astype(str).str.replace(r"\s+", "", regex=True).astype(int)

df.to_csv("data_statut_occupation.csv", index=False, encoding="utf-8-sig")