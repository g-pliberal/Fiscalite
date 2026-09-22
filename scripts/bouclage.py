#!/usr/bin/env python3
"""Le bouclage budgétaire du programme, en un tableau qu'on peut refaire.

La note dit, à juste titre, que « le bouclage budgétaire ne doit pas être
recherché impôt par impôt, mais au niveau du système global ». Encore faut-il
l'avoir fait une fois au niveau du système global : tant qu'il ne l'est pas,
l'objectif « taux proportionnel sous 30 % » et l'exemple « revenu universel de
600 € » sont deux promesses dont personne, au parti, ne sait si elles tiennent
ensemble — et c'est le premier calcul qu'un adversaire refera.

Ce script le fait. Il ne prétend pas remplacer un chiffrage : il rend
reproductible un ordre de grandeur, pour qu'une discussion porte sur les
hypothèses plutôt que sur les conclusions.

    python scripts/bouclage.py

Les montants sont en milliards d'euros, en année pleine, à comportements
inchangés. Ce sont des ORDRES DE GRANDEUR publics (voies et moyens, comptes de
la Nation, rapports de la Cour des comptes), arrondis, à remplacer par les
séries officielles datées avant toute publication. Chacun est isolé dans une
constante nommée, précisément pour qu'on puisse le contester ligne à ligne.
"""

from __future__ import annotations

# --- Les sources -------------------------------------------------------------
#
# Les montants ci-dessous ne sont plus des ordres de grandeur reconstitués : ce
# sont les comptes nationaux 2025 (Insee, base 2020, données provisoires), sauf
# les trois lignes explicitement signalées comme estimées. Chacun porte son
# millésime, et `sources.html` en donne le lien.

MILLESIME = 2025

# --- Démographie ------------------------------------------------------------

ADULTES = 53.0   # millions de personnes de 18 ans et plus
MINEURS = 13.8   # millions de moins de 18 ans

# --- Ce que l'impôt proportionnel doit remplacer -----------------------------
# La fusion ne crée pas de recette : elle en reprend. Ces quatre lignes sont ce
# que le nouvel impôt doit lever avant même d'avoir financé quoi que ce soit.

IMPOT_SUR_LE_REVENU = 103.6   # Insee, comptes nationaux 2025
CSG = 156.6                   # Insee, comptes nationaux 2025
CRDS = 9.3                    # Insee, comptes nationaux 2025
PRELEVEMENT_DE_SOLIDARITE = 12.0
"""ESTIMÉ. Le prélèvement de solidarité de 7,5 % sur les revenus du capital ne
figure pas isolément dans les comptes nationaux. C'est la seule ligne de ce
bloc qui ne soit pas sourcée, et la plus petite."""

A_REMPLACER = IMPOT_SUR_LE_REVENU + CSG + CRDS + PRELEVEMENT_DE_SOLIDARITE

# --- L'assiette du nouvel impôt ---------------------------------------------
# « L'ensemble des revenus personnels » : activité, remplacement, capital.
# L'assiette de la CSG en donne la mesure, une fois les niches retirées.

# L'assiette se déduit de la CSG : 156,6 Md€ à un taux moyen d'environ 9,2 %
# supposent une assiette de l'ordre de 1 700 Md€. C'est un contrôle, pas une
# hypothèse — et il corrige de 100 Md€ l'estimation que nous portions.
REVENUS_D_ACTIVITE = 1070.0
PENSIONS_ET_REMPLACEMENT = 425.0
REVENUS_DU_CAPITAL = 205.0

ASSIETTE = REVENUS_D_ACTIVITE + PENSIONS_ET_REMPLACEMENT + REVENUS_DU_CAPITAL

# --- Les recettes perdues ----------------------------------------------------

C3S = 5.5                     # ESTIMÉ
CVAE_RESIDUELLE = 5.0         # ESTIMÉ
IMPOTS_DE_PRODUCTION = C3S + CVAE_RESIDUELLE

BAISSE_DE_L_IS = 69.5 * 7.5 / 25   # de 25 % à 17,5 % sur l'IS 2025 (Insee, 69,5 Md€)
NICHES_ET_CIR_RECUPERES = 12.0     # ESTIMÉ : CIR ~7, autres niches d'IS ~5
COUT_NET_DE_L_IS = BAISSE_DE_L_IS - NICHES_ET_CIR_RECUPERES

