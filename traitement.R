library(dplyr)
library(openxlsx)

cc <- read.csv("data_tranche_d-age.csv", check.names = FALSE)
str(cc)


cc <- cc %>% 
  mutate(`0-14 ans` = round(`0 à 14 ans`/ Ensemble, digits = 4)*100,
         `15-29 ans` = round(`15 à 29 ans`/ Ensemble, digits = 4)*100,
         `30-44 ans` = round(`30 à 44 ans`/ Ensemble, digits = 4)*100,
         `45-59 ans` = round(`45 à 59 ans`/ Ensemble, digits = 4)*100,
         `60-74 ans` = round(`60 à 74 ans`/ Ensemble, digits = 4)*100,
         `75-+ ans` = round(`75 ans ou plus`/ Ensemble, digits = 4)*100)


write.csv(cc, "data_tranche_d-age_pourcentage.csv")






cc <- read.csv("data_sexe.csv", check.names = FALSE)
str(cc)


cc <- cc %>% 
  mutate(`Homme` = round(`Hommes`/ (Hommes + Femmes), digits = 4)*100,
         `Femme` = round(`Femmes`/ (Hommes + Femmes), digits = 4)*100)


write.csv(cc, "data_sexe_pourcentage.csv")




cc <- read.csv("communes-france-2025.csv", check.names = FALSE)
cc <- cc %>% 
  select(-c(1)) %>% 
  filter(population >= 20000)


which(is.na(cc[[38]]) | is.na(cc[[39]]))

cc[34,38] <- "48.8566"
cc[34,39] <- "2.3522"
cc[219,38] <- "45.7640"
cc[219,39] <- "4.8357"
cc[241,38] <- "43.2965"
cc[241,39] <- "5.3698"

write.csv(cc, "communes-france-2025.csv")




cc <- read.csv("communes-france-2025.csv", check.names = FALSE)
cc <- cc %>% 
  select(-c(1)) %>% 
  filter(population >= 20000)

cc2 <- read.csv("data_dvf_2019-2023.csv", sep=";", check.names = FALSE)
cc2$INSEE_COM <- ifelse(nchar(cc2$INSEE_COM) == 4, paste0("0", cc2$INSEE_COM), cc2$INSEE_COM)

cc2 <- cc2[cc2$INSEE_COM %in% unique(cc$code_insee), ]
cc2 <- cc2 %>% 
  mutate(PrixMoyen = round(PrixMoyen, digits = 2),
         Prixm2Moyen = round(Prixm2Moyen, digits = 2),
         SurfaceMoy = round(SurfaceMoy, digits = 2),)

write.csv(cc2, "data_dfv_2019-2023_reduit.csv")









cc <- read.csv("data_piece_moy.csv", sep=",", check.names = FALSE)
cc$INSEE_COM <- ifelse(nchar(cc2$INSEE_COM) == 4, paste0("0", cc2$INSEE_COM), cc2$INSEE_COM)

cc2 <- cc2[cc2$INSEE_COM %in% unique(cc$code_insee), ]
cc2 <- cc2 %>% 
  mutate(PrixMoyen = round(PrixMoyen, digits = 2),
         Prixm2Moyen = round(Prixm2Moyen, digits = 2),
         SurfaceMoy = round(SurfaceMoy, digits = 2),)

write.csv(cc2, "data_dfv_2019-2023_reduit.csv")














cc <- read.csv("data_menage_compositon.csv", sep=",", check.names = FALSE)

colnames(cc)[colnames(cc) == "%"] <- paste0("%", 1:sum(colnames(cc) == "%"))
cc <- cc %>%
  filter(`Type de ménages` %in% c("Ménages d'une personne", "Autres ménages sans famille", "Un couple sans enfant", "Un couple avec enfant(s)", "Une famille monoparentale")) %>% 
  mutate(`Type de ménages` = case_when(
    `Type de ménages` == "Un couple sans enfant" ~ "Couples sans enfant",
    `Type de ménages` == "Un couple avec enfant(s)" ~ "Couples avec enfant(s)",
    `Type de ménages` == "Une famille monoparentale" ~ "Familles monoparentales",
    TRUE ~ `Type de ménages`
  ))

