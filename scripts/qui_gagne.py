#!/usr/bin/env python3
"""Qui gagne, qui perd : la table par décile et les dix cas types.

C'est le premier document qu'on réclamera au programme, et le seul qui réponde
à l'accusation qui vient toujours — « votre réforme est un cadeau aux plus
aisés ». Tant qu'il n'existe pas, la réponse appartient à celui qui accuse.

Le modèle additionne les cinq canaux par lesquels la réforme atteint un ménage,
là où le simulateur du site n'en montre qu'un :

    impôt direct   IR + CSG + CRDS        ->  impôt proportionnel
    transferts     prestations actuelles  ->  revenu universel
    consommation   TVA actuelle           ->  TVA à 25 %
    logement       taxe foncière + DMTO   ->  Land Value Tax
    énergie        fiscalité carbone      ->  prix plancher + dividende

CE QUE CE SCRIPT N'EST PAS. Ce n'est pas une microsimulation : il n'y a pas
d'enquête Revenus fiscaux et sociaux derrière, seulement dix ménages moyens
calibrés sur des ordres de grandeur publics. Sa validité tient à un contrôle,
imprimé à la fin : réagrégé, il doit retrouver les masses nationales. Il les
retrouve à 5 % près. C'est assez pour arbitrer, pas pour publier — la table
publiée devra être refaite sur données individuelles.

    python scripts/qui_gagne.py

Convention : le panier de consommation est tenu constant en volume, et l'on
mesure la variation de pouvoir d'achat. Les montants sont annuels, en euros
courants, à comportements inchangés.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Les paramètres de la réforme -------------------------------------------
# Les deux jeux cohérents identifiés par `scripts/bouclage.py` : le revenu
# universel de la note avec le taux qui le finance vraiment, et le taux annoncé
# avec le revenu universel qu'il permet.

@dataclass(frozen=True)
class Reforme:
    nom: str
    taux: float          # impôt proportionnel sur les revenus personnels
    ru_adulte: float     # euros par mois
    ru_enfant: float     # euros par mois
    tva: float = 0.25
    lvt: float = 0.02
    carbone: float = 200.0   # euros par tonne, prix plancher cible
    seuil_haut: float = float("inf")
    taux_haut: float = 0.0
    """Une tranche supérieure unique. Elle coûte au système cible sa pureté
    doctrinale et lui rend sa défendabilité : sans elle, le sommet de la
    distribution encaisse à la fois la baisse du taux moyen et le revenu
    universel, et la table par décile devient l'arme de l'adversaire."""
    supplements: bool = False
    """Le supplément handicap, l'aide au logement en zone tendue et l'allocation
    d'autonomie survivent-ils au revenu universel ? C'est la ligne qui décide du
    sort des deux premiers déciles."""


CIBLE = Reforme("Le programme tel qu'il est écrit — RU 600 € / taux 34 %", 0.34, 600, 300)
VARIANTE = Reforme("La variante « sous 30 % » — RU 480 € / taux 30 %", 0.30, 480, 240)
CORRIGEE = Reforme("Le programme corrigé — RU 600 €, taux 34 %, tranche à 45 %, suppléments maintenus",
                   0.34, 600, 300, seuil_haut=250_000, taux_haut=0.45, supplements=True)

PRIX_CARBONE_ACTUEL = 90.0
"""Prix implicite moyen du carbone sur les usages des ménages aujourd'hui :
élevé sur le carburant routier, faible sur le gaz, nul sur le fioul agricole.
Seul l'écart avec la cible est un coût nouveau."""

ACTUALISATION = 0.035
"""Rendement attendu du foncier. Il fixe de combien la LVT se capitalise
négativement dans le prix du terrain — et donc quelle est son assiette une fois
la réforme faite."""

DECOTE_DU_TERRAIN = ACTUALISATION / (ACTUALISATION + 0.02)   # ~0,64

TAUX_TAXE_FONCIERE = 0.012
"""Taxe foncière des ménages, exprimée en part de la valeur du seul terrain.
Calibré pour retrouver les ~30 Md€ que les ménages acquittent."""