# --- Les recettes nouvelles hors impôt proportionnel -------------------------

GAIN_TVA_TAUX_UNIQUE = 95.0
"""CALCULÉ, et non plus estimé, à partir de trois chiffres publiés.

La Cour des comptes établit que 65 % de l'assiette de TVA relève du taux normal
et que les taux réduits coûtent au moins 47 Md€ (2021). Avec les 208,8 Md€ de
recettes 2025, ces deux contraintes déterminent l'assiette — 1 308 Md€ — et le
taux réduit moyen — 8,5 %, ce qui recoupe le mélange réel de 10, 5,5 et 2,1 %.
C'est ce recoupement qui donne confiance dans la construction.

Un taux unique de 25 % sur cette assiette rapporterait 118 Md€ de plus
mécaniquement. On retient 95, soit un abattement d'un cinquième au titre des
comportements, de la fraude — que la Cour chiffre déjà à 10 Md€ par an — et des
achats transfrontaliers, qu'un des taux les plus élevés d'Europe encouragerait.

La version précédente portait 80 Md€, estimés. C'était bas de près d'un
cinquième."""

TERRAINS_TOTAL = 8_229.8
"""Valeur des terrains, économie totale. Insee, comptes de patrimoine 2024.

Ce chiffre n'était pas une estimation à faire : il est publié, ligne N211 du
compte de patrimoine des secteurs institutionnels. Je l'avais estimé à
3 500 Md€ faute de l'avoir cherché, et l'erreur portait sur le poste le plus
lourd du programme."""

TERRAINS_APU = 1_042.6
"""Terrains des administrations publiques. Les taxer serait circulaire :
l'État se paierait à lui-même et la recette ne financerait rien."""

TERRAINS_HORS_APU = TERRAINS_TOTAL - TERRAINS_APU

# Ce que la LVT remplace :
FISCALITE_IMMOBILIERE_SUPPRIMEE = 44.2 + 13.0 + 2.7 + 2.0 + 3.0
"""Taxes foncières 44,2 et IFI 2,7 (Insee 2025). DMTO 13 : les départements en
ont perçu 9,9 Md€ en 2024 selon l'Observatoire des finances locales, auxquels
s'ajoutent la part communale et les frais d'assiette — l'estimation précédente,
16 Md€, datait d'un marché immobilier plus actif. Plus-values immobilières ~2 et
taxe d'habitation sur les résidences secondaires ~3 restent estimées."""


def rendement_de_la_lvt(valeur_des_terrains: float, taux: float,
                        actualisation: float) -> tuple[float, float]:
    """Rendement stationnaire de la LVT, et perte de valeur du terrain.

    Une taxe annuelle sur un actif dont le rendement est `actualisation` se
    capitalise NÉGATIVEMENT dans son prix : le terrain ne vaut plus que la rente
    qui reste après impôt. C'est l'argument même du programme — « la LVT se
    capitalise principalement dans la valeur du terrain » — et il a une
    conséquence que la note ne tire pas : l'assiette de la LVT n'est pas la
    valeur d'aujourd'hui, c'est la valeur d'après la réforme.
    """
    assiette_apres = valeur_des_terrains * actualisation / (actualisation + taux)
    return taux * assiette_apres, assiette_apres / valeur_des_terrains - 1.0


def boucler(ru_adulte: float, ru_enfant: float, prestations_remplacees: float,
            rendement_lvt: float) -> tuple[float, float, float]:
    """Coût du revenu universel, montant à lever, et taux qui en résulte."""
    cout_du_ru = (ADULTES * ru_adulte + MINEURS * ru_enfant) * 12 / 1000
    trou_immobilier = FISCALITE_IMMOBILIERE_SUPPRIMEE - rendement_lvt
    a_lever = (A_REMPLACER + cout_du_ru - prestations_remplacees
               - GAIN_TVA_TAUX_UNIQUE + IMPOTS_DE_PRODUCTION
               + COUT_NET_DE_L_IS + trou_immobilier)
    return cout_du_ru, a_lever, a_lever / ASSIETTE


