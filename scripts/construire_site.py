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
        ("qui-gagne.html", "Qui gagne, qui perd"),
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
  <p>Une exception, et elle est signalée : la page
  <a href="qui-gagne.html">Qui gagne, qui perd</a> avance des chiffres qui ne
  figurent pas dans la note. Ils sortent d'un modèle dont les hypothèses, les
  contrôles et le code sont publics, et qui est décrit
  <a href="qui-gagne.html#methode">sur la page même</a>.</p>
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
     "abattement universel de 200 000 € sur la vie entière.",
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
    '<p class="valeur">36 %</p>'
    '<p class="precision">Un seul taux, proportionnel, à la place de l’IR, de la '
    'CSG et de la CRDS. C’est le taux que donne notre chiffrage, et non un '
    'objectif d’affichage.</p></div>',
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
          ("progressivite", "La progressivité"), ("logement", "Le logement"),
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
    section("taux", "Un taux de 36 %, et pourquoi nous ne disons plus 30 %",
            "<p>La note fixait un objectif politique&nbsp;: maintenir le taux "
            "<strong>sous les 30 %</strong>, grâce à l’élargissement de "
            "l’assiette, à la suppression des niches, à la TVA à taux unique, "
            "à la <i>Land Value Tax</i> et à la réforme des prestations autour "
            "du revenu universel.</p>"
            "<p>Nous avons fait le calcul. <strong>Il ne tient pas.</strong> Un "
            "revenu universel de 600 € par adulte coûte 382 milliards d’euros "
            "par an&nbsp;; le nouvel impôt doit en outre lever ce que l’impôt "
            "sur le revenu, la CSG et la CRDS lèvent aujourd’hui. En face, les "
            "prestations remplacées et le gain de la TVA à taux unique ne "
            "couvrent pas l’écart. Le taux d’équilibre se situe entre 35,5 % "
            "et 36 %.</p>"
            + '<div class="note vigilance"><p>Nous aurions pu garder « moins de '
              '30 % » jusqu’à ce qu’un contradicteur refasse l’addition. Un '
              'chiffre de tract tient une campagne&nbsp;; il ne tient pas un '
              'débat. Nous publions donc 36 %, et le calcul avec.</p></div>'
            + "<p>Ce taux reste plus lisible que l’empilement qu’il remplace, "
              "et surtout il ne se lit pas seul&nbsp;: c’est le couple impôt + "
              "revenu universel qui fait le système, et c’est lui qu’il faut "
              "juger. Un ménage au salaire médian y gagne.</p>"
            + '<p><a class="bouton" href="qui-gagne.html">Voir qui gagne et qui '
              'perd</a></p>'
            + encadre("", "<p>Un impôt proportionnel large, lisible, et chiffré "
                          "à 36 %.</p>")),
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
              "revenu. Aucun seuil à ne pas franchir, aucune aide à perdre.</p>"
            + "<h3>Ce que le revenu universel remplace, et ce qui lui "
              "survit</h3>"
            + "<p>Un revenu universel qui remplacerait tout ferait perdre à "
              "un allocataire de l’AAH quatre cents euros par mois. Nous ne le "
              "proposons pas, et nous écrivons la liste plutôt que de la "
              "laisser deviner.</p>"
            + tableau(
                ["Remplacé par le revenu universel", "Maintenu au-dessus de lui"],
                [["Le RSA", "Le supplément handicap"],
                 ["La prime d’activité", "L’aide au logement en zone tendue"],
                 ["Les prestations familiales de base", "L’allocation d’autonomie"]],
                legende="Trois suppléments subsistent. Un revenu universel "
                        "assorti de trois compléments explicites reste dix "
                        "fois plus simple que l’empilement actuel : la "
                        "redistribution doit être lisible, pas unique.")
            + "<h3>Deux règles de calibrage, et pourquoi il a fallu les "
              "écrire</h3>"
            + "<p>Un supplément mal réglé protège sur le papier et laisse "
              "perdre en pratique. Nos deux premières versions l’ont montré, "
              "et les deux règles qui suivent en sont tirées.</p>"
            + "<p><strong>Un supplément se calcule sur la position entière du "
              "ménage, pas sur le seul écart avec le revenu universel.</strong> "
              "Réglé sur cet écart seul, le supplément handicap laissait "
              "l’allocataire de l’AAH perdre 482 € de TVA supplémentaire&nbsp;: "
              "on avait protégé un canal sur cinq. Le supplément est désormais "
              "fixé au montant qui laisse le ménage protégé à son niveau de "
              "vie — ni gagnant, ni perdant.</p>"
            + "<p><strong>L’aide au logement est attachée au logement, pas à la "
              "personne.</strong> C’est la correction qui règle le sort du "
              "célibataire, et elle mérite son paragraphe.</p>"
            + '<p><a class="bouton" href="#logement">Le célibataire, et ce que '
              'nous en avons appris</a></p>'),

    section("logement", "Le logement, et le célibataire",
            "<p>Le revenu universel double avec le nombre d’adultes. Un loyer, "
            "non. C’est toute la difficulté, et nous ne l’avions pas vue.</p>"
            "<p>Nos premiers chiffrages faisaient perdre 391 € par an à un "
            "célibataire au SMIC en zone tendue, quand un couple aux mêmes "
            "revenus par tête gagnait 454 € par adulte. L’écart ne venait ni "
            "de l’impôt, ni de la zone tendue&nbsp;: il venait de ce que nous "
            "transformions une prestation attachée au <strong>ménage</strong> "
            "— l’aide au logement — en un transfert versé par "
            "<strong>tête</strong>. Ce faisant, nous déplacions 600 € par "
            "adulte du ménage d’une personne vers le couple.</p>"
            + "<p>Un adulte seul sur deux ménages français&nbsp;: l’erreur "
              "n’était pas marginale. Voici comment l’aide au logement est "
              "construite&nbsp;:</p>"
            + liste([
                "<strong>Elle est attachée au logement</strong>, et partagée "
                "entre les adultes qui y résident. Un loyer ne double pas "
                "quand on est deux&nbsp;; l’aide non plus.",
                "<strong>Elle est forfaitaire par zone</strong>, et non "
                "indexée sur le loyer effectivement payé. Une aide qui suit le "
                "loyer en finance une part&nbsp;: le bailleur en capte une "
                "fraction substantielle, et c’est bien documenté. Dans un "
                "programme qui entend <a href=\"foncier.html\">taxer la rente "
                "foncière</a>, une aide qui la nourrit serait une "
                "contradiction.",
                "<strong>Elle ne demande que le nombre d’adultes à une "
                "adresse</strong>, jamais la nature de leur relation. C’est la "
                "fin du contrôle de la vie maritale, que nous reprochons au RSA "
                "depuis toujours et que nous aurions réintroduit sans y "
                "penser.",
                "<strong>Elle est calée sur le ménage le plus exposé</strong> — "
                "l’adulte seul en zone tendue —, de sorte que personne ne perde "
                "à la réforme par ce canal.",
            ])
            + '<div class="note vigilance"><p>Elle reste une prestation sous '
              'condition de ressources, et c’est la seule que le programme '
              'conserve. Nous l’assumons&nbsp;: le coût du logement varie du '
              'simple au triple selon le territoire, et un transfert national '
              'uniforme ne peut pas l’égaliser sans coûter trois fois plus. Le '
              'remède de fond est ailleurs — la <i>Land Value Tax</i> fait '
              'baisser le prix du sol et la rente qu’il porte. L’aide est le '
              'pont, pas la destination.</p></div>'
            + encadre("", "<p>Le revenu universel se verse par tête, parce "
                          "qu’on vit un par un. L’aide au logement se verse par "
                          "logement, parce qu’on s’y loge ensemble.</p>")),
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
            + "<p>Cette règle, prise seule, avait deux défauts que nous avons "
              "corrigés. Elle aurait fait <strong>baisser</strong> le revenu "
              "universel en récession — le PIB par habitant a reculé de plus de "
              "3 % en 2009 —, et elle l’aurait laissé s’éroder d’environ un "
              "point par an, la croissance réelle étant le plus souvent "
              "inférieure à l’inflation. Un transfert censé compenser la TVA "
              "aurait été le premier à la subir.</p>"
            + "<p>Deux garde-fous s’y ajoutent donc&nbsp;:</p>"
            + liste(["un <strong>cliquet</strong>&nbsp;: le revenu universel ne "
                     "baisse jamais en euros courants&nbsp;;",
                     "un <strong>plancher d’inflation</strong>&nbsp;: il suit le "
                     "plus élevé de l’inflation et de la croissance réelle par "
                     "habitant, lissé sur trois ans."])
            + encadre("", "<p>Le revenu universel est une part de la prospérité "
                          "commune, et il ne recule jamais.</p>")),
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
          ("agricole", "Foncier agricole et naturel"), ("local", "Taux national"),
          ("aides", "Les aides au logement")]),
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
    section("aides", "Pourquoi l’aide au logement ne suit pas le loyer",
            "<p>Une taxe sur la rente foncière et une aide qui la nourrit ne "
            "peuvent pas coexister dans le même programme. C’est pourtant ce "
            "que nous allions faire.</p>"
            "<p>Une aide indexée sur le loyer effectivement payé solvabilise "
            "la demande sans augmenter l’offre&nbsp;: là où le foncier est "
            "rare, le bailleur en capte une fraction substantielle, et c’est "
            "bien documenté pour l’aide personnalisée au logement. L’argent "
            "public finit dans la rente que la <i>Land Value Tax</i> a "
            "précisément pour objet de taxer.</p>"
            + "<p>Notre aide au logement est donc <strong>forfaitaire par "
              "zone</strong>, attachée au logement, et indifférente au loyer "
              "que vous payez. Elle protège le locataire sans renchérir son "
              "loyer, et elle laisse au signal-prix du sol le soin de faire "
              "son travail.</p>"
            + encadre("", "<p>Une aide qui suit le loyer finance le "
                          "propriétaire. Une aide forfaitaire finance le "
                          "locataire.</p>")
            + '<p><a class="bouton" href="revenus.html#logement">Comment elle '
              'est construite</a></p>'),

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
    plan([("receveur", "Imposer le receveur"), ("comparaison", "La comparaison"),
          ("hors-ligne", "Hors ligne directe"), ("effets", "Ce que ça change"),
          ("illiquides", "Actifs illiquides"), ("entreprise", "Transmission d’entreprise"),
          ("cruc", "Épargne retraite (CRUC)"), ("exit", "Exit tax"),
          ("non-residents", "Non-résidents")]),
    section("receveur", "Ce qui compte, c’est ce que vous recevez",
            "<p>Les donations et successions seront fusionnées dans un même "
            "régime, et imposées <strong>chez le receveur</strong> — non selon le "
            "lien de parenté.</p>"
            + "<p>Chaque individu disposera d’un <strong>compte de réception "
              "patrimoniale</strong> sur l’ensemble de sa vie, doté d’un "
              "<strong>abattement universel de 200 000 €</strong>. Au-delà, les "
              "transmissions reçues sont imposées au taux commun de 36 %, puis "
              "à <strong>45 % au-delà de 2 millions d’euros</strong> reçus dans "
              "une vie.</p>"
            + '<div class="note vigilance"><p>La note fixait cet abattement à '
              '100 000 €, par symétrie avec le droit actuel. C’était une erreur '
              'de lecture&nbsp;: aujourd’hui, 100 000 € s’entendent <em>par '
              'parent</em>. Un enfant qui hérite de son père et de sa mère en a '
              'donc deux. L’abattement viager en remplace deux&nbsp;: il en '
              'vaut deux.</p></div>'
            + encadre("", "<p>Ce qui compte n’est pas le lien familial avec le "
                          "donateur, mais le montant reçu par l’individu au cours "
                          "de sa vie.</p>")),

    section("comparaison", "Ce que vous paieriez, et ce que vous payez",
            "<p>Deux parents, un enfant qui reçoit la moitié de chacun&nbsp;: "
            "la structure dans laquelle on hérite vraiment.</p>"
            + tableau(
                ["Reçu par enfant", "Droits aujourd’hui", "Système cible", "Écart"],
                [["150 000 €", "0 €", "0 €", "—"],
                 ["200 000 €", "0 €", "0 €", "—"],
                 ["300 000 €", "16 389 €", "36 000 €", "+19 611 €"],
                 ["400 000 €", "36 389 €", "72 000 €", "+35 611 €"],
                 ["1 000 000 €", "156 389 €", "288 000 €", "+131 611 €"],
                 ["4 000 000 €", "1 234 789 €", "1 548 000 €", "+313 211 €"],
                 ["20 000 000 €", "8 434 789 €", "8 748 000 €", "+313 211 €"]],
                legende="Ligne directe, droit en vigueur contre système cible. "
                        "La transmission médiane — la maison de famille partagée "
                        "entre deux enfants — reste non imposée, comme "
                        "aujourd’hui.")
            + "<p>Deux choses se lisent dans ce tableau, et nous les assumons "
              "toutes les deux.</p>"
            + "<p><strong>Aucune transmission en ligne directe n’est imposée "
              "moins qu’aujourd’hui</strong>, de 50 000 € à 100 millions. Le "
              "soupçon de cadeau aux grands héritages ne tient pas, et il ne "
              "tient pas parce que le calcul le dit.</p>"
            + "<p><strong>Au-dessus de 200 000 € reçus, les transmissions "
              "paient davantage.</strong> C’est la contrepartie de ce que nous "
              "fermons&nbsp;: l’abattement qui se rouvre tous les quinze ans, "
              "l’assurance-vie, les régimes de faveur — autant de dispositifs "
              "dont profite surtout celui qui a les moyens d’organiser sa "
              "transmission à l’avance. Nous préférons un abattement plus "
              "large pour tous à des portes dérobées pour quelques-uns.</p>"
            + encadre("", "<p>Nous taxons davantage ce qu’on reçoit sans "
                          "l’avoir gagné, pour taxer moins ce qu’on gagne en "
                          "travaillant.</p>")),

    section("hors-ligne", "Les vrais gagnants : tous ceux qui ne sont pas des enfants",
            "<p>C’est l’effet le plus spectaculaire de la réforme, et celui "
            "dont on parle le moins. Aujourd’hui, ce que vous payez dépend "
            "moins de ce que vous recevez que de votre lien avec le "
            "défunt.</p>"
            + tableau(
                ["Qui reçoit 200 000 €", "Aujourd’hui", "Système cible"],
                [["Un enfant", "0 €", "0 €"],
                 ["Un neveu ou une nièce", "105 618 €", "0 €"],
                 ["Un beau-fils, un filleul, un ami, un concubin",
                  "119 044 €", "0 €"]],
                legende="Un neveu supporte aujourd’hui 55 % après un abattement "
                        "de 7 967 € ; une personne sans lien de parenté, 60 % "
                        "après 1 594 €. Le système cible ne connaît que le "
                        "montant reçu.")
            + "<p>Familles recomposées, couples sans enfant, personnes seules, "
              "fratries, amitiés d’une vie&nbsp;: le droit actuel les traite "
              "comme des étrangers, et leur prend la moitié de ce qu’on leur "
              "laisse. Le nôtre leur applique la règle commune.</p>"),
    section("effets", "Ce que ça change",
            liste(["simplifier radicalement les droits de succession&nbsp;;",
                   "supprimer les écarts arbitraires selon le lien familial&nbsp;;",
                   "laisser la transmission médiane non imposée, comme "
                   "aujourd’hui&nbsp;;",
                   "favoriser indirectement les familles nombreuses, chaque enfant "
                   "disposant de son propre abattement&nbsp;;",
                   "ramener au taux commun ce que le droit actuel taxe à "
                   "55 ou 60 % hors ligne directe&nbsp;;",
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
    [["Impôt proportionnel IR-CSG-CRDS", "36 %, d’après notre chiffrage"],
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
     "prix.</p>"
     "<p>Nous l’avons chiffré plutôt que de l’affirmer&nbsp;: un ménage du "
     "premier décile paie environ 1 400 € de TVA en plus et reçoit 5 200 € de "
     "plus en transferts. Il est <a href=\"qui-gagne.html#deciles\">gagnant "
     "net</a>. Et parce que l’ordre compte autant que le montant&nbsp;: "
     "<strong>aucun relèvement de TVA n’interviendra avant que le revenu "
     "universel ne soit versé à taux plein.</strong></p>"),
    ("L’impôt proportionnel n’est pas progressif",
     "<p>Le taux est proportionnel, mais le système est progressif.</p>"
     "<p>Le revenu universel transforme l’ensemble impôt + transfert en système "
     "progressif&nbsp;: les bas revenus sont bénéficiaires nets, les hauts revenus "
     "contributeurs nets. La progressivité est simplement rendue "
     "<a href=\"revenus.html#progressivite\">lisible</a>.</p>"
     "<p>La <a href=\"qui-gagne.html\">table par décile</a> le montre&nbsp;: "
     "les six premiers déciles gagnent, les quatre derniers contribuent, et le "
     "millime supérieur paie davantage qu’aujourd’hui — parce qu’il acquitte "
     "aujourd’hui 30,5 % de ses revenus, le prélèvement forfaitaire abritant "
     "l’essentiel de son capital. Un taux unique à 36 % est pour lui une "
     "hausse, sans qu’il ait fallu ajouter une tranche.</p>"),
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

# -- qui gagne, qui perd -----------------------------------------------------
#
# La page que tout le monde réclame à un programme fiscal, et qu'aucun ne
# publie. Elle sort de `scripts/qui_gagne.py`, au paramétrage corrigé : revenu
# universel de 600 €, taux unique de 36 %, suppléments maintenus.
#
# C'est la seule page du site qui avance des chiffres absents de la note. Elle
# le dit, elle dit d'où ils viennent, et elle dit ce qu'ils valent.

# Décile, solde annuel en euros, part du revenu disponible en points.
SOLDES_PAR_DECILE = [
    ("D1", 1549, 7.9), ("D2", 1357, 5.8), ("D3", 1852, 6.9), ("D4", 1652, 5.5),
    ("D5", 1613, 4.7), ("D6", 731, 1.8), ("D7", -366, -0.8), ("D8", -1920, -3.5),
    ("D9", -4080, -6.0), ("D10", -7432, -6.0),
]
SOLDES_AU_SOMMET = [
    ("Dernier décile, hors 1 %", -5298, -5.2),
    ("Le centile supérieur", -8733, -3.0),
    ("Le millime supérieur", -37300, -3.6),
]

# Ménage, revenu disponible actuel, solde, part.
SOLDES_PAR_MENAGE = [
    ("Couple, deux enfants, deux SMIC", 42197, 5796, 13.7),
    ("Retraité seul, 1 400 €/mois", 16111, 1251, 7.8),
    ("Allocataire de l’AAH", 12000, 18, 0.2),
    ("Propriétaire âgé à Paris, faible revenu", 18221, 2467, 13.5),
    ("Célibataire au SMIC, en zone tendue", 22559, 9, 0.0),
    ("Agriculteur propriétaire de ses terres", 30450, 8277, 27.2),
    ("Ménage rural, gaz et deux voitures", 44016, 5409, 12.3),
    ("Cadre célibataire, 80 000 €", 60467, -4087, -6.8),
    ("Dirigeant de PME, 160 000 €", 124410, -5393, -4.3),
    ("Héritier de 400 000 €", 31542, -1510, -4.8),
]


def part_lue(part: float) -> str:
    """La part du revenu disponible, telle qu'on la lit.

    Deux ménages sont tenus à l'équilibre par construction : le supplément qui
    les protège est FIXÉ au montant qui annule leur solde. Écrire « +0,0 % »
    ferait passer pour une coïncidence ce qui est une règle."""
    # Un quart de point : en dessous, le solde vaut quelques dizaines d'euros
    # sur l'année, et l'écrire au dixième de point donnerait à un arrondi
    # l'allure d'un résultat.
    if abs(part) < 0.25:
        return "à l’équilibre"
    signe = "+" if part >= 0 else "−"
    return signe + f"{abs(part):.1f}".replace(".", ",") + " %"


def barres_divergentes(lignes: list[tuple[str, int, float]],
                       sommet: list[tuple[str, int, float]]) -> str:
    """Le solde de chaque décile, en part du revenu disponible.

    Des barres divergentes, parce que la donnée porte un SIGNE : ce qui se lit
    d'abord n'est pas l'ampleur mais le côté. D'où le zéro au milieu, et deux
    couleurs opposées de part et d'autre.

    Le vert et le rose de la charte ne se distinguent qu'à ΔE 7,1 pour un œil
    deutéranope — sous le seuil de 8 en dessous duquel la couleur ne peut plus
    porter seule une information. Elle ne la porte pas seule : le côté du zéro
    et le signe du nombre la portent aussi, et ce sont eux qu'on lit. La couleur
    ne fait que confirmer.

    Le SVG est écrit ici, à la fabrication, et non par un script dans le
    navigateur : cette page doit se lire sans JavaScript comme les onze autres.
    """
    gauche, droite = 168, 736
    zero = (gauche + droite) / 2
    # L'échelle se déduit des données. Figée à une amplitude choisie d'avance,
    # elle laissait la plus longue barre sortir du cadre dès que le chiffrage
    # bougeait — et c'est arrivé. On réserve en outre de quoi poser l'étiquette
    # au bout de cette plus longue barre, faute de quoi c'est elle qu'on rogne.
    reserve = 62
    amplitude = max(abs(part) for _, _, part in lignes + sommet) * 1.02
    echelle = ((droite - gauche) / 2 - reserve) / amplitude
    haut_ligne, epaisseur = 27, 15          # 15 px de barre : sous le plafond de 24
    marge_haut, separateur = 16, 22

    parties = []
    y = marge_haut

    def barre(nom, solde, part, discrete=False):
        nonlocal y
        largeur = abs(part) * echelle
        x = zero if part >= 0 else zero - largeur
        sens = "gain" if part >= 0 else "perte"
        # Le bout de la barre est arrondi, son pied reste carré sur le zéro :
        # c'est le zéro qui doit se lire d'un trait, pas chaque barre.
        rayon = min(4, largeur)
        if part >= 0:
            trace = (f"M{x} {y} h{max(largeur - rayon, 0)} a{rayon} {rayon} 0 0 1 "
                     f"{rayon} {rayon} v{epaisseur - 2 * rayon} a{rayon} {rayon} 0 0 1 "
                     f"{-rayon} {rayon} h{-max(largeur - rayon, 0)} z")
        else:
            trace = (f"M{zero} {y} h{-max(largeur - rayon, 0)} a{rayon} {rayon} 0 0 0 "
                     f"{-rayon} {rayon} v{epaisseur - 2 * rayon} a{rayon} {rayon} 0 0 0 "
                     f"{rayon} {rayon} h{max(largeur - rayon, 0)} z")
        parties.append(f'<path class="marque {sens}" d="{trace}"/>')
        classe = "nom discret" if discrete else "nom"
        parties.append(f'<text class="{classe}" x="{gauche - 14}" y="{y + 11}" '
                       f'text-anchor="end">{escape(nom)}</text>')
        # Le nombre se pose au bout de la barre, hors d'elle : à 15 px
        # d'épaisseur, aucun libellé ne tient dedans avec de l'air autour.
        bout = (x + largeur + 10) if part >= 0 else (x - 10)
        ancre = "start" if part >= 0 else "end"
        # La virgule décimale ne se pose que sur le NOMBRE. Appliquée à la
        # ligne entière, elle atteignait aussi les coordonnées du SVG — et un
        # `x="612,0"` ne se lit pas : l'étiquette repartait à l'origine.
        signe = "+" if part >= 0 else "\u2212"
        mesure = f"{signe}{abs(part):.1f}".replace(".", ",") + "\u00a0%"
        parties.append(f'<text class="mesure" x="{bout}" y="{y + 11}" '
                       f'text-anchor="{ancre}">{mesure}</text>')
        y += haut_ligne

    for nom, solde, part in lignes:
        barre(nom, solde, part)
    y += separateur - haut_ligne + haut_ligne
    trait = y - separateur / 2 - 4
    parties.append(f'<line class="coupure" x1="{gauche - 150}" x2="{droite}" '
                   f'y1="{trait}" y2="{trait}"/>')
    parties.append(f'<text class="intitule" x="{gauche - 150}" y="{trait + 18}">'
                   f'Le dernier décile, ouvert</text>')
    y = trait + 30
    for nom, solde, part in sommet:
        barre(nom, solde, part, discrete=True)

    hauteur = y + 24
    axe = (f'<line class="zero" x1="{zero}" x2="{zero}" y1="{marge_haut - 6}" '
           f'y2="{hauteur - 30}"/>')
    reperes = (f'<text class="cote" x="{zero - 12}" y="{hauteur - 12}" '
               f'text-anchor="end">\u2190 ce que le ménage perd</text>'
               f'<text class="cote" x="{zero + 12}" y="{hauteur - 12}">'
               f'ce qu\u2019il gagne \u2192</text>')
    return (f'<figure class="barres"><div class="defilant" tabindex="0">'
            f'<svg viewBox="0 0 760 {hauteur:.0f}" role="img" aria-label="'
            f'Solde de la réforme par décile, en part du revenu disponible : '
            f'positif du premier au sixième décile, négatif ensuite.">'
            f'{axe}{"".join(parties)}{reperes}</svg></div>'
            f'<figcaption>Variation du revenu disponible annuel, en part de ce '
            f'dont le ménage dispose aujourd\u2019hui. Les déciles rangent les '
            f'ménages du plus modeste au plus aisé ; les trois dernières lignes '
            f'ouvrent le dernier d\u2019entre eux.</figcaption></figure>')

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
      <input type="number" id="taux-impot" name="taux" value="36" min="0" max="60"
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



QUI_GAGNE = "\n".join([
    plan([("change", "Ce que le chiffrage a changé"), ("deciles", "Par décile"),
          ("menages", "Dix ménages"), ("perdants", "Ceux qui y perdent"),
          ("methode", "D’où viennent ces chiffres")]),

    section("change", "Ce que le chiffrage nous a fait changer",
            "<p>Nous avons chiffré notre propre programme avant qu’on le fasse "
            "à notre place. Le calcul a contredit trois de nos annonces. Nous "
            "les avons corrigées plutôt que de les défendre.</p>"
            + tableau(
                ["Ce que nous disions", "Ce que nous disons"],
                [["Un taux « sous 30 % »",
                  "<strong>36 %</strong> — un taux sous 30 % ne finance pas un "
                  "revenu universel de 600 €, et le prétendre aurait coûté plus "
                  "cher que le reconnaître."],
                 ["Le revenu universel remplace les prestations",
                  "Il remplace le RSA, la prime d’activité et les prestations "
                  "familiales. Il <strong>ne remplace pas</strong> le supplément "
                  "handicap, l’aide au logement en zone tendue ni l’allocation "
                  "d’autonomie, qui subsistent au-dessus de lui."],
                 ["Le revenu universel suit la croissance",
                  "Il suit la croissance <strong>et ne recule jamais</strong> : "
                  "un cliquet en euros courants, et un plancher d’inflation."],
                 ["Un abattement successoral de 100 000 €",
                  "<strong>200 000 €</strong> — les 100 000 € du droit actuel "
                  "s’entendent <em>par parent</em>, et nous en avions fait un "
                  "abattement viager unique. Nous divisions par deux ce dont "
                  "dispose un enfant qui hérite de ses deux parents, sans "
                  "l’avoir voulu ni l’avoir dit — "
                  "<a href=\"transmissions.html#comparaison\">la "
                  "comparaison</a>."],
                 ["L’aide au logement est maintenue",
                  "Elle est maintenue <strong>et refaite</strong> : attachée au "
                  "logement et non à la personne, forfaitaire par zone plutôt "
                  "qu’indexée sur le loyer payé. Sans quoi nous faisions perdre "
                  "391 € par an à un célibataire au SMIC — "
                  "<a href=\"revenus.html#logement\">le détail</a>."]],
                legende="Trois corrections issues du chiffrage. Le détail du "
                        "calcul est public, et refaisable.")
            + encadre("", "<p>Le taux qui équilibre se situe entre 35,5 % et "
                          "36 %. Nous publions la borne haute. D’un programme "
                          "accusé de ne pas être chiffré, l’erreur qui coûte "
                          "est celle qui laisse un trou, pas celle qui laisse "
                          "une marge.</p>")
            + "<p>Une quatrième correction a été envisagée puis écartée, et il "
              "vaut mieux dire pourquoi. Nous avons étudié une tranche "
              "supérieure, pour éviter que le haut de la distribution ne "
              "profite de la réforme. Elle s’est révélée <strong>inutile</strong> : "
              "le millime supérieur acquitte aujourd’hui 30,5 % de ses revenus, "
              "parce que le prélèvement forfaitaire abrite l’essentiel de son "
              "capital. Un taux unique à 36 % est donc, pour lui, une hausse. "
              "C’est le taux commun qui répond au soupçon de cadeau, et la "
              "doctrine — un impôt, un taux — en sort intacte.</p>"),

    section("deciles", "Par décile",
            "<p>Les déciles rangent les ménages du plus modeste au plus aisé, "
            "dix groupes de trois millions de foyers. Voici ce que la réforme "
            "leur fait, tous canaux confondus : impôt, transferts, TVA, "
            "foncier et énergie.</p>"
            + barres_divergentes(SOLDES_PAR_DECILE, SOLDES_AU_SOMMET)
            + tableau(
                ["Décile", "Solde annuel", "Part du revenu disponible"],
                [[nom, f"{'+' if solde >= 0 else '−'}{abs(solde):,} €".replace(",", " "),
                  part_lue(part)]
                 for nom, solde, part in SOLDES_PAR_DECILE]
                + [[f"<span class=\"dont\">{nom}</span>",
                    f"{'+' if solde >= 0 else '−'}{abs(solde):,} €".replace(",", " "),
                    part_lue(part)]
                   for nom, solde, part in SOLDES_AU_SOMMET],
                legende="Les mêmes chiffres que la figure, pour qui préfère "
                        "les lire. Les trois dernières lignes ouvrent le "
                        "dernier décile : elles ne s’ajoutent pas aux dix "
                        "premières, elles les détaillent.")
            + "<p>Le profil est celui d’une réforme redistributive ordinaire : "
              "les six premiers déciles y gagnent, les quatre derniers y "
              "contribuent. Le septième est à l’équilibre, à moins d’un point "
              "près — c’est la charnière, et nous ne prétendons pas la "
              "connaître au dixième de point.</p>"),

    section("menages", "Dix ménages",
            "<p>Un décile est une moyenne, et personne ne vit dans une "
            "moyenne. Voici dix ménages réels dans leur composition, calculés "
            "un par un. Ils n’ont pas été choisis pour nous arranger : trois "
            "d’entre eux y perdent.</p>"
            + tableau(
                ["Ménage", "Revenu disponible aujourd’hui", "Solde", "Part"],
                [[nom, f"{dispo:,} €".replace(",", " "),
                  f"{'+' if solde >= 0 else '−'}{abs(solde):,} €".replace(",", " "),
                  part_lue(part)]
                 for nom, dispo, solde, part in SOLDES_PAR_MENAGE],
                legende="Le système actuel de chaque ménage est calculé depuis "
                        "le barème en vigueur : quotient familial, décote, "
                        "prélèvement forfaitaire sur le capital, et net des "
                        "réductions et crédits d’impôt.")
            + '<p><a class="bouton" href="simulateur.html">Calculer votre '
              'cas</a></p>'),

    section("perdants", "Ceux qui y perdent",
            "<p>Un programme qui ne fait aucun perdant n’existe pas. Un "
            "programme qui prétend n’en faire aucun se fait démentir par le "
            "premier journaliste venu. Voici les nôtres.</p>"
            + liste([
                "<strong>Les quatre derniers déciles</strong>, de 0,9 % à 6 % "
                "de leur revenu disponible. C’est le choix assumé d’un système "
                "où la solidarité passe par un transfert visible plutôt que "
                "par des niches invisibles.",
                "<strong>Personne, parmi les ménages protégés.</strong> Deux "
                "d’entre eux perdaient encore dans nos versions précédentes — "
                "l’allocataire de l’AAH 482 € par an, le célibataire au SMIC "
                "en zone tendue 391 €. Les deux sont désormais tenus à "
                "l’équilibre, non par hasard mais par règle : un supplément "
                "est <a href=\"revenus.html#logement\">fixé au montant qui "
                "annule la perte</a>, tous canaux comptés.",
                "<strong>Les propriétaires perdent de la valeur foncière.</strong> "
                "La <i>Land Value Tax</i> se capitalise dans le prix du "
                "terrain : environ un tiers de sa valeur, une fois. Un "
                "ménage médian propriétaire perd de l’ordre de 19 000 € de "
                "patrimoine, un ménage du dernier décile près de 100 000 €. "
                "Cela ne figure dans aucune colonne ci-dessus, parce que ce "
                "n’est pas un flux annuel — mais c’est réel, et c’est le but : "
                "faire baisser le prix du sol.",
                "<strong>Les héritiers, au-dessus de 200 000 € reçus.</strong> "
                "La transmission médiane reste non imposée, comme aujourd’hui. "
                "Au-delà, les droits augmentent&nbsp;: 72 000 € sur 400 000 € "
                "reçus, contre 36 389 € aujourd’hui. C’est la contrepartie de "
                "l’abattement qui cesse de se rouvrir tous les quinze ans et "
                "des régimes de faveur que nous fermons&nbsp;; c’est un choix, "
                "et il est <a href=\"transmissions.html#comparaison\">chiffré "
                "ligne à ligne</a>. Rien de tout cela ne figure dans les "
                "tableaux ci-dessus : une succession n’est pas un revenu "
                "annuel.",
            ])),

    section("methode", "D’où viennent ces chiffres",
            "<p>Cette page est la seule du site à avancer des chiffres qui ne "
            "figurent pas dans la note. Elle doit donc dire ce qu’ils valent, "
            "et elle le dit sans indulgence.</p>"
            + liste([
                "<strong>Ce n’est pas une microsimulation.</strong> Il n’y a "
                "pas d’enquête sur données individuelles derrière, mais treize "
                "ménages moyens calibrés sur des ordres de grandeur publics.",
                "<strong>Le modèle se contrôle.</strong> Réagrégé sur la "
                "population, il retrouve les masses nationales : CSG à 3 % "
                "près, impôt sur le revenu à 1 %, prestations à 0,5 %, taxe "
                "foncière et patrimoine foncier à moins de 1 %. Et deux "
                "chemins de calibration indépendants donnent au dernier décile "
                "le même taux effectif, 23,5 % et 23,6 %.",
                "<strong>Le calcul est à comportements inchangés</strong> : il "
                "ignore ce que la réforme ferait aux prix, aux salaires et à "
                "l’emploi. Ces effets sont réels, et ils joueraient "
                "probablement en sa faveur — nous ne les comptons pas.",
                "<strong>Le bouclage laisse un résidu</strong> de l’ordre de "
                "quatre milliards d’euros, soit environ trois dixièmes de "
                "point de taux. Nous préférons l’écrire que l’arrondir.",
                "<strong>Tout est public et refaisable.</strong> Le modèle, "
                "ses hypothèses et ses contrôles tiennent dans deux fichiers "
                "du dépôt, <code>scripts/qui_gagne.py</code> et "
                "<code>scripts/bouclage.py</code>. Chaque montant y est isolé "
                "dans une constante nommée, pour qu’on puisse le contester "
                "ligne à ligne.",
            ])
            + encadre("", "<p>Ces tableaux seront refaits sur données "
                          "individuelles avant la campagne. Nous les publions "
                          "dès maintenant parce qu’un ordre de grandeur "
                          "vérifiable vaut mieux qu’un silence, et parce qu’un "
                          "programme qui montre lui-même qui y perd ne peut "
                          "plus être accusé de l’avoir caché.</p>")),
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
     "Fusion IR-CSG-CRDS en un impôt proportionnel de 36 %, assiette large, "
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
     "abattement universel de 200 000 € sur la vie entière&nbsp;; l’entreprise "
     "productive protégée&nbsp;; l’épargne retraite taxée une seule fois.",
     "Successions et donations imposées chez le receveur avec abattement "
     "universel de 200 000 €, carry-over basis pour la transmission "
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
    ("qui-gagne.html", "Qui gagne, qui perd",
     "Nous avons chiffré,<br> et nous publions le résultat",
     "Décile par décile et ménage par ménage&nbsp;: ce que la réforme fait au "
     "revenu disponible, y compris à ceux qui y perdent — et les trois "
     "annonces que le chiffrage nous a fait corriger.",
     "Qui gagne et qui perd au programme fiscal : le solde par décile et pour "
     "dix ménages types, tous canaux confondus, avec la méthode et ses limites.",
     QUI_GAGNE),
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