TAUX_DMTO = 0.0056
"""DMTO annualisés : ~2,6 % de chance de déménager dans l'année, ~5,8 % de
droits, sur un bien dont le terrain est la moitié. Annualiser est le seul moyen
de faire figurer dans une table annuelle un impôt qu'on paie tous les dix ans —
et c'est aussi ce qui en cache la brutalité pour celui qui déménage."""


# --- Le système actuel, pour les cas types -----------------------------------
# Les déciles portent des taux effectifs moyens, calibrés sur les masses. Un cas
# type, lui, sera vérifié au centime par celui qui voudra le démentir : ses taux
# se calculent depuis le barème, pas depuis une moyenne.

BAREME_IR = ((11_294, .00), (28_797, .11), (82_341, .30), (177_106, .41),
             (float("inf"), .45))
"""Barème de l'impôt sur le revenu, par part. À redater à chaque loi de finances."""

ABATTEMENT_SALAIRE = 0.10      # plafonné à 14 171 €
ABATTEMENT_PENSION = 0.10      # plafonné à 4 321 €
REDUCTIONS_ET_CREDITS = 0.20   # écart moyen entre impôt brut et impôt net


def impot_sur_le_revenu(salaire: float, pension: float, capital: float,
                        parts: float) -> float:
    """IR dû aujourd'hui, décote comprise, capital au prélèvement forfaitaire.

    Le capital n'entre pas au barème : il supporte les 12,8 % d'impôt du
    prélèvement forfaitaire unique, les 17,2 % de prélèvements sociaux étant
    comptés avec la CSG. C'est ce qui explique qu'un revenu du capital soit
    aujourd'hui moins imposé qu'un salaire de même montant — et donc qu'un taux
    unique à 34 % représente, pour le haut de la distribution, une hausse.
    """
    net = (salaire - min(salaire * ABATTEMENT_SALAIRE, 14_171)
           + pension - min(pension * ABATTEMENT_PENSION, 4_321))
    par_part = max(0.0, net) / parts
    impot, bas = 0.0, 0.0
    for haut, taux in BAREME_IR:
        if par_part <= bas:
            break
        impot += (min(par_part, haut) - bas) * taux
        bas = haut
    impot *= parts
    # Décote : elle efface l'impôt des foyers modestes, et c'est elle qui rend
    # si coûteux, pour eux, le passage à un taux proportionnel dès le premier euro.
    plafond = 1_929 if parts >= 2 else 1_166
    if impot < plafond:
        impot = max(0.0, impot - (plafond - 0.4525 * impot))
    # Le barème donne l'impôt brut ; ce qu'un ménage acquitte est l'impôt net
    # des réductions et crédits — emploi à domicile, garde d'enfants, dons,
    # investissement locatif —, soit une vingtaine de milliards concentrés dans
    # le haut de la distribution. Les ignorer surestimerait l'impôt payé
    # aujourd'hui, donc le gain apparent de la réforme pour ceux qui en
    # bénéficient le plus. L'abattement forfaitaire retenu ici est grossier ; il
    # a le mérite d'aller dans le sens qui ne flatte pas le programme.
    return impot * (1 - REDUCTIONS_ET_CREDITS) + capital * 0.128


def csg_crds(salaire: float, pension: float, capital: float,
             pension_reduite: bool = False) -> float:
    """CSG, CRDS et prélèvements sociaux acquittés aujourd'hui."""
    taux_pension = 0.041 if pension_reduite else 0.092
    return (salaire * 0.9825 * 0.097 + pension * taux_pension
            + capital * 0.172)


def taux_actuels(salaire: float, pension: float, capital: float, parts: float,
                 pension_reduite: bool = False) -> tuple[float, float]:
    """Les deux taux effectifs que le moteur attend, dérivés du barème."""
    revenu = salaire + pension + capital
    if revenu <= 0:
        return 0.0, 0.0
    return (csg_crds(salaire, pension, capital, pension_reduite) / revenu,
            impot_sur_le_revenu(salaire, pension, capital, parts) / revenu)


# --- Le ménage ---------------------------------------------------------------

