/* Forge Creator — app.js */
(() => {
"use strict";

// ── Trait Definitions (mirrored from portrait_generator.py) ──
const BACKGROUNDS = {
  warrior: "battle-scarred warrior with confident stance and weathered armor",
  scholar: "learned scholar with wise eyes, robes, and arcane symbols",
  rogue:   "cunning rogue with sharp features, hooded cloak, and hidden blades",
  mystic:  "enigmatic mystic with glowing eyes, flowing ethereal garments, and an aura of power",
};
const BUILDS = {
  imposing: "tall and powerfully built, commanding presence",
  average:  "average build, approachable and adaptable",
  slight:   "lean and agile, quick and precise",
};
const AUGMENTATIONS = {
  organic:    "fully organic, natural appearance",
  cybernetic: "visible cybernetic augmentations — glowing circuit lines, a mechanical arm or eye, chrome accents blended with medieval armor",
  psychic:    "psychic-touched — faint ethereal glow around the head, wisps of energy trailing from the eyes, slightly otherworldly appearance",
};

const MODEL_HINTS = {
  "gemini-3-pro-image-preview": "10 req/min · Best quality",
  "gemini-2.5-flash-image":     "10 req/min · Fast & good",
  "imagen-4.0-ultra-generate-001": "5 req/min · Ultra resolution",
  "gemini-2.0-flash-exp-image-generation": "10 req/min · Original classic",
};

const MERITH_QUOTES = [
  "Hold still... no, not like that...",
  "A little more to the left... YOUR left...",
  "I said I wanted fireball, not portrait! ...oh well.",
  "The brush is doing that thing again...",
  "Almost... almost... don't sneeze...",
  "This might be my best work yet. Don't tell the Council.",
  "Do you smell burning? ...Never mind, that's normal.",
  "The last person who fidgeted got turned into a still life.",
  "Purple is NOT a creative choice, it's the only color I have left!",
];

// ── DOM refs ──
const $ = id => document.getElementById(id);
const screens = {
  creator:  $("screen-creator"),
  painting: $("screen-painting"),
  portrait: $("screen-portrait"),
  gallery:  $("screen-gallery"),
};

// ── State ──
let state = {
  background: "warrior",
  build: "average",
  augmentation: "organic",
};
let quoteInterval = null;

// ── Screen management ──
function showScreen(name) {
  Object.values(screens).forEach(s => s.classList.remove("active"));
  screens[name].classList.add("active");
  window.scrollTo(0, 0);
}

// ── Toast ──
function toast(msg, ms = 3000) {
  const el = $("toast");
  el.textContent = msg;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), ms);
}

// ── Toggle button groups ──
document.querySelectorAll(".btn-group").forEach(group => {
  const field = group.dataset.field;
  group.querySelectorAll(".sel-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      group.querySelectorAll(".sel-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state[field] = btn.dataset.val;
    });
    // Set defaults
    if (btn.dataset.val === state[field]) btn.classList.add("active");
  });
});

// ── Model hint ──
$("sel-model").addEventListener("change", () => {
  $("model-hint").textContent = MODEL_HINTS[$("sel-model").value] || "";
});

// ── Load saved API key ──
const savedKey = localStorage.getItem("forge_api_key");
if (savedKey) $("inp-key").value = savedKey;

// ── Prompt builder (mirrors portrait_generator.py) ──
function buildPrompt(traits) {
  const desc = (traits.description || "").trim();
  const bg = BACKGROUNDS[traits.background] || BACKGROUNDS.warrior;
  const build = BUILDS[traits.build] || BUILDS.average;
  const aug = AUGMENTATIONS[traits.augmentation] || AUGMENTATIONS.organic;
  const name = traits.ruler_name || "the ruler";

  let prompt = "Create a fantasy portrait painting in rich oil paint style. " +
    `This is a royal portrait of ${name}, the new ruler of the Forge Kingdom. ` +
    "Painted by a wizard named Merith who accidentally turns all his spells into art. \n\n";

  if (desc) prompt += `Subject description: ${desc}\n`;

  prompt += `Character archetype: ${bg}. ` +
    `Physical build: ${build}. ` +
    `Special traits: ${aug}. \n\n` +
    "Art style: Oil painting with visible brushstrokes, warm firelight and purple magical ambiance, " +
    "ornate golden frame border, medieval fantasy aesthetic with a hint of steampunk. " +
    "The portrait should look like it belongs in a castle gallery. " +
    "Dramatic lighting from the left. Rich colors — deep purples, warm golds, ember oranges. " +
    "The subject should look regal but approachable, like someone you'd follow into battle " +
    "or trust with your kingdom's API keys. " +
    "Portrait orientation, head and upper body, facing slightly left. " +
    "Resolution: high quality, detailed.";

  return prompt;
}

// ── API call ──
async function generatePortrait(traits, apiKey, model) {
  const prompt = buildPrompt(traits);
  const isImagen = model.startsWith("imagen");
  let url, payload;

  if (isImagen) {
    url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:predict?key=${apiKey}`;
    payload = {
      instances: [{ prompt }],
      parameters: { sampleCount: 1, aspectRatio: "3:4", outputOptions: { mimeType: "image/png" } },
    };
  } else {
    url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    payload = {
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { responseModalities: ["IMAGE", "TEXT"], temperature: 1.0 },
    };
  }

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${errText.slice(0, 300)}`);
  }

  const data = await res.json();

  if (isImagen) {
    const pred = (data.predictions || [])[0];
    if (!pred || !pred.bytesBase64Encoded) throw new Error("No image in Imagen response");
    return { base64: pred.bytesBase64Encoded, mime: pred.mimeType || "image/png" };
  }

  const parts = (data.candidates || [])[0]?.content?.parts || [];
  for (const part of parts) {
    if (part.inlineData?.data) {
      return { base64: part.inlineData.data, mime: part.inlineData.mimeType || "image/png" };
    }
  }
  throw new Error("No image data in response");
}

