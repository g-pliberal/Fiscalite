// Le simulateur : les cinq canaux par lesquels la réforme atteint un ménage.
//
// La version précédente n'en montrait qu'un — l'impôt proportionnel et le
// revenu universel — et c'était sa faiblesse : montrer la moitié favorable
// d'une réforme, sur un site dont l'objet est la transparence, est la première
// chose qu'on lui aurait reprochée. Elle en montre cinq : impôt direct,
// transferts, TVA, logement, énergie.
//
// Le modèle est celui de `scripts/qui_gagne.py`, à la virgule près. Les deux
// doivent dire la même chose : si la table par décile et le simulateur du site
// divergeaient, c'est le programme qui serait pris en défaut, pas le script.
//
// Tout se fait dans le navigateur : aucune valeur saisie ne quitte la page, et
// il n'y a pas de serveur à qui elle pourrait partir.

"use strict";

// --- Le système actuel -------------------------------------------------------

const BAREME = [[11294, 0], [28797, 0.11], [82341, 0.30], [177106, 0.41],
                [Infinity, 0.45]];

// L'écart moyen entre l'impôt brut du barème et l'impôt net des réductions et
// crédits — emploi à domicile, garde d'enfants, dons. L'ignorer surestimerait
// ce qu'on paie aujourd'hui, donc le gain apparent de la réforme.
const REDUCTIONS_ET_CREDITS = 0.20;

function partsFiscales(adultes, enfants) {
  const demiParts = Math.min(enfants, 2) * 0.5 + Math.max(enfants - 2, 0);
  return adultes + demiParts;
}

function impotSurLeRevenu(revenu, capital, parts, pension) {
  const plafond = pension ? 4321 : 14171;
  const net = revenu - Math.min(revenu * 0.10, plafond);
  const parPart = Math.max(0, net) / parts;
  let impot = 0, bas = 0;
  for (const [haut, taux] of BAREME) {
    if (parPart <= bas) { break; }
    impot += (Math.min(parPart, haut) - bas) * taux;
    bas = haut;
  }
  impot *= parts;
  // La décote efface l'impôt des foyers modestes. C'est elle qui rend si
  // coûteux, pour eux, le passage à un taux proportionnel dès le premier euro :
  // sans elle, on croirait leur imposition déjà entamée.
  const seuil = parts >= 2 ? 1929 : 1166;
  if (impot < seuil) { impot = Math.max(0, impot - (seuil - 0.4525 * impot)); }
  return impot * (1 - REDUCTIONS_ET_CREDITS) + capital * 0.128;
}

function csgCrds(revenu, capital, pension) {
  // Une pension modeste supporte un taux réduit, et c'est ce qui explique
  // qu'un retraité modeste ait tant à perdre à un taux unique.
  const tauxPension = revenu < 24000 ? 0.041 : 0.083;
  const tauxRevenu = pension ? tauxPension : 0.9825 * 0.097;
  return revenu * tauxRevenu + capital * 0.172;
}

// --- Les hypothèses du canal consommation, foncier et carbone ---------------
// Elles ne sont pas demandées au lecteur : personne ne connaît la part de son
// panier soumise à TVA. Elles sont écrites ici, en clair, avec leur valeur.

const PART_TAXABLE = 0.80;        // le loyer, la santé et l'école ne portent pas de TVA
const TVA_ACTUELLE = 0.168;       // taux moyen supporté aujourd'hui, en % HT
const PART_DU_TERRAIN = 0.50;     // part du terrain dans la valeur d'un logement
const TAXE_FONCIERE = 0.012;      // en part de la valeur du terrain
const DMTO_ANNUALISES = 0.0056;   // un déménagement tous les quarante ans, lissé
const ACTUALISATION = 0.035;
// Une taxe annuelle de 2 % sur un actif actualisé à 3,5 % ampute sa valeur de
// 36 % : c'est l'argument même du programme — « la LVT se capitalise dans la
// valeur du terrain » —, et il vaut aussi pour l'assiette de la LVT.
const DECOTE_DU_TERRAIN = ACTUALISATION / (ACTUALISATION + 0.02);
const PRIX_CARBONE_ACTUEL = 90;
const DIVIDENDE_PAR_ADULTE = 421;  // recette carbone des ménages, rendue par tête
const CO2_CHAUFFAGE = { aucun: 0, gaz: 4.0, fioul: 6.0 };
const CO2_PAR_KM = 0.00018;

// --- Le calcul ---------------------------------------------------------------

