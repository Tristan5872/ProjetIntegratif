// Variables Three.js pour la serre
let serreScene, serreCamera, serreRenderer;
let serreGroup, capteurInt, capteurExt, trappe, chauffage;
let serreAnimationId;

// États des équipements
let etatTrappe = false; // false = fermé, true = ouvert
let etatChauffage = false;

function initSerre3D() {
  const container = document.getElementById('serre-3d-container');
  const width = container.offsetWidth;
  const height = container.offsetHeight;

  // Scène
  serreScene = new THREE.Scene();
  serreScene.background = new THREE.Color(0x87CEEB);

  // Caméra
  serreCamera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
  serreCamera.position.set(12, 8, 12);
  serreCamera.lookAt(0, 0, 0);

  // Renderer
  serreRenderer = new THREE.WebGLRenderer({ antialias: true });
  serreRenderer.setSize(width, height);
  serreRenderer.shadowMap.enabled = true;
  serreRenderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(serreRenderer.domElement);

  // Éclairage
  const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
  serreScene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(30, 30, 20);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 1024;
  directionalLight.shadow.mapSize.height = 1024;
  serreScene.add(directionalLight);

  // Contrôles de caméra
  setupSerreControls();

  // Construction de la serre
  createSerre();

  // Sol
  const groundGeometry = new THREE.PlaneGeometry(30, 30);
  const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x90EE90 });
  const ground = new THREE.Mesh(groundGeometry, groundMaterial);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  serreScene.add(ground);

  // Animation
  animateSerre();

  // Masquer le loading
  document.getElementById('serre-3d-loading').style.display = 'none';

  // Observer les changements d'état des équipements
  observerEquipements();

  serreCamera.position.set(12, 8, 12); // bonne distance
  serreCamera.lookAt(0, 0, 0); // viser le centre de la serre

}

function createSerre() {
  serreGroup = new THREE.Group();

  // Dimensions: 10m x 3m x 2.2m
  const largeur = 10, profondeur = 3, hauteur = 2.2;

  // Matériaux
  const structureMat = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
  const verreMat = new THREE.MeshLambertMaterial({ 
    color: 0x87CEEB, 
    transparent: true, 
    opacity: 0.3 
  });

  // Structure (poteaux)
  const poteaux = [
    [largeur/2, hauteur/2, profondeur/2],
    [largeur/2, hauteur/2, -profondeur/2],
    [-largeur/2, hauteur/2, profondeur/2],
    [-largeur/2, hauteur/2, -profondeur/2]
  ];

  poteaux.forEach(pos => {
    const poteau = new THREE.Mesh(
      new THREE.CylinderGeometry(0.08, 0.08, hauteur),
      structureMat
    );
    poteau.position.set(pos[0], pos[1], pos[2]);
    poteau.castShadow = true;
    serreGroup.add(poteau);
  });

  // Murs de verre
  const murs = [
    { pos: [0, hauteur/2, profondeur/2], size: [largeur, hauteur, 0.05] },
    { pos: [0, hauteur/2, -profondeur/2], size: [largeur, hauteur, 0.05] },
    { pos: [largeur/2, hauteur/2, 0], size: [profondeur, hauteur, 0.05] },
    { pos: [-largeur/2, hauteur/2, 0], size: [profondeur, hauteur, 0.05] }
  ];

  murs.forEach((mur, index) => {
    const panel = new THREE.Mesh(
      new THREE.BoxGeometry(mur.size[0], mur.size[1], mur.size[2]),
      verreMat
    );
    panel.position.set(mur.pos[0], mur.pos[1], mur.pos[2]);
    if (index >= 2) panel.rotation.y = Math.PI/2;
    panel.receiveShadow = true;
    serreGroup.add(panel);
  });

  // Toit principal
  const toitGeometry = new THREE.ConeGeometry(largeur/2.2, 1.2, 4);
  toitGeometry.rotateY(Math.PI/4);
  const toit = new THREE.Mesh(toitGeometry, verreMat);
  toit.position.set(0, hauteur + 0.6, 0);
  toit.scale.set(1.6, 1, 1);
  toit.castShadow = true;
  serreGroup.add(toit);

  // Trappe sur le toit (fenêtre)
  trappe = new THREE.Group();
  const trappeBase = new THREE.Mesh(
    new THREE.BoxGeometry(1.5, 0.05, 1),
    new THREE.MeshLambertMaterial({ color: 0x654321 })
  );
  trappeBase.position.set(0, hauteur + 1.2, 0);
  
  const trappeVitre = new THREE.Mesh(
    new THREE.BoxGeometry(1.4, 0.02, 0.9),
    new THREE.MeshLambertMaterial({ 
      color: 0x87CEEB, 
      transparent: true, 
      opacity: 0.7 
    })
  );
  trappeVitre.position.set(0, hauteur + 1.22, 0);
  
  trappe.add(trappeBase);
  trappe.add(trappeVitre);
  serreGroup.add(trappe);

  // Capteur intérieur (à 1.5m du sol)
  capteurInt = createCapteur(0x2196F3, 'intérieur');
  capteurInt.position.set(2, 1.5, 0);
  capteurInt.userData = { type: 'interieur' };
  serreGroup.add(capteurInt);

  // Capteur extérieur
  capteurExt = createCapteur(0xFF9800, 'extérieur');
  capteurExt.position.set(-8, 1.5, 2);
  capteurExt.userData = { type: 'exterieur' };
  serreScene.add(capteurExt);

  // Système de chauffage (fil chauffant au sol)
  chauffage = new THREE.Group();
  const filMaterial = new THREE.MeshBasicMaterial({ 
    color: 0xff4500,
    emissive: 0x441100 
  });
  
  // Plusieurs segments de fil en zigzag
  for (let i = 0; i < 8; i++) {
    const segment = new THREE.Mesh(
      new THREE.CylinderGeometry(0.02, 0.02, largeur - 2),
      filMaterial
    );
    segment.position.set(0, 0.05, -1 + (i * 0.3));
    segment.rotation.z = Math.PI / 2;
    chauffage.add(segment);
  }
  
  chauffage.visible = false; // Initialement éteint
  serreGroup.add(chauffage);

  serreScene.add(serreGroup);
}