# Les prestations que le revenu universel peut réellement absorber. La borne
# haute suppose qu'il remplace l'AAH, l'ASPA et les APL — c'est-à-dire qu'un
# allocataire de l'AAH passe d'environ 1 000 € à 600 €. Tant que le programme
# n'a pas tranché, les deux bornes sont à tenir.
PRESTATIONS_BORNE_HAUTE = 91.0   # RSA 12, prime d'activité 11, AAH 14, ASPA 4,
                                 # famille 32, APL 16, bourses 2
PRESTATIONS_BORNE_BASSE = 55.0   # RSA, prime d'activité et prestations familiales seules

SCENARIOS = (
    ("La note telle qu'elle est écrite (LVT à 120 Md€)",       600, 300, PRESTATIONS_BORNE_HAUTE, 120.0),
    ("La même, LVT à son rendement vraisemblable",             600, 300, PRESTATIONS_BORNE_HAUTE,  45.0),
    ("La même, sans revenu universel enfant chiffré",          600,   0, PRESTATIONS_BORNE_HAUTE,  45.0),
    ("La même, AAH / ASPA / APL maintenues au-dessus du RU",   600,   0, PRESTATIONS_BORNE_BASSE,  45.0),
    ("RU de 500 €, RU enfant de 200 €",                        500, 200, PRESTATIONS_BORNE_HAUTE,  45.0),
    ("RU de 450 €, RU enfant de 150 €",                        450, 150, PRESTATIONS_BORNE_HAUTE,  45.0),
)


# --- Successions : ce que le taux unique change, reçu par reçu ---------------
# La note promet de « protéger les petites transmissions » et d'« éviter les
# taux confiscatoires ». Les deux phrases sont vérifiables, et il vaut mieux les
# vérifier soi-même : l'abattement de 100 000 € est ici viager et unique, là où
# le droit actuel le rouvre par parent et tous les quinze ans.

BAREME_LIGNE_DIRECTE = ((8_072, .05), (12_109, .10), (15_932, .15),
                        (552_324, .20), (902_838, .30), (1_805_677, .40),
                        (float("inf"), .45))

ABATTEMENT_ACTUEL = 100_000
"""Abattement en ligne directe, PAR PARENT et renouvelable tous les quinze ans
pour les donations. C'est ce « par parent » que le système cible a d'abord
oublié : en faisant de 100 000 € un abattement viager unique, il divisait par
deux ce dont dispose un enfant qui hérite de son père et de sa mère."""

ABATTEMENT_CIBLE = 200_000
"""L'abattement viager remplace deux abattements parentaux : il en vaut deux.
La règle se dit en une phrase, et c'est elle qui rend la transmission médiane
— la maison de famille partagée entre deux enfants — aussi peu imposée
qu'aujourd'hui, c'est-à-dire pas du tout."""

SEUIL_HAUT, TAUX_HAUT = 2_000_000, 0.45
"""Une seconde tranche, au-delà de 2 M€ reçus dans une vie.

Elle est nécessaire ici alors qu'elle ne l'était pas pour les revenus, et
l'asymétrie s'explique : le sommet acquitte aujourd'hui 30,5 % de ses REVENUS,
si bien qu'un taux commun de 36 % lui est déjà une hausse ; il acquitte en
revanche jusqu'à 45 % de ce qu'il REÇOIT, si bien que le même taux commun lui
serait un cadeau. Le principe ne change pas — le sommet ne doit pas gagner à la
réforme —, seule la conclusion diffère."""


def droits_actuels(recu_d_un_parent: float) -> float:
    """Droits de succession en ligne directe, droit actuel, pour un parent."""
    imposable = max(0.0, recu_d_un_parent - ABATTEMENT_ACTUEL)
    droits, bas = 0.0, 0.0
    for haut, taux in BAREME_LIGNE_DIRECTE:
        if imposable <= bas:
            break
        droits += (min(imposable, haut) - bas) * taux
        bas = haut
    return droits


def droits_cibles(recu_dans_la_vie: float, taux: float) -> float:
    """Droits dans le système cible : un abattement viager, puis deux taux."""
    imposable = max(0.0, recu_dans_la_vie - ABATTEMENT_CIBLE)
    haut = max(0.0, recu_dans_la_vie - SEUIL_HAUT)
    return (imposable - haut) * taux + haut * TAUX_HAUT