function calculerCanaux(saisie) {
  const { adultes, enfants, revenu, capital, pension, prestations,
          epargne, logement, chauffage, kilometres,
          taux, ruAdulte, ruEnfant, tva, lvt, carbone } = saisie;

  const total = revenu + capital;
  const parts = partsFiscales(adultes, enfants);
  const impotActuel = impotSurLeRevenu(revenu, capital, parts, pension)
                    + csgCrds(revenu, capital, pension);
  const impotCible = total * taux;

  const disponible = total - impotActuel + prestations;
  const consommation = Math.max(0, disponible) * (1 - epargne);
  const taxable = consommation * PART_TAXABLE;
  const tvaActuelle = taxable * TVA_ACTUELLE / (1 + TVA_ACTUELLE);
  // Le panier est tenu constant en volume : on compare deux fiscalités sur la
  // même dépense hors taxe, et non deux niveaux de vie différents.
  const tvaCible = (taxable / (1 + TVA_ACTUELLE)) * tva;

  const terrain = logement * PART_DU_TERRAIN;
  const foncierActuel = terrain * (TAXE_FONCIERE + DMTO_ANNUALISES);
  const lvtDue = terrain * DECOTE_DU_TERRAIN * lvt;

  const tonnes = CO2_CHAUFFAGE[chauffage] + kilometres * CO2_PAR_KM;
  const surcoutCarbone = tonnes * (carbone - PRIX_CARBONE_ACTUEL);
  const dividende = adultes * DIVIDENDE_PAR_ADULTE;

  return {
    canaux: [
      { cle: "impot", nom: "Impôt direct", montant: impotActuel - impotCible,
        detail: `${euros(impotActuel)} aujourd’hui, ${euros(impotCible)} demain` },
      { cle: "transferts", nom: "Transferts",
        montant: (adultes * ruAdulte + enfants * ruEnfant) * 12 - prestations,
        detail: `${euros((adultes * ruAdulte + enfants * ruEnfant) * 12)} de revenu `
                + `universel, ${euros(prestations)} de prestations remplacées` },
      { cle: "tva", nom: "TVA", montant: tvaActuelle - tvaCible,
        detail: `${euros(tvaActuelle)} aujourd’hui, ${euros(tvaCible)} demain` },
      { cle: "logement", nom: "Logement", montant: foncierActuel - lvtDue,
        detail: logement > 0
          ? `${euros(foncierActuel)} de taxe foncière et de droits de mutation `
            + `lissés, ${euros(lvtDue)} de LVT`
          : "Vous n’êtes pas propriétaire : ni taxe foncière, ni LVT" },
      { cle: "carbone", nom: "Énergie", montant: dividende - surcoutCarbone,
        detail: `${tonnes.toFixed(1)} tonnes de CO₂, ${euros(surcoutCarbone)} de `
                + `surcoût, ${euros(dividende)} de dividende` },
    ],
    disponible,
    perteEnCapital: -terrain * (1 - DECOTE_DU_TERRAIN),
    impotActuel, impotCible,
  };
}

// --- Les formats -------------------------------------------------------------
// `Intl` connaît la virgule décimale, l'espace insécable des milliers et les
// préférences du lecteur : inutile de les réécrire à la main.

