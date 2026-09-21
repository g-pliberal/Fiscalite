#!/usr/bin/env python3
"""Écrit les pages du site à partir du contenu défini ici.

Le site est un site STATIQUE : ce script produit les fichiers `.html` du dépôt,
qui sont livrés tels quels et lus sans JavaScript. La raison de passer par un
script est le bandeau de tête et le pied : ils sont identiques sur onze pages,
et onze copies à la main dérivent toujours — la première page corrigée, les dix
autres oubliées. Ici la barre de navigation n'existe qu'une fois, et l'onglet
courant se déduit du nom du fichier.

    python scripts/construire_site.py            # écrit les pages
    python scripts/construire_site.py --verifier  # échoue si elles ont changé

Le contenu vient de `documents/note-fiscalite.pdf` (« Note interne — Chapitre
Fiscalité »), dont le texte brut est repris dans `documents/note-fiscalite.txt`.
Le site n'ajoute aucun chiffre qui n'y figure pas : quand la note dit « à
calibrer », la page dit « à calibrer ».

L'apparence vient du dépôt `retraitecomptenotionelle` : `moteur/style.css` et
`moteur/polices/` en sont copiés tels quels, et ne doivent pas être modifiés ici
(voir README.md). Les rares règles propres à ce site sont dans
`moteur/site.css`, chargée après.
"""

from __future__ import annotations

import argparse
import sys
from html import escape
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

SITE_PARENT = "https://www.partiliberalfrancais.fr/"
DEPOT = "https://github.com/g-pliberal/fiscalite"
NOTE = "documents/note-fiscalite.pdf"

# Les onglets du bandeau, par groupe : une étiquette lue par les synthèses
# vocales, puis les pages. L'ordre est celui de la note.
GROUPES = [
    ("Le cap", [
        ("index.html", "Accueil"),
        ("principes.html", "Principes"),
    ]),
    ("Les réformes", [
        ("revenus.html", "Revenus"),
        ("consommation.html", "TVA"),
        ("foncier.html", "Foncier"),
        ("entreprises.html", "Entreprises"),
        ("carbone.html", "Carbone"),
        ("transmissions.html", "Transmissions"),
    ]),
    ("Comprendre", [
        ("simulateur.html", "Simulateur"),
        ("calendrier.html", "Calendrier"),
        ("objections.html", "Objections"),
        ("glossaire.html", "Glossaire"),
    ]),
]


def navigation(courant: str) -> str:
    """Les onglets du bandeau, l'onglet courant marqué."""
    groupes = []
    for etiquette, liens in GROUPES:
        rendus = "".join(
            f'<a href="{fichier}"'
            + (' aria-current="page"' if fichier == courant else "")
            + f">{escape(libelle)}</a>"
            for fichier, libelle in liens
        )
        groupes.append(
            f'<span class="groupe"><span class="etiquette">{escape(etiquette)}</span>'
            f'<span class="liens">{rendus}</span></span>'
        )
    return "".join(groupes)


def entete(courant: str) -> str:
    """Bandeau de tête, précédé du lien d'évitement.

    Le lien d'évitement est le premier élément parcouru au clavier : sans lui,
    atteindre le contenu impose de traverser les onze onglets à chaque page.
    """
    return (
        '<a class="evitement" href="#contenu">Aller au contenu</a>\n'
        '<header class="bandeau"><div class="interieur">\n'
        '  <p class="nom"><a href="index.html"><span>Programme fiscal</span></a></p>\n'
        f'  <nav aria-label="Navigation principale">{navigation(courant)}</nav>\n'
        "</div></header>"
    )


def pied() -> str:
    """Pied de page.

    Il porte ce que le lecteur doit savoir avant de citer un chiffre : d'où
    vient le texte, ce qui y est arrêté et ce qui ne l'est pas.
    """
    return f"""<footer>
  <p><strong>Ce site n'est pas un texte de loi.</strong> Il présente le chapitre
  Fiscalité du programme du Parti libéral français. Les taux et les rendements
  qui y figurent sont des <em>cibles de travail</em> et des ordres de grandeur à
  consolider : la note dont ces pages sont tirées le dit elle-même, le bouclage
  budgétaire n'est pas fait impôt par impôt mais au niveau du système entier.</p>
  <p>Texte de référence : <a href="{NOTE}">Note interne — Chapitre Fiscalité</a>
  (PDF), dont le texte brut est repris dans
  <a href="documents/note-fiscalite.txt">note-fiscalite.txt</a>. Site et code sur
  <a href="{DEPOT}">GitHub</a> (code sous licence Apache 2.0, textes et
  infographies sous
  <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">CC BY-SA 4.0</a>).
  L'apparence est celle du
  <a href="https://github.com/g-pliberal/retraitecomptenotionelle">simulateur de
  retraite</a> du même parti, dont la charte est reprise sans modification.</p>
  <p class="retour-site">Un site du
  <a href="{SITE_PARENT}" target="_top">Parti libéral français</a>.</p>
</footer>"""


def affiche(surtitre: str, titre: str, chapeau: str) -> str:
    """Le bloc de tête d'une page : sur-titre, titre massif, chapeau.

    C'est l'unité qui fait de chaque page une affiche. Le titre est mis en
    capitales par le STYLE, jamais dans le texte : une synthèse vocale qui lit
    des capitales les épelle parfois lettre à lettre.
    """
    return (
        f'<div class="affiche"><p class="surtitre">{escape(surtitre)}</p>'
        f'<h1>{titre}</h1><p class="chapeau">{chapeau}</p></div>'
    )


def liste(elements: list[str], classe: str = "") -> str:
    attribut = f' class="{classe}"' if classe else ""
    points = "".join(f"\n  <li>{e}</li>" for e in elements)
    return f"<ul{attribut}>{points}\n</ul>"


def tableau(entetes: list[str], lignes: list[list[str]], legende: str = "",
            colonnes: list[str] | None = None) -> str:
    """Un tableau, enveloppé dans son cadre défilant.

    Le cadre est ce qui défile quand le tableau est plus large que l'écran : le
    document, lui, ne défile jamais latéralement (voir `overflow-x` sur `body`
    dans la charte). La légende est un `<caption>`, et non un paragraphe
    au-dessus : c'est ce qui la rattache à la grille pour un lecteur d'écran.
    """
    classes = colonnes or [""] * len(entetes)
    tete = "".join(
        "<th" + (' class="%s"' % c if c else "") + ' scope="col">' + intitule + "</th>"
        for intitule, c in zip(entetes, classes)
    )
    corps = []
    for ligne in lignes:
        cellules = []
        for i, valeur in enumerate(ligne):
            balise = "th" if i == 0 else "td"
            portee = ' scope="row"' if i == 0 else ""
            classe = f' class="{classes[i]}"' if classes[i] else ""
            cellules.append(f"<{balise}{portee}{classe}>{valeur}</{balise}>")
        corps.append("<tr>" + "".join(cellules) + "</tr>")
    texte = "".join(corps)
    caption = f"<caption>{legende}</caption>" if legende else ""
    return ('<div class="defilant"><table>' + caption
            + f"<thead><tr>{tete}</tr></thead><tbody>{texte}</tbody></table></div>")


def plan(liens: list[tuple[str, str]], etiquette: str = "Sur cette page") -> str:
    """Le plan d'une page longue : ses intertitres, en une rangée d'onglets."""
    entrees = "".join(
        f'<li><a href="#{ancre}">{escape(libelle)}</a></li>' for ancre, libelle in liens
    )
    return ('<nav class="plan" aria-label="Plan de la page">'
            f'<p class="etiquette">{escape(etiquette)}</p><ol>{entrees}</ol></nav>')


def section(ancre: str, titre: str, corps: str) -> str:
    return f'<h2 id="{ancre}">{titre}</h2>\n{corps}'


def encadre(titre: str, corps: str) -> str:
    """La formule qu'on retient : une phrase, encadrée d'or.

    Ce sont les « formulations de principe » de la note, et elles gardent son
    mot à mot quand elle en propose un.
    """
    tete = f'<h3 class="serif">{titre}</h3>' if titre else ""
    return f'<div class="encadre">{tete}{corps}</div>'


# -- les huit piliers --------------------------------------------------------
#
# Ce sont les huit de la section 3 de la note, dans son ordre. Ils servent deux
# fois : la frise de l'accueil, et le tableau du calendrier.

PILIERS = [
    ("01", "Un impôt, pas trois",
     "Fusion de l’impôt sur le revenu, de la CSG et de la CRDS dans un impôt "
     "proportionnel unique sur les revenus personnels.",
     "revenus.html"),
    ("02", "Une TVA, un taux",
     "Convergence vers un taux unique cible de 25 %, sans mosaïque de taux "
     "réduits décidés secteur par secteur.",
     "consommation.html"),
    ("03", "Un revenu universel",
     "Versé à chacun, indexé sur la croissance réelle par habitant : c’est lui "
     "qui rend le système progressif.",
     "revenus.html"),
    ("04", "Le sol, pas la maison",
     "Une <i>Land Value Tax</i> nationale sur la valeur du foncier nu, à la "
     "place de l’empilement immobilier actuel.",
     "foncier.html"),
    ("05", "Les pires impôts, tout de suite",
     "Suppression immédiate des droits de mutation, de la C3S, de la CVAE "
     "résiduelle et de l’exit tax.",
     "calendrier.html"),
    ("06", "Un impôt sur les sociétés simple",
     "Maintenu d’abord autour de 25 %, puis ramené vers 15 à 20 % à mesure que "
     "les niches disparaissent.",
     "entreprises.html"),
    ("07", "Un prix du carbone rendu",
     "Un prix plancher lisible, et une recette reversée aux citoyens sous forme "
     "de dividende carbone.",
     "carbone.html"),
    ("08", "Imposer celui qui reçoit",
     "Successions et donations fusionnées, imposées chez le receveur, avec un "
     "abattement universel de 100 000 € sur la vie entière.",
     "transmissions.html"),
]


def piliers_frise() -> str:
    blocs = []
    for rang, promesse, detail, lien in PILIERS:
        blocs.append(
            f'<div class="engagement"><p class="rang">Pilier {rang}</p>'
            f'<p class="chiffre">{rang}</p>'
            f'<p class="promesse"><a href="{lien}">{promesse}</a></p>'
            f'<p class="detail">{detail}</p></div>'
        )
    return ('<section class="engagements" aria-labelledby="piliers">'
            '<h2 id="piliers" class="hors-ecran">Les huit piliers</h2>'
            f'<div class="grille">{"".join(blocs)}</div></section>')


# -- accueil -----------------------------------------------------------------

