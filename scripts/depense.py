#!/usr/bin/env python3
"""Le chapitre Dépense publique, en une trajectoire qu'on peut refaire.

Le chapitre Fiscalité y renvoie six fois — « État moins dépensier », « État
social recentré », « réforme de la dépense sociale », compensation des
collectivités, financement de la santé universelle, « baisse possible du taux
si la croissance et les dépenses le permettent ». Tant qu'il n'existe pas, la
fiscalité porte seule des promesses qu'elle ne peut pas tenir.

Ce script ne cherche pas à démontrer qu'un programme d'économies tient. Il
cherche l'inverse : à établir ce qu'il faudrait pour qu'il tienne, et à dire de
combien les mesures qu'on sait nommer restent en dessous. C'est le seul usage
honnête d'un chiffrage de dépense — un exercice où l'on peut toujours écrire
un nombre plus grand.

    python scripts/depense.py

Montants en milliards d'euros. Ce sont des ORDRES DE GRANDEUR publics arrondis,
à remplacer par les séries officielles datées avant toute publication.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Le point de départ ------------------------------------------------------

PIB = 2_920.0
DEPENSE = 1_670.0
RECETTES = 1_500.0
DETTE = 3_300.0

CROISSANCE_REELLE = 0.012
INFLATION = 0.018
CROISSANCE_NOMINALE = (1 + CROISSANCE_REELLE) * (1 + INFLATION) - 1

TENDANCIEL = 0.032
"""Progression spontanée de la dépense, en valeur : vieillissement, dépense de
santé, et surtout charge de la dette, qui passe d'environ 55 à 75 Md€ sur la
période du seul fait des taux. C'est contre cette pente que se mesure un
effort — et non contre zéro, comme le font les programmes qui annoncent des
économies sans dire par rapport à quoi."""

# --- Où va l'argent ----------------------------------------------------------
# Huit masses plutôt que soixante lignes : un lecteur qui ne sait pas où va
# l'argent ne peut juger aucune proposition d'économie, et une nomenclature
# budgétaire ne le lui apprend pas.

POSTES = [
    ("Retraites", 380.0),
    ("Santé", 250.0),
    ("Fonctionnement des administrations", 250.0),
    ("Autres prestations sociales", 230.0),
    ("Enseignement et recherche", 175.0),
    ("Soutien à l’économie et investissement", 175.0),
    ("Régalien : défense, sécurité, justice, diplomatie", 155.0),
    ("Charge de la dette", 55.0),
]


@dataclass(frozen=True)
class Levier:
    nom: str
    rendement: float      # en Md€, à l'horizon de cinq ans
    solidite: str
    commentaire: str


LEVIERS = [
    Levier("Retraites : le compte notionnel stabilise la dépense", 20.0,
           "portée par un autre chapitre",
           "Le premier poste de dépense publique. Le programme Retraites en "
           "porte le mécanisme ; ce chapitre n'en reprend que l'effet."),
    Levier("Santé : progression de l’objectif de dépense à l’inflation", 25.0,
           "exigeant",
           "C'est la mesure la plus lourde et la moins spectaculaire : ne pas "
           "réduire la dépense de santé, seulement cesser de la laisser "
           "croître deux points au-dessus des prix."),
    Levier("Aides aux entreprises : audit général, suppression par défaut", 20.0,
           "cohérent, difficile",
           "Direct prolongement de la doctrine fiscale — l'État n'a pas à "
           "organiser l'économie. Chaque dispositif a sa filière et son "
           "défenseur : l'exécution sera plus dure que le principe."),
    Levier("Millefeuille territorial : une strate en moins", 10.0,
           "incertain",
           "Les économies de fusion territoriale sont régulièrement annoncées "
           "et rarement constatées. Nous le retenons à un montant prudent."),
    Levier("Effectifs : un départ sur trois non remplacé, hors régalien et "
           "enseignement", 5.0, "solide, lent",
           "Environ vingt mille postes par an sur cinq ans. Le rendement est "
           "modeste et il est certain, ce qui en fait l'inverse des deux "
           "lignes précédentes."),
    Levier("Opérateurs et agences : fusions et suppressions", 5.0, "modeste",
           "Plus d'un millier d'opérateurs. Le gain budgétaire est faible ; "
           "le gain de lisibilité ne l'est pas."),
    Levier("Gestion des prestations : le revenu universel remplace six guichets",
           3.0, "solide",
           "Conséquence mécanique du chapitre Fiscalité : un versement "
           "automatique coûte moins à gérer que six prestations sous "
           "condition."),
]


def trajectoire(regle: float, annees: int = 5) -> list[dict]:
    """La dépense sous une règle de progression, année par année."""
    lignes = []
    depense, tendance, pib, recettes = DEPENSE, DEPENSE, PIB, RECETTES
    for annee in range(1, annees + 1):
        depense *= 1 + regle
        tendance *= 1 + TENDANCIEL
        pib *= 1 + CROISSANCE_NOMINALE
        recettes = RECETTES / PIB * pib      # à prélèvements obligatoires constants
        lignes.append({
            "annee": annee, "depense": depense, "tendance": tendance,
            "pib": pib, "deficit": depense - recettes,
            "part": depense / pib, "effort": tendance - depense,
        })
    return lignes


def afficher(regle: float) -> None:
    print(f"\nRègle : la dépense progresse de {regle:.1%} par an en valeur "
          f"(inflation attendue {INFLATION:.1%})\n")
    print(f"{'année':>6} {'dépense':>9} {'% du PIB':>9} {'déficit':>9} "
          f"{'% du PIB':>9} {'effort cumulé':>14}")
    for l in trajectoire(regle):
        print(f"{l['annee']:>6} {l['depense']:>9.0f} {l['part']:>8.1%} "
              f"{l['deficit']:>9.0f} {l['deficit'] / l['pib']:>8.1%} "
              f"{l['effort']:>14.0f}")


def main() -> None:
    print(f"Point de départ : dépense {DEPENSE:.0f} Md€ "
          f"({DEPENSE / PIB:.1%} du PIB), recettes {RECETTES:.0f} Md€, "
          f"déficit {DEPENSE - RECETTES:.0f} Md€ "
          f"({(DEPENSE - RECETTES) / PIB:.1%}), dette {DETTE / PIB:.0%} du PIB.")

    print("\nOù va l'argent\n")
    for nom, montant in POSTES:
        part = montant / DEPENSE
        barre = "█" * round(part * 60)
        print(f"  {montant:>5.0f} Md€  {part:>5.1%}  {barre} {nom}")
    total = sum(m for _, m in POSTES)
    print(f"\n  Total des postes : {total:.0f} Md€ contre {DEPENSE:.0f} "
          f"({total / DEPENSE - 1:+.1%})")

    for regle in (0.015, 0.020, 0.025):
        afficher(regle)

    print("\nCe que les mesures nommées couvrent\n")
    somme = sum(l.rendement for l in LEVIERS)
    for levier in sorted(LEVIERS, key=lambda l: -l.rendement):
        print(f"  {levier.rendement:>5.0f} Md€  [{levier.solidite:<28}] {levier.nom}")
    print(f"  {somme:>5.0f} Md€  total à l'horizon de cinq ans")
    besoin = trajectoire(0.020)[-1]["effort"]
    print(f"\n  Effort exigé par la règle des 2 % en cinquième année : "
          f"{besoin:.0f} Md€")
    print(f"  Couvert par les mesures nommées : {somme / besoin:.0%}")
    print(f"  Reste à trouver : {besoin - somme:.0f} Md€\n")
    print("  C'est ce dernier nombre qui décide de la sincérité du chapitre.")
    print("  Nous ne savons pas aujourd'hui où il tombera, et nous préférons")
    print("  l'écrire que d'allonger la liste au jugé.")

    print("\nQuand le taux de l'impôt proportionnel peut-il baisser ?\n")
    for regle in (0.015, 0.020, 0.025):
        lignes = trajectoire(regle, 8)
        sous_trois = next((l["annee"] for l in lignes
                           if l["deficit"] / l["pib"] < 0.03), None)
        quand = f"année {sous_trois}" if sous_trois else "pas avant huit ans"
        print(f"  règle à {regle:.1%} : déficit sous 3 % du PIB en {quand}")
    print("\n  La règle du programme : aucune baisse du taux avant que le")
    print("  déficit ne soit durablement sous 3 %. Sur nos propres hypothèses,")
    print("  cela ne se produit pas dans le quinquennat.")


if __name__ == "__main__":
    main()
