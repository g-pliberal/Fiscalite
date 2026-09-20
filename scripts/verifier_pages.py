#!/usr/bin/env python3
"""Contrôle les pages produites : balises appariées, liens et ancres résolus.

Un site statique de onze pages n'a pas de compilateur pour lui dire qu'un lien
pointe vers une ancre qui n'existe plus. Ce script le dit.

    python scripts/verifier_pages.py
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag

RACINE = Path(__file__).resolve().parent.parent

# Les éléments sans contenu : ils n'ont pas de balise de fermeture à attendre.
VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
         "meta", "source", "track", "wbr"}


class Analyse(HTMLParser):
    """Relève les identifiants, les liens, et les balises mal appariées."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.pile: list[tuple[str, int]] = []
        self.identifiants: set[str] = set()
        self.liens: list[tuple[str, int]] = []
        self.erreurs: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributs = dict(attrs)
        if "id" in attributs:
            if attributs["id"] in self.identifiants:
                self.erreurs.append(
                    f"ligne {self.getpos()[0]} : identifiant en double "
                    f"« {attributs['id']} »")
            self.identifiants.add(attributs["id"])
        if tag == "a" and "href" in attributs:
            self.liens.append((attributs["href"], self.getpos()[0]))
        if tag not in VIDES:
            self.pile.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VIDES:
            return
        if not self.pile:
            self.erreurs.append(f"ligne {self.getpos()[0]} : </{tag}> sans ouverture")
            return
        ouverte, ligne = self.pile.pop()
        if ouverte != tag:
            self.erreurs.append(
                f"ligne {self.getpos()[0]} : </{tag}> ferme <{ouverte}> "
                f"ouverte ligne {ligne}")

    def termine(self) -> None:
        for tag, ligne in self.pile:
            self.erreurs.append(f"ligne {ligne} : <{tag}> jamais fermée")


def main() -> int:
    pages = sorted(RACINE.glob("*.html"))
    if not pages:
        print("aucune page : lancer scripts/construire_site.py", file=sys.stderr)
        return 1

    analyses: dict[str, Analyse] = {}
    problemes: list[str] = []

    for page in pages:
        analyse = Analyse()
        analyse.feed(page.read_text(encoding="utf-8"))
        analyse.termine()
        analyses[page.name] = analyse
        problemes += [f"{page.name} : {e}" for e in analyse.erreurs]

    for nom, analyse in analyses.items():
        for href, ligne in analyse.liens:
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            cible, ancre = urldefrag(href)
            if cible and not (RACINE / cible).exists():
                problemes.append(f"{nom} ligne {ligne} : « {cible} » n'existe pas")
                continue
            if ancre:
                voisine = analyses.get(cible or nom)
                if voisine is None:
                    continue  # une cible hors .html (un PDF) n'a pas d'ancres
                if ancre not in voisine.identifiants:
                    problemes.append(
                        f"{nom} ligne {ligne} : ancre « #{ancre} » absente de "
                        f"{cible or nom}")

    # Les ressources citées par les pages doivent être là, elles aussi.
    for page in pages:
        texte = page.read_text(encoding="utf-8")
        for chemin in re.findall(r'(?:href|src)="((?:moteur|documents)/[^"#]+)"', texte):
            if not (RACINE / chemin).exists():
                problemes.append(f"{page.name} : ressource manquante « {chemin} »")

    # Les polices que la charte appelle sont relatives à moteur/style.css.
    style = (RACINE / "moteur" / "style.css").read_text(encoding="utf-8")
    for police in re.findall(r"url\(([^)]+)\)", style):
        if not (RACINE / "moteur" / police).exists():
            problemes.append(f"moteur/style.css : « {police} » manquante")

    if problemes:
        for probleme in problemes:
            print(probleme, file=sys.stderr)
        print(f"\n{len(problemes)} problème(s)", file=sys.stderr)
        return 1
    print(f"{len(pages)} pages, "
          f"{sum(len(a.liens) for a in analyses.values())} liens : rien à signaler")
    return 0


if __name__ == "__main__":
    sys.exit(main())