ACCUEIL = "\n".join([
    '<div class="fiches reperes">',
    '  <div class="fiche"><p class="etiquette">Impôt sur les revenus</p>'
    '<p class="valeur">&lt; 30 %</p>'
    '<p class="precision">Un seul taux, proportionnel, à la place de l’IR, de la '
    'CSG et de la CRDS. Le taux exact sort du bouclage budgétaire.</p></div>',
    '  <div class="fiche"><p class="etiquette">TVA</p><p class="valeur">25 %</p>'
    '<p class="precision">Taux unique cible, atteint progressivement, le temps '
    'que le revenu universel monte en charge.</p></div>',
    '  <div class="fiche"><p class="etiquette">Land Value Tax</p>'
    '<p class="valeur">2 %</p>'
    '<p class="precision">De la valeur du terrain nu — pas du bâtiment. Environ '
    '120 Md€ visés à terme, sous réserve d’évaluation.</p></div>',
    '  <div class="fiche"><p class="etiquette">Revenu universel</p>'
    '<p class="valeur">600 €</p>'
    '<p class="precision">Par mois et par adulte dans l’exemple chiffré de la '
    'note, versé sans condition et indexé sur la croissance réelle.</p></div>',
    '</div>',
    piliers_frise(),
    '<div class="paire">',
    '  <div>',
    '    <h2 id="pourquoi">Pourquoi remettre à plat</h2>',
    "    <p>La fiscalité française n’est pas seulement lourde : elle est "
    "illisible, et elle frappe en priorité ce qui produit. La note dont ce site "
    "est tiré lui reproche sept défauts&nbsp;:</p>",
    liste([
        "elle taxe lourdement le travail&nbsp;;",
        "elle pénalise la production avant même le bénéfice&nbsp;;",
        "elle multiplie les niches, exonérations, régimes spéciaux et effets de "
        "seuil&nbsp;;",
        "elle empile fiscalité nationale, sociale et locale sans responsabilité "
        "claire&nbsp;;",
        "elle entretient une redistribution opaque&nbsp;;",
        "elle décourage la mobilité résidentielle, l’investissement productif et "
        "l’augmentation de l’offre foncière&nbsp;;",
        "elle donne à l’État le pouvoir de définir en permanence ce qui serait "
        "socialement ou économiquement désirable.",
    ]),
    "    <p>D’où le choix de ne pas proposer une réforme paramétrique de plus — "
    "un taux ici, une niche là — mais une remise à plat complète.</p>",
    '  </div>',
    '  <div>',
    '    <h2 id="couple">Le couple central</h2>',
    encadre("", "<p><strong class=\"cle-texte\">Impôt proportionnel + revenu "
                "universel.</strong></p>"),
    "    <p>Chacun contribue en proportion de ses revenus&nbsp;; chacun reçoit "
    "une part universelle de la solidarité nationale. Le système devient "
    "progressif non par la complexité du barème, mais par le versement "
    "forfaitaire du revenu universel.</p>",
    "    <p>C’est la réponse à l’objection qui vient d’abord&nbsp;: un taux "
    "unique n’est pas un système plat. Un revenu de 10 000 € reste "
    "<em>bénéficiaire net</em>&nbsp;; un revenu de 200 000 € paie un taux moyen "
    "de 21 %. Le taux marginal, lui, ne bouge pas — il n’y a donc plus de seuil "
    "à redouter, ni de trappe à inactivité.</p>",
    '    <div class="note entree"><p>Le calcul est fait, chiffre par chiffre, '
    'sur la page des revenus — et le simulateur, qui tourne dans votre '
    'navigateur.</p><p class="actions">'
    '<a class="bouton" href="simulateur.html">Calculer mon cas</a>'
    '</p></div>',
    '  </div>',
    '</div>',
    section("immediat", "Ce qui change dès la première année",
            "<p>La note distingue les impôts assez nocifs pour être supprimés "
            "tout de suite, et ceux qu’on fait converger progressivement. Dans "
            "la première catégorie&nbsp;:</p>"
            + liste([
                "les <strong>droits de mutation à titre onéreux</strong>, qui "
                "taxent le fait de déménager&nbsp;;",
                "la <strong>C3S</strong>, qui taxe le chiffre d’affaires, "
                "bénéfice ou pas&nbsp;;",
                "la <strong>CVAE résiduelle</strong>, qui taxe la valeur "
                "ajoutée productive&nbsp;;",
                "l’<strong>exit tax</strong>, qui prétend retenir les "
                "contribuables par la menace&nbsp;;",
                "la <strong>taxation spécifique des plus-values "
                "immobilières</strong>&nbsp;;",
                "les premières petites taxes redondantes et à faible rendement.",
            ])
            + '<p class="actions"><a class="bouton" href="calendrier.html">'
              "Voir le calendrier complet</a></p>"),
    section("doctrine", "La formule",
            encadre("", "<p>Taxer moins le travail, moins la production, moins "
                        "l’investissement productif&nbsp;; taxer mieux la "
                        "consommation, la rente foncière et le carbone&nbsp;; "
                        "redistribuer simplement par le revenu universel et le "
                        "dividende carbone.</p>")
            + "<p>Version politique&nbsp;: moins d’impôts sur ceux qui "
              "travaillent, produisent et investissent&nbsp;; plus de clarté sur "
              "ce que chacun paie et reçoit&nbsp;; une fiscalité qui cesse de "
              "punir la croissance.</p>"),
])


# -- principes ---------------------------------------------------------------

PRINCIPES = "\n".join([
    plan([("separer", "Impôt, cotisation, redistribution"),
          ("productives", "Les bases productives"),
          ("gratuite", "L’illusion de la gratuité")]),
    section("separer", "Séparer impôt, cotisation et redistribution",
            "<p>Le système actuel mélange trois logiques qui devraient être "
            "distinguées. Les séparer est le premier geste de la réforme, parce "
            "que c’est lui qui rend tous les autres lisibles.</p>"
            + '<div class="points">'
              '<div class="point"><h3>L’impôt</h3><p>Il finance les missions '
              'régaliennes, les biens publics, la solidarité nationale, le revenu '
              'universel, le socle universel de santé et les dépenses publiques '
              'non individualisables. Il doit être large, simple, transparent et '
              'économiquement peu distorsif.</p></div>'
              '<div class="point"><h3>La cotisation</h3><p>Elle ne finance que '
              'des droits contributifs&nbsp;: retraite contributive, assurance '
              'chômage contributive, indemnités journalières, prestations liées à '
              'une carrière. Un prélèvement qui n’ouvre aucun droit '
              'individualisé n’est pas une cotisation&nbsp;: c’est un impôt, et '
              'il doit être assumé comme tel.</p></div>'
              '<div class="point"><h3>La redistribution</h3><p>Elle doit être '
              'simple, automatique et visible. Plus de taux différenciés, de '
              'niches, de prestations conditionnelles ni d’effets de seuil comme '
              'instrument principal&nbsp;: elle passe d’abord par le revenu '
              'universel.</p></div></div>'
            + '<div class="note"><p>C’est ce raisonnement qui justifie la fusion '
              'IR-CSG-CRDS&nbsp;: la CSG et la CRDS ne financent aucun droit '
              'contributif individualisé. Elles relèvent donc de l’impôt général, '
              'et doivent être appelées ainsi.</p></div>'),
    section("productives", "Taxer moins les bases productives",
            "<p>À rendement égal, tous les impôts ne coûtent pas la même chose à "
            "l’économie. La réforme déplace donc la charge, plutôt que de "
            "l’alourdir ou de l’alléger en bloc.</p>"
            + '<div class="bascules">'
              '<div class="colonne"><h3>On sort la fiscalité de&nbsp;:</h3>'
              + liste(["le travail&nbsp;;", "la production&nbsp;;",
                       "l’investissement productif&nbsp;;",
                       "la mobilité résidentielle&nbsp;;",
                       "l’électricité bas-carbone&nbsp;;",
                       "la transmission d’entreprise productive."])
              + '</div><div class="colonne cible">'
                '<h3>On l’assume plus clairement sur&nbsp;:</h3>'
              + liste(["la consommation&nbsp;;", "les revenus larges&nbsp;;",
                       "la rente foncière&nbsp;;",
                       "les externalités carbone&nbsp;;",
                       "les transmissions patrimoniales reçues."])
              + "</div></div>"
            + encadre("", "<p>Taxer moins ce qui produit, davantage ce qui relève "
                          "de la rente, et redistribuer simplement.</p>")),
    section("gratuite", "Supprimer l’illusion de la gratuité",
            "<p>Un système fiscal sain rend les coûts visibles. Aujourd’hui ils "
            "sont dissimulés, et ce qu’on ne voit pas, on ne peut pas en "
            "débattre.</p>"
            + liste([
                "la <strong>fiche de paie</strong> doit faire apparaître le coût "
                "total du travail&nbsp;;",
                "les <strong>impôts locaux</strong> doivent être "
                "compréhensibles&nbsp;;",
                "le <strong>financement du réseau électrique</strong> ne doit pas "
                "être dissimulé dans des taxes sur le kWh&nbsp;;",
                "la <strong>fiscalité carbone</strong> doit être assumée comme un "
                "signal-prix, et redistribuée explicitement.",
            ])
            + "<p>La transparence fiscale n’est pas une coquetterie comptable&nbsp;: "
              "c’est une condition de la responsabilité démocratique. Un citoyen "
              "qui ne sait pas qui le taxe ne peut pas sanctionner celui qui "
              "dépense.</p>"
            + '<p class="actions"><a class="bouton" href="calendrier.html#paie">'
              "La fiche de paie cible</a></p>"),
])


# -- revenus -----------------------------------------------------------------

TABLE_RU = tableau(
    ["Revenu annuel", "Impôt (25 %)", "Revenu universel", "Solde",
     "Taux net effectif"],
    [
        ["0 €", "0 €", "+7 200 €", "+7 200 €", "bénéficiaire net"],
        ["10 000 €", "−2 500 €", "+7 200 €", "+4 700 €", "bénéficiaire net"],
        ["20 000 €", "−5 000 €", "+7 200 €", "+2 200 €", "bénéficiaire net"],
        ["30 000 €", "−7 500 €", "+7 200 €", "−300 €", "1 %"],
        ["50 000 €", "−12 500 €", "+7 200 €", "−5 300 €", "10,6 %"],
        ["100 000 €", "−25 000 €", "+7 200 €", "−17 800 €", "17,8 %"],
        ["200 000 €", "−50 000 €", "+7 200 €", "−42 800 €", "21,4 %"],
    ],
    legende="Exemple stylisé de la note : revenu universel de 600 €/mois, soit "
            "7 200 €/an, et impôt proportionnel de 25 %. Ni l’un ni l’autre n’est "
            "un chiffre arrêté.",
)