@dataclass
class Menage:
    nom: str
    adultes: float
    enfants: float
    revenu: float                 # revenus personnels bruts : activité, pension, capital
    prestations: float            # RSA, prime d'activité, prestations familiales, APL, AAH...
    taux_csg: float               # CSG + CRDS + prélèvements sociaux, taux effectif actuel
    taux_ir: float                # impôt sur le revenu, taux effectif actuel
    part_taxable: float           # part de la dépense soumise à TVA (le loyer, la santé, l'école ne le sont pas)
    taux_tva_actuel: float        # taux moyen de TVA supporté, en % HT
    epargne: float                # part du revenu disponible non consommée
    terrain: float = 0.0          # valeur du terrain détenu, AVANT réforme
    co2: float = 0.0              # tonnes émises directement dans l'année
    ifi: float = 0.0
    """Impôt sur la fortune immobilière acquitté aujourd'hui. Nul partout sauf
    au sommet — et c'est précisément pour cela qu'il faut le faire figurer."""
    prestations_maintenues: float = 0.0
    """Ce que le revenu universel ne remplace pas : supplément handicap, aide au
    logement en zone tendue, allocation d'autonomie. Tant que le programme ne
    tranche pas, c'est la ligne qui décide du sort de ses cas les plus exposés."""

    # --- système actuel ---
    def impot_direct_actuel(self) -> float:
        return self.revenu * (self.taux_csg + self.taux_ir)

    def disponible_actuel(self) -> float:
        return self.revenu - self.impot_direct_actuel() + self.prestations

    def consommation_ttc(self) -> float:
        return self.disponible_actuel() * (1 - self.epargne)

    def depense_taxable_ttc(self) -> float:
        """Le loyer, la santé, l'école et les services financiers ne portent pas
        de TVA. Les ignorer surestimerait le choc sur les premiers déciles, qui
        consacrent au logement la part la plus lourde de leur budget."""
        return self.consommation_ttc() * self.part_taxable

    def tva_actuelle(self) -> float:
        taux = self.taux_tva_actuel
        return self.depense_taxable_ttc() * taux / (1 + taux)

    def consommation_ht(self) -> float:
        """Le panier taxable, hors taxe : c'est lui qu'on tient constant d'un
        système à l'autre, faute de quoi on compare deux niveaux de vie."""
        return self.depense_taxable_ttc() / (1 + self.taux_tva_actuel)

    def foncier_actuel(self) -> float:
        return self.terrain * (TAUX_TAXE_FONCIERE + TAUX_DMTO) + self.ifi

    def carbone_actuel(self) -> float:
        return self.co2 * PRIX_CARBONE_ACTUEL

    # --- système cible ---
    def impot_direct_cible(self, r: Reforme) -> float:
        haut = max(0.0, self.revenu - r.seuil_haut)
        return (self.revenu - haut) * r.taux + haut * r.taux_haut

    def revenu_universel(self, r: Reforme) -> float:
        return (self.adultes * r.ru_adulte + self.enfants * r.ru_enfant) * 12

    def tva_cible(self, r: Reforme) -> float:
        return self.consommation_ht() * r.tva

    def lvt(self, r: Reforme) -> float:
        return self.terrain * DECOTE_DU_TERRAIN * r.lvt

    def carbone_cible(self, r: Reforme) -> float:
        return self.co2 * r.carbone

    def perte_en_capital(self) -> float:
        """Ce que le ménage perd sur la valeur de son terrain. Ce n'est pas un
        flux, et cela ne figure donc pas dans le solde — mais c'est ce qu'il
        verra, et ce qu'on lui montrera."""
        return -self.terrain * (1 - DECOTE_DU_TERRAIN)

    # --- le solde, canal par canal ---
    def canaux(self, r: Reforme, dividende_par_adulte: float) -> dict[str, float]:
        return {
            "impôt direct": self.impot_direct_actuel() - self.impot_direct_cible(r),
            "transferts": (self.revenu_universel(r)
                           + (self.prestations_maintenues if r.supplements else 0.0)
                           - self.prestations),
            "TVA": self.tva_actuelle() - self.tva_cible(r),
            "logement": self.foncier_actuel() - self.lvt(r),
            "carbone": (self.adultes * dividende_par_adulte
                        - (self.carbone_cible(r) - self.carbone_actuel())),
        }

    def solde(self, r: Reforme, dividende_par_adulte: float) -> float:
        return sum(self.canaux(r, dividende_par_adulte).values())



