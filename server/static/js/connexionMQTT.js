// connexionMQTT.js

const options = {
    username: 'mqtt-access@ttn',
    password: 'NNSXS.LJDO5CK3GZ6ORBP6RQ3DDQBIDUXOA73RSEUEB5Y.7N6NA427MLRFJEGKV62WMNTLB3R6L6BDNUBHDQVDEX6PMGXTKXHQ',
    protocol: 'wss'
};

const client = mqtt.connect('wss://eu1.cloud.thethings.network/mqtt', options);

client.on('connect', () => {
    console.log("Connecté à TTN MQTT");
    client.subscribe('v3/tonAppID@ttn/devices/+/up');
});