// ── Merith quotes ──
function startQuotes() {
  let i = Math.floor(Math.random() * MERITH_QUOTES.length);
  const el = $("merith-quote");
  el.textContent = `"${MERITH_QUOTES[i]}"`;
  quoteInterval = setInterval(() => {
    i = (i + 1) % MERITH_QUOTES.length;
    el.style.opacity = "0";
    setTimeout(() => {
      el.textContent = `"${MERITH_QUOTES[i]}"`;
      el.style.opacity = "1";
    }, 300);
  }, 2000);
}
function stopQuotes() {
  if (quoteInterval) clearInterval(quoteInterval);
  quoteInterval = null;
}

// ── IndexedDB for full images ──
function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open("ForgeGallery", 1);
    req.onupgradeneeded = () => req.result.createObjectStore("images", { keyPath: "id" });
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function saveImage(id, base64, mime) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("images", "readwrite");
    tx.objectStore("images").put({ id, base64, mime });
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function loadImage(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("images", "readonly");
    const req = tx.objectStore("images").get(id);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

// ── Gallery metadata in localStorage ──
function getGallery() {
  try { return JSON.parse(localStorage.getItem("forge_gallery") || "[]"); } catch { return []; }
}
function saveGallery(g) { localStorage.setItem("forge_gallery", JSON.stringify(g)); }

function createThumbnail(base64, mime) {
  return new Promise(resolve => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement("canvas");
      const s = 200;
      const aspect = img.width / img.height;
      c.width = aspect >= 1 ? s : s * aspect;
      c.height = aspect >= 1 ? s / aspect : s;
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      resolve(c.toDataURL("image/jpeg", 0.7));
    };
    img.src = `data:${mime};base64,${base64}`;
  });
}

// ── Paint button ──
$("btn-paint").addEventListener("click", async () => {
  const name = $("inp-name").value.trim();
  const apiKey = $("inp-key").value.trim();
  if (!apiKey) { toast("Enter your Gemini API key first!"); return; }
  if (!name) { toast("Your ruler needs a name!"); return; }

  localStorage.setItem("forge_api_key", apiKey);

  const traits = {
    ruler_name: name,
    description: $("inp-desc").value,
    background: state.background,
    build: state.build,
    augmentation: state.augmentation,
  };
  const model = $("sel-model").value;

  showScreen("painting");
  startQuotes();
  $("btn-paint").disabled = true;

  try {
    const { base64, mime } = await generatePortrait(traits, apiKey, model);

    // Save to gallery
    const id = "portrait_" + Date.now();
    await saveImage(id, base64, mime);
    const thumb = await createThumbnail(base64, mime);
    const gallery = getGallery();
    gallery.unshift({ id, name, thumb, date: new Date().toISOString() });
    if (gallery.length > 50) gallery.length = 50; // cap
    saveGallery(gallery);

    // Show portrait
    showPortrait(name, base64, mime);
  } catch (e) {
    console.error(e);
    toast("Merith's brush exploded: " + e.message, 5000);
    showScreen("creator");
  } finally {
    stopQuotes();
    $("btn-paint").disabled = false;
  }
});

// ── Show portrait ──
let currentPortrait = null;
function showPortrait(name, base64, mime) {
  currentPortrait = { name, base64, mime };
  $("portrait-name").textContent = name;
  $("portrait-img").src = `data:${mime};base64,${base64}`;
  showScreen("portrait");
}

// ── Portrait actions ──
$("btn-download").addEventListener("click", () => {
  if (!currentPortrait) return;
  const ext = currentPortrait.mime.includes("png") ? "png" : "jpg";
  const a = document.createElement("a");
  a.href = `data:${currentPortrait.mime};base64,${currentPortrait.base64}`;
  a.download = `${currentPortrait.name.replace(/\s+/g, "_")}_portrait.${ext}`;
  a.click();
  toast("Saved! 💾");
});

$("btn-share").addEventListener("click", async () => {
  if (!currentPortrait || !navigator.share) { toast("Share not available"); return; }
  try {
    const blob = await (await fetch(`data:${currentPortrait.mime};base64,${currentPortrait.base64}`)).blob();
    const file = new File([blob], "portrait.png", { type: currentPortrait.mime });
    await navigator.share({ title: `${currentPortrait.name}'s Portrait`, files: [file] });
  } catch (e) {
    if (e.name !== "AbortError") toast("Share failed");
  }
});

$("btn-repaint").addEventListener("click", () => showScreen("creator"));
$("btn-back").addEventListener("click", () => showScreen("creator"));

// ── Gallery ──
$("btn-gallery").addEventListener("click", () => renderGallery());
$("btn-gallery-back").addEventListener("click", () => showScreen("creator"));

function renderGallery() {
  const gallery = getGallery();
  const grid = $("gallery-grid");
  grid.innerHTML = "";

  if (!gallery.length) {
    grid.innerHTML = '<div class="gallery-empty">No portraits yet. Merith awaits!</div>';
    showScreen("gallery");
    return;
  }

  gallery.forEach(item => {
    const div = document.createElement("div");
    div.className = "gallery-item";
    div.innerHTML = `<img src="${item.thumb}" alt="${item.name}"><div class="gallery-label">${item.name}</div>`;
    div.addEventListener("click", async () => {
      const full = await loadImage(item.id);
      if (full) showPortrait(item.name, full.base64, full.mime);
      else toast("Image not found");
    });
    grid.appendChild(div);
  });

  showScreen("gallery");
}

// ── Service Worker ──
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
})();