def menage_type(nom: str, adultes: float, enfants: float, *, salaire: float = 0.0,
                pension: float = 0.0, capital: float = 0.0, parts: float,
                prestations: float = 0.0, part_taxable: float, taux_tva: float,
                epargne: float, terrain: float = 0.0, co2: float = 0.0,
                ifi: float = 0.0, prestations_maintenues: float = 0.0) -> Menage:
    """Un ménage décrit par ce qu'il gagne, pas par des taux effectifs posés.

    C'est la différence entre un cas type qu'on peut vérifier et un cas type
    qu'on peut contester : les deux taux ci-dessous sortent du barème en vigueur,
    ligne par ligne, et se refont à la main."""
    pension_reduite = pension > 0 and salaire == 0 and pension < 24_000
    csg, ir = taux_actuels(salaire, pension, capital, parts, pension_reduite)
    return Menage(nom, adultes, enfants, salaire + pension + capital, prestations,
                  csg, ir, part_taxable, taux_tva, epargne, terrain, co2, ifi,
                  prestations_maintenues)


# --- Les dix déciles ---------------------------------------------------------
# Rangés par niveau de vie. Les profils sont calibrés pour retrouver, réagrégés,
# les masses nationales : contrôle imprimé en fin de sortie.

MENAGES_PAR_DECILE = 30.9e6 / 10

DECILES = [
    #          ad   enf   revenu  prest   csg    ir   taxable  tva  éparg  terrain   co2
    Menage("D1",  1.40, 0.45,  11_000, 9_500, .080, .000, .76, .155, -0.12,  11_000, 4.0, prestations_maintenues=3_000),
    Menage("D2",  1.45, 0.48,  18_000, 7_000, .080, .000, .78, .157, -0.07,  19_500, 4.5, prestations_maintenues=2_200),
    Menage("D3",  1.55, 0.47,  24_000, 5_000, .097, .000, .79, .160, -0.03,  29_500, 5.0, prestations_maintenues=1_500),
    Menage("D4",  1.60, 0.46,  30_000, 3_200, .097, .002, .80, .163,  0.00,  40_500, 5.5, prestations_maintenues=900),
    Menage("D5",  1.70, 0.46,  36_000, 2_000, .097, .005, .81, .166,  0.03,  52_000, 6.0, prestations_maintenues=550),
    Menage("D6",  1.75, 0.45,  43_000, 1_200, .097, .010, .82, .169,  0.06,  64_500, 6.5, prestations_maintenues=320),
    Menage("D7",  1.80, 0.44,  51_000,   700, .097, .018, .83, .172,  0.09,  80_500, 7.0, prestations_maintenues=180),
    Menage("D8",  1.85, 0.44,  62_000,   400, .097, .030, .84, .175,  0.13, 102_000, 7.5, prestations_maintenues=100),
    Menage("D9",  1.90, 0.43,  80_000,   200, .100, .050, .85, .178,  0.18, 138_500, 8.5, prestations_maintenues=50),
    Menage("D10", 2.00, 0.40, 163_000,   100, .110, .125, .87, .182,  0.28, 274_000, 10.5,
           ifi=650, prestations_maintenues=25),
]
# Le terrain porté par un décile est déjà pondéré par le taux de propriétaires
# (de 25 % en D1 à 85 % en D10) : c'est une moyenne de décile, pas le patrimoine
# d'un propriétaire. Un propriétaire de D1 paie quatre fois la ligne « logement ».

SOMMET = [
    menage_type("D10 hors 1 %", 2.00, 0.40, salaire=100_000, capital=28_000, parts=2.3,
                prestations=100, part_taxable=.74, taux_tva=.182, epargne=0.29,
                terrain=235_000, co2=10.0, prestations_maintenues=25),
    menage_type("Top 1 %", 2.05, 0.40, salaire=250_000, capital=170_000, parts=2.0,
                part_taxable=.76, taux_tva=.185, epargne=0.45,
                terrain=700_000, co2=13.0, ifi=3_200),
    menage_type("Top 0,1 %", 2.10, 0.35, salaire=300_000, capital=1_200_000, parts=2.0,
                part_taxable=.78, taux_tva=.185, epargne=0.70,
                terrain=2_400_000, co2=18.0, ifi=32_000),
]
"""Le décile ne suffit pas : l'attaque portera sur le centile, et la réponse
n'est pas la même. Le taux moyen d'imposition du haut de la distribution est
aujourd'hui très au-dessus de la moyenne du décile — et le revenu du sommet
est largement du capital, déjà imposé au prélèvement forfaitaire de 30 %."""


