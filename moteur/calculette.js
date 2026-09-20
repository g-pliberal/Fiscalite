// Le simulateur de la page Revenus : impôt proportionnel, revenu universel,
// solde, taux net effectif. Il n'y a rien de plus à calculer, et c'est le point
// — la note tient le dispositif pour lisible, une page qui aurait besoin de
// deux cents lignes de script pour le montrer dirait le contraire.
//
// Tout se fait dans le navigateur : aucune valeur saisie ne quitte la page, et
// il n'y a pas de serveur à qui elle pourrait partir.

"use strict";

// Les formats à la française : virgule décimale, espace insécable des milliers.
// `Intl` les connaît, et connaît aussi les préférences du lecteur — inutile de
// les réécrire à la main.
const EUROS = new Intl.NumberFormat("fr-FR", {
  style: "currency", currency: "EUR", maximumFractionDigits: 0,
});
const POURCENT = new Intl.NumberFormat("fr-FR", {
  style: "percent", maximumFractionDigits: 1,
});

const champ = (id) => document.getElementById(id);

// Une saisie vide, négative ou absurde ne doit pas produire « NaN € » : elle
// retombe sur la valeur par défaut du champ, qui est celle de l'exemple de la
// note.
function nombre(id, defaut, maximum) {
  const brut = Number.parseFloat(champ(id).value.replace(",", "."));
  if (!Number.isFinite(brut) || brut < 0) { return defaut; }
  return Math.min(brut, maximum);
}

function calculer() {
  const revenu = nombre("revenu", 30000, 100000000);
  const taux = nombre("taux-impot", 25, 60) / 100;
  const ru = nombre("ru", 600, 5000) * 12;

  const impot = revenu * taux;
  // Le solde est ce que vous versez NET : négatif quand l'impôt dépasse le
  // revenu universel, positif quand c'est l'inverse. Le signe est celui de la
  // note, où « +7 200 € » se lit « reçu ».
  const solde = ru - impot;
  // Le taux net effectif ne se lit que pour un contributeur net, et n'existe
  // pas pour un revenu nul : on ne divise pas par zéro pour faire joli.
  const effectif = revenu > 0 ? -solde / revenu : 0;

  champ("r-impot").textContent = "−" + EUROS.format(impot);
  champ("r-ru").textContent = "+" + EUROS.format(ru);
  champ("r-solde").textContent = (solde >= 0 ? "+" : "−") + EUROS.format(Math.abs(solde));
  // La couleur ne dit rien ici : c'est ce mot qui porte le sens, et il est lu
  // par les synthèses vocales comme il est vu.
  champ("r-sens").textContent = solde >= 0
    ? "Vous êtes bénéficiaire net."
    : "Vous êtes contributeur net.";
  champ("r-taux").textContent = solde >= 0 ? "—" : POURCENT.format(effectif);
}

// `input` et non `change` : le résultat suit la frappe, sans bouton à presser.
// Le formulaire n'a d'ailleurs pas de bouton — il n'a rien à envoyer —, et son
// `submit` est neutralisé pour que la touche Entrée ne recharge pas la page.
const formulaire = document.getElementById("formulaire");
if (formulaire) {
  formulaire.addEventListener("input", calculer);
  formulaire.addEventListener("submit", (evenement) => {
    evenement.preventDefault();
    calculer();
  });
  calculer();
}
