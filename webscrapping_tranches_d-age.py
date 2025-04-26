import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_tranche_age(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "produit-tableau-POP_T0"})

    if table is None:
        print(f"[⚠️] Aucun tableau trouvé à l’URL : {url}")
        return None

    rows = table.find_all("tr")
    data = []

    for row in rows:
        cells = row.find_all(["th", "td"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        if row_data:
            data.append(row_data)

    df = pd.DataFrame(data[1:], columns=data[0])

    if "Âge" not in df.columns or "2021" not in df.columns:
        print(f"[⚠️] Données incomplètes dans : {url}")
        return None

    df_filtered = df[["Âge", "2021"]].copy()
    return df_filtered.set_index("Âge").T

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

        recherche = get_tranche_age(url)
        if recherche is not None:
            recherche["code_insee"] = code_insee
            recherche["Ville"] = ville
            data_concat.append(recherche)

            print("✅ Ligne ajoutée au DataFrame :")
            print(recherche)
            print("------------------------------------------------------------")

# Concat final
df_final = pd.concat(data_concat, ignore_index=True)
df_final.to_csv("data_tranche_d-age.csv", index=False, encoding="utf-8-sig")

df = pd.read_csv("data_tranche_d-age.csv")

colonnes_a_convertir = [
    "Ensemble",
    "0 à 14 ans",
    "15 à 29 ans",
    "30 à 44 ans",
    "45 à 59 ans",
    "60 à 74 ans",
    "75 ans ou plus"
]

for col in colonnes_a_convertir:
    df[col] = df[col].astype(str).str.replace(r"\s+", "", regex=True).astype(int)

df.to_csv("data_tranche_d-age.csv", index=False, encoding="utf-8-sig")