def dividende_carbone(r: Reforme) -> float:
    """Recette carbone des ménages, rendue par tête d'adulte. Ne compte que les
    émissions directes des ménages : le dividende réel, qui inclurait la recette
    industrielle, serait plus élevé. L'hypothèse joue donc contre le programme."""
    recette = sum((m.carbone_cible(r) - m.carbone_actuel()) * MENAGES_PAR_DECILE
                  for m in DECILES)
    adultes = sum(m.adultes * MENAGES_PAR_DECILE for m in DECILES)
    return recette / adultes


def table_par_decile(r: Reforme) -> None:
    dividende = dividende_carbone(r)
    print(f"\n{r.nom} — variation annuelle du revenu disponible, en euros\n")
    entetes = ("impôt", "transf.", "TVA", "logement", "carbone", "SOLDE", "% dispo")
    print(f"{'':>4} {'revenu':>9} {'dispo act.':>11} " + " ".join(f"{e:>9}" for e in entetes))
    for m in DECILES:
        c = m.canaux(r, dividende)
        s = sum(c.values())
        print(f"{m.nom:>4} {m.revenu:>9,.0f} {m.disponible_actuel():>11,.0f} "
              f"{c['impôt direct']:>+9,.0f} {c['transferts']:>+9,.0f} {c['TVA']:>+9,.0f} "
              f"{c['logement']:>+9,.0f} {c['carbone']:>+9,.0f} {s:>+9,.0f} "
              f"{s / m.disponible_actuel():>+8.1%}")
    print(f"{'':>4} {'':>9} {'':>11} " + " ".join("-" * 9 for _ in range(7)))
    for m in SOMMET:
        c = m.canaux(r, dividende)
        s = sum(c.values())
        print(f"{m.nom:>13} {m.revenu:>9,.0f}".rjust(0)[:0] +
              f"{m.nom:<14}{m.revenu:>10,.0f} {m.disponible_actuel():>11,.0f} "
              f"{c['impôt direct']:>+9,.0f} {c['transferts']:>+9,.0f} {c['TVA']:>+9,.0f} "
              f"{c['logement']:>+9,.0f} {c['carbone']:>+9,.0f} {s:>+9,.0f} "
              f"{s / m.disponible_actuel():>+8.1%}")
    cout = -sum(m.solde(r, dividende) for m in DECILES) * MENAGES_PAR_DECILE / 1e9
    print(f"\n  Solde agrégé sur les ménages : {cout:+,.0f} Md€"
          f" ({'les ménages paient davantage' if cout > 0 else 'coût budgétaire supplémentaire'}).")
    print(f"  Pour mémoire, le système cible fait porter aux ménages les ~17 Md€"
          f" d'impôts de production et d'IS supprimés, et le manque de la LVT.")
    print(f"  Dividende carbone : {dividende:,.0f} € par adulte et par an.")
    print(f"  Perte de valeur du terrain (hors solde, une fois) : "
          f"D1 {DECILES[0].perte_en_capital():,.0f} €, "
          f"D5 {DECILES[4].perte_en_capital():,.0f} €, "
          f"D10 {DECILES[9].perte_en_capital():,.0f} €.")


# --- Les dix cas types -------------------------------------------------------
# Ce sont les ménages qu'on interviewera. Ils ne sont pas choisis pour flatter
# le programme : quatre d'entre eux y perdent, et c'est pour eux que le
# programme doit avoir une réponse écrite avant qu'on la lui demande.

@dataclass
class Cas:
    menage: Menage
    commentaire: str
    note: str = ""
    capital: bool = False   # faut-il afficher l'effet patrimonial ?


