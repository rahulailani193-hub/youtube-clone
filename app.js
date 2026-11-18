const grid = document.getElementById("videoGrid");
const categoryStrip = document.getElementById("categoryStrip");
const searchInput = document.getElementById("searchInput");
const searchForm = document.getElementById("searchForm");
const loadStatus = document.getElementById("loadStatus");
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("mainContent");
const playerOverlay = document.getElementById("playerOverlay");
const mainPlayer = document.getElementById("mainPlayer");
const playerTitle = document.getElementById("playerTitle");
const playerMeta = document.getElementById("playerMeta");
const closePlayer = document.getElementById("closePlayer");

let activeCategory = "All";
let currentSearch = "";
let renderBatch = 50;
let displayedVideos = [];
let activePreview = null;
let hoverTimer = null;

function buildCategoryButtons() {
  categoryStrip.innerHTML = "";
  CATEGORY_NAMES.forEach(name => {
    const button = document.createElement("button");
    button.className = `category-chip ${name === activeCategory ? "active" : ""}`;
    button.textContent = name;
    button.addEventListener("click", () => {
      activeCategory = name;
      currentSearch = "";
      searchInput.value = "";
      renderCategoryButtons();
      loadVideos(true);
    });
    categoryStrip.appendChild(button);
  });
}
function renderCategoryButtons(){
  categoryStrip.querySelectorAll(".category-chip").forEach(btn => btn.classList.toggle("active", btn.textContent === activeCategory));
}
function getCategoryVideos(category) {
  if (category === "All") return ALL_VIDEOS;
  if (category === "Recently uploaded") return [...ALL_VIDEOS].reverse();
  if (category === "Watched") return ALL_VIDEOS.filter(v => watchedVideoIds.has(v.id));
  return VIDEOS_BY_CATEGORY[category] || ALL_VIDEOS;
}
const watchedVideoIds = new Set();
function getFilteredVideos() {
  let list = getCategoryVideos(activeCategory);
  if (currentSearch.trim()) {
    const term = currentSearch.trim().toLowerCase();
    list = list.filter(v => `${v.title} ${v.channel} ${v.category}`.toLowerCase().includes(term));
  }
  return list;
}
function createCard(video) {
  const card = document.createElement("article");
  card.className = "video-card";
  card.dataset.videoId = video.id;
  card.innerHTML = `
    <div class="thumbnail-wrap">
      <img class="thumbnail" src="${video.thumbnail}" alt="${escapeHtml(video.title)}" loading="lazy" />
      <video class="preview-video" muted playsinline preload="none"></video>
      <span class="duration">${video.duration}</span>
    </div>
    <div class="card-details">
      <img class="channel-avatar" src="${video.channelAvatar}" alt="" loading="lazy" />
      <div class="card-text"><h3 class="video-title">${escapeHtml(video.title)}</h3><p class="video-meta">${escapeHtml(video.channel)}<br>${video.views} · ${video.age}</p></div>
      <button class="more-btn" aria-label="More options">⋮</button>
    </div>`;
  const wrap = card.querySelector(".thumbnail-wrap");
  const preview = card.querySelector(".preview-video");
  card.addEventListener("click", (event) => {
    if (event.target.closest(".more-btn")) return;
    openVideo(video);
  });
  wrap.addEventListener("mouseenter", () => {
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => startPreview(preview, wrap, video), 450);
  });
  wrap.addEventListener("mouseleave", () => {
    clearTimeout(hoverTimer);
    stopPreview(preview, wrap);
  });
  return card;
}
function startPreview(videoEl, wrap, item) {
  if (activePreview && activePreview !== videoEl) {
    stopPreview(activePreview, activePreview.parentElement);
  }
  activePreview = videoEl;
  videoEl.muted = true;
  videoEl.playsInline = true;
  videoEl.setAttribute("playsinline", "");
  videoEl.preload = "auto";
  videoEl.controls = false;
  wrap.classList.add("previewing");

  // Assign the source and call load() before attempting playback.
  videoEl.pause();
  videoEl.removeAttribute("src");
  videoEl.load();
  videoEl.src = item.videoUrl;
  videoEl.load();

  const playPreview = () => {
    if (activePreview !== videoEl || !wrap.matches(":hover")) return;
    videoEl.play().catch(() => wrap.classList.remove("previewing"));
  };
  videoEl.onloadeddata = playPreview;
  videoEl.oncanplay = playPreview;
  videoEl.onerror = () => {
    wrap.classList.remove("previewing");
    console.warn("Preview video failed to load:", item.videoUrl, videoEl.error);
  };
}
function stopPreview(videoEl, wrap) {
  if (!videoEl) return;
  videoEl.onloadeddata = null;
  videoEl.onerror = null;
  videoEl.pause();
  try { videoEl.currentTime = 0; } catch (_) {}
  videoEl.removeAttribute("src");
  videoEl.load();
  if (wrap) wrap.classList.remove("previewing");
  if (activePreview === videoEl) activePreview = null;
}
function loadVideos(reset = false) {
  if (reset) {
    grid.innerHTML = "";
    displayedVideos = [];
    renderBatch = 50;
  }
  const list = getFilteredVideos();
  if (reset) {
    if (!list.length) {
      grid.innerHTML = `<div class="empty-state">No videos found.</div>`;
      loadStatus.textContent = "";
      return;
    }
    displayedVideos = list.slice(0, renderBatch);
  } else {
    const next = list.slice(displayedVideos.length, displayedVideos.length + renderBatch);
    displayedVideos = displayedVideos.concat(next);
  }
  const start = reset ? 0 : grid.children.length;
  displayedVideos.slice(start).forEach(video => grid.appendChild(createCard(video)));
  loadStatus.textContent = displayedVideos.length < list.length ? `Showing ${displayedVideos.length} of ${list.length} videos — scroll to load more` : `${displayedVideos.length} videos loaded`;
}
function openVideo(video) {
  watchedVideoIds.add(video.id);
  if (activePreview) stopPreview(activePreview, activePreview.parentElement);

  // Open the overlay first so the player remains visible even if autoplay is blocked.
  playerOverlay.classList.remove("hidden");
  playerTitle.textContent = video.title;
  playerMeta.textContent = `${video.channel} · ${video.views} · ${video.age} · Loading video…`;

  mainPlayer.pause();
  mainPlayer.onerror = () => {
    const errorCode = mainPlayer.error?.code;
    const errorText = errorCode ? `Media error ${errorCode}` : "Video could not be loaded";
    playerMeta.textContent = `${video.channel} · ${video.views} · ${video.age} · ${errorText}. Make sure the media folder is present and open this project through a local server (e.g. Live Server or "python3 -m http.server").`;
    console.error("Main video failed:", video.videoUrl, mainPlayer.error);
  };
  mainPlayer.onloadedmetadata = () => {
    try { mainPlayer.currentTime = 0; } catch (_) {}
  };
  mainPlayer.oncanplay = () => {
    mainPlayer.play().catch(() => {
      playerMeta.textContent = `${video.channel} · ${video.views} · ${video.age} · Press ▶ to play`;
    });
  };
  mainPlayer.removeAttribute("src");
  mainPlayer.load();
  mainPlayer.src = video.videoUrl;
  mainPlayer.load();
}
function closeVideo() {
  mainPlayer.pause();
  mainPlayer.onloadeddata = null;
  mainPlayer.onerror = null;
  mainPlayer.removeAttribute("src");
  mainPlayer.load();
  playerOverlay.classList.add("hidden");
}
function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
}
searchForm.addEventListener("submit", e => {
  e.preventDefault();
  currentSearch = searchInput.value;
  activeCategory = "All";
  renderCategoryButtons();
  loadVideos(true);
});
document.getElementById("sidebarToggle").addEventListener("click", () => {
  sidebar.classList.toggle("collapsed");
  mainContent.classList.toggle("sidebar-collapsed");
  categoryStrip.classList.toggle("sidebar-collapsed");
});
sidebar.querySelectorAll("[data-category]").forEach(item => item.addEventListener("click", () => {
  activeCategory = item.dataset.category;
  currentSearch = "";
  searchInput.value = "";
  renderCategoryButtons();
  loadVideos(true);
}));
sidebar.querySelectorAll("[data-nav]").forEach(item => item.addEventListener("click", () => {
  const nav = item.dataset.nav;
  if (nav === "Home") activeCategory = "All";
  if (nav === "Shorts") activeCategory = "Gaming";
  if (nav === "Subscriptions") activeCategory = "Recently uploaded";
  if (nav === "Watch later" || nav === "Liked videos") activeCategory = "Watched";
  if (["Your channel","History","Playlists","Your videos","Downloads"].includes(nav)) activeCategory = "All";
  renderCategoryButtons();
  loadVideos(true);
}));
closePlayer.addEventListener("click", closeVideo);
playerOverlay.addEventListener("click", e => { if (e.target === playerOverlay) closeVideo(); });
document.addEventListener("keydown", e => { if (e.key === "Escape" && !playerOverlay.classList.contains("hidden")) closeVideo(); });
let loadingMore = false;function maybeLoadMore() {
  if (loadingMore) return;
  const remaining = document.documentElement.scrollHeight - (window.scrollY + window.innerHeight);
  if (remaining < 700 && displayedVideos.length < getFilteredVideos().length) {
    loadingMore = true;
    setTimeout(() => { loadVideos(false); loadingMore = false; }, 180);
  }
}
window.addEventListener("scroll", maybeLoadMore, { passive: true });
buildCategoryButtons();
loadVideos(true);
