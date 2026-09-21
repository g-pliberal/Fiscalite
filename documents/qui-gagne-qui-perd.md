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

## 4. Le programme corrigé — et la tranche supérieure dont il n'a pas besoin

Paramètres retenus, publiés sur `qui-gagne.html` : revenu universel de 600 €,
**taux unique de 36,5 %**, **suppléments handicap, logement en zone tendue et
autonomie maintenus au-dessus du revenu universel**, et **aucune tranche
supérieure**.

| | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | Top 1 % | Top 0,1 % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Solde | +1 253 | +886 | +1 244 | +928 | +792 | −165 | −1 278 | −2 628 | −3 787 | −3 635 | −5 054 | −41 810 |
| % dispo | +6,2 % | +3,6 % | +4,4 % | +2,9 % | +2,2 % | −0,4 % | −2,6 % | −4,6 % | −5,4 % | −3,0 % | −1,7 % | −3,8 % |

Gain décroissant du premier au sixième décile, perte croissante ensuite : le
profil d'une réforme redistributive ordinaire, qui se défend en une phrase.

**La tranche supérieure que le §2 de la revue critique réclamait s'avère
inutile — et c'est le résultat le plus utile de tout l'exercice.** Le millime
supérieur acquitte aujourd'hui 30,5 % de ses revenus, le prélèvement
forfaitaire abritant l'essentiel de son capital. Un taux unique à 36,5 % est donc
pour lui une hausse, sans aucune tranche. C'est le
taux de base, et non une concession doctrinale, qui répond à l'objection du
cadeau aux plus aisés — et la doctrine « un impôt, un taux » en sort intacte.

Une réserve, qui est un réglage : **le taux d'équilibre se situe entre 35,5 % et
36 %**, et 36 % laisse une marge d'environ 4 Md€. C'est volontaire. D'un
programme accusé de ne pas être chiffré, l'erreur coûteuse est celle qui laisse
un trou, pas celle qui laisse une marge.

(La tranche supérieure reste pertinente **pour les successions**, où le
croisement du §2 est réel et où aucun taux de base ne le corrige.)

## 5. Les dix cas types

Programme tel qu'il est écrit, à gauche ; corrigé, à droite. Ils ne sont pas
choisis pour flatter : quatre y perdent.

| Ménage | Dispo. actuel | Solde écrit | % | Solde corrigé | % |
| --- | ---: | ---: | ---: | ---: | ---: |
| Couple, 2 enfants, deux SMIC | 42 197 | +5 436 | +12,9 % | +5 796 | +13,7 % |
| Retraité seul, 1 400 €/mois | 16 111 | +1 587 | +9,9 % | +1 251 | +7,8 % |
| **Allocataire de l'AAH** | 12 000 | **−5 282** | **−44,0 %** | +18 | à l'équilibre |
| Propriétaire âgé à Paris, faible revenu | 18 221 | +2 847 | +15,6 % | +2 467 | +13,5 % |
| **Célibataire au SMIC, zone tendue** | 22 559 | **−2 371** | **−10,5 %** | +9 | à l'équilibre |
| Agriculteur propriétaire de ses terres | 30 450 | +8 467 | +27,8 % | +8 277 | +27,2 % |
| Ménage rural, gaz et deux voitures | 44 016 | +5 629 | +12,8 % | +5 409 | +12,3 % |
| Cadre célibataire, 80 000 € | 60 467 | −2 487 | −4,1 % | −4 087 | −6,8 % |
| Dirigeant de PME, 160 000 € | 124 410 | −2 193 | −1,8 % | −5 393 | −4,3 % |
| Héritier de 400 000 € | 31 542 | −750 | −2,4 % | −1 510 | −4,8 % |

Les taux effectifs de ces dix ménages ne sont pas posés : ils sortent du barème
en vigueur, décote et prélèvement forfaitaire compris, nets des réductions et
crédits d'impôt. Ils se refont à la main, et c'est le but.

**Ce que les cas disent, et que la table par décile cachait.**

*L'allocataire de l'AAH perd 44 % de son revenu.* C'est le cas qui décide seul de
la crédibilité sociale du programme, et il se règle par une ligne : le supplément
handicap survit au revenu universel. Tant que cette ligne n'est pas écrite, elle
sera écrite par quelqu'un d'autre.

*Le célibataire au SMIC en zone tendue perdait 10,5 %, puis 1,7 %.* Il est
maintenant à l'équilibre, et le §7 dit par quelle correction — qui n'est pas
celle qu'on croit.

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