write.csv(cc, "data_menage_composition.csv")






cc <- read.csv("data_statut_occupation.csv", sep=",", check.names = FALSE)
cc <- cc %>% 
  mutate(`Propriétaires` = round(`Propriétaire`/ Ensemble, digits = 4)*100,
         `Locataires` = round(`Locataire`/ Ensemble, digits = 4)*100,
         `Logés gratuitement` = round(`Logé gratuitement` / Ensemble, digits = 4)*100)


write.csv(cc, "data_statut_occupation.csv")






cc <- read.csv("data_superficie_log.csv", sep=",", check.names = FALSE)
cc <- cc %>% 
  mutate(`2` = substr(`2`, 1, nchar(`2`) - 2))

write.csv(cc, "data_superficie_log.csv")




cc <- read.csv("data_statut_conj.csv")
names(cc)[1] <- "Statut"
names(cc)[2] <- "%"

write.csv(cc, "data_statut_conj.csv")






cc <- read.csv("data_superficie_log.csv")
cc <- cc %>% 
  mutate(X0 = case_when(
    X0 == "Résidences principales de moins de 30 m²" ~ "Moins de 30 m²",
    X0 == "Résidences principales de 30 m² à 40 m²" ~ "Entre 30 et 40 m²",
    X0 == "Résidences principales de 40 m² à 60 m²" ~ "Entre 40 et 60 m²",
    X0 == "Résidences principales de 60 m² à 80 m²" ~ "Entre 60 et 80 m²",
    X0 == "Résidences principales de 80 m² à 100 m²" ~ "Entre 80 et 100 m²",
    X0 == "Résidences principales de 100 m² à 120 m²" ~ "Entre 100 et 120 m²",
    X0 == "Résidences principales de 120 m² et plus" ~ "Plus de 120 m²",
    TRUE ~ X0
  ))

write.csv(cc, "data_superficie_log.csv")




cc <- read.csv("data_naissance_deces.csv")
cc <- cc %>% 
  mutate(X = case_when(
    X == "Naissances domiciliées" ~ "Naissances",
    X == "Décès domiciliés" ~ "Décès",
    TRUE ~ X
  ))

write.csv(cc, "data_naissance_deces.csv")





cc <- read.csv("data_date_log.csv", sep=",", check.names = FALSE)
cc <- cc %>% 
  select(-c(1))
cc <- cc %>% 
  mutate(`2` = substr(`2`, 1, nchar(`2`) - 2))
cc <- cc %>% 
  mutate(`0` = case_when(
    `0` == "Résidences principales construites avant 1919" ~ "Avant 1919",
    `0` == "Résidences principales construites de 1919 à 1945" ~ "De 1919 à 1945",
    `0` == "Résidences principales construites de 1946 à 1970" ~ "De 1946 à 1970",
    `0` == "Résidences principales construites de 1971 à 1990" ~ "De 1971 à 1990",
    `0` == "Résidences principales construites de 1991 à 2005" ~ "De 1991 à 2005",
    `0` == "Résidences principales construites après 2005" ~ "Après 2005",
    TRUE ~ `0`
  ))

write.csv(cc, "data_date_log.csv")







cc <- read.csv("climat_saison.csv")
cc <- cc %>% 
  filter(X %in% c("Heures d'ensoleillement", "Hauteur de pluie")) %>% 
  mutate(across(2:5, ~ case_when(
    X == "Heures d'ensolleillement" ~ substr(.x, 1, nchar(.x) - 2),
    TRUE ~ substr(.x, 1, nchar(.x) - 3)
  )))

write.csv(cc, "data_climat_saison.csv")





