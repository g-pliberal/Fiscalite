# Programme fiscal — Parti libéral français

Le site qui présente le **chapitre Fiscalité** du programme aux électeurs :
onze pages statiques, lisibles sans JavaScript, servies telles quelles.

👉 `index.html` — ou, une fois publié,
<https://g-pliberal.github.io/fiscalite/>

## Ce qu'il y a dedans

| Page | Ce qu'elle dit |
| --- | --- |
| `index.html` | Les huit piliers, les quatre chiffres, et la formule du programme. |
| `principes.html` | Séparer impôt, cotisation et redistribution ; taxer moins les bases productives ; supprimer l'illusion de la gratuité. |
| `revenus.html` | Fusion IR-CSG-CRDS, taux sous 30 %, assiette, individualisation, revenu universel — avec un simulateur. |
| `consommation.html` | La TVA à taux unique cible de 25 %, et sa transition. |
| `foncier.html` | La *Land Value Tax*, les DMTO supprimés, les reports prévus. |
| `entreprises.html` | Impôts de production supprimés, IS ramené vers 15-20 %, extinction du CIR. |
| `carbone.html` | Prix plancher, dividende carbone, électricité et réseaux. |
| `transmissions.html` | Successions imposées chez le receveur, transmission d'entreprise, CRUC, exit tax. |
| `calendrier.html` | La trajectoire année par année, la fiche de paie cible, les ordres de grandeur. |
| `objections.html` | Les huit objections, et les réponses. |
| `glossaire.html` | Les vingt termes, en clair. |

## D'où vient le contenu

De `documents/note-fiscalite.pdf` — « Note interne — Chapitre Fiscalité »,
l'unique document de ce dépôt à l'origine. Son texte brut est repris tel quel
dans `documents/note-fiscalite.txt`, pour qu'une phrase du site se retrouve
d'un `grep`.

**Le site n'ajoute aucun chiffre qui n'y figure pas.** Quand la note dit « à
calibrer », la page dit « à calibrer » : le taux de l'impôt proportionnel n'est
pas écrit parce qu'il sort du bouclage budgétaire, et les 120 Md€ de la LVT sont
donnés pour ce qu'ils sont, un ordre de grandeur à évaluer.

## D'où vient l'apparence

Du dépôt [`retraitecomptenotionelle`](https://github.com/g-pliberal/retraitecomptenotionelle),
le simulateur de retraite du même parti : les deux sites doivent se reconnaître
comme un seul.

* `moteur/style.css` en est **copié sans une modification** ;
* `moteur/polices/` aussi (Public Sans et Instrument Serif, sous licence OFL,
  servies par le dépôt et non par un tiers) ;
* `moteur/site.css` est chargée **après** et ne fait que redéfinir ce qui est
  propre à ce site-ci — le simulateur, le glossaire, les colonnes « avant /
  après ».

C'est le point de contact que la charte prévoit elle-même : « un hôte qui
voudrait ajuster une couleur les redéfinit dans une feuille chargée après
celle-ci ». Ne rien corriger dans `style.css` garde une mise à jour de la charte
recopiable en une commande.

## Fabriquer et vérifier

Les pages `.html` de la racine sont **écrites par un script** et versionnées :
le site est statique, il n'y a rien à construire pour le servir. Le script
existe parce que le bandeau de tête et le pied sont identiques sur onze pages,
et que onze copies à la main dérivent toujours.

```sh
python scripts/construire_site.py             # écrit les pages
python scripts/construire_site.py --verifier   # échoue si elles ont changé
python scripts/verifier_pages.py               # balises, liens, ancres, ressources
```

Une correction se fait donc dans `scripts/construire_site.py`, jamais dans le
`.html` produit — `--verifier` est là pour le rappeler, et tourne à chaque
poussée (voir `.github/workflows/verifier.yml`).

Pour regarder le site en local, il faut un serveur : les pages chargent une
feuille de style et des polices, qu'un navigateur refuse de lire depuis
`file://`.

```sh
python -m http.server 8000
```

## Licences

* Code sous **Apache 2.0** (voir `LICENSE`), comme le dépôt dont la charte est
  reprise.
* Textes et infographies sous
  [**CC BY-SA 4.0**](https://creativecommons.org/licenses/by-sa/4.0/deed.fr).
* Polices sous **OFL** (voir `moteur/polices/`).
* Pictogrammes dérivés de Lucide, sous **ISC**.
