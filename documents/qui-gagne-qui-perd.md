# Qui gagne, qui perd

*Document de travail interne, comme `revue-critique.md`. Il n'est pas publié en
l'état : ce qui sera publié devra être refait sur données individuelles. Ce qui
suit sert à décider, pas à convaincre.*

La table par décile est le premier document qu'on réclamera au programme, et le
seul qui réponde à l'accusation qui vient toujours. Tant qu'il n'existe pas, la
réponse appartient à celui qui accuse.

Les chiffres sortent de `scripts/qui_gagne.py`. Le modèle additionne les cinq
canaux par lesquels la réforme atteint un ménage — impôt direct, transferts,
TVA, logement, énergie — là où le simulateur du site n'en montre qu'un.

**Ce que ce modèle n'est pas.** Ce n'est pas une microsimulation : dix ménages
moyens calibrés sur des ordres de grandeur publics, pas une enquête Revenus
fiscaux et sociaux. Sa validité tient à deux contrôles, imprimés à chaque
exécution :

- **réagrégé, il retrouve les masses nationales** — CSG à 3 % près, IR à 1 %,
  prestations à 0,5 %, TVA des ménages à 2,5 %, taxe foncière, DMTO, IFI et
  patrimoine foncier à moins de 1 % ;
- **les deux routes de calibration se rejoignent** — le taux effectif du dernier
  décile vaut 23,5 % quand on le pose sur les masses, 23,6 % quand on le
  reconstitue depuis le barème appliqué à ses deux sous-populations. Rien ne les
  y obligeait.

C'est assez pour arbitrer. Ce n'est pas assez pour publier.

---

## 1. Le programme tel qu'il est écrit

Revenu universel de 600 €, taux proportionnel à 34 % — le couple qui boucle,
d'après `bouclage.py`. Variation annuelle du revenu disponible, en euros.

| | Revenu | Dispo. actuel | Impôt | Transferts | TVA | Logement | Carbone | **Solde** | **% dispo** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D1 | 11 000 | 19 620 | −2 860 | +2 200 | −1 374 | +54 | +149 | **−1 831** | **−9,3 %** |
| D2 | 18 000 | 23 560 | −4 680 | +5 168 | −1 581 | +95 | +115 | **−883** | **−3,7 %** |
| D3 | 24 000 | 26 672 | −5 832 | +7 852 | −1 684 | +144 | +102 | +582 | +2,2 % |
| D4 | 30 000 | 30 230 | −7 230 | +9 976 | −1 809 | +197 | +68 | +1 202 | +4,0 % |
| D5 | 36 000 | 34 328 | −8 568 | +11 896 | −1 943 | +253 | +55 | +1 693 | +4,9 % |
| D6 | 43 000 | 39 599 | −10 019 | +13 020 | −2 115 | +314 | +21 | +1 221 | +3,1 % |
| D7 | 51 000 | 45 835 | −11 475 | +13 844 | −2 304 | +392 | −13 | +444 | +1,0 % |
| D8 | 62 000 | 54 526 | −13 206 | +14 504 | −2 543 | +497 | −47 | **−795** | **−1,5 %** |
| D9 | 80 000 | 68 200 | −15 200 | +15 028 | −2 905 | +675 | −136 | **−2 538** | **−3,7 %** |
| D10 | 163 000 | 124 795 | −17 115 | +15 740 | −4 497 | +1 985 | −314 | **−4 201** | **−3,4 %** |
| *D10 hors 1 %* | 128 000 | 100 923 | −14 031 | +15 740 | −2 981 | +1 145 | −259 | −386 | −0,4 % |
| **Top 1 %** | 420 000 | 293 057 | −2 827 | +16 200 | −6 421 | +6 611 | −568 | **+12 996** | **+4,6 %** |
| **Top 0,1 %** | 1 500 000 | 1 042 891 | −35 762 | +16 380 | −13 166 | +43 695 | −1 097 | **+10 050** | **+1,0 %** |

Solde agrégé : les ménages paient +16 Md€, ce qui est exactement la contrepartie
des ~17 Md€ d'impôts de production et d'IS supprimés. Le modèle et le bouclage
disent donc la même chose, ce qui est un troisième contrôle.

**Trois lectures, et elles sont toutes hostiles.**

*La courbe est en U.* Les déciles 3 à 7 gagnent, les deux premiers et les trois
derniers perdent. Comptés en ménages, **la moitié de la population est
perdante** — D1, D2, D8, D9, D10. C'est le titre, et il est exact.

*Le premier décile perd 9,3 %.* Le canal coupable n'est pas celui qu'on croit :
ce n'est pas l'impôt, c'est la TVA. Un ménage de D1 paie 1 374 € de TVA en plus,
et le revenu universel ne dépasse ses prestations actuelles que de 2 200 €. La
réponse du programme à l'objection n° 1 — « la TVA finance le revenu
universel » — n'est donc vraie qu'au-dessus du troisième décile. En dessous, la
TVA mange la compensation.

