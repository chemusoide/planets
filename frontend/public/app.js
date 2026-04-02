const apiStatus = document.querySelector('#api-status');
const planetCount = document.querySelector('#planet-count');
const planetList = document.querySelector('#planet-list');
const planetDetail = document.querySelector('#planet-detail');
const selectedPlanet = document.querySelector('#selected-planet');
const planetSummaryChip = document.querySelector('#planet-summary-chip');
const randomFact = document.querySelector('#random-fact');
const quickStats = document.querySelector('#planet-quick-stats');
const quickStatsNote = document.querySelector('#quick-stats-note');
const requestView = document.querySelector('#request-view');
const responseView = document.querySelector('#response-view');
const requestIdView = document.querySelector('#request-id');
const responseStatusView = document.querySelector('#response-status');
const responseTimeView = document.querySelector('#response-time');
const refreshButton = document.querySelector('#refresh-list');
const toggleTechButton = document.querySelector('#toggle-tech');
const toggleTechCloseButton = document.querySelector('#toggle-tech-close');
const techPanel = document.querySelector('#tech-panel');
const stepBrowser = document.querySelector('#step-browser');
const stepProxy = document.querySelector('#step-proxy');
const stepBackend = document.querySelector('#step-backend');
const stepStorage = document.querySelector('#step-storage');
const logsList = document.querySelector('#logs-list');
const syncNowButton = document.querySelector('#sync-now');
const syncSourceName = document.querySelector('#sync-source-name');
const syncStatusLabel = document.querySelector('#sync-status-label');
const syncLastSuccess = document.querySelector('#sync-last-success');
const syncCacheMode = document.querySelector('#sync-cache-mode');
const syncMessage = document.querySelector('#sync-message');
const architectureList = document.querySelector('#architecture-list');
const projectFlowList = document.querySelector('#project-flow-list');
const categoryFilters = document.querySelector('#category-filters');
const categoryFilterButtons = categoryFilters ? Array.from(categoryFilters.querySelectorAll('button[data-category]')) : [];

let planetsCache = [];
let adminOverviewCache = null;
let activeCategory = 'all';

function clearElement(element) {
  element.replaceChildren();
}

function appendTextElement(parent, tagName, text, className = '') {
  const element = document.createElement(tagName);
  if (className) {
    element.className = className;
  }
  element.textContent = text;
  parent.appendChild(element);
  return element;
}

function createLabeledValue(label, value) {
  const wrapper = document.createElement('div');
  const term = document.createElement('dt');
  const description = document.createElement('dd');
  term.textContent = label;
  description.textContent = value;
  wrapper.append(term, description);
  return wrapper;
}

function getSafeImageUrl(url) {
  if (!url) {
    return '';
  }

  try {
    const parsedUrl = new URL(url, window.location.origin);
    if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:') {
      return '';
    }
    return parsedUrl.toString();
  } catch {
    return '';
  }
}

function formatResponseBody(responseData) {
  if (typeof responseData === 'string') {
    return responseData;
  }
  return JSON.stringify(responseData, null, 2);
}

async function parseResponseBody(response) {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }
  return response.text();
}

function getResponseErrorMessage(response, responseData) {
  if (responseData && typeof responseData === 'object' && typeof responseData.detail === 'string') {
    return responseData.detail;
  }

  if (typeof responseData === 'string' && responseData.trim()) {
    return responseData.trim().slice(0, 300);
  }

  return `HTTP ${response.status} ${response.statusText}`.trim();
}

function updateDebugPanel(requestData, responseData, response) {
  requestView.textContent = JSON.stringify(requestData, null, 2);
  responseView.textContent = formatResponseBody(responseData);
  responseStatusView.textContent = `${response.status} ${response.statusText}`.trim();
  requestIdView.textContent = response.headers.get('x-request-id') || 'No enviado';
  responseTimeView.textContent = `${response.headers.get('x-response-time-ms') || '0'} ms`;

  stepBrowser.textContent = `El navegador ha preparado una petición ${requestData.method} hacia ${requestData.url}.`;
  stepProxy.textContent = 'Nginx sirve el frontend y reenvía la ruta /api al contenedor backend por la red interna de Docker.';
  stepBackend.textContent = `FastAPI procesa ${requestData.url} y usa el servicio de planetas para construir la respuesta.`;
  stepStorage.textContent = 'La información se lee desde SQLite, que queda guardada en un volumen persistente para sobrevivir a reinicios.';
}

function setApiStatus(text, className) {
  apiStatus.textContent = text;
  apiStatus.className = `badge ${className}`;
}

function formatDayLength(hours) {
  if (hours > 72) {
    return `${hours.toLocaleString('es-ES')} h`;
  }
  return `${hours.toLocaleString('es-ES', { maximumFractionDigits: 1 })} h`;
}

function formatDistance(distance) {
  return `${distance.toLocaleString('es-ES', { maximumFractionDigits: 1 })} millones de km`;
}

function formatDistanceCompact(distance) {
  return `${distance.toLocaleString('es-ES', { maximumFractionDigits: 1 })} M km`;
}