function createCapteur(couleur, type) {
  const capteur = new THREE.Group();

  // Boîtier
  const boitier = new THREE.Mesh(
    new THREE.BoxGeometry(0.3, 0.2, 0.1),
    new THREE.MeshLambertMaterial({ color: couleur })
  );
  boitier.castShadow = true;
  capteur.add(boitier);

  // Antenne
  const antenne = new THREE.Mesh(
    new THREE.CylinderGeometry(0.015, 0.015, 0.4),
    new THREE.MeshLambertMaterial({ color: 0x424242 })
  );
  antenne.position.set(0, 0.3, 0);
  capteur.add(antenne);

  // LED
  const led = new THREE.Mesh(
    new THREE.SphereGeometry(0.025),
    new THREE.MeshBasicMaterial({ color: type === 'intérieur' ? 0x00ff00 : 0xff0000 })
  );
  led.position.set(0.1, 0.08, 0.06);
  capteur.add(led);
  capteur.userData.led = led;

  // Label flottant avec données
  const labelDiv = document.createElement('div');
  labelDiv.style.position = 'absolute';
  labelDiv.style.background = 'rgba(255,255,255,0.9)';
  labelDiv.style.padding = '5px';
  labelDiv.style.borderRadius = '3px';
  labelDiv.style.fontSize = '10px';
  labelDiv.style.pointerEvents = 'none';
  labelDiv.style.display = 'none';
  labelDiv.style.zIndex = '1000';
  document.body.appendChild(labelDiv);
  capteur.userData.label = labelDiv;

  return capteur;
}