CAS_TYPES = [
    Cas(menage_type("Couple, 2 enfants, deux SMIC", 2, 2, salaire=42_000, parts=3,
                    prestations=4_200, part_taxable=.67, taux_tva=.164, epargne=0.02,
                    terrain=48_000, co2=6.5, prestations_maintenues=1_200),
        "Locataires en ville moyenne. Le revenu universel enfant décide de tout."),

    Cas(menage_type("Retraité seul, 1 400 €/mois", 1, 0, pension=16_800, parts=1,
                    part_taxable=.70, taux_tva=.166, epargne=0.05,
                    terrain=64_000, co2=5.0),
        "Propriétaire sans emprunt, consomme presque tout ce qu'il perçoit.",
        capital=True),

    Cas(menage_type("Allocataire de l'AAH", 1, 0, parts=1, prestations=12_000,
                    part_taxable=.58, taux_tva=.155, epargne=0.00, co2=3.0,
                    prestations_maintenues=4_800),
        "Le cas qui décide à lui seul de la crédibilité sociale du programme.",
        note="sans supplément handicap, il perd 4 800 € : c'est la ligne à trancher"),

    Cas(menage_type("Propriétaire âgé à Paris, faible revenu", 1, 0, pension=19_000,
                    parts=1, part_taxable=.70, taux_tva=.166, epargne=0.02,
                    terrain=450_000, co2=3.5),
        "Riche en foncier, pauvre en revenu : le ménage que la LVT fabrique.",
        capital=True),

    Cas(menage_type("Célibataire au SMIC, zone tendue", 1, 0, salaire=21_000, parts=1,
                    prestations=3_600, part_taxable=.55, taux_tva=.160, epargne=0.00,
                    co2=3.0, prestations_maintenues=2_400),
        "Locataire. Un adulte seul ne touche qu'un revenu universel.",
        note="APL de zone tendue maintenue dans le scénario corrigé"),

    Cas(menage_type("Agriculteur propriétaire de ses terres", 2, 1, salaire=32_000,
                    parts=2.5, prestations=1_500, part_taxable=.68, taux_tva=.164,
                    epargne=0.05, terrain=400_000, co2=14.0, prestations_maintenues=450),
        "80 hectares. Le foncier professionnel entre dans l'assiette de la LVT.",
        capital=True),

    Cas(menage_type("Ménage rural, gaz et deux voitures", 2, 2, salaire=46_000, parts=3,
                    prestations=2_400, part_taxable=.72, taux_tva=.168, epargne=0.06,
                    terrain=75_000, co2=13.0, prestations_maintenues=700),
        "Le ménage de 2018. C'est sur lui que se juge le dividende carbone.",
        capital=True),

    Cas(menage_type("Cadre célibataire, 80 000 €", 1, 0, salaire=80_000, parts=1,
                    part_taxable=.74, taux_tva=.178, epargne=0.22,
                    terrain=95_000, co2=7.0),
        "Propriétaire, sans enfant, un seul revenu universel pour un fort impôt.",
        capital=True),

    Cas(menage_type("Dirigeant de PME, 160 000 €", 2, 1, salaire=90_000, capital=70_000,
                    parts=2.5, part_taxable=.75, taux_tva=.182, epargne=0.30,
                    terrain=210_000, co2=9.0, ifi=1_500),
        "Salaire et dividendes. La transmission de l'entreprise est traitée à part.",
        capital=True),

    Cas(menage_type("Héritier de 400 000 €", 1, 0, salaire=38_000, parts=1,
                    part_taxable=.70, taux_tva=.170, epargne=0.10, co2=5.0),
        "Salarié ordinaire, une succession reçue dans l'année.",
        note="succession : 36 389 € aujourd'hui contre 102 000 € au taux commun"),
]


def table_des_cas(r: Reforme) -> None:
    dividende = dividende_carbone(r)
    print(f"\n{r.nom} — dix cas types\n")
    largeur = max(len(c.menage.nom) for c in CAS_TYPES)
    print(f"{'':{largeur}} {'dispo act.':>11} {'impôt':>9} {'transf.':>9} {'TVA':>9} "
          f"{'logement':>9} {'carbone':>9} {'SOLDE':>9} {'% dispo':>8}")
    for cas in CAS_TYPES:
        m = cas.menage
        c = m.canaux(r, dividende)
        s = sum(c.values())
        print(f"{m.nom:{largeur}} {m.disponible_actuel():>11,.0f} "
              f"{c['impôt direct']:>+9,.0f} {c['transferts']:>+9,.0f} {c['TVA']:>+9,.0f} "
              f"{c['logement']:>+9,.0f} {c['carbone']:>+9,.0f} {s:>+9,.0f} "
              f"{s / m.disponible_actuel():>+8.1%}")
    print()
    for cas in CAS_TYPES:
        ligne = f"  {cas.menage.nom} — {cas.commentaire}"
        if cas.capital:
            ligne += f" Valeur du terrain : {cas.menage.perte_en_capital():+,.0f} €."
        if cas.note:
            ligne += f" [{cas.note}]"
        print(ligne)