function getCategoryLabel(category) {
  if (category === 'solar-system') {
    return 'Sistema solar';
  }
  if (category === 'exoplanets') {
    return 'Fuera del sistema solar';
  }
  return 'Todos los mundos';
}

function formatDateTime(value) {
  if (!value) {
    return 'Todavía no disponible';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString('es-ES');
}

function updateQuickStats(planet) {
  clearElement(quickStats);
  quickStats.append(
    createLabeledValue('Lunas', String(planet.moons)),
    createLabeledValue('Duración', formatDayLength(planet.day_length_hours)),
    createLabeledValue('Distancia', formatDistanceCompact(planet.distance_from_sun_million_km)),
  );
  quickStatsNote.textContent = `Modo actual: ${getCategoryLabel(activeCategory)}.`;
}

function updateRandomFact(planet) {
  randomFact.textContent = planet.fun_fact;
}

function renderAdminOverview(overview) {
  adminOverviewCache = overview;
  syncSourceName.textContent = overview.sync.source_name;
  syncStatusLabel.textContent = overview.sync.last_status;
  syncLastSuccess.textContent = formatDateTime(overview.sync.last_success_at);
  syncCacheMode.textContent = overview.sync.using_cached_data ? 'Sirviendo desde caché SQLite' : 'Datos recién sincronizados';
  syncMessage.textContent = overview.sync.last_message;

  clearElement(architectureList);
  overview.architecture.forEach((section) => {
    const item = document.createElement('li');
    item.className = 'architecture-item';
    appendTextElement(item, 'strong', section.name);
    appendTextElement(item, 'p', section.responsibility);
    const technologies = document.createElement('div');
    technologies.className = 'tech-pill-row';
    section.technologies.forEach((technology) => {
      appendTextElement(technologies, 'span', technology, 'tech-pill');
    });
    item.appendChild(technologies);
    architectureList.appendChild(item);
  });

  clearElement(projectFlowList);
  overview.flow.forEach((step) => {
    const item = document.createElement('li');
    item.textContent = step;
    projectFlowList.appendChild(item);
  });
}

function setTechPanelVisibility(isOpen) {
  techPanel.classList.toggle('is-collapsed', !isOpen);
  techPanel.setAttribute('aria-hidden', String(!isOpen));
  toggleTechButton.setAttribute('aria-expanded', String(isOpen));
  toggleTechButton.textContent = isOpen ? 'Ocultar modo técnico' : 'Abrir modo técnico';
}

async function loadRecentLogs() {
  try {
    const response = await fetch('/api/logs/recent?limit=8');
    const payload = await parseResponseBody(response);
    if (!response.ok || !payload || typeof payload !== 'object' || !Array.isArray(payload.items)) {
      throw new Error(getResponseErrorMessage(response, payload));
    }

    clearElement(logsList);
    payload.items.forEach((entry) => {
      const item = document.createElement('li');
      item.textContent = entry;
      logsList.appendChild(item);
    });
  } catch (error) {
    clearElement(logsList);
    appendTextElement(logsList, 'li', 'No se pudieron cargar los logs recientes.');
  }
}

async function loadAdminOverview() {
  const overview = await callApi('/admin/overview');
  renderAdminOverview(overview);
  return overview;
}

async function triggerSync() {
  syncNowButton.disabled = true;
  syncNowButton.textContent = 'Sincronizando...';

  try {
    const overview = await callApi('/admin/sync', { method: 'POST' });
    renderAdminOverview(overview);
    await loadPlanetList();
    const preferredPlanet = planetsCache.find((planet) => planet.id === 3) || planetsCache[0];
    if (preferredPlanet) {
      await loadPlanetDetail(preferredPlanet.id);
    }
  } finally {
    syncNowButton.disabled = false;
    syncNowButton.textContent = 'Sincronizar ahora';
  }
}

async function callApi(path, options = {}) {
  const requestData = {
    method: options.method || 'GET',
    url: `/api${path}`,
    headers: options.headers || {},
  };

  try {
    const response = await fetch(`/api${path}`, options);
    const responseData = await parseResponseBody(response);

    updateDebugPanel(requestData, responseData, response);
    await loadRecentLogs();

    if (!response.ok) {
      throw new Error(getResponseErrorMessage(response, responseData));
    }

    setApiStatus('API conectada', 'badge-ok');
    return responseData;
  } catch (error) {
    const responseData = { error: error.message };
    requestView.textContent = JSON.stringify(requestData, null, 2);
    responseView.textContent = JSON.stringify(responseData, null, 2);
    responseStatusView.textContent = 'Fallo';
    requestIdView.textContent = 'Sin respuesta';
    setApiStatus('Error de conexión', 'badge-error');
    throw error;
  }
}

function renderPlanetList(planets) {
  clearElement(planetList);
  planetCount.textContent = `${planets.length}`;

  planets.forEach((planet) => {
    const item = document.createElement('li');
    const button = document.createElement('button');
    button.className = 'planet-button';
    button.type = 'button';
    appendTextElement(button, 'span', planet.emoji, 'planet-emoji');

    const copy = document.createElement('span');
    copy.className = 'planet-copy';
    appendTextElement(copy, 'strong', planet.name);
    appendTextElement(copy, 'small', getCategoryLabel(planet.category), 'planet-tag');
    appendTextElement(copy, 'small', planet.kid_summary);
    button.appendChild(copy);

    button.addEventListener('click', () => loadPlanetDetail(planet.id));
    item.appendChild(button);
    planetList.appendChild(item);
  });
}

function renderPlanetDetail(planet) {
  selectedPlanet.textContent = planet.name;
  const categoryPrefix = planet.category === 'exoplanets' ? 'exoplaneta' : 'planeta';
  planetSummaryChip.textContent = `${planet.emoji} ${categoryPrefix} ${planet.position}`;
  planetDetail.className = 'planet-spotlight';
  clearElement(planetDetail);

  const spotlightTop = document.createElement('div');
  spotlightTop.className = 'spotlight-top';
  appendTextElement(spotlightTop, 'div', planet.emoji, 'spotlight-emoji');

  const copy = document.createElement('div');
  appendTextElement(copy, 'h3', planet.name);
  appendTextElement(copy, 'p', planet.kid_summary, 'spotlight-intro');
  spotlightTop.appendChild(copy);
  planetDetail.appendChild(spotlightTop);

  const safeImageUrl = getSafeImageUrl(planet.image_url);
  if (safeImageUrl) {
    const image = document.createElement('img');
    image.className = 'planet-image';
    image.src = safeImageUrl;
    image.alt = `Imagen de ${planet.name}`;
    image.loading = 'lazy';
    planetDetail.appendChild(image);
  }

  appendTextElement(planetDetail, 'p', planet.description, 'spotlight-description');
  appendTextElement(planetDetail, 'div', `Curiosidad: ${planet.fun_fact}`, 'fact-ribbon');

  const details = document.createElement('dl');
  details.className = 'detail-grid';
  details.append(
    createLabeledValue('Clima', planet.climate),
    createLabeledValue('Terreno', planet.terrain),
    createLabeledValue('Población', planet.population),
  );
  planetDetail.appendChild(details);

  updateQuickStats(planet);
  updateRandomFact(planet);
}

async function loadPlanetList() {
  setApiStatus('Cargando lista', 'badge-waiting');
  const suffix = activeCategory === 'all' ? '' : `?category=${encodeURIComponent(activeCategory)}`;
  const data = await callApi(`/planets${suffix}`);
  planetsCache = data.items;
  renderPlanetList(data.items);
}

function getPreferredPlanet() {
  if (activeCategory === 'solar-system') {
    return planetsCache.find((planet) => planet.id === 3) || planetsCache[0];
  }

  return planetsCache[0] || null;
}

function setActiveCategory(category) {
  activeCategory = category;
  categoryFilterButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.category === category);
    button.setAttribute('aria-selected', String(button.dataset.category === category));
  });
}

