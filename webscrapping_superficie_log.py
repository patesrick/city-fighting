import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_nombre_habitants_par_logement(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    div_immobilier = soup.find("div", {"id": "immobilier"})
    if div_immobilier is None:
        print(f"[⚠️] Aucun div avec id='immobilier' trouvé à l’URL : {url}")
        return None

    section_wrappers = div_immobilier.find_all("div", class_="section-wrapper")
    if len(section_wrappers) < 3:
        print("[⚠️] Moins de 3 div.section-wrapper trouvés.")
        return None

    if len(section_wrappers) <= 16:
        print(f"[⚠️] Moins de 17 div.section-wrapper trouvés sur la page : {url}")
        return None

    section_wrapper = section_wrappers[16]

    table = section_wrapper.select_one("table.odTable.odTableAuto")
    if table is None:
        print(f"[⚠️] Aucune table avec class='odTable odTableAuto' trouvée.")
        return None

    # Recherche de la ligne spécifique
    target_rows = []
    target_labels = [
        "Résidences principales de moins de 30 m²",
        "Résidences principales de 30 m² à 40 m²",
        "Résidences principales de 40 m² à 60 m²",
        "Résidences principales de 60 m² à 80 m²",
        "Résidences principales de 80 m² à 100 m²",
        "Résidences principales de 100 m² à 120 m²",
        "Résidences principales de 120 m² et plus"
    ]

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if cells and cells[0].get_text(strip=True) in target_labels:
            extracted_row = [cell.get_text(strip=True) for cell in cells]
            target_rows.append(extracted_row)

    if not target_rows:
        print(f"[⚠️] Aucune ligne correspondant aux tailles de résidences principales trouvée.")
        return None

    # Retourner un DataFrame avec toutes les lignes
    df = pd.DataFrame(target_rows)
    return df




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

        url = f"https://www.linternaute.com/ville/{ville}/ville-{code_insee}/immobilier"
        print(f"[{chunk_index+1}] étape : {i+1}/{filtered_source.shape[0]} - {ville} ({code_insee})")

        recherche = get_nombre_habitants_par_logement(url)
        if recherche is not None:
            recherche["code_insee"] = code_insee
            recherche["Ville"] = ville
            data_concat.append(recherche)

            print("✅ Ligne ajoutée au DataFrame :")
            print(recherche)
            print("------------------------------------------------------------")



# Concat final
df_final = pd.concat(data_concat, ignore_index=True)

df_final.to_csv("data_superficie_log.csv", index=False, encoding="utf-8-sig")

df = pd.read_csv("data_superficie_log.csv")
df.columns = [col.split("(")[0].strip() for col in df.columns]
df = df.loc[:, ~df.columns.str.contains("^Unnamed") & df.columns.notna()]

colonnes_a_convertir = [
    "1"
]

for col in colonnes_a_convertir:
    df[col] = df[col].astype(str).str.replace(r"\s+", "", regex=True).astype(int)

df.to_csv("data_superficie_log.csv", index=False, encoding="utf-8-sig")