REVENUS = "\n".join([
    plan([("fusion", "Fusion IR-CSG-CRDS"), ("taux", "Le taux"),
          ("assiette", "L’assiette"), ("individuel", "Individualisation"),
          ("progressivite", "La progressivité"),
          ("indexation", "L’indexation du RU")]),
    section("fusion", "Un impôt à la place de trois",
            "<p>L’impôt sur le revenu, la CSG et la CRDS seront fusionnés dans un "
            "<strong>impôt proportionnel unique</strong> sur les revenus "
            "personnels. Il ne s’agit pas d’ajouter un impôt, mais de remplacer un "
            "empilement de prélèvements superposés par un impôt général "
            "lisible.</p>"
            + "<p>L’impôt proportionnel remplacera notamment&nbsp;:</p>"
            + liste(["l’impôt sur le revenu&nbsp;;", "la CSG&nbsp;;",
                     "la CRDS&nbsp;;",
                     "les prélèvements sociaux non contributifs sur les revenus "
                     "du capital."])
            + "<p>La CSG et la CRDS ne financent pas de droits contributifs "
              "individualisés&nbsp;: elles relèvent de l’impôt général, et doivent "
              "être assumées comme telles.</p>"),
    section("taux", "Un taux sous 30 %, et pourquoi il n’est pas encore écrit",
            "<p>Le taux exact sera déterminé par le bouclage budgétaire général. "
            "L’objectif politique est de le maintenir <strong>sous les "
            "30 %</strong>, grâce&nbsp;:</p>"
            + liste(["à l’élargissement de l’assiette&nbsp;;",
                     "à la fusion IR-CSG-CRDS&nbsp;;",
                     "à la suppression des niches&nbsp;;",
                     "à la TVA à taux unique&nbsp;;",
                     "à la <i>Land Value Tax</i>&nbsp;;",
                     "à la réforme des prestations sociales autour du revenu "
                     "universel&nbsp;;",
                     "à la réduction des dépenses publiques non prioritaires."])
            + '<div class="note vigilance"><p>Annoncer un taux avant le chiffrage '
              'complet serait un chiffre de tract, pas un engagement. La note s’y '
              'refuse explicitement&nbsp;: la contrainte politique est claire, le '
              'nombre viendra du bouclage.</p></div>'
            + encadre("", "<p>Un impôt proportionnel large, lisible, et si "
                          "possible inférieur à 30 %.</p>")),
    section("assiette", "Tous les revenus, traités pareil",
            "<p>L’impôt proportionnel portera sur l’ensemble des revenus "
            "personnels&nbsp;: salaires, revenus indépendants, pensions, revenus "
            "de remplacement imposables, dividendes, intérêts, revenus fonciers "
            "nets, plus-values mobilières réalisées, revenus professionnels et "
            "assimilés, distributions de sociétés, et revenus étrangers "
            "imposables en France selon les conventions fiscales.</p>"
            + encadre("", "<p>À revenu économique équivalent, le traitement fiscal "
                          "doit être équivalent.</p>")
            + "<p>C’est la fin des arbitrages artificiels entre salaire, "
              "dividende, plus-value, revenu professionnel et revenu "
              "patrimonial&nbsp;: aujourd’hui, le même euro est taxé "
              "différemment selon l’étiquette qu’on lui donne, et une part de "
              "l’ingénierie fiscale ne sert qu’à changer l’étiquette.</p>"
            + "<h3>Plus-values mobilières</h3>"
            + "<p>Elles seront imposées à la réalisation, au taux proportionnel, "
              "sur les gains nets, avec report des moins-values, et sur une base "
              "réelle après inflation pour les détentions longues. L’objectif est "
              "de taxer les gains effectifs sans pénaliser artificiellement "
              "l’épargne longue par l’inflation.</p>"
            + "<h3>Revenus fonciers</h3>"
            + "<p>Les revenus locatifs restent imposés comme les autres revenus, "
              "mais uniquement sur une <strong>base nette</strong>. Pour éviter la "
              "double imposition de la rente foncière&nbsp;: la LVT est déductible "
              "du revenu locatif imposable, les charges réelles, l’entretien et la "
              "gestion sont déductibles, l’amortissement du bâti peut être pris en "
              "compte — et le terrain lui-même n’est pas amortissable.</p>"
            + encadre("", "<p>Le sol est taxé comme une rente&nbsp;; le loyer net "
                          "est taxé comme un revenu.</p>")),
    section("individuel", "Un impôt individuel, une politique familiale explicite",
            "<p>Le foyer fiscal est supprimé comme unité de base&nbsp;: l’impôt "
            "proportionnel est strictement individuel. Votre imposition ne dépend "
            "plus de la situation conjugale ou patrimoniale de votre foyer.</p>"
            + "<p>La politique familiale ne disparaît pas&nbsp;: elle est traitée "
              "explicitement, par le revenu universel enfant, un éventuel crédit "
              "familial, des dispositifs dédiés aux familles monoparentales, et "
              "une redistribution horizontale assumée entre ménages avec et sans "
              "enfants.</p>"
            + '<div class="note"><p>La différence est de nature&nbsp;: aujourd’hui '
              'l’aide aux familles passe par un mécanisme de calcul de l’impôt, '
              'dont l’effet dépend du revenu et que personne ne lit. Demain elle '
              'est un montant, versé, qu’on peut discuter et voter pour '
              'lui-même.</p></div>'),
    section("progressivite", "Un taux unique, un système progressif",
            "<p>La suppression du barème progressif ne fait pas disparaître la "
            "progressivité&nbsp;: elle la déplace du barème vers le revenu "
            "universel. Le taux marginal est constant, mais le taux moyen augmente "
            "avec le revenu.</p>"
            + TABLE_RU
            + "<p>Le système est donc redistributif sans être confiscatoire, et "
              "sans créer de trappes à inactivité&nbsp;: un euro de plus gagné "
              "rapporte toujours la même fraction, quel que soit le niveau de "
              "revenu. Aucun seuil à ne pas franchir, aucune aide à perdre.</p>"),
    encadre("", "<p>Ce tableau ne tient compte que de l’impôt et du revenu "
                "universel. Le simulateur, lui, ajoute la TVA, le foncier et "
                "l’énergie&nbsp;: c’est là que se lit votre cas réel.</p>"
                '<p><a class="bouton" href="simulateur.html">Ouvrir le '
                'simulateur</a></p>'),
    section("indexation", "Ce qui fait bouger le revenu universel",
            "<p>Le revenu universel sera indexé sur le <strong>PIB réel par "
            "habitant</strong>, lissé sur trois ans. Trois raisons&nbsp;:</p>"
            + "<ol><li>donner à chaque citoyen un intérêt direct à la "
              "croissance&nbsp;;</li><li>éviter une indexation automatique sur "
              "l’inflation, qui rigidifierait la dépense publique&nbsp;;</li>"
              "<li>lier la progression du revenu universel à la prospérité réelle "
              "du pays.</li></ol>"
            + "<p>Il ne sera donc pas indexé automatiquement sur les prix. En cas "
              "de choc inflationniste exceptionnel, le Parlement reste souverain "
              "pour voter une revalorisation&nbsp;: mais elle devra être "
              "explicite, financée et temporaire.</p>"
            + encadre("", "<p>Le revenu universel est une part de la prospérité "
                          "commune, pas une dépense indexée sans limite.</p>")),
])


# -- consommation (TVA) ------------------------------------------------------

CONSOMMATION = "\n".join([
    plan([("principe", "Le principe"), ("permet", "Ce que le taux unique permet"),
          ("transition", "La transition"), ("juste", "« Et la justice sociale ? »")]),
    section("principe", "Un grand impôt de rendement, à un seul taux",
            "<p>La TVA doit devenir un grand impôt universel de rendement, à "
            "<strong>taux unique cible de 25 %</strong>.</p>"
            + "<p>L’objectif n’est pas d’augmenter aveuglément la fiscalité sur la "
              "consommation. Il est de remplacer une partie des impôts les plus "
              "nocifs — sur le travail, sur la production, sur la mobilité — par un "
              "impôt plus large, plus simple et plus difficile à éviter.</p>"),
    section("permet", "Ce que le taux unique permet",
            liste(["de supprimer les arbitrages sectoriels&nbsp;;",
                   "de réduire les niches déguisées&nbsp;;",
                   "de limiter le lobbying fiscal&nbsp;;",
                   "de rendre la fiscalité plus lisible&nbsp;;",
                   "d’éviter que l’État définisse politiquement ce qui serait ou "
                   "non «&nbsp;de première nécessité&nbsp;»."])
            + encadre("", "<p>À terme, l’État n’a pas vocation à définir par la TVA "
                          "ce qui est essentiel ou non. La justice sociale doit "
                          "passer par le revenu universel, non par une mosaïque de "
                          "taux réduits.</p>")),
    section("transition", "Une convergence, pas un choc",
            "<p>La convergence vers 25 % doit être <strong>progressive</strong>, "
            "notamment le temps que le revenu universel monte pleinement en "
            "charge.</p>"
            + "<p>Les taux réduits existants sont appelés à disparaître, mais leur "
              "extinction pourra être lissée. Il ne s’agit pas de conserver des "
              "exceptions permanentes&nbsp;: il s’agit d’éviter un choc de prix "
              "brutal sur certains biens aujourd’hui fortement subventionnés "
              "fiscalement.</p>"
            + '<div class="note"><p>La compensation sociale ne se fera pas par le '
              'maintien indéfini de taux réduits, mais par le revenu '
              'universel.</p></div>'),
    section("juste", "« Une TVA à 25 %, ce n’est pas juste »",
            "<p>Prise isolément, la TVA peut être régressive&nbsp;: les ménages "
            "modestes consomment une part plus grande de leur revenu. Mais elle "
            "n’est pas prise isolément — ici, elle finance un revenu "
            "universel.</p>"
            + "<p>Un ménage modeste reçoit le revenu universel et le dividende "
              "carbone&nbsp;: il est protégé <em>directement</em>, par un virement "
              "qu’il constate, plutôt que par l’espoir incertain qu’un taux réduit "
              "soit intégralement répercuté dans les prix qu’il paie.</p>"
            + '<p class="actions"><a class="bouton" href="objections.html">Les huit '
              "objections, et les réponses</a></p>"),
])


# -- foncier (LVT) -----------------------------------------------------------

TABLE_TERRAINS = tableau(
    ["Terrain", "Traitement"],
    [["Terrain agricole productif", "LVT sur la valeur agricole réelle"],
     ["Forêt exploitée durablement",
      "LVT + paiement possible pour services écologiques"],
     ["Zone humide protégée",
      "LVT faible si la valeur économique est faible, + rémunération écologique "
      "possible"],
     ["Terrain constructible non bâti en zone tendue", "LVT pleine"],
     ["Friche spéculative", "LVT pleine"]],
    legende="Le foncier non bâti est taxé selon sa valeur réelle : pas "
            "d’exonération opaque, mais une rémunération budgétée des services "
            "écosystémiques réels.",
)