*Le sommet gagne.* Le top 1 % encaisse +12 996 €, le top 0,1 % +10 050 €.

## 2. Mais le sommet gagne par un canal inattendu, et c'est une bonne nouvelle

Regardez la ligne « impôt » du top 0,1 % : **−35 762 €**. Ils paient *davantage*
d'impôt sur le revenu, pas moins. Leur taux effectif actuel est de 30,5 %, parce
que l'essentiel de leur revenu est du capital soumis au prélèvement forfaitaire
de 30 %. Un taux unique à 34 % est, pour eux, une hausse.

Leur gain vient presque entièrement du **canal logement : +43 695 €**, dont
32 000 € d'IFI supprimé et le reste de la taxe foncière remplacée par une LVT
moins lourde sur leur patrimoine. Et il faudrait y ajouter la succession, traitée
au §4.

C'est une information stratégique de premier ordre, et elle inverse l'instinct :

- **Sur les revenus, le programme est défendable tel quel.** « Vous baissez
  l'impôt des plus riches » est faux : la fusion IR-CSG-CRDS à 34 % augmente
  l'imposition du capital des très hauts patrimoines, aujourd'hui protégé par le
  prélèvement forfaitaire. Cet argument est bon, il est vérifiable, et il n'est
  écrit nulle part.
- **Sur le patrimoine, il est indéfendable en l'état.** La suppression de l'IFI,
  l'allègement foncier du sommet et le régime successoral se cumulent sur les
  mêmes 300 000 foyers. Ce sont les trois seules mesures à corriger — pas la
  doctrine.

## 3. La variante « sous 30 % » est strictement pire, et cela tranche le §1 de l'audit

Revenu universel de 480 €, taux à 30 % : le couple qui respecte la promesse
affichée sur la page d'accueil.

| | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | Top 1 % | Top 0,1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Solde | −3 731 | −2 596 | −1 029 | −233 | +354 | +97 | −424 | −1 296 | −2 384 | −849 | +13 227 | +49 424 |
| % dispo | **−19,0 %** | **−11,0 %** | −3,9 % | −0,8 % | +1,0 % | +0,2 % | −0,9 % | −2,4 % | −3,5 % | −0,7 % | **+4,5 %** | **+4,7 %** |

**Neuf déciles sur dix perdent. Le premier perd 19 %. Le top 0,1 % gagne
49 424 €.** C'est la table que l'adversaire rêve de trouver, et elle découle
mécaniquement de la promesse affichée en page d'accueil.

L'audit posait trois portes au §1 et laissait le choix ouvert. **La table le
ferme.** Baisser le revenu universel pour tenir « sous 30 % » ne coûte pas
seulement de la générosité : cela détruit la progressivité qui est l'argument
central du programme, parce que le taux baisse pour tout le monde tandis que le
transfert ne baisse que pour ceux qui en vivent. Le slogan « moins de 30 % » est
donc à abandonner, et il vaut mieux l'abandonner soi-même.

## 4. Le programme corrigé

Trois corrections issues de l'audit : revenu universel maintenu à 600 €, **une
tranche unique à 45 % au-delà de 250 000 €**, et **les suppléments handicap,
logement en zone tendue et autonomie maintenus au-dessus du revenu universel**.

| | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | Top 1 % | Top 0,1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Solde | +1 169 | +1 317 | +2 082 | +2 102 | +2 243 | +1 541 | +624 | −695 | −2 488 | −4 176 | −19 033 | −144 800 |
| % dispo | +6,0 % | +5,6 % | +7,8 % | +7,0 % | +6,5 % | +3,9 % | +1,4 % | −1,3 % | −3,6 % | −3,3 % | −6,5 % | −13,9 % |

La courbe est redressée : gain décroissant du premier au septième décile, perte
croissante ensuite. C'est le profil d'une réforme redistributive ordinaire, et
il se défend en une phrase.

Deux réserves, qui sont des réglages et non des objections :

- **Il coûte 11 Md€ de plus que la neutralité**, soit environ 0,7 point de taux
  proportionnel. Le couple cohérent devient donc *revenu universel de 600 €,
  taux de 35 %, tranche à 45 %*. Mieux vaut annoncer 35 % et tenir que 30 % et
  reculer.
- **La tranche à 45 % dès 250 000 € corrige trop** : le top 0,1 % perd 13,9 %.
  Le seuil et le taux sont deux molettes. Une tranche à 42 % au-delà de
  400 000 € ramènerait le sommet autour de la neutralité, ce qui est
  probablement le bon réglage pour un parti libéral : **la cible n'est pas de
  faire payer le sommet davantage, elle est qu'il ne gagne pas.**

## 5. Les dix cas types

Programme tel qu'il est écrit, à gauche ; corrigé, à droite. Ils ne sont pas
choisis pour flatter : quatre y perdent.

