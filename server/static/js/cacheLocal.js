const cacheName = 'header-image-cache-v1';

// Fonction pour récupérer le chemin correct selon la page
function getImageUrl() {
  // Si la page est dans un dossier, on remonte d'un niveau, sinon pas
  if (window.location.pathname.startsWith('/pages/')) {
    return '../ressources/feuillage.webp';
  } else {
    return 'ressources/feuillage.webp';
  }
}

const imageUrl = getImageUrl();

async function cacheHeaderImage() {
  if ('caches' in window) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(imageUrl);
    if (!cachedResponse) {
      console.log('Mise en cache de l\'image...');
      await cache.add(imageUrl);
    } else {
      console.log('Image déjà en cache.');
    }
  } else {
    console.warn('Cache API non supporté.');
  }
}

async function loadImageFromCache() {
  if ('caches' in window) {
    const cache = await caches.open(cacheName);
    const response = await cache.match(imageUrl);
    if (response) {
      const blob = await response.blob();
      const objectURL = URL.createObjectURL(blob);
      document.querySelector('header').style.backgroundImage = `url(${objectURL})`;
    } else {
      document.querySelector('header').style.backgroundImage = `url(${imageUrl})`;
    }
  } else {
    document.querySelector('header').style.backgroundImage = `url(${imageUrl})`;
  }
}

window.addEventListener('load', async () => {
  await cacheHeaderImage();
  await loadImageFromCache();
});