FONCIER = "\n".join([
    plan([("pourquoi", "L’empilement actuel"), ("principe", "Le sol, pas le bâti"),
          ("taux", "Le taux"), ("remplace", "Ce qui disparaît"),
          ("dmto", "Les droits de mutation"), ("revenus-modestes", "Reports et garanties"),
          ("agricole", "Foncier agricole et naturel"), ("local", "Taux national")]),
    section("pourquoi", "Un empilement qui punit la construction",
            "<p>La fiscalité immobilière actuelle est l’un des exemples les plus "
            "nets d’empilement inefficace. Elle taxe la détention, la transaction, "
            "la transmission, <em>la construction</em>, les loyers, les "
            "plus-values, la vacance, les résidences secondaires — et parfois "
            "l’investissement ou la rénovation eux-mêmes.</p>"
            + "<p>Résultat&nbsp;: elle pénalise la mobilité, freine la circulation "
              "du foncier et favorise les situations acquises.</p>"),
    section("principe", "Taxer le sol, pas ce qu’on bâtit dessus",
            "<p>Le programme remplace cette logique par une <strong><i>Land Value "
            "Tax</i></strong> (LVT), ou taxe sur la valeur du foncier nu&nbsp;: "
            "<strong>la valeur du terrain, non celle du bâtiment</strong>.</p>"
            + '<div class="bascules">'
              '<div class="colonne cible"><h3>Elle ne pénalise pas</h3>'
            + liste(["la construction&nbsp;;", "la rénovation&nbsp;;",
                     "la densification&nbsp;;", "l’entretien&nbsp;;",
                     "l’investissement productif sur le terrain."])
            + '</div><div class="colonne"><h3>Elle taxe</h3>'
              "<p>la rente d’emplacement&nbsp;: la valeur créée par la rareté du "
              "sol, les infrastructures publiques, l’urbanisme et l’attractivité "
              "collective. Autrement dit, ce que le propriétaire n’a pas "
              "produit.</p></div></div>"),
    section("taux", "2 % de la valeur du foncier nu",
            "<p>Le taux cible de travail est fixé à <strong>2 %</strong> de la "
            "valeur du foncier nu. Il pourra être ajusté selon le bouclage "
            "budgétaire et la qualité du cadastre foncier.</p>"
            + "<p>L’ordre de grandeur de rendement visé est d’environ "
              "<strong>120 Md€</strong> à terme, sous réserve d’évaluation.</p>"),
    section("remplace", "La LVT remplace, elle ne s’ajoute pas",
            "<p>La LVT a vocation à remplacer l’essentiel de la fiscalité "
            "immobilière actuelle. Sont supprimés&nbsp;:</p>"
            + liste(["les droits de mutation à titre onéreux&nbsp;;",
                     "la taxation spécifique des plus-values immobilières&nbsp;;",
                     "la taxe d’habitation sur les résidences secondaires&nbsp;;",
                     "les taxes sur les logements vacants&nbsp;;",
                     "les surtaxes locales sur les résidences secondaires&nbsp;;",
                     "l’IFI&nbsp;;",
                     "les fiscalités immobilières redondantes&nbsp;;",
                     "la fiscalité spécifique de détention, remplacée par la LVT."])
            + "<p>Les locations de courte durée ne font pas l’objet d’une fiscalité "
              "spéciale de détention&nbsp;: elles sont taxées comme une activité "
              "économique normale. Les nuisances éventuelles relèvent de "
              "l’urbanisme, de la police locale ou de la réglementation "
              "économique — pas d’un empilement de micro-taxes.</p>"),
    section("dmto", "Les droits de mutation, supprimés immédiatement",
            "<p>Les droits de mutation à titre onéreux (DMTO) sont parmi les impôts "
            "les plus nocifs du système français&nbsp;: ils taxent la mobilité "
            "résidentielle, freinent les déménagements, réduisent la fluidité du "
            "marché du logement et pénalisent les ménages qui doivent changer de "
            "lieu de vie ou d’emploi.</p>"
            + "<p>Ils seront supprimés <strong>immédiatement</strong>.</p>"
            + '<div class="note vigilance"><p>Il ne faut pas parler de '
              '«&nbsp;suppression des frais de notaire&nbsp;»&nbsp;: les frais '
              'strictement administratifs et les émoluments réglementés des '
              'notaires sont autre chose, et seront traités séparément. Ce qui est '
              'supprimé, ce sont les <strong>droits de mutation à titre '
              'onéreux</strong> — la part qui va à l’impôt.</p></div>'
            + "<h3>Et les plus-values immobilières&nbsp;?</h3>"
            + "<p>Leur taxation spécifique est supprimée. Avec une LVT forte, la "
              "rente foncière est déjà taxée chaque année&nbsp;; maintenir une "
              "taxation spécifique des plus-values reviendrait à réintroduire "
              "l’empilement qu’on vient de défaire. La baisse de la valeur du "
              "foncier induite par la LVT réduira d’ailleurs une partie des "
              "plus-values latentes.</p>"
            + "<p>Si la réforme provoque un surcroît de ventes, c’est un effet "
              "positif&nbsp;: le but est précisément de faire circuler le foncier "
              "et de réduire la rétention spéculative.</p>"),
    section("revenus-modestes", "Propriétaires à faible revenu : reports, pas exonérations",
            "<p>La LVT doit rester aussi pure que possible&nbsp;: des exonérations "
            "permanentes selon le revenu permettraient à des propriétaires riches "
            "en foncier mais pauvres en revenu de conserver indéfiniment des "
            "terrains rares sans en supporter le coût d’opportunité.</p>"
            + "<p>En revanche, une transition humaine est nécessaire. Le programme "
              "prévoit&nbsp;:</p>"
            + liste(["un <strong>report de paiement</strong> pendant les cinq "
                     "premières années de mise en place&nbsp;;",
                     "puis, à terme, la possibilité de bénéficier de jusqu’à "
                     "<strong>deux ans de crédit</strong> en cas de mise en vente "
                     "du bien&nbsp;;",
                     "une <strong>créance fiscale garantie</strong> sur le bien en "
                     "cas de report&nbsp;;",
                     "une récupération à la vente ou à la succession."])
            + "<p>L’objectif n’est pas de brutaliser les ménages, mais de faire "
              "circuler le foncier à terme.</p>"),
    section("agricole", "Foncier agricole, forestier et naturel",
            "<p>La LVT s’applique aussi au foncier non bâti, selon sa valeur "
            "réelle. Il faut éviter les exonérations permanentes, qui recréeraient "
            "une fiscalité mitée — mais certains terrains fournissent des services "
            "écologiques réels&nbsp;: stockage de carbone, biodiversité, gestion de "
            "l’eau, protection des sols. Ces services peuvent être rémunérés "
            "explicitement.</p>"
            + encadre("", "<p>Pas d’exonération fiscale opaque, mais une "
                          "rémunération budgétée et conditionnée des services "
                          "écosystémiques réels.</p>")
            + TABLE_TERRAINS),
    section("local", "Un taux national, une recette partagée",
            "<p>La LVT aura un <strong>taux national</strong>. Son produit pourra "
            "être partagé entre l’État et les collectivités territoriales, avec un "
            "mécanisme de péréquation.</p>"
            + encadre("", "<p>La LVT doit être nationale dans son taux, mais "
                          "compatible avec une ressource locale lisible et "
                          "péréquée.</p>")
            + "<p>Cela évite deux dérives&nbsp;: que les communes les plus riches "
              "en foncier captent seules toute la rente, et que chaque collectivité "
              "négocie ses propres exceptions.</p>"
            + "<p>La fiscalité locale fera l’objet d’un chapitre dédié, mais trois "
              "principes sont déjà fixés&nbsp;: la LVT devient une ressource "
              "centrale&nbsp;; son taux est national&nbsp;; son produit est partagé "
              "ou péréqué pour éviter l’explosion des inégalités territoriales. La "
              "suppression immédiate des DMTO devra être compensée dans le cadre de "
              "la réforme d’ensemble des collectivités.</p>"),
])


# -- entreprises -------------------------------------------------------------

ENTREPRISES = "\n".join([
    plan([("production", "Les impôts de production"), ("immediat", "Supprimés tout de suite"),
          ("locale", "CFE et fiscalité locale"), ("is", "Impôt sur les sociétés"),
          ("niches", "Niches et CIR"), ("dividendes", "IS et dividendes")]),
    section("production", "Une entreprise ne doit pas être taxée parce qu’elle produit",
            "<p>Une entreprise doit être imposée lorsqu’elle réalise un bénéfice, "
            "distribue un revenu, consomme une ressource rare ou génère une "
            "externalité. Pas parce qu’elle existe et qu’elle tourne.</p>"
            + "<p>Les impôts de production sont particulièrement destructeurs "
              "parce qu’ils frappent l’activité <em>avant même qu’elle ne soit "
              "rentable</em>. Ils pénalisent l’industrie, les marges faibles, les "
              "entreprises en croissance et les activités capitalistiques&nbsp;: "
              "exactement ce dont une réindustrialisation a besoin.</p>"),
    section("immediat", "Supprimés immédiatement",
            liste(["la <strong>C3S</strong>, qui taxe le chiffre d’affaires&nbsp;;",
                   "la <strong>CVAE résiduelle</strong>, qui taxe la valeur "
                   "ajoutée productive."])
            + "<p>Ces deux impôts frappent le chiffre d’affaires ou la valeur "
              "ajoutée, indépendamment de la rentabilité effective de "
              "l’entreprise. Ils sont incompatibles avec une stratégie de "
              "réindustrialisation et de croissance.</p>"),
    section("locale", "CFE et fiscalité locale économique",
            "<p>La CFE sera traitée dans le cadre de la bascule vers la LVT "
            "professionnelle et de la réforme de la fiscalité locale&nbsp;: "
            "l’objectif est de ne plus taxer l’existence d’une activité "
            "productive, mais la <strong>valeur foncière réellement "
            "occupée</strong>.</p>"
            + "<p>Les taxes sectorielles sur chiffre d’affaires feront l’objet d’un "
              "audit général, avec <strong>suppression par défaut</strong> sauf "
              "justification claire liée à une externalité.</p>"),
    section("is", "L’impôt sur les sociétés : 25 %, puis 15 à 20 %",
            "<p>L’impôt sur les sociétés est maintenu au départ autour de son "
            "niveau actuel, soit environ <strong>25 %</strong>. Il doit ensuite "
            "converger vers une cible de <strong>15 à 20 %</strong>.</p>"
            + "<p>Cette baisse doit être financée par&nbsp;:</p>"
            + liste(["la suppression ou la réduction massive des niches&nbsp;;",
                     "l’élargissement de l’assiette&nbsp;;",
                     "la stabilité fiscale&nbsp;;",
                     "la croissance de l’investissement et des bases imposables."])),
    section("niches", "Un taux plus bas suppose une assiette plus propre",
            "<p>Le programme assume la suppression ou le recentrage massif des "
            "niches d’IS, et notamment du <strong>crédit d’impôt recherche</strong>. "
            "À terme, le CIR doit être supprimé.</p>"
            + "<p>L’innovation doit être financée par des instruments "
              "assumés&nbsp;:</p>"
            + liste(["la commande publique&nbsp;;", "les concours "
                     "technologiques&nbsp;;", "les achats publics innovants&nbsp;;",
                     "les marchés de précommercialisation&nbsp;;",
                     "les agences de financement de rupture&nbsp;;",
                     "les partenariats de recherche évalués."])
            + encadre("", "<p>Mieux vaut un IS bas et une commande publique "
                          "stratégique qu’un IS élevé mité par des niches fiscales "
                          "permanentes.</p>")),
    section("dividendes", "IS et dividendes : deux impositions, assumées",
            "<p>Les bénéfices distribués seront imposés deux fois&nbsp;: à l’IS, "
            "puis, en cas de distribution, à l’impôt proportionnel personnel.</p>"
            + "<p>La baisse progressive de l’IS vers 15-20 % vise précisément à "
              "éviter une taxation combinée excessive du capital productif. "
              "L’objectif n’est pas d’exonérer le capital, mais de ne pas "
              "pénaliser l’investissement productif par rapport à la consommation "
              "immédiate ou à la rente foncière.</p>"),
])


# -- carbone -----------------------------------------------------------------

CARBONE = "\n".join([
    plan([("principe", "Un signal-prix"), ("plancher", "Le prix plancher"),
          ("competitivite", "Compétitivité"), ("dividende", "Le dividende carbone"),
          ("electricite", "L’électricité"), ("reseau", "Le réseau")]),
    section("principe", "Un prix, plutôt qu’un plan",
            "<p>La fiscalité carbone doit fournir un signal-prix <strong>crédible, "
            "stable et lisible</strong>.</p>"
            + "<p>L’objectif n’est pas de planifier d’en haut la transition "
              "écologique, secteur par secteur, technologie par technologie. Il est "
              "d’envoyer aux ménages et aux entreprises un prix prévisible du "
              "carbone, pour que la transition se fasse autant que possible par "
              "adaptation organique&nbsp;: substitution technologique, "
              "électrification des usages, efficacité énergétique, innovation, "
              "sobriété choisie, investissement privé, adaptation des chaînes de "
              "valeur.</p>"
            + "<p>Le prix du carbone doit donc remplacer, autant que possible, la "
              "logique des normes, des interdictions, des subventions "
              "contradictoires et de la planification administrative.</p>"),
    section("plancher", "Un prix plancher pluriannuel, cible 200 €/tCO₂",
            "<p>Le programme défend un <strong>prix plancher carbone "
            "pluriannuel</strong>. La cible doctrinale de long terme est de "
            "l’ordre de <strong>200 €/tCO₂</strong>.</p>"
            + '<div class="note"><p>Cette cible est une <strong>boussole</strong>, '
              'non un choc fiscal immédiat. Elle est cohérente avec l’ordre de '
              'grandeur déjà atteint implicitement par la fiscalité des carburants '
              'routiers — mais elle doit être appliquée de manière plus lisible, '
              'plus homogène et mieux redistribuée.</p></div>'
            + "<p>Le prix plancher pourra compléter le marché européen du carbone "
              "lorsque celui-ci est insuffisant ou trop instable.</p>"),
    section("competitivite", "Ne pas déplacer les émissions",
            "<p>Une taxe carbone qui déplace les émissions plutôt que de les "
            "réduire ne rend service ni à l’économie ni au climat. Le programme "
            "assume donc une approche flexible&nbsp;:</p>"
            + liste(["priorité au marché carbone européen lorsque c’est "
                     "possible&nbsp;;",
                     "mécanismes d’ajustement aux frontières lorsque "
                     "nécessaire&nbsp;;",
                     "prise en compte des secteurs exposés à la concurrence "
                     "internationale&nbsp;;",
                     "trajectoire prévisible plutôt que chocs soudains&nbsp;;",
                     "suppression des exemptions injustifiées, mais prudence sur "
                     "les risques de fuite carbone&nbsp;;",
                     "coordination européenne autant que possible."])
            + encadre("", "<p>Un bon prix carbone doit orienter les choix "
                          "économiques, pas organiser la "
                          "désindustrialisation.</p>")),
    section("dividende", "La recette vous est rendue",
            "<p>Les recettes carbone seront reversées aux citoyens sous forme de "
            "<strong>dividende carbone</strong>. Il sera&nbsp;:</p>"
            + liste(["affiché séparément&nbsp;;",
                     "versé avec le revenu universel&nbsp;;",
                     "strictement fonction des recettes carbone collectées&nbsp;;",
                     "non indexé indépendamment."])
            + "<p>Si les émissions baissent et que les recettes diminuent, le "
              "dividende diminue aussi. L’État ne devient donc pas dépendant de la "
              "fiscalité carbone pour financer ses dépenses permanentes — ce qui "
              "est aujourd’hui le vice caché de toute taxe écologique de "
              "rendement.</p>"
            + encadre("", "<p>Le prix carbone renchérit les usages fossiles, mais "
                          "sa recette est rendue aux citoyens.</p>")
            + "<p>Les ménages modestes, qui émettent généralement moins que les "
              "ménages aisés, peuvent ainsi être <strong>bénéficiaires "
              "nets</strong> du dispositif.</p>"),
    section("electricite", "Pas de taxe spécifique sur l’électricité",
            "<p>L’électricité bas-carbone ne doit pas être pénalisée "
            "fiscalement&nbsp;: elle ne supportera pas de taxe spécifique de "
            "rendement hors TVA.</p>"
            + "<p>La fiscalité énergétique doit distinguer clairement les énergies "
              "fossiles, qui émettent du CO₂, et l’électricité bas-carbone, qui "
              "permet de décarboner les usages.</p>"
            + encadre("", "<p>Le signal-prix doit favoriser l’électrification "
                          "bas-carbone, non la pénaliser.</p>")),
    section("reseau", "Le réseau se paie en puissance, pas en kWh",
            "<p>Les coûts de réseau ne doivent pas être financés principalement par "
            "une taxation proportionnelle au kWh consommé&nbsp;: cela pénalise "
            "l’électrification et favorise des comportements de contournement.</p>"
            + "<p>Le financement devra reposer principalement sur&nbsp;:</p>"
            + liste(["une part fixe&nbsp;;", "la puissance souscrite&nbsp;;",
                     "la capacité d’accès au réseau&nbsp;;",
                     "éventuellement une contribution budgétaire de l’État lorsque "
                     "l’intérêt général le justifie."])
            + "<p>Ce modèle fait contribuer équitablement les "
              "autoconsommateurs — qui utilisent le réseau comme assurance "
              "collective — sans les exonérer de fait du coût de "
              "l’infrastructure.</p>"
            + encadre("", "<p>Le réseau est une infrastructure de puissance et de "
                          "sécurité d’approvisionnement&nbsp;; son coût ne doit pas "
                          "être dissimulé dans une pénalisation du kWh "
                          "décarboné.</p>")),
])


