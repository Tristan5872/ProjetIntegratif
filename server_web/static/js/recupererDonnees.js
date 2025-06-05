// Récupère les données de la serre depuis l'API et met à jour l'interface utilisateur.
async function fetchSerreData() {
    try {
        const response = await fetch('/api/serre');
    if (!response.ok) throw new Error('Erreur HTTP ' + response.status);

    const data = await response.json();

    // Intérieur
    document.getElementById('temperature-int').textContent = data.interieur.temperature ?? 'N/A';
    document.getElementById('co2-int').textContent = data.interieur.co2 ?? 'N/A';
    document.getElementById('humidity-int').textContent = data.interieur.humidity ?? 'N/A';

    // Extérieur
    document.getElementById('temperature-ext').textContent = data.exterieur.temperature ?? 'N/A';
    document.getElementById('humidity-ext').textContent = data.exterieur.humidity ?? 'N/A';

    } catch (error) {
        console.error('Erreur lors de la récupération des données :', error);
    }
}

// Attendre que le DOM soit chargé avant de lancer la récupération des données
window.addEventListener('load', () => {
    fetchSerreData();
    
    // Rafraîchir les données toutes les 5 secondes
    setInterval(fetchSerreData, 5000);
});
