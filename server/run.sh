#!/bin/bash

# Active l'environnement virtuel
source monenv/bin/activate

# Lance les deux scripts en parallèle
python mqtt_ttn.py & 
python app.py