1. ~~**Abandonner « moins de 30 % »**~~ — fait. Le site publie 36 %, dit que la
   note disait autre chose, et dit pourquoi.
2. ~~**Écrire la ligne des suppléments**~~ — fait, sur `revenus.html`. Reste à
   la calibrer pour qu'elle couvre aussi la hausse de TVA.
3. ~~**Ajouter une tranche supérieure**~~ — **écartée, et c'est un gain.** Le
   taux de base à 36 % suffit à rendre le sommet contributeur net, puisqu'il
   n'acquitte aujourd'hui que 30,5 %. La doctrine « un impôt, un taux » tient.
4. **Traiter le patrimoine des très hauts revenus comme un bloc** — IFI,
   allègement foncier, succession. C'est là que passe encore le seul transfert
   net vers le sommet, et la succession reste non arbitrée.
5. ~~**Publier la ligne « impôt » du top 0,1 %**~~ — faite, et elle est devenue
   l'argument central de l'objection n° 2.
6. **Refaire ces tables sur données individuelles** avant la campagne. Ce
   modèle dit où regarder ; il ne dit pas au centime, et la page le dit.
7. ~~**Traiter le célibataire en zone tendue**~~ — fait, et la cause n'était
   pas la zone tendue. Voir le §7.


---

## 7. Le célibataire, et la règle qu'il a fallu écrire

Le dernier perdant identifié n'était pas un cas particulier : c'était une erreur
de conception, et elle touchait un ménage français sur deux.

**Le diagnostic.** À revenu identique par tête, un couple gagnait +454 € par
adulte quand le célibataire perdait −391 €. Canal par canal, l'écart ne venait
ni de l'impôt (161 €) ni de la TVA (84 €) : il venait des **transferts, pour
600 € par adulte**.

La cause est mécanique. *Le revenu universel double avec le nombre d'adultes ;
un loyer, non.* En convertissant une prestation attachée au **ménage** — l'aide
au logement — en un transfert versé par **tête**, le programme déplaçait 600 €
par adulte du ménage d'une personne vers le couple. La zone tendue n'y était
pour rien : elle ne faisait qu'amplifier le montant en jeu.

**Deux règles en sortent**, et elles valent au-delà de ce cas :

1. **Un supplément se calcule sur la position entière du ménage**, pas sur le
   seul écart avec le revenu universel. Réglé sur cet écart, le supplément
   handicap laissait l'allocataire de l'AAH perdre les 482 € de TVA : on avait
   protégé un canal sur cinq.
2. **Une aide au logement s'attache au logement**, et se partage entre les
   adultes qui y résident. Trois conséquences, toutes bonnes : elle épouse
   l'échelle d'équivalence sans qu'on ait à la décréter ; elle ne demande que
   le *nombre* d'adultes à une adresse, jamais la nature de leur relation — donc
   pas de contrôle de la vie maritale, que le programme reproche au RSA ; et
   elle est **forfaitaire par zone**, non indexée sur le loyer payé, ce qui
   l'empêche d'être captée par le bailleur. Une aide indexée sur le loyer
   nourrit la rente que la LVT a pour objet de taxer : la contradiction était
   dans le programme, et personne ne l'avait vue.

**Le coût : nul.** Le recalibrage consomme 5 Md€, exactement la marge que le
taux de 36 % portait déjà — le solde agrégé passe de +21 à +16 Md€, soit la
neutralité visée. Les suppléments n'étaient pas sous-financés, ils étaient
mal réglés.

**Ce qui reste.** L'aide au logement demeure la seule prestation sous condition
de ressources que le programme conserve, et c'est une exception à assumer : le
coût du logement varie du simple au triple selon le territoire, et aucun
transfert national uniforme ne l'égalise sans coûter trois fois plus. Le remède
de fond reste la LVT, qui fait baisser le prix du sol. L'aide est le pont.

---

## 8. La succession moyenne, et l'erreur de lecture qui la frappait

Le dernier point ouvert de la revue critique, et le seul où les deux attaques —
« cadeau aux grandes fortunes » et « vous triplez les droits sur la maison de
vos parents » — étaient **toutes deux exactes**.

**L'erreur était une erreur de lecture.** La note fixait l'abattement viager à
100 000 €, par symétrie avec le droit en vigueur. Mais les 100 000 € du droit
en vigueur s'entendent **par parent**. Un enfant qui hérite de son père et de sa
mère en a deux, et le programme lui en laissait un. Il divisait par deux, sans
l'avoir voulu ni l'avoir dit, ce dont dispose la quasi-totalité des héritiers.