function setupSerreControls() {
  let isMouseDown = false;
  let mouseX = 0, mouseY = 0;
  let targetRotationX = 0, targetRotationY = 0;

  serreRenderer.domElement.addEventListener('mousedown', onSerreMouseDown);
  serreRenderer.domElement.addEventListener('mousemove', onSerreMouseMove);
  serreRenderer.domElement.addEventListener('mouseup', onSerreMouseUp);
  serreRenderer.domElement.addEventListener('wheel', onSerreWheel);
  serreRenderer.domElement.addEventListener('click', onSerreClick);

  function onSerreMouseDown(event) {
    isMouseDown = true;
    mouseX = event.clientX;
    mouseY = event.clientY;
  }

  function onSerreMouseMove(event) {
    if (isMouseDown) {
      const deltaX = event.clientX - mouseX;
      const deltaY = event.clientY - mouseY;
      
      targetRotationY += deltaX * 0.01;
      targetRotationX += deltaY * 0.01;
      
      // Rotation de la caméra autour de la serre
      const radius = 15;
      serreCamera.position.x = Math.cos(targetRotationY) * radius;
      serreCamera.position.z = Math.sin(targetRotationY) * radius;
      serreCamera.position.y = Math.max(3, 8 + targetRotationX);
      
      serreCamera.lookAt(0, 1, 0);
      
      mouseX = event.clientX;
      mouseY = event.clientY;
      // Rotation Y limitée entre -45° et 45°
      targetRotationY = Math.max(Math.min(targetRotationY, Math.PI / 4), -Math.PI / 4);
    }
  }

  function onSerreMouseUp() {
    isMouseDown = false;
  }

  function onSerreWheel(event) {
    event.preventDefault();
    const zoomSpeed = 0.1;
    const delta = event.deltaY * zoomSpeed;

    // Nouvelle position limitée
    const distance = serreCamera.position.length();
    const newDistance = THREE.MathUtils.clamp(distance + delta, 10, 30); // Limites min/max

    // Direction depuis l'origine (0, 0, 0)
    const direction = serreCamera.position.clone().normalize();
    serreCamera.position.copy(direction.multiplyScalar(newDistance));
  }

  function onSerreClick(event) {
    // Détection de clic sur les capteurs
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    
    const rect = serreRenderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, serreCamera);
    const intersects = raycaster.intersectObjects([capteurInt, capteurExt], true);
    
    if (intersects.length > 0) {
      const capteur = intersects[0].object.parent;
      if (capteur.userData.type) {
        showSensorModal(capteur.userData.type);
      }
    }
  }
}

function observerEquipements() {
  // Observer le bouton de trappe
  const btnOuvrir = document.getElementById("btn-ouvrir");
  const btnFermer = document.getElementById("btn-fermer");
  
  if (btnOuvrir) {
    btnOuvrir.addEventListener("click", () => {
      setTimeout(() => {
        etatTrappe = btnOuvrir.classList.contains("ouvert");
        updateTrappe();
      }, 100);
    });
  }
  
  if (btnFermer) {
    btnFermer.addEventListener("click", () => {
      setTimeout(() => {
        etatTrappe = !btnFermer.classList.contains("ferme");
        updateTrappe();
      }, 100);
    });
  }

  // Observer le bouton de chauffage
  const btnChauffage = document.getElementById("btn-chauffage");
  if (btnChauffage) {
    btnChauffage.addEventListener("click", () => {
      setTimeout(() => {
        etatChauffage = btnChauffage.textContent.includes("Éteindre");
        updateChauffage();
      }, 100);
    });
  }
}

function updateTrappe() {
  if (trappe) {
    if (etatTrappe) {
      // Ouvrir la trappe
      trappe.rotation.x = -Math.PI / 3;
    } else {
      // Fermer la trappe
      trappe.rotation.x = 0;
    }
  }
}

function updateChauffage() {
  if (chauffage) {
    chauffage.visible = etatChauffage;
    
    // Animation du chauffage
    if (etatChauffage) {
      chauffage.children.forEach((segment, index) => {
        setTimeout(() => {
          segment.material.emissive.setHex(0x441100);
        }, index * 100);
      });
    }
  }
}