# -- transmissions -----------------------------------------------------------

TABLE_CRUC = tableau(
    ["Étape", "Traitement fiscal"],
    [["Versement", "Revenu déjà taxé"],
     ["Capitalisation", "Exonérée"],
     ["Sortie", "Exonérée"]],
    legende="Le régime « TEE » du Compte Retraite Universel Capitalisé : l’État ne "
            "taxe l’épargne retraite qu’une seule fois.",
)

TRANSMISSIONS = "\n".join([
    plan([("receveur", "Imposer le receveur"), ("effets", "Ce que ça change"),
          ("illiquides", "Actifs illiquides"), ("entreprise", "Transmission d’entreprise"),
          ("cruc", "Épargne retraite (CRUC)"), ("exit", "Exit tax"),
          ("non-residents", "Non-résidents")]),
    section("receveur", "Ce qui compte, c’est ce que vous recevez",
            "<p>Les donations et successions seront fusionnées dans un même "
            "régime, et imposées <strong>chez le receveur</strong> — non selon le "
            "lien de parenté.</p>"
            + "<p>Chaque individu disposera d’un <strong>compte de réception "
              "patrimoniale</strong> sur l’ensemble de sa vie, doté d’un "
              "<strong>abattement universel de 100 000 €</strong>. Au-delà, les "
              "transmissions reçues sont imposées au taux proportionnel commun — le "
              "même que celui des revenus.</p>"
            + encadre("", "<p>Ce qui compte n’est pas le lien familial avec le "
                          "donateur, mais le montant reçu par l’individu au cours "
                          "de sa vie.</p>")),
    section("effets", "Ce que ça change",
            liste(["simplifier radicalement les droits de succession&nbsp;;",
                   "supprimer les écarts arbitraires selon le lien familial&nbsp;;",
                   "protéger les petites transmissions&nbsp;;",
                   "favoriser indirectement les familles nombreuses, chaque enfant "
                   "disposant de son propre abattement&nbsp;;",
                   "éviter les taux confiscatoires&nbsp;;",
                   "réduire les incitations à l’exil patrimonial&nbsp;;",
                   "mieux traiter les transmissions hors cadre familial "
                   "traditionnel."])),
    section("illiquides", "Un impôt qui ne force pas à vendre",
            "<p>Pour les actifs illiquides, l’impôt pourra être étalé ou "
            "reporté&nbsp;: résidence principale, terres agricoles, forêts, parts "
            "d’entreprise non cotée, biens professionnels, actifs difficiles à "
            "vendre sans destruction de valeur.</p>"
            + "<p>Il pourra être garanti par une créance sur l’actif, récupérée à la "
              "cession ou à la succession suivante. Le but est d’éviter les ventes "
              "forcées tout en maintenant le principe d’imposition.</p>"),
    section("entreprise", "Protéger l’entreprise, pas l’enveloppe",
            "<p>La transmission d’une entreprise ne doit pas provoquer la vente "
            "forcée d’une activité productive. Mais elle ne doit pas devenir un "
            "véhicule d’optimisation permettant de transformer une fortune "
            "patrimoniale en transmission exonérée.</p>"
            + "<p>La doctrine distingue donc les <strong>actifs professionnels "
              "nécessaires à l’exploitation</strong> et les <strong>actifs "
              "patrimoniaux passifs</strong> logés dans une société. Le régime "
              "favorable ne concerne que les premiers.</p>"
            + "<h3>Report d’imposition (<i>carry-over basis</i>)</h3>"
            + liste(["il n’y a pas d’imposition immédiate si l’activité est "
                     "conservée&nbsp;;",
                     "le receveur reprend la base fiscale historique du "
                     "donateur&nbsp;;",
                     "la plus-value latente n’est pas effacée&nbsp;;",
                     "l’imposition est reportée jusqu’à la cession."])
            + "<p>Ce mécanisme évite de tuer les entreprises au moment de la "
              "transmission, tout en empêchant l’effacement fiscal pur et simple "
              "des plus-values latentes.</p>"
            + "<h3>En cas de cession</h3>"
            + "<p>La plus-value latente est imposée selon le régime commun&nbsp;; "
              "la plus-value créée après transmission est imposée chez le "
              "receveur&nbsp;; un étalement peut être prévu si la cession répond à "
              "un motif économique légitime&nbsp;: cession à un salarié ou à un "
              "repreneur industriel, restructuration nécessaire, recapitalisation, "
              "cession partielle pour régler une dette fiscale, sauvegarde de "
              "l’activité. Les cessions purement patrimoniales ne bénéficient "
              "d’aucun régime préférentiel automatique.</p>"
            + "<h3>Ce que le régime favorable exclut</h3>"
            + liste(["les holdings patrimoniales passives&nbsp;;",
                     "l’immobilier locatif logé artificiellement dans une "
                     "société&nbsp;;",
                     "les portefeuilles financiers passifs&nbsp;;",
                     "la trésorerie excessive non nécessaire à "
                     "l’exploitation&nbsp;;",
                     "les actifs de jouissance&nbsp;;",
                     "les structures sans substance économique."])
            + encadre("", "<p>On protège l’entreprise productive, pas l’enveloppe "
                          "patrimoniale.</p>")),
    section("cruc", "Le Compte Retraite Universel Capitalisé",
            "<p>Le programme crée un <strong>Compte Retraite Universel "
            "Capitalisé</strong> (CRUC), destiné à accompagner la montée en "
            "puissance d’un pilier de retraite par capitalisation, en complément du "
            "socle de répartition. Il doit être simple, portable, universel, peu "
            "coûteux, fiscalement stable, investi à long terme et accessible à tous "
            "les statuts.</p>"
            + TABLE_CRUC
            + "<p>Ce modèle est plus lisible qu’un régime d’exonération à l’entrée, "
              "qui peut être perçu comme une niche pour hauts revenus.</p>"
            + encadre("", "<p>Vous avez payé l’impôt une fois&nbsp;; l’épargne "
                          "longue vous appartient.</p>")
            + "<p>Le CRUC sera ouvert automatiquement à chaque adulte, alimenté par "
              "versements volontaires, abondable par l’employeur, portable entre "
              "statuts, investi par défaut dans des fonds diversifiés à horizon de "
              "retraite, assorti de frais plafonnés et soumis à des règles de sortie "
              "retraite. Pour les salariés, une adhésion par défaut avec possibilité "
              "de sortie pourra être envisagée&nbsp;: une montée en puissance "
              "progressive, sans obligation brutale.</p>"
            + '<div class="note entree"><p>Le pilier par répartition, lui, fait '
              'l’objet d’un programme et d’un simulateur à part.</p>'
              '<p class="actions"><a class="bouton" '
              'href="https://g-pliberal.github.io/retraitecomptenotionelle/">'
              'Le programme retraites</a></p></div>'),
    section("exit", "L’exit tax est supprimée",
            "<p>Dans un système fiscal compétitif, stable et modéré, l’exit tax "
            "devient inutile. Elle sera supprimée.</p>"
            + "<p>L’objectif n’est pas de retenir les contribuables par la menace, "
              "mais par l’attractivité du système fiscal. Les dispositifs "
              "anti-fraude de droit commun resteront applicables aux montages "
              "artificiels dépourvus de substance économique.</p>"
            + encadre("", "<p>Un pays fiscalement compétitif n’a pas besoin de "
                          "construire des murs à la sortie.</p>")),
    section("non-residents", "Les non-résidents restent imposés sur leurs bases françaises",
            "<p>La suppression de l’exit tax ne signifie pas l’abandon de toute "
            "souveraineté fiscale. Resteront imposés en France, selon les "
            "conventions fiscales applicables&nbsp;:</p>"
            + liste(["les revenus de source française&nbsp;;",
                     "le foncier situé en France&nbsp;;",
                     "les entreprises imposables en France&nbsp;;",
                     "les établissements stables&nbsp;;",
                     "les transmissions portant sur des actifs français ou reçues "
                     "par des résidents français, selon les règles à définir."])
            + encadre("", "<p>Pas de fiscalité punitive du départ, mais une "
                          "imposition normale des bases économiques "
                          "françaises.</p>")),
])


# -- calendrier --------------------------------------------------------------

TABLE_PAIE = tableau(
    ["Niveau", "Signification"],
    [["Salaire complet", "Coût total payé par l’employeur"],
     ["Cotisations contributives", "Droits individualisables ouverts"],
     ["Impôt général", "Financement de la solidarité et des biens publics"],
     ["Revenu universel", "Transfert universel reçu"],
     ["Salaire disponible", "Revenu réellement disponible"]],
    legende="La fiche de paie cible : cinq lignes, dont chacune répond à une "
            "question que la fiche actuelle laisse sans réponse.",
)

TABLE_MASSES = tableau(
    ["Poste", "Ordre de grandeur / orientation"],
    [["Impôt proportionnel IR-CSG-CRDS", "Taux à calibrer, objectif &lt; 30 %"],
     ["TVA à taux unique de 25 %",
      "Rendement majeur, supérieur au système actuel selon l’assiette"],
     ["LVT à 2 %", "Environ 120 Md€ visés, à évaluer"],
     ["Impôt sur les sociétés", "Maintien initial autour de 25 %, cible 15-20 %"],
     ["Suppression des DMTO", "Coût brut important, assumé pour la mobilité"],
     ["Suppression de la C3S", "Coût brut limité, effet pro-production fort"],
     ["Suppression de la CVAE résiduelle", "Cohérence pro-production"],
     ["Dividende carbone", "Ne pèse pas sur le budget net : recette reversée"],
     ["CRUC", "Coût fiscal limité en TEE, les versements n’étant pas déductibles"],
     ["Successions et donations", "Rendement à calibrer selon abattement et taux"]],
    legende="Les montants ci-dessous sont des masses de travail à consolider, pas "
            "un chiffrage définitif.",
)