# --- Le contrôle -------------------------------------------------------------
# Un modèle calibré à la main ne vaut que par ce qu'il retrouve. Sans ce
# tableau, la table par décile n'est qu'une opinion mise en colonnes.

CIBLES_NATIONALES = {
    "CSG + CRDS + prélèvements sociaux": 166,
    "Impôt sur le revenu": 87,
    "Prestations remplaçables": 91,
    "TVA acquittée par les ménages": 150,
    "Consommation en espèces": 1280,
    "Taxe foncière des ménages": 30,
    "IFI": 2,
    "DMTO des ménages": 14,
    "Terrain détenu par les ménages": 2500,
    "Adultes (millions)": 53.0,
    "Mineurs (millions)": 13.8,
}


def controle() -> None:
    n = MENAGES_PAR_DECILE
    obtenu = {
        "CSG + CRDS + prélèvements sociaux": sum(m.revenu * m.taux_csg for m in DECILES) * n / 1e9,
        "Impôt sur le revenu": sum(m.revenu * m.taux_ir for m in DECILES) * n / 1e9,
        "Prestations remplaçables": sum(m.prestations for m in DECILES) * n / 1e9,
        "TVA acquittée par les ménages": sum(m.tva_actuelle() for m in DECILES) * n / 1e9,
        "Consommation en espèces": sum(m.consommation_ttc() for m in DECILES) * n / 1e9,
        "Taxe foncière des ménages": sum(m.terrain * TAUX_TAXE_FONCIERE for m in DECILES) * n / 1e9,
        "IFI": sum(m.ifi for m in DECILES) * n / 1e9,
        "DMTO des ménages": sum(m.terrain * TAUX_DMTO for m in DECILES) * n / 1e9,
        "Terrain détenu par les ménages": sum(m.terrain for m in DECILES) * n / 1e9,
        "Adultes (millions)": sum(m.adultes for m in DECILES) * n / 1e6,
        "Mineurs (millions)": sum(m.enfants for m in DECILES) * n / 1e6,
    }
    print("\nContrôle d'agrégation — le modèle retrouve-t-il les masses nationales ?\n")
    largeur = max(len(k) for k in CIBLES_NATIONALES)
    for nom, cible in CIBLES_NATIONALES.items():
        eu = obtenu[nom]
        ecart = eu / cible - 1
        drapeau = "" if abs(ecart) <= 0.06 else "   ← à recalibrer"
        print(f"  {nom:{largeur}} {eu:>8.1f}  contre {cible:>7.1f}  ({ecart:+.1%}){drapeau}")
    revenu = sum(m.revenu for m in DECILES) * n / 1e9
    print(f"  {'Assiette du nouvel impôt':{largeur}} {revenu:>8.1f}  contre {1600:>7.1f}"
          f"  ({revenu / 1600 - 1:+.1%})")
    # Deuxième contrôle, indépendant du premier : le dernier décile est calibré
    # sur les masses, ses deux sous-lignes sur le barème. Rien n'oblige les deux
    # routes à se rejoindre — si elles se rejoignent, aucune n'est de fantaisie.
    d10, (hors, top, _) = DECILES[9], SOMMET
    pose = d10.taux_csg + d10.taux_ir
    poids = (0.9 * hors.revenu, 0.1 * top.revenu)
    reconstitue = (poids[0] * (hors.taux_csg + hors.taux_ir)
                   + poids[1] * (top.taux_csg + top.taux_ir)) / sum(poids)
    print(f"\n  Taux effectif du dernier décile : {pose:.1%} posé sur les masses,"
          f" {reconstitue:.1%} reconstitué depuis le barème.")


def main() -> None:
    controle()
    for reforme in (CIBLE, VARIANTE, CORRIGEE):
        table_par_decile(reforme)
    table_des_cas(CIBLE)
    table_des_cas(CORRIGEE)


if __name__ == "__main__":
    main()