| Ménage | Dispo. actuel | Solde écrit | % | Solde corrigé | % |
| --- | ---: | ---: | ---: | ---: | ---: |
| Couple, 2 enfants, deux SMIC | 42 197 | +5 436 | +12,9 % | +6 636 | +15,7 % |
| Retraité seul, 1 400 €/mois | 16 111 | +1 587 | +9,9 % | +1 587 | +9,9 % |
| **Allocataire de l'AAH** | 12 000 | **−5 282** | **−44,0 %** | −482 | −4,0 % |
| Propriétaire âgé à Paris, faible revenu | 18 221 | +2 847 | +15,6 % | +2 847 | +15,6 % |
| **Célibataire au SMIC, zone tendue** | 22 559 | **−2 371** | **−10,5 %** | +29 | +0,1 % |
| Agriculteur propriétaire de ses terres | 30 450 | +8 467 | +27,8 % | +8 917 | +29,3 % |
| Ménage rural, gaz et deux voitures | 44 016 | +5 629 | +12,8 % | +6 329 | +14,4 % |
| Cadre célibataire, 80 000 € | 60 467 | −2 487 | −4,1 % | −2 487 | −4,1 % |
| Dirigeant de PME, 160 000 € | 124 410 | −2 193 | −1,8 % | −2 193 | −1,8 % |
| Héritier de 400 000 € | 31 542 | −750 | −2,4 % | −750 | −2,4 % |

Les taux effectifs de ces dix ménages ne sont pas posés : ils sortent du barème
en vigueur, décote et prélèvement forfaitaire compris, nets des réductions et
crédits d'impôt. Ils se refont à la main, et c'est le but.

**Ce que les cas disent, et que la table par décile cachait.**

*L'allocataire de l'AAH perd 44 % de son revenu.* C'est le cas qui décide seul de
la crédibilité sociale du programme, et il se règle par une ligne : le supplément
handicap survit au revenu universel. Tant que cette ligne n'est pas écrite, elle
sera écrite par quelqu'un d'autre.

*Le célibataire au SMIC en zone tendue perd 10,5 %.* Un adulte seul ne reçoit
qu'un revenu universel là où un couple en reçoit deux, et l'aide au logement
qu'il perd vaut la moitié de ce qu'il gagne. Le maintien de l'APL en zone tendue
le ramène à l'équilibre exact — ce qui montre qu'il n'y a pas de marge.

*Le propriétaire âgé de Paris gagne 15,6 %… et perd 163 636 € de valeur de
terrain.* C'est le cas où la table de flux et la réalité vécue divergent le plus.
Aucun tableau ne le convaincra ; seul le mécanisme de report le peut, et il doit
être mis en avant, pas mentionné.

*L'agriculteur gagne 29 % en flux et perd 145 455 € de patrimoine.* Même
divergence, avec en plus une facture carbone en hausse de 699 €. C'est le ménage
qui manifestera le plus tôt, et le programme n'a aujourd'hui rien à lui dire
au-delà de « la LVT s'applique aussi au foncier non bâti ».

*Le ménage rural au gaz et aux deux voitures gagne 12,8 %.* C'est le ménage de
2018, et le dividende carbone fait son travail : il perd 589 € sur l'énergie et
récupère largement ailleurs. **C'est le meilleur résultat du programme, et
personne ne le sait.** Il mérite sa propre page.

*L'héritier de 400 000 € ne perd que 750 € par an — et 65 611 € en une fois.* La
succession n'est pas dans le tableau parce qu'elle n'est pas annuelle. Elle est
pourtant le plus gros transfert que ce ménage subira dans sa vie, et elle va dans
le sens inverse de tout le reste. Voir `revue-critique.md`, §2.

## 6. Ce qu'il faut faire de tout cela

1. **Abandonner « moins de 30 % »** et annoncer 35 % avec un revenu universel de
   600 €. La table du §3 montre que la promesse actuelle est la plus coûteuse
   politiquement des deux.
2. **Écrire la ligne des suppléments** (handicap, logement en zone tendue,
   autonomie). Elle vaut 27 Md€ et elle vaut le programme.
3. **Ajouter une tranche supérieure**, calibrée non pour punir mais pour que le
   sommet ne gagne pas : autour de 42 % au-delà de 400 000 €.
4. **Traiter le patrimoine des très hauts revenus comme un bloc** — IFI,
   allègement foncier, succession —, puisque c'est par là, et seulement par là,
   que passe le transfert vers le sommet.
5. **Publier la ligne « impôt » du top 0,1 %.** Elle dit que la réforme augmente
   l'imposition des très grands patrimoines de revenus. C'est vrai, c'est
   contre-intuitif, et c'est votre meilleure réponse.
6. **Refaire cette table sur données individuelles** avant publication. Ce
   modèle dit où regarder ; il ne dit pas au centime.