const EUROS = new Intl.NumberFormat("fr-FR",
  { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
const POURCENT = new Intl.NumberFormat("fr-FR",
  { style: "percent", maximumFractionDigits: 1 });

const euros = (v) => EUROS.format(Math.round(v));

// Sur l'axe, « −10 000 € » est plus large que la marge qui l'accueille, et se
// faisait rogner de son signe : au millier près, la graduation se dit en k€.
const graduation = (v) => (Math.abs(v) >= 1000
  ? `${(v / 1000).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} k€`
  : EUROS.format(v));
// Un canal sans effet n'est ni un gain ni une perte : « +0 € » le ferait
// passer pour un gain minuscule, alors qu'il ne s'est rien passé du tout.
const signe = (v) => {
  const arrondi = Math.round(v);
  if (arrondi === 0) { return EUROS.format(0); }
  return (arrondi > 0 ? "+" : "−") + EUROS.format(Math.abs(arrondi));
};

// --- La cascade --------------------------------------------------------------
// Cinq marches et un total : c'est la forme que la charte prévoit pour « le
// pont d'un total à un autre », et c'est exactement ce qu'est un solde en cinq
// canaux. Rien n'est ajouté à la feuille de style pour l'obtenir.

const SVG = "http://www.w3.org/2000/svg";
const LARGEUR = 760, HAUTEUR = 330;
const MARGE = { haut: 26, bas: 62, gauche: 62, droite: 14 };

function balise(nom, attributs, texte) {
  const element = document.createElementNS(SVG, nom);
  for (const [cle, valeur] of Object.entries(attributs)) {
    element.setAttribute(cle, valeur);
  }
  if (texte !== undefined) { element.textContent = texte; }
  return element;
}

/** Des graduations rondes : un pas de 1 ; 2 ; 2,5 ; 5 ou 10 fois une puissance
    de dix. Le pas se cherche sur un sixième de l'amplitude et non un quart :
    avec un quart, une cascade ordinaire n'obtenait que deux lignes, et un axe
    à deux lignes ne se lit pas. */
function graduations(bas, haut) {
  const brut = (haut - bas) / 6;
  const dix = Math.pow(10, Math.floor(Math.log10(Math.max(brut, 1))));
  const pas = [1, 2, 2.5, 5, 10].map((m) => m * dix).find((p) => p >= brut) || dix * 10;
  const lignes = [];
  for (let v = Math.ceil(bas / pas) * pas; v <= haut; v += pas) { lignes.push(v); }
  return lignes;
}

function dessinerCascade(canaux, solde) {
  const marches = canaux.map((c) => ({ ...c }));
  let cumul = 0;
  for (const marche of marches) {
    marche.depart = cumul;
    cumul += marche.montant;
    marche.arrivee = cumul;
  }
  marches.push({ cle: "solde", nom: "Solde", montant: solde, depart: 0,
                 arrivee: solde, total: true,
                 detail: solde >= 0 ? "Vous y gagnez sur l’année"
                                    : "Vous y perdez sur l’année" });

  const valeurs = marches.flatMap((m) => [m.depart, m.arrivee]).concat([0]);
  const bas = Math.min(...valeurs), haut = Math.max(...valeurs);
  const marge = Math.max((haut - bas) * 0.12, 200);
  const min = bas - marge, max = haut + marge;
  const hauteurUtile = HAUTEUR - MARGE.haut - MARGE.bas;
  const y = (v) => MARGE.haut + (max - v) / (max - min) * hauteurUtile;

  const svg = balise("svg", {
    viewBox: `0 0 ${LARGEUR} ${HAUTEUR}`, role: "img",
    "aria-label": `Cascade des cinq canaux, du premier euro au solde de `
                  + `${signe(solde)} par an.`,
  });

  for (const valeur of graduations(min, max)) {
    svg.append(balise("line", { class: "grille", x1: MARGE.gauche - 8,
                                x2: LARGEUR - MARGE.droite, y1: y(valeur), y2: y(valeur) }));
    svg.append(balise("text", { class: "graduation", x: MARGE.gauche - 14,
                                y: y(valeur) + 4, "text-anchor": "end" },
                      graduation(valeur)));
  }
  svg.append(balise("line", { class: "axe", x1: MARGE.gauche - 8,
                              x2: LARGEUR - MARGE.droite, y1: y(0), y2: y(0) }));

  const large = (LARGEUR - MARGE.gauche - MARGE.droite) / marches.length;
  const barre = large * 0.56;
  marches.forEach((marche, i) => {
    const x = MARGE.gauche + i * large + (large - barre) / 2;
    const hautMarche = y(Math.max(marche.depart, marche.arrivee));
    const basMarche = y(Math.min(marche.depart, marche.arrivee));
    const groupe = balise("g", { class: "marche-groupe", "data-index": i });
    const classe = marche.total ? "total"
                 : marche.montant === 0 ? "nulle"
                 : marche.montant > 0 ? "gain" : "perte";
    groupe.append(balise("rect", {
      class: `marche ${classe}`, x, y: hautMarche, width: barre,
      height: Math.max(basMarche - hautMarche, 2),
    }));
    // Le chiffre se pose du côté où la marche ne va pas, pour ne jamais
    // recouvrir la barre qu'il mesure.
    const place = marche.montant >= 0 ? hautMarche - 9 : basMarche + 18;
    groupe.append(balise("text", {
      class: `valeur ${classe}`, x: x + barre / 2, y: place, "text-anchor": "middle",
    }, marche.total ? signe(marche.montant) : signe(marche.montant)));
    groupe.append(balise("text", {
      class: `etiquette${marche.total ? " total" : ""}`, x: x + barre / 2,
      y: HAUTEUR - MARGE.bas + 22, "text-anchor": "middle",
    }, marche.nom));
    if (i < marches.length - 2) {
      svg.append(balise("line", { class: "liaison", x1: x + barre,
                                  x2: x + large, y1: y(marche.arrivee),
                                  y2: y(marche.arrivee) }));
    }
    svg.append(groupe);
  });

  const survol = balise("g", { class: "survol" });
  svg.append(survol);
  return { svg, marches, large, barre, y };
}

// --- Le rendu ----------------------------------------------------------------

const champ = (id) => document.getElementById(id);

// Une saisie vide, négative ou absurde ne doit pas produire « NaN € » : elle
// retombe sur la valeur par défaut du champ. Celle-ci est lue sur le champ
// lui-même — `defaultValue`, c'est-à-dire l'attribut `value` du HTML — et non
// recopiée ici : deux listes de valeurs par défaut finissent toujours par
// diverger, et le calcul se ferait alors sur un nombre que la page n'affiche
// nulle part. La borne haute, elle, est celle de l'attribut `max`.
function nombre(id) {
  const element = champ(id);
  if (!element) { return 0; }
  const lire = (v) => Number.parseFloat(String(v).replace(",", "."));
  const defaut = lire(element.defaultValue) || 0;
  const maximum = lire(element.max) || Infinity;
  const brut = lire(element.value);
  if (!Number.isFinite(brut) || brut < 0) { return defaut; }
  return Math.min(brut, maximum);
}

function lire() {
  const nature = champ("nature");
  return {
    adultes: nombre("adultes"),
    enfants: nombre("enfants"),
    revenu: nombre("revenu"),
    capital: nombre("capital"),
    pension: nature ? nature.value === "pension" : false,
    prestations: nombre("prestations") * 12,
    epargne: nombre("epargne") / 100,
    logement: nombre("logement"),
    chauffage: champ("chauffage") ? champ("chauffage").value : "aucun",
    kilometres: nombre("kilometres"),
    taux: nombre("taux-impot") / 100,
    ruAdulte: nombre("ru"),
    ruEnfant: nombre("ru-enfant"),
    tva: nombre("tva") / 100,
    lvt: nombre("lvt") / 100,
    carbone: nombre("carbone"),
  };
}

let selection = -1;
let derniere = null;

function ecrire(resultat) {
  const solde = resultat.canaux.reduce((somme, c) => somme + c.montant, 0);
  const relatif = resultat.disponible > 0 ? solde / resultat.disponible : 0;

  champ("r-solde").textContent = signe(solde);
  champ("r-sens").textContent = solde >= 0
    ? "Vous y gagnez sur l’année." : "Vous y perdez sur l’année.";
  champ("r-part").textContent = resultat.disponible > 0
    ? POURCENT.format(relatif) : "—";
  champ("r-impot").textContent = signe(resultat.impotActuel - resultat.impotCible);
  champ("r-capital").textContent = resultat.perteEnCapital < 0
    ? signe(resultat.perteEnCapital) : "—";

  const figure = champ("cascade");
  const dessin = dessinerCascade(resultat.canaux, solde);
  figure.replaceChildren(dessin.svg);
  derniere = dessin;
  viser(selection);
}

/** Encadre une marche et la dit en toutes lettres, sans couleur pour seul guide. */
function viser(index) {
  if (!derniere) { return; }
  const lecture = champ("lecture");
  const survol = derniere.svg.querySelector(".survol");
  survol.replaceChildren();
  for (const groupe of derniere.svg.querySelectorAll(".marche")) {
    groupe.classList.remove("visee");
  }
  const marche = derniere.marches[index];
  if (!marche) {
    lecture.hidden = true;
    selection = -1;
    return;
  }
  selection = index;
  const x = MARGE.gauche + index * derniere.large + (derniere.large - derniere.barre) / 2;
  const hautMarche = derniere.y(Math.max(marche.depart, marche.arrivee));
  const basMarche = derniere.y(Math.min(marche.depart, marche.arrivee));
  survol.append(balise("rect", {
    class: "cadre", x: x - 4, y: hautMarche - 4, width: derniere.barre + 8,
    height: Math.max(basMarche - hautMarche, 2) + 8,
  }));
  derniere.svg.querySelectorAll(".marche")[index].classList.add("visee");
  lecture.hidden = false;
  lecture.innerHTML = `<strong>${marche.nom} : ${signe(marche.montant)}</strong> `
                    + `<span class="part">— ${marche.detail}.</span>`;
}

function calculer() {
  ecrire(calculerCanaux(lire()));
}

const formulaire = document.getElementById("formulaire");
if (formulaire) {
  formulaire.addEventListener("input", calculer);
  formulaire.addEventListener("change", calculer);
  formulaire.addEventListener("submit", (evenement) => {
    evenement.preventDefault();
    calculer();
  });

  const figure = champ("cascade");
  figure.addEventListener("pointermove", (evenement) => {
    const groupe = evenement.target.closest(".marche-groupe");
    if (groupe) { viser(Number(groupe.dataset.index)); }
  });
  figure.addEventListener("pointerleave", () => viser(-1));
  // Au clavier, la cascade se parcourt aux flèches : la boîte prend le focus,
  // les flèches déplacent le cadre, Échap le retire.
  figure.addEventListener("keydown", (evenement) => {
    const pas = { ArrowRight: 1, ArrowLeft: -1 }[evenement.key];
    if (pas) {
      evenement.preventDefault();
      const total = derniere.marches.length;
      viser(((selection < 0 ? (pas > 0 ? -1 : 0) : selection) + pas + total) % total);
    } else if (evenement.key === "Escape") {
      viser(-1);
    }
  });
  figure.addEventListener("blur", () => viser(-1));

  calculer();
}