Comparer les deux systèmes sur un héritier à donateur unique — ce que faisait
mon propre tableau du §2 de la revue — masquait exactement cela. La bonne
structure de comparaison est : deux parents, chaque enfant reçoit la moitié de
chacun.

| Reçu par enfant | Aujourd'hui | Abattement à 100 k€ | Abattement à 200 k€ |
| ---: | ---: | ---: | ---: |
| 200 000 € | 0 € | 36 000 € | **0 €** |
| 400 000 € | 36 389 € | 108 000 € | 72 000 € |
| 1 000 000 € | 156 389 € | 324 000 € | 288 000 € |

**Retenu : abattement viager de 200 000 €, taux commun de 36 %, puis 45 % au-delà
de 2 M€ reçus dans la vie.** La règle se dit en une phrase — *l'abattement
viager remplace deux abattements parentaux, il en vaut deux* — et c'est ce qui
la rend défendable.

**Vérification par balayage, de 50 000 € à 100 M€ : aucune transmission en ligne
directe n'est imposée moins qu'aujourd'hui.** Le soupçon de cadeau aux grands
héritages ne tombe pas par un argument, il tombe par le calcul. La seconde
tranche est ce qui l'assure : sans elle, la réforme allégeait les transmissions
au-dessus de 6 M€ environ.

**Ce qui augmente, et qu'il faut assumer.** Au-dessus de 200 000 € reçus, les
droits montent — 72 000 € sur 400 000 € reçus contre 36 389 € aujourd'hui. C'est
la contrepartie de ce qui se ferme : l'abattement qui se rouvre tous les quinze
ans, l'assurance-vie, les régimes de faveur. Autant de dispositifs dont profite
surtout celui qui a les moyens d'organiser sa transmission à l'avance. La
formule : *nous taxons davantage ce qu'on reçoit sans l'avoir gagné, pour taxer
moins ce qu'on gagne en travaillant.*

**Et l'argument qui n'était écrit nulle part.** Un neveu qui reçoit 200 000 €
paie aujourd'hui 105 618 € ; un beau-fils, un filleul, un concubin, un ami :
119 044 €. Dans le système cible, tous paient **zéro**, comme un enfant. Familles
recomposées, couples sans enfant, personnes seules, fratries — le droit actuel
les traite en étrangers et leur prend la moitié de ce qu'on leur laisse. C'est
l'effet le plus spectaculaire de la réforme, et celui dont le programme ne
parlait pas.

---

## 9. Refonte sur séries sourcées — ce que les comptes 2025 ont changé

Les tables précédentes reposaient sur des ordres de grandeur que j'avais
reconstitués. Elles reposent désormais sur les comptes nationaux 2025 de
l'Insee, et quatre choses ont bougé.

**L'impôt sur le revenu : 103,6 Md€, non 87.** Je retenais la présentation
budgétaire là où les comptes nationaux s'imposaient. Seize milliards de
différence sur ce que l'impôt proportionnel doit remplacer.

**Le taux d'équilibre : 36,5 % et non 36 %.** Deux calibrations indépendantes —
le bouclage d'ensemble et l'agrégation du modèle par décile — donnent 36,2 % et
36,5 %. On publie la borne haute, comme annoncé.

**Le déficit de départ : 5,1 % et non 5,8 %.** Le millésime 2025 au lieu de
2024. Conséquence : sous la règle des 2 %, le déficit repasse sous 3 % en
quatrième année et non en sixième. Une baisse du taux devient envisageable en
fin de quinquennat. *Un demi-point de déficit de départ déplace la conclusion
de deux ans* — c'est l'argument le plus fort en faveur de la datation des
sources, et je ne l'avais pas vu venir.

**Une divergence entre mes deux modèles, trouvée et corrigée.** Ils ne donnaient
pas le même taux. Le rapprochement canal par canal a révélé deux erreurs
réelles : le prélèvement de solidarité sur le capital était sous-compté dans le
modèle par décile, et le gain de la TVA à taux unique était fixé dans le
bouclage à 68 Md€ — soit *moins* que ce que le modèle par décile attribuait aux
seuls ménages, ce qui était impossible. Les deux modèles convergent maintenant à
trois dixièmes de point.

Reste ce que ce travail ne peut pas faire : ce n'est toujours pas une
microsimulation. Les treize ménages moyens sont mieux calibrés, pas remplacés.