CALENDRIER = "\n".join([
    plan([("deux", "Deux catégories"), ("an1", "Année 1"), ("an23", "Années 2 et 3"),
          ("an45", "Années 4 et 5"), ("paie", "La fiche de paie"),
          ("masses", "Ordres de grandeur")]),
    section("deux", "Deux catégories d’impôts",
            "<p>La réforme distingue les impôts assez nocifs pour être supprimés "
            "<strong>immédiatement</strong>, et ceux qu’on fait "
            "<strong>converger progressivement</strong> vers le système cible.</p>"
            + '<div class="bascules">'
              '<div class="colonne cible"><h3>Supprimés immédiatement</h3>'
            + liste(["les DMTO&nbsp;;", "la C3S&nbsp;;",
                     "la CVAE résiduelle&nbsp;;", "l’exit tax&nbsp;;",
                     "la fiscalité spécifique des plus-values immobilières&nbsp;;",
                     "les premières petites taxes redondantes et à faible "
                     "rendement."])
            + '</div><div class="colonne"><h3>Convergence progressive</h3>'
            + liste(["la TVA vers un taux unique de 25 %&nbsp;;",
                     "la LVT vers son taux cible de 2 %&nbsp;;",
                     "l’IS vers 15-20 %&nbsp;;",
                     "la suppression des niches&nbsp;;",
                     "l’extinction du CIR&nbsp;;",
                     "la réforme de la fiscalité locale&nbsp;;",
                     "le financement des réseaux électriques par part fixe de "
                     "puissance&nbsp;;",
                     "la bascule des cotisations non contributives vers l’impôt "
                     "général."])
            + "</div></div>"),
    section("an1", "Année 1 : on supprime, et on prépare",
            liste(["suppression des DMTO&nbsp;;", "suppression de la C3S&nbsp;;",
                   "suppression de la CVAE résiduelle&nbsp;;",
                   "suppression de l’exit tax&nbsp;;",
                   "lancement du cadastre foncier économique&nbsp;;",
                   "préparation administrative de la LVT&nbsp;;",
                   "audit des niches fiscales&nbsp;;",
                   "première réforme de la fiche de paie&nbsp;;",
                   "annonce de la trajectoire TVA / LVT / IS / carbone."])),
    section("an23", "Années 2 et 3 : la bascule",
            liste(["montée en charge progressive de la LVT&nbsp;;",
                   "convergence de la TVA vers le taux unique&nbsp;;",
                   "mise en place du revenu universel&nbsp;;",
                   "fusion IR-CSG-CRDS&nbsp;;",
                   "suppression progressive des niches&nbsp;;",
                   "réforme de la fiscalité locale&nbsp;;",
                   "bascule des financements santé universels vers l’impôt&nbsp;;",
                   "montée en puissance du CRUC&nbsp;;",
                   "introduction du dividende carbone."])),
    section("an45", "Années 4 et 5 : on stabilise",
            liste(["IS convergeant vers 15-20 %&nbsp;;",
                   "extinction du CIR&nbsp;;",
                   "stabilisation du système fiscal&nbsp;;",
                   "évaluation de la LVT&nbsp;;",
                   "baisse possible du taux proportionnel si la croissance et les "
                   "dépenses le permettent&nbsp;;",
                   "simplification résiduelle."])
            + '<div class="note"><p>La stabilité est un élément du programme, pas '
              'une conséquence&nbsp;: un système fiscal qui change tous les ans '
              'coûte cher même quand ses taux sont bas.</p></div>'),
    section("paie", "La fiche de paie doit dire la vérité",
            "<p>La distinction entre cotisations salariales et patronales entretient "
            "une illusion&nbsp;: le salarié ne voit pas le coût total de son "
            "emploi.</p>"
            + TABLE_PAIE
            + "<p>Le citoyen doit pouvoir comprendre ce que coûte son emploi, ce qui "
              "finance ses droits, ce qui finance la solidarité, et ce qu’il reçoit "
              "de la solidarité nationale.</p>"),
    section("masses", "Les ordres de grandeur",
            TABLE_MASSES
            + "<p>Le bouclage budgétaire ne doit pas être recherché impôt par impôt, "
              "mais au niveau du système global&nbsp;: hausse d’assiettes larges, "
              "suppression d’impôts nocifs, simplification, réduction des niches, "
              "meilleure croissance potentielle, réforme de la dépense sociale, "
              "stabilisation fiscale.</p>"),
])


# -- objections --------------------------------------------------------------

OBJECTIONS_TEXTE = [
    ("La TVA à 25 % est injuste",
     "<p>La TVA prise isolément peut être régressive. Mais notre système ne la "
     "prend pas isolément&nbsp;: elle finance un revenu universel.</p>"
     "<p>La justice sociale ne passe plus par des taux réduits invisibles, mais par "
     "un transfert monétaire explicite. Un ménage modeste reçoit le revenu universel "
     "et le dividende carbone&nbsp;: il est protégé directement, plutôt que par "
     "l’espoir incertain qu’un taux réduit soit intégralement répercuté dans les "
     "prix.</p>"),
    ("L’impôt proportionnel n’est pas progressif",
     "<p>Le taux est proportionnel, mais le système est progressif.</p>"
     "<p>Le revenu universel transforme l’ensemble impôt + transfert en système "
     "progressif&nbsp;: les bas revenus sont bénéficiaires nets, les hauts revenus "
     "contributeurs nets. La progressivité est simplement rendue "
     "<a href=\"revenus.html#progressivite\">lisible</a>.</p>"),
    ("La LVT va faire exploser les charges des propriétaires",
     "<p>La LVT <strong>remplace</strong> des impôts existants&nbsp;: taxe foncière, "
     "DMTO, IFI, taxes sur la vacance, fiscalité des plus-values. Elle ne s’ajoute "
     "pas à l’ancien système.</p>"
     "<p>Par ailleurs, elle taxe la valeur du terrain, non le bâtiment&nbsp;: elle ne "
     "pénalise donc ni la construction, ni la rénovation, ni la densification. Des "
     "mécanismes de report sont prévus pour les premières années et en cas de mise en "
     "vente du bien.</p>"),
    ("Les propriétaires vont répercuter la LVT sur les loyers",
     "<p>Une taxe sur le foncier pur ne se répercute pas comme une taxe ordinaire. Le "
     "propriétaire ne peut pas augmenter le loyer simplement parce que son impôt "
     "augmente&nbsp;: le loyer dépend de la demande solvable et de l’offre "
     "disponible.</p>"
     "<p>À long terme, la LVT se capitalise principalement dans la valeur du "
     "terrain&nbsp;: elle réduit le prix du foncier et incite à mieux utiliser les "
     "terrains rares.</p>"),
    ("Supprimer les DMTO coûte trop cher",
     "<p>Les DMTO sont l’un des impôts les plus destructeurs&nbsp;: ils bloquent la "
     "mobilité résidentielle, freinent les transactions et pénalisent le changement "
     "d’emploi ou de logement.</p>"
     "<p>Leur suppression immédiate est un choix pro-croissance et pro-mobilité. La "
     "compensation sera traitée dans la réforme globale des collectivités "
     "territoriales.</p>"),
    ("La fiscalité carbone pénalise les modestes",
     "<p>La recette carbone est reversée sous forme de dividende carbone.</p>"
     "<p>Les ménages modestes étant en moyenne moins émetteurs que les ménages aisés, "
     "ils peuvent être bénéficiaires nets. Le signal-prix est maintenu, mais la "
     "recette est rendue aux citoyens.</p>"),
    ("La baisse de l’IS est un cadeau aux entreprises",
     "<p>La baisse de l’IS accompagne la suppression des niches.</p>"
     "<p>Le système cible est plus simple&nbsp;: moins de niches, moins "
     "d’optimisation, taux plus bas, assiette plus large. Ce n’est pas un cadeau "
     "sectoriel, mais une stratégie pro-investissement.</p>"),
    ("La suppression de l’exit tax favorise l’exil fiscal",
     "<p>L’exit tax est un aveu d’échec&nbsp;: elle tente de retenir les "
     "contribuables par la contrainte.</p>"
     "<p>Notre objectif est inverse&nbsp;: rendre le système fiscal suffisamment "
     "compétitif et stable pour que les contribuables n’aient pas intérêt à partir. "
     "Les montages artificiels resteront combattus par les règles anti-fraude de "
     "droit commun.</p>"),
]


def objections() -> str:
    blocs = []
    for i, (question, reponse) in enumerate(OBJECTIONS_TEXTE, 1):
        blocs.append(
            f'<section class="cle objection" id="objection-{i}" '
            f'aria-labelledby="titre-{i}">'
            f'<h3 class="question" id="titre-{i}">« {question} »</h3>'
            f'<div class="reponse">{reponse}</div></section>'
        )
    return "\n".join(blocs)


OBJECTIONS = "\n".join([
    "<p>Huit objections reviennent toujours, et aucune n’est absurde. Voici ce que "
    "le programme leur répond — sans esquive, et sans prétendre qu’un choix fiscal "
    "n’a jamais de contrepartie.</p>",
    objections(),
])


# -- glossaire ---------------------------------------------------------------
#
# Un programme fiscal parle une langue que personne n'apprend à l'école. Les
# sigles ci-dessous sont tous employés par la note : le glossaire ne les
# commente pas, il les traduit.

TERMES = [
    ("Assiette",
     "Ce sur quoi l’impôt est calculé. Élargir l’assiette, c’est taxer plus de "
     "choses — ce qui permet de baisser le taux à rendement égal."),
    ("C3S",
     "Contribution sociale de solidarité des sociétés. Elle porte sur le "
     "<em>chiffre d’affaires</em>, donc se paie même quand l’entreprise perd de "
     "l’argent. Supprimée immédiatement."),
    ("CFE",
     "Cotisation foncière des entreprises. Traitée dans le cadre de la bascule "
     "vers une LVT professionnelle&nbsp;: on taxerait la valeur foncière occupée, "
     "non l’existence de l’activité."),
    ("CIR",
     "Crédit d’impôt recherche. Le programme le supprime à terme, et finance "
     "l’innovation par des instruments assumés — commande publique, concours, "
     "agences de rupture — plutôt que par une niche fiscale permanente."),
    ("CRUC",
     "Compte Retraite Universel Capitalisé. Un compte d’épargne retraite "
     "universel, portable, à frais plafonnés, en régime TEE."),
    ("CSG / CRDS",
     "Deux prélèvements sur les revenus qui n’ouvrent aucun droit contributif "
     "individualisé. Le programme les appelle donc ce qu’ils sont — de l’impôt — "
     "et les fusionne dans l’impôt proportionnel."),
    ("CVAE",
     "Cotisation sur la valeur ajoutée des entreprises. Sa part résiduelle est "
     "supprimée immédiatement&nbsp;: elle taxe la valeur ajoutée productive, "
     "rentable ou non."),
    ("Dividende carbone",
     "Le reversement aux citoyens de la recette de la fiscalité carbone. Affiché "
     "séparément, versé avec le revenu universel, et strictement égal à ce qui a "
     "été collecté&nbsp;: si les émissions baissent, il baisse."),
    ("DMTO",
     "Droits de mutation à titre onéreux&nbsp;: l’impôt payé lors de l’achat d’un "
     "logement, souvent confondu avec les «&nbsp;frais de notaire&nbsp;». Ce sont "
     "les droits qui sont supprimés, pas les émoluments du notaire."),
    ("Effet de seuil",
     "Le moment où gagner un euro de plus fait perdre davantage en impôt ou en "
     "aides. Un impôt proportionnel assorti d’un revenu universel n’en produit "
     "aucun&nbsp;: c’est l’argument central du dispositif."),
    ("Exit tax",
     "L’imposition déclenchée par le départ d’un contribuable à l’étranger. "
     "Supprimée&nbsp;: le programme mise sur l’attractivité, pas sur la "
     "contrainte."),
    ("IFI",
     "Impôt sur la fortune immobilière. Supprimé, absorbé par la LVT."),
    ("LVT (<i>Land Value Tax</i>)",
     "Une taxe annuelle sur la valeur du <strong>terrain nu</strong>, hors "
     "bâtiment. Elle frappe la rente d’emplacement — créée par la rareté du sol et "
     "les équipements publics — et pas ce que le propriétaire a construit."),
    ("Plus-value latente",
     "Un gain existant sur le papier, tant que le bien n’est pas vendu. Le "
     "<i>carry-over basis</i> ne l’efface pas&nbsp;: il en reporte l’imposition à "
     "la cession."),
    ("Prix plancher carbone",
     "Un prix minimum garanti de la tonne de CO₂, fixé pour plusieurs années, qui "
     "complète le marché européen quand celui-ci est trop bas ou trop instable. "
     "Cible doctrinale&nbsp;: de l’ordre de 200 €/tCO₂."),
    ("Progressivité",
     "Le fait que le taux moyen d’imposition augmente avec le revenu. Elle peut "
     "venir d’un barème à tranches, ou — comme ici — d’un taux unique combiné à un "
     "versement forfaitaire."),
    ("Rente",
     "Un revenu qui ne rémunère aucune production&nbsp;: typiquement, la valeur "
     "qu’un terrain gagne parce qu’un tramway passe à côté. La doctrine du "
     "programme est de taxer la rente plutôt que la production."),
    ("Revenu universel (RU)",
     "Un versement sans condition à chaque citoyen, indexé sur le PIB réel par "
     "habitant, lissé sur trois ans. C’est lui qui rend le système progressif, et "
     "lui qui remplace les taux réduits comme instrument de justice sociale."),
    ("TEE",
     "«&nbsp;Taxé, exonéré, exonéré&nbsp;»&nbsp;: on verse de l’argent déjà "
     "imposé, la capitalisation n’est pas taxée, la sortie ne l’est pas non plus. "
     "Le régime fiscal du CRUC."),
    ("Taux marginal / taux moyen",
     "Le taux marginal porte sur le dernier euro gagné&nbsp;; le taux moyen sur "
     "l’ensemble du revenu. Dans ce programme le premier est constant, le second "
     "augmente&nbsp;: c’est exactement ce que fait le revenu universel."),
]