function updateCapteurData() {
  // Récupérer les données depuis les éléments HTML existants
  const tempInt = document.getElementById("temperature-int")?.textContent || "--";
  const humInt = document.getElementById("humidity-int")?.textContent || "--";
  const co2Int = document.getElementById("co2-int")?.textContent || "--";
  const lightInt = document.getElementById("light-int")?.textContent || "--";
  const vddInt = document.getElementById("vdd-int")?.textContent || "--";

  const tempExt = document.getElementById("temperature-ext")?.textContent || "--";
  const humExt = document.getElementById("humidity-ext")?.textContent || "--";
  const lightExt = document.getElementById("light-ext")?.textContent || "--";
  const vddExt = document.getElementById("vdd-ext")?.textContent || "--";

  // Afficher les données près des capteurs
  if (capteurInt && capteurInt.userData.label) {
    capteurInt.userData.label.innerHTML = `
      <strong>Capteur Int.</strong><br>
      T: ${tempInt}<br>
      H: ${humInt}<br>
      CO₂: ${co2Int}
    `;
  }

  if (capteurExt && capteurExt.userData.label) {
    capteurExt.userData.label.innerHTML = `
      <strong>Capteur Ext.</strong><br>
      T: ${tempExt}<br>
      H: ${humExt}
    `;
  }
}

function showSensorModal(type) {
  const modal = document.getElementById("sensor-modal");
  const title = document.getElementById("modal-sensor-title");
  const data = document.getElementById("modal-sensor-data");

  if (type === 'interieur') {
    title.textContent = "🏠 Capteur Intérieur";
    data.innerHTML = `
      <p><strong>Température:</strong> ${document.getElementById("temperature-int")?.textContent || "--"}</p>
      <p><strong>Humidité:</strong> ${document.getElementById("humidity-int")?.textContent || "--"}</p>
      <p><strong>CO₂:</strong> ${document.getElementById("co2-int")?.textContent || "--"}</p>
      <p><strong>Luminosité:</strong> ${document.getElementById("light-int")?.textContent || "--"}</p>
      <p><strong>Alimentation:</strong> ${document.getElementById("vdd-int")?.textContent || "--"}</p>
      <p><strong>Présence:</strong> ${document.getElementById("motion-int")?.textContent || "--"}</p>
    `;
  } else {
    title.textContent = "🌿 Capteur Extérieur";
    data.innerHTML = `
      <p><strong>Température:</strong> ${document.getElementById("temperature-ext")?.textContent || "--"}</p>
      <p><strong>Humidité:</strong> ${document.getElementById("humidity-ext")?.textContent || "--"}</p>
      <p><strong>Luminosité:</strong> ${document.getElementById("light-ext")?.textContent || "--"}</p>
      <p><strong>Alimentation:</strong> ${document.getElementById("vdd-ext")?.textContent || "--"}</p>
      <p><strong>Présence:</strong> ${document.getElementById("motion-ext")?.textContent || "--"}</p>
    `;
  }

  modal.style.display = "block";
}

function closeSensorModal() {
  document.getElementById("sensor-modal").style.display = "none";
}

function animateSerre() {
  serreAnimationId = requestAnimationFrame(animateSerre);

  // Animation des LEDs
  const time = Date.now() * 0.003;
  if (capteurInt && capteurInt.userData.led) {
    capteurInt.userData.led.material.emissive.setHex(
      Math.sin(time) > 0 ? 0x002200 : 0x000000
    );
  }
  if (capteurExt && capteurExt.userData.led) {
    capteurExt.userData.led.material.emissive.setHex(
      Math.sin(time + 1) > 0 ? 0x220000 : 0x000000
    );
  }

  // Animation du chauffage si activé
  if (chauffage && chauffage.visible) {
    chauffage.children.forEach((segment, index) => {
      const intensity = 0.3 + 0.2 * Math.sin(time * 2 + index);
      segment.material.emissive.setRGB(intensity, intensity * 0.3, 0);
    });
  }

  // Mise à jour des données capteurs
  updateCapteurData();

  serreRenderer.render(serreScene, serreCamera);
}

function handleSerreResize() {
  const container = document.getElementById('serre-3d-container');
  const width = container.offsetWidth;
  const height = container.offsetHeight;
  
  serreCamera.aspect = width / height;
  serreCamera.updateProjectionMatrix();
  serreRenderer.setSize(width, height);
}

// Initialisation au chargement de la page
window.addEventListener('load', () => {
  setTimeout(initSerre3D, 500); // Délai pour s'assurer que tout est chargé
});

// Gestion du redimensionnement
window.addEventListener('resize', handleSerreResize);

// Nettoyage
window.addEventListener('beforeunload', () => {
  if (serreAnimationId) {
    cancelAnimationFrame(serreAnimationId);
  }
});