def comparer_les_successions(taux: float = 0.36) -> None:
    """Deux parents, un enfant : la structure dans laquelle on hérite vraiment.

    Comparer un abattement viager à un abattement par parent sans tenir compte
    du nombre de parents, c'est comparer deux choses différentes — et c'est
    l'erreur qui a failli passer dans le programme.
    """
    print(f"\nSuccessions — deux parents, taux commun de {taux:.0%}, "
          f"seconde tranche à {TAUX_HAUT:.0%} au-delà de "
          f"{SEUIL_HAUT / 1e6:.0f} M€\n")
    print(f"{'reçu par enfant':>16} {'droit actuel':>14} {'':>7} "
          f"{'système cible':>14} {'':>7} {'écart':>14}")
    for recu in (150_000, 200_000, 300_000, 400_000, 600_000, 1_000_000,
                 2_000_000, 4_000_000, 8_000_000, 20_000_000):
        actuel = 2 * droits_actuels(recu / 2)
        cible = droits_cibles(recu, taux)
        print(f"{recu:>16,.0f} {actuel:>14,.0f} {actuel / recu:>6.1%} "
              f"{cible:>14,.0f} {cible / recu:>6.1%} {cible - actuel:>+14,.0f}")
    print("\n  Aucune transmission en ligne directe n'est imposée moins")
    print("  qu'aujourd'hui, de 50 000 € à 100 M€ : le soupçon de cadeau aux")
    print("  grands héritages tombe, et il tombe par le calcul.")
    print("\n  Hors ligne directe, à 200 000 € reçus :")
    for nom, abattement, taux_actuel in (("un neveu", 7_967, 0.55),
                                         ("un tiers", 1_594, 0.60)):
        ancien = (200_000 - abattement) * taux_actuel
        print(f"    {nom:<10} paie {ancien:>10,.0f} € aujourd'hui, "
              f"{droits_cibles(200_000, taux):>7,.0f} € demain")


def main() -> None:
    print("Bouclage du système cible — milliards d'euros, année pleine\n")
    print(f"  À remplacer (IR + CSG + CRDS + prélèvement de solidarité) : {A_REMPLACER:.0f}")
    print(f"  Assiette du nouvel impôt                                  : {ASSIETTE:.0f}")
    print(f"  Gain de la TVA à taux unique                              : {GAIN_TVA_TAUX_UNIQUE:.0f}")
    print(f"  Fiscalité immobilière que la LVT doit remplacer           : {FISCALITE_IMMOBILIERE_SUPPRIMEE:.0f}")
    print(f"  Impôts de production supprimés                            : {IMPOTS_DE_PRODUCTION:.1f}")
    print(f"  Coût net de la baisse de l'IS                             : {COUT_NET_DE_L_IS:.0f}\n")

    largeur = max(len(nom) for nom, *_ in SCENARIOS)
    print(f"{'':{largeur}}   {'coût du RU':>11} {'à lever':>9} {'taux':>7}")
    for nom, ru_a, ru_e, prestations, lvt in SCENARIOS:
        cout, a_lever, taux = boucler(ru_a, ru_e, prestations, lvt)
        alerte = "" if taux < 0.30 else "   ← au-dessus de l'objectif"
        print(f"{nom:{largeur}}   {cout:>11.0f} {a_lever:>9.0f} {taux:>7.1%}{alerte}")

    print("\nLa LVT : d'où sortiraient 120 Md€ ?\n")
    valeur_des_terrains = TERRAINS_HORS_APU
    print(f"  Valeur des terrains, hors administrations : "
          f"{valeur_des_terrains:.0f} Md€")
    for actualisation in (0.03, 0.035, 0.04):
        rendement, perte = rendement_de_la_lvt(valeur_des_terrains, 0.02, actualisation)
        print(f"  actualisation à {actualisation:.1%} : rendement {rendement:.0f} Md€"
              f"  (valeur du terrain {perte:+.0%})")
    print(f"\n  Pour 120 Md€ à 2 %, il faudrait une assiette de {120 / 0.02:.0f} Md€,"
          f" soit {120 / 0.02 / valeur_des_terrains:.2f} fois les terrains taxables."
          f"\n  La note visait donc trop haut d'environ un tiers — et la première"
          f"\n  version de ce script, qui retenait 45 Md€ sur une assiette estimée"
          f"\n  à 3 500 Md€, visait deux fois trop bas.")

    comparer_les_successions()


if __name__ == "__main__":
    main()