async function reloadCategoryView() {
  await loadPlanetList();
  const preferredPlanet = getPreferredPlanet();
  if (preferredPlanet) {
    await loadPlanetDetail(preferredPlanet.id);
    return;
  }

  selectedPlanet.textContent = 'Sin resultados';
  planetSummaryChip.textContent = getCategoryLabel(activeCategory);
  planetDetail.className = 'planet-spotlight empty-state';
  planetDetail.textContent = 'No hay mundos disponibles en esta categoría.';
}

async function loadPlanetDetail(id) {
  setApiStatus(`Cargando planeta ${id}`, 'badge-waiting');
  const planet = await callApi(`/planets/${id}`);
  renderPlanetDetail(planet);
}

refreshButton.addEventListener('click', () => {
  loadPlanetList().catch((error) => {
    planetDetail.textContent = `No se pudo cargar la lista: ${error.message}`;
  });
});

toggleTechButton.addEventListener('click', () => {
  const isOpen = techPanel.classList.contains('is-collapsed');
  setTechPanelVisibility(isOpen);
});

toggleTechCloseButton.addEventListener('click', () => {
  setTechPanelVisibility(false);
});

syncNowButton.addEventListener('click', () => {
  triggerSync().catch((error) => {
    syncMessage.textContent = `No se pudo sincronizar: ${error.message}`;
  });
});

categoryFilterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setActiveCategory(button.dataset.category);
    reloadCategoryView().catch((error) => {
      planetDetail.textContent = `No se pudo cambiar la categoría: ${error.message}`;
    });
  });
});

loadPlanetList()
  .then(() => {
    const preferredPlanet = getPreferredPlanet();
    if (preferredPlanet) {
      return loadPlanetDetail(preferredPlanet.id);
    }
    return null;
  })
  .catch((error) => {
    planetDetail.textContent = `No se pudo conectar con la API: ${error.message}`;
  });

loadAdminOverview().catch(() => {
  syncMessage.textContent = 'No se pudo cargar el estado de administración.';
});