GLOSSAIRE = "\n".join([
    "<p>Un programme fiscal parle une langue que personne n’apprend à l’école. "
    "Voici, en clair, les vingt termes employés sur ce site.</p>",
    '<dl class="glossaire">',
    "\n".join(f"  <dt>{terme}</dt>\n  <dd>{definition}</dd>"
              for terme, definition in TERMES),
    "</dl>",
    '<p class="actions"><a class="bouton" href="index.html">Revenir au '
    "programme</a></p>",
])


# -- les pages ---------------------------------------------------------------

# -- le simulateur -----------------------------------------------------------
#
# Il a longtemps tenu sur trois champs, et ne montrait que l'impôt et le revenu
# universel. C'était la moitié favorable de la réforme, sur un site dont l'objet
# est la transparence : la TVA à 25 %, la LVT et le prix du carbone en étaient
# absents, et c'est par là qu'on l'aurait pris en défaut. Il en montre cinq.
#
# Les hypothèses que le lecteur ne peut pas connaître — la part de son panier
# soumise à TVA, la part du terrain dans la valeur de son logement — ne lui sont
# pas demandées : elles sont écrites dans `moteur/calculette.js`, en clair, et
# rappelées sous le résultat.

FORMULAIRE = """<form id="formulaire" novalidate>
  <fieldset>
    <legend>Votre foyer</legend>
    <div class="champs">
    <p><label for="adultes">Adultes</label>
    <input type="number" id="adultes" name="adultes" value="2" min="1" max="2"
           step="1" inputmode="numeric"></p>
    <p><label for="enfants">Enfants à charge</label>
    <input type="number" id="enfants" name="enfants" value="2" min="0" max="12"
           step="1" inputmode="numeric"></p>
    <p><label for="nature">Nature des revenus</label>
    <select id="nature" name="nature">
      <option value="activite">Salaires ou activité</option>
      <option value="pension">Pensions de retraite</option>
    </select></p>
    <p><label for="revenu">Revenus annuels du foyer</label>
    <input type="number" id="revenu" name="revenu" value="42000" min="0"
           max="100000000" step="500" inputmode="numeric"></p>
    <p><label for="capital">Dont revenus du capital</label>
    <input type="number" id="capital" name="capital" value="0" min="0"
           max="100000000" step="500" inputmode="numeric"></p>
    <p><label for="prestations">Prestations reçues (€/mois)</label>
    <input type="number" id="prestations" name="prestations" value="350" min="0"
           max="10000" step="10" inputmode="numeric"></p>
    </div>
  </fieldset>
  <fieldset>
    <legend>Ce que vous dépensez, ce que vous possédez</legend>
    <div class="champs">
    <p><label for="epargne">Part du revenu épargnée (%)</label>
    <input type="number" id="epargne" name="epargne" value="5" min="0" max="90"
           step="1" inputmode="numeric"></p>
    <p><label for="logement">Valeur de votre logement</label>
    <input type="number" id="logement" name="logement" value="0" min="0"
           max="100000000" step="10000" inputmode="numeric"></p>
    <p><label for="chauffage">Chauffage</label>
    <select id="chauffage" name="chauffage">
      <option value="gaz">Gaz</option>
      <option value="fioul">Fioul</option>
      <option value="aucun">Électricité, bois ou réseau</option>
    </select></p>
    <p><label for="kilometres">Kilomètres en voiture par an</label>
    <input type="number" id="kilometres" name="kilometres" value="12000" min="0"
           max="200000" step="500" inputmode="numeric"></p>
    </div>
  </fieldset>
  <details>
    <summary>Les hypothèses du programme</summary>
    <p class="discret">Aucune n’est un chiffre arrêté&nbsp;: la note les donne
    comme des cibles de travail, et vous pouvez les déplacer.</p>
    <div class="champs">
      <p><label for="taux-impot">Impôt proportionnel (%)</label>
      <input type="number" id="taux-impot" name="taux" value="34" min="0" max="60"
             step="0.5" inputmode="decimal"></p>
      <p><label for="ru">Revenu universel (€/mois)</label>
      <input type="number" id="ru" name="ru" value="600" min="0" max="5000"
             step="10" inputmode="numeric"></p>
      <p><label for="ru-enfant">Revenu universel enfant (€/mois)</label>
      <input type="number" id="ru-enfant" name="ru-enfant" value="300" min="0"
             max="5000" step="10" inputmode="numeric"></p>
      <p><label for="tva">TVA (%)</label>
      <input type="number" id="tva" name="tva" value="25" min="0" max="40"
             step="0.5" inputmode="decimal"></p>
      <p><label for="lvt">Land Value Tax (%)</label>
      <input type="number" id="lvt" name="lvt" value="2" min="0" max="10"
             step="0.1" inputmode="decimal"></p>
      <p><label for="carbone">Prix du carbone (€/t)</label>
      <input type="number" id="carbone" name="carbone" value="200" min="0"
             max="1000" step="10" inputmode="numeric"></p>
    </div>
  </details>
</form>"""

RESULTAT = """<div class="fiches reperes" id="resultat" aria-live="polite">
  <div class="fiche"><p class="etiquette">Solde annuel</p>
  <p class="valeur" id="r-solde">—</p>
  <p class="precision sens" id="r-sens">—</p></div>
  <div class="fiche"><p class="etiquette">Part du revenu disponible</p>
  <p class="valeur" id="r-part">—</p>
  <p class="precision">Ce que le solde pèse dans ce dont vous disposez
  aujourd’hui.</p></div>
  <div class="fiche"><p class="etiquette">Impôt direct seul</p>
  <p class="valeur" id="r-impot">—</p>
  <p class="precision">Ce que l’ancien simulateur montrait, et rien de
  plus.</p></div>
  <div class="fiche"><p class="etiquette">Valeur de votre terrain</p>
  <p class="valeur" id="r-capital">—</p>
  <p class="precision">Une fois, pas chaque année&nbsp;: la LVT se capitalise
  dans le prix du sol.</p></div>
</div>"""

CASCADE = """<div class="cascade">
  <div class="defilant" id="cascade" tabindex="0"></div>
  <p class="lecture" id="lecture" hidden></p>
  <p class="aide-clavier">Flèches gauche et droite pour parcourir les marches,
  Échap pour quitter.</p>
  <ul class="legende">
    <li><span class="pastille ecart-plus"></span> Ce que vous gagnez</li>
    <li><span class="pastille ecart-moins"></span> Ce que vous perdez</li>
  </ul>
</div>"""

SIMULATEUR = "\n".join([
    plan([("votre-cas", "Votre cas"), ("canaux", "Les cinq canaux"),
          ("hypotheses", "Ce que le calcul suppose"),
          ("limites", "Ce qu’il ne dit pas")]),
    section("votre-cas", "Ce que le programme changerait pour vous",
            "<p>Le calcul se fait dans votre navigateur&nbsp;: rien n’est "
            "envoyé, rien n’est enregistré, et il n’y a pas de serveur à qui "
            "vos réponses pourraient partir.</p>"
            "<p>Il compare deux systèmes fiscaux entiers sur le même ménage. "
            "Le vôtre d’aujourd’hui est calculé depuis le barème en "
            "vigueur — décote comprise, et net des réductions et crédits "
            "d’impôt. Le système cible est celui de la note.</p>"
            + '<div class="creme calculette" id="calculette">'
            + FORMULAIRE + RESULTAT + CASCADE
            + "<p class=\"discret\">La cascade part de zéro et ajoute les cinq "
              "canaux l’un après l’autre&nbsp;; la dernière colonne est leur "
              "somme. Survolez une marche, ou parcourez-les au clavier, pour "
              "lire ce qu’elle recouvre.</p>"
            + "<noscript>" + tableau(
                ["Canal", "Effet sur l’année"],
                [["Impôt direct", "− 10 277 €"],
                 ["Transferts", "+ 17 400 €"],
                 ["TVA", "− 2 251 €"],
                 ["Logement", "0 €"],
                 ["Énergie", "+ 164 €"],
                 ["<strong>Solde</strong>", "<strong>+ 5 036 €</strong>"]],
                legende="Le simulateur a besoin de JavaScript. À défaut, voici "
                        "le même calcul pour le ménage par défaut du "
                        "formulaire : deux adultes, deux enfants, 42 000 € de "
                        "revenus, 350 € de prestations par mois, locataires, "
                        "chauffage au gaz, 12 000 km par an.") + "</noscript>"
            + "</div>"),
    section("canaux", "Les cinq canaux, et pourquoi il en faut cinq",
            "<p>Une réforme fiscale n’atteint pas un ménage par un seul "
            "chemin. Ne montrer que l’impôt sur le revenu et le revenu "
            "universel — ce que faisait ce simulateur jusqu’ici — revient à "
            "n’en montrer que la moitié favorable&nbsp;:</p>"
            + tableau(
                ["Canal", "Aujourd’hui", "Dans le système cible"],
                [["Impôt direct", "IR, CSG, CRDS, prélèvements sociaux",
                  "Un impôt proportionnel unique"],
                 ["Transferts", "RSA, prime d’activité, prestations familiales, APL",
                  "Le revenu universel, adulte et enfant"],
                 ["Consommation", "TVA à 20 %, 10 %, 5,5 % et 2,1 %",
                  "TVA à taux unique de 25 %"],
                 ["Logement", "Taxe foncière, droits de mutation, IFI",
                  "Land Value Tax sur le terrain nu"],
                 ["Énergie", "TICPE et taxes sectorielles",
                  "Prix plancher du carbone, et dividende rendu"]],
                legende="Les cinq canaux du simulateur. Les droits de mutation "
                        "y sont lissés sur la durée moyenne de détention : on "
                        "les paie tous les quarante ans, et une table annuelle "
                        "ne saurait les montrer autrement.")
            + "<p>Le tableau des cas types de la note montre que le classement "
              "d’un ménage change selon les canaux retenus&nbsp;: un "
              "propriétaire âgé gagne sur les flux et perd sur son patrimoine, "
              "un ménage rural perd sur l’énergie et regagne ailleurs. C’est "
              "pour cela qu’ils sont tous les cinq ici.</p>"),
    section("hypotheses", "Ce que le calcul suppose",
            "<p>Trois grandeurs ne vous sont pas demandées, parce que personne "
            "ne les connaît de mémoire. Elles sont posées, et les voici&nbsp;:</p>"
            + liste([
                "<strong>80 %</strong> de votre dépense porte de la "
                "TVA&nbsp;; le loyer, la santé et l’école n’en portent pas.",
                "<strong>16,8 %</strong> est le taux moyen que vous supportez "
                "aujourd’hui, tous taux réduits confondus.",
                "<strong>La moitié</strong> de la valeur d’un logement est "
                "celle du terrain — c’est une moyenne nationale, et elle est "
                "bien plus élevée dans les grandes villes.",
                "<strong>36 %</strong> est la part de valeur qu’une LVT de 2 % "
                "retire au terrain, en se capitalisant dans son prix. C’est "
                "l’argument du programme, et il vaut aussi pour l’assiette de "
                "l’impôt.",
                "<strong>421 €</strong> par adulte est le dividende carbone, "
                "soit la recette du prix plancher rendue aux citoyens.",
            ])
            + "<p>Le panier de consommation est tenu constant en volume&nbsp;: "
              "on compare deux fiscalités sur la même dépense hors taxe, et non "
              "deux niveaux de vie différents.</p>"),
    section("limites", "Ce que ce simulateur ne dit pas",
            "<p>Il calcule un ménage moyen, pas votre feuille d’impôt. Il "
            "ignore&nbsp;:</p>"
            + liste([
                "les cotisations contributives, qui ne changent pas&nbsp;;",
                "les droits de succession, qui ne sont pas annuels — et qui, "
                "pour une transmission, pèsent plus lourd que tout le "
                "reste&nbsp;;",
                "les effets de la réforme sur les prix, les salaires et "
                "l’emploi, qui sont réels et qu’aucun calcul à comportements "
                "inchangés ne peut donner&nbsp;;",
                "votre situation propre, dès qu’elle sort de la moyenne.",
            ])
            + "<p>Un simulateur qui prétendrait davantage mentirait. "
              "Celui-ci dit d’où viennent ses chiffres, et c’est à cela qu’on "
              "juge un chiffrage.</p>"),
])


