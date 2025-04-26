import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_categ_socio_pro(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "produit-tableau-EMP_T1"})

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

    if "Type d'activité" not in df.columns or "2021" not in df.columns or "2015" not in df.columns or "2010" not in df.columns:
        print(f"[⚠️] Données incomplètes dans : {url}")
        return None

    return df.set_index("Type d'activité").T

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

        recherche = get_categ_socio_pro(url)
        if recherche is not None:
            recherche["code_insee"] = code_insee
            recherche["Ville"] = ville
            data_concat.append(recherche)

# Concat final
df_final = pd.concat(data_concat, ignore_index=True)
df_final.to_csv("data_statut_pro.csv", index=False, encoding="utf-8-sig")