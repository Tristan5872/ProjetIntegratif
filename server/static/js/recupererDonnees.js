// Fonction asynchrone qui récupère les données de la serre via l'API Flask (/api/serre)
// et met à jour le contenu HTML correspondant
async function fetchSerreData() {
    try {
        const response = await fetch('/api/serre');  // Appel API REST pour récupérer JSON
        if (!response.ok) throw new Error('Erreur HTTP ' + response.status);

        const data = await response.json();  // Conversion de la réponse en JSON

        console.log('Données récupérées :', data.interieur, data.exterieur);

        // Mise à jour des éléments du DOM avec les valeurs récupérées ou 'N/A' si absentes

        // Intérieur
        document.getElementById('temperature-int').textContent = data.interieur.temperature ?? 'N/A';
        document.getElementById('co2-int').textContent = data.interieur.co2 ?? 'N/A';
        document.getElementById('humidity-int').textContent = data.interieur.humidity ?? 'N/A';


        console.log(data.interieur, data.exterieur);

        // Extérieur
        document.getElementById('temperature-ext').textContent = data.exterieur.temperature ?? 'N/A';
        document.getElementById('humidity-ext').textContent = data.exterieur.humidity ?? 'N/A';

    } catch (error) {
        // Gestion des erreurs lors de la récupération des données
        console.error('Erreur lors de la récupération des données :', error);
    }
}

// On attend que la page soit complètement chargée avant d'exécuter le fetch initial
window.addEventListener('load', () => {
    fetchSerreData();

    // Puis on rafraîchit automatiquement les données toutes les 15 secondes
    setInterval(fetchSerreData, 15000);
});


// Quand le DOM est prêt, on récupère les données pour remplir les listes déroulantes
document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/serre")
    .then(response => response.json())
    .then(data => {
      const capteurSelect = document.getElementById("graph-sensor-select");
      const actionSelect = document.getElementById("table-sensor-select");

      const capteurs = new Set();
      // Liste des actions disponibles dans le filtre historique (à étendre si besoin)
      const actions = ["chauffage_on", "chauffage_off"];

      // Parcours des données pour extraire tous les noms de capteurs présents
      for (let type in data) {
        for (let capteur in data[type]) {
          capteurs.add(capteur);
        }
      }

      // Remplissage du select "graph-sensor-select" avec les capteurs détectés
      capteurs.forEach(c => {
        const option = document.createElement("option");
        option.value = c;
        option.textContent = c;
        capteurSelect.appendChild(option);
      });

      // Remplissage du select "table-sensor-select" avec les actions disponibles
      actions.forEach(a => {
        const option = document.createElement("option");
        option.value = a;
        option.textContent = a;
        actionSelect.appendChild(option);
      });
    });
});

// Quand l'utilisateur change de capteur dans le select graphique, on met à jour le graphique
document.getElementById("graph-sensor-select").addEventListener("change", (e) => {
  const capteur = e.target.value;
  fetch("/api/serre")
    .then(res => res.json())
    .then(data => {
      const valeurs = [];
      const labels = [];

      // Construction des valeurs et labels à afficher dans le graphique selon le capteur choisi
      for (let type in data) {
        if (data[type][capteur] !== undefined) {
          valeurs.push(data[type][capteur]);
          labels.push(type);
        }
      }

      // On vide le conteneur graphique puis on insère un canvas pour Chart.js
      const div = document.querySelector(".graphique");
      div.innerHTML = `<canvas id="graphiqueCapteur"></canvas>`;

      // Création du graphique en barres avec Chart.js
      new Chart(document.getElementById("graphiqueCapteur"), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: `Valeurs de ${capteur}`,
            data: valeurs
          }]
        },
        options: {
          responsive: true
        }
      });
    });
});

// Après remplissage du select, on sélectionne automatiquement la première option utile et déclenche l'affichage du graphique
document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("graph-sensor-select");
  
  // Petit délai pour laisser le temps au fetch de remplir le select avant d'agir
  setTimeout(() => {
    const firstValue = select.options[1]?.value; // On évite la première option placeholder
    if (firstValue) {
      select.value = firstValue;

      // Déclenche manuellement l'événement 'change' pour afficher le graphique
      const event = new Event("change");
      select.dispatchEvent(event);
    }
  }, 300);
});

// Filtrage de l'historique selon l'action choisie dans la liste déroulante
document.getElementById("table-sensor-select").addEventListener("change", (e) => {
  const action = e.target.value;

  // Exemple d'historique local (à remplacer par un vrai appel API si besoin)
  const historique = [
    { date: "2025-06-05 10:12", action: "chauffage_on" },
    { date: "2025-06-05 11:10", action: "chauffage_off" }
  ];

  // Filtre sur l'action choisie (vide = tout afficher)
  const filtré = historique.filter(ligne => action === "" || ligne.action === action);

  // Génération du tableau HTML affiché dans le div dédié
  const div = document.querySelector(".tableau");
  div.innerHTML = `
    <table>
      <thead><tr><th>Date</th><th>Action</th></tr></thead>
      <tbody>
        ${filtré.map(l => `<tr><td>${l.date}</td><td>${l.action}</td></tr>`).join("")}
      </tbody>
    </table>
  `;
});

// Ajout d'écouteurs sur les boutons de sélection de période de temps
document.querySelectorAll(".temps .indicator").forEach(bouton => {
  bouton.addEventListener("click", () => {
    // Exemple : récupération de la classe qui indique la période choisie (ex : 'ajd', 'semaine')
    const periode = bouton.classList[0];
    
    // Log dans la console pour debug
    console.log("🕓 Période sélectionnée :", periode);

    // Gestion du style visuel "actif"
    document.querySelectorAll(".temps .indicator").forEach(b => b.classList.remove("actif"));
    bouton.classList.add("actif");

    // Appel d'une fonction pour filtrer ou recharger les données selon la période sélectionnée
    filtrerParPeriode(periode);
  });
});

// Exemple de fonction de filtrage à implémenter selon ta logique métier
function filtrerParPeriode(periode) {
  // Ici tu peux appeler une API, ou filtrer localement les données affichées
  console.log("🔍 Chargement des données pour :", periode);
}
