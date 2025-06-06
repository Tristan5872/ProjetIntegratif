// envoyerDonnees.js

client.on('message', (topic, message) => {
    const json = JSON.parse(message.toString());
    const payload = json.uplink_message.decoded_payload;

    const temperature = payload.temperature;
    const humidity = payload.humidity;

    // Affichage sur la page
    document.getElementById('temperature').textContent = temperature;
    document.getElementById('humidity').textContent = humidity;

    // Envoi vers le serveur Flask (pour stocker dans InfluxDB)
    fetch('/api/receive_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            temperature: temperature,
            humidity: humidity
        })
    }).then(response => {
        if (!response.ok) {
            console.error('Erreur lors de l\'envoi des données au serveur');
        }
    });
});