PAGES = [
    ("index.html", "Programme fiscal — Parti libéral français",
     "Taxer moins le travail,<br> mieux la rente,<br> et redistribuer simplement",
     "Nous remettrons à plat le système fiscal français&nbsp;: un impôt "
     "proportionnel unique rendu progressif par un revenu universel, une TVA à "
     "taux unique, une taxe sur la valeur du foncier à la place de l’empilement "
     "immobilier, et la suppression immédiate des impôts qui punissent la "
     "production.",
     "Le chapitre Fiscalité du programme du Parti libéral français, expliqué "
     "page par page : impôt proportionnel, revenu universel, TVA à taux unique, "
     "Land Value Tax, fiscalité carbone rendue aux citoyens.",
     ACCUEIL),
    ("principes.html", "Principes directeurs",
     "Trois choses qu’on a cessé de distinguer",
     "Impôt, cotisation, redistribution&nbsp;: le système actuel mélange trois "
     "logiques. Les séparer est le premier geste de la réforme, parce que c’est "
     "lui qui rend tous les autres lisibles.",
     "Les trois principes du programme fiscal : séparer impôt, cotisation et "
     "redistribution ; taxer moins les bases productives ; supprimer l’illusion "
     "de la gratuité.",
     PRINCIPES),
    ("revenus.html", "Impôt sur les revenus",
     "Un seul impôt, un seul taux,<br> et un revenu universel",
     "L’impôt sur le revenu, la CSG et la CRDS fusionnent dans un impôt "
     "proportionnel unique. Le barème disparaît, la progressivité reste&nbsp;: "
     "c’est le revenu universel qui la porte.",
     "Fusion IR-CSG-CRDS en un impôt proportionnel sous 30 %, assiette large, "
     "individualisation complète, et revenu universel : le calcul, chiffre par "
     "chiffre.",
     REVENUS),
    ("consommation.html", "Consommation",
     "Une TVA, un taux",
     "La TVA doit devenir un grand impôt de rendement à taux unique cible de "
     "25 %, pour remplacer une partie des impôts qui frappent le travail, la "
     "production et la mobilité.",
     "TVA à taux unique cible de 25 % : ce que ça permet, comment la transition "
     "est lissée, et pourquoi la justice sociale passe par le revenu universel "
     "plutôt que par des taux réduits.",
     CONSOMMATION),
    ("foncier.html", "Foncier",
     "Taxer le sol,<br> pas ce qu’on bâtit dessus",
     "Une <i>Land Value Tax</i> nationale de 2 % sur la valeur du terrain nu "
     "remplace l’essentiel de la fiscalité immobilière — droits de mutation "
     "compris, et supprimés immédiatement.",
     "Land Value Tax à 2 % sur le foncier nu : ce qu’elle remplace, pourquoi "
     "elle ne pénalise pas la construction, et les reports prévus pour les "
     "propriétaires à faible revenu.",
     FONCIER),
    ("entreprises.html", "Entreprises",
     "Imposer le bénéfice,<br> pas la production",
     "C3S et CVAE résiduelle supprimées immédiatement&nbsp;; un impôt sur les "
     "sociétés maintenu autour de 25 % puis ramené vers 15 à 20 %, à mesure que "
     "les niches disparaissent.",
     "Suppression des impôts de production (C3S, CVAE résiduelle), réforme de la "
     "CFE, impôt sur les sociétés ramené vers 15-20 % et extinction du crédit "
     "d’impôt recherche.",
     ENTREPRISES),
    ("carbone.html", "Carbone et énergie",
     "Un prix du carbone,<br> rendu aux citoyens",
     "Un prix plancher pluriannuel plutôt qu’une planification secteur par "
     "secteur&nbsp;; une recette intégralement reversée en dividende "
     "carbone&nbsp;; et aucune taxe spécifique sur l’électricité bas-carbone.",
     "Fiscalité carbone : prix plancher de l’ordre de 200 €/tCO₂, dividende "
     "carbone reversé aux citoyens, pas de taxe spécifique sur l’électricité "
     "bas-carbone, réseau financé en puissance.",
     CARBONE),
    ("transmissions.html", "Transmissions et épargne",
     "Ce qui compte,<br> c’est ce que vous recevez",
     "Successions et donations fusionnées et imposées chez le receveur, avec un "
     "abattement universel de 100 000 € sur la vie entière&nbsp;; l’entreprise "
     "productive protégée&nbsp;; l’épargne retraite taxée une seule fois.",
     "Successions et donations imposées chez le receveur avec abattement "
     "universel de 100 000 €, carry-over basis pour la transmission "
     "d’entreprise, Compte Retraite Universel Capitalisé, suppression de l’exit "
     "tax.",
     TRANSMISSIONS),
    ("simulateur.html", "Simulateur",
     "Ce que ça change<br> pour vous",
     "Le programme atteint un ménage par cinq canaux&nbsp;: l’impôt, les "
     "transferts, la TVA, le foncier et l’énergie. Les voici tous les cinq, "
     "calculés dans votre navigateur.",
     "Simulateur du programme fiscal : impôt proportionnel, revenu universel, "
     "TVA à 25 %, Land Value Tax et dividende carbone, calculés ensemble pour "
     "votre ménage.",
     SIMULATEUR),
    ("calendrier.html", "Mise en œuvre",
     "Cinq ans,<br> et ce qui tombe dès la première année",
     "Ce qui est supprimé immédiatement, ce qui converge progressivement, et les "
     "ordres de grandeur budgétaires — tels que la note les donne, c’est-à-dire "
     "comme des masses de travail à consolider.",
     "Le calendrier de la réforme fiscale année par année, la fiche de paie "
     "cible, et les ordres de grandeur budgétaires du programme.",
     CALENDRIER),
    ("objections.html", "Objections",
     "Les huit objections,<br> et les réponses",
     "Une TVA à 25 % est-elle injuste&nbsp;? Un impôt proportionnel est-il "
     "progressif&nbsp;? La LVT finira-t-elle dans les loyers&nbsp;? Les questions "
     "qui reviennent toujours, et ce que le programme leur répond.",
     "Les huit objections au programme fiscal libéral et les réponses du "
     "programme : TVA, impôt proportionnel, Land Value Tax, loyers, DMTO, "
     "carbone, impôt sur les sociétés, exit tax.",
     OBJECTIONS),
    ("glossaire.html", "Glossaire",
     "Les mots,<br> en clair",
     "LVT, DMTO, CSG, TEE, assiette, rente, taux marginal&nbsp;: les vingt termes "
     "qu’il faut connaître pour lire ce programme, et rien de plus.",
     "Glossaire du programme fiscal : LVT, DMTO, C3S, CVAE, CIR, CRUC, TEE, "
     "assiette, rente, progressivité, dividende carbone.",
     GLOSSAIRE),
]


GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- La couleur du bandeau : sur un téléphone, la barre du navigateur la reprend,
     et la page commence où elle commence. -->
<meta name="theme-color" content="#0b3d3a">
<title>{titre_onglet}</title>
<meta name="description" content="{description}">
<link rel="icon" href="moteur/icone.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="moteur/icone.svg">
<!-- La charte vient du dépôt du simulateur de retraite, copiée sans une
     modification ; site.css ne fait que redéfinir ce qui est propre à ce
     site-ci. C'est le point de contact prévu par la charte elle-même. -->
<link rel="stylesheet" href="moteur/style.css">
<link rel="stylesheet" href="moteur/site.css">
</head>
<body>
{entete}
<main id="contenu" tabindex="-1">
{affiche}
{corps}
</main>
{pied}
{script}
</body>
</html>
"""

SCRIPT_CALCULETTE = '<script src="moteur/calculette.js" defer></script>'


def ecrire(verifier: bool = False) -> int:
    """Écrit les pages, ou vérifie qu'elles sont à jour.

    `--verifier` sert au contrôle avant publication : il échoue si un fichier du
    dépôt ne correspond plus à ce que ce script produit, ce qui arrive dès qu'on
    a corrigé une page à la main plutôt qu'ici.
    """
    ecarts = 0
    for fichier, surtitre, titre, chapeau, description, corps in PAGES:
        titre_onglet = ("Programme fiscal — Parti libéral français"
                        if fichier == "index.html"
                        else f"{surtitre} — Programme fiscal")
        page = GABARIT.format(
            titre_onglet=escape(titre_onglet, quote=False),
            description=escape(description, quote=True),
            entete=entete(fichier),
            affiche=affiche(surtitre, titre, chapeau),
            corps=corps,
            pied=pied(),
            script=SCRIPT_CALCULETTE if fichier == "simulateur.html" else "",
        )
        chemin = RACINE / fichier
        ancien = chemin.read_text(encoding="utf-8") if chemin.exists() else None
        if ancien == page:
            continue
        if verifier:
            etat = "absente" if ancien is None else "différente"
            print(f"{fichier} : {etat} de ce que produit le script", file=sys.stderr)
            ecarts += 1
        else:
            chemin.write_text(page, encoding="utf-8")
            print(f"écrit {fichier}")
    if verifier and ecarts:
        print(f"\n{ecarts} page(s) à régénérer : python scripts/construire_site.py",
              file=sys.stderr)
    return 1 if ecarts else 0


if __name__ == "__main__":
    analyse = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyse.add_argument("--verifier", action="store_true",
                         help="échoue si les pages du dépôt ne sont pas à jour")
    sys.exit(ecrire(analyse.parse_args().verifier))
