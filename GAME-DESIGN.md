# Forge the Kingdom — Visual Novel Game Design Document

## Overview
**Title:** Forge the Kingdom
**Engine:** Ren'Py (Python-based, free, exports to Windows/Mac/Linux/Steam)
**Genre:** Visual Novel / Comedy Fantasy
**Playtime:** 45-90 minutes (first playthrough)
**Rating:** E for Everyone

## Story Summary
A wizard named Merith accidentally destroys the Forge Kingdom with a fireball while trying to help. His wand is confiscated. He finds a paintbrush and discovers every spell he attempts now produces art instead. The player arrives as the new ruler and must rebuild the Kingdom chapter by chapter, with Merith painting the journey and providing comic relief.

---

## COMPLETE SCENE MAP

### ACT I: The Fall (Prologue)
**Scenes: 3 | Art: 3 images | Choices: 1**

#### Scene P-1: "The Kingdom Before"
- **Art:** `ch00-the-kingdom-before.png` — Magnificent kingdom at golden hour
- **Dialog:** Narrator introduces the Forge Kingdom in its glory days
- **Characters on screen:** None (establishing shot)
- **Music:** Grand orchestral theme, warm

#### Scene P-2: "The Fireball"
- **Art:** `ch00-the-fireball.png` — Merith's catastrophic fireball
- **Dialog:**
  - Narrator: Introduces Merith as brilliant, loyal, "perhaps too vigilant"
  - Narrator: Merith spots vulnerability, does what any well-meaning wizard would do...
  - [ASCII fireball equivalent → screen shake + flash effect in Ren'Py]
  - Narrator: "He cast PYROBLAST. Full power. Point blank."
  - Narrator: "He meant to save the Kingdom. He always means well."
- **Effects:** Screen shake, red flash, explosion SFX

#### Scene P-3: "The Aftermath"
- **Art:** `ch00-the-aftermath.png` — Ruins with dawn breaking
- **Dialog:**
  - Narrator: The Forge went cold. Scrying Glass shattered. Knights fell silent.
  - Narrator: Council's verdict: "Merith. Give us the wand."
  - Narrator: Merith finds paintbrush, can't cast spells, only makes art
  - Narrator: "The paintings are *magnificent*."
- **Transition:** Narrator addresses the player: "All we need... is a new ruler."
- **Choice 1:** "Do you accept the crown?" → Yes (continue) / No (game over joke → restart)
- **Input:** Player enters their ruler name

---

### ACT II: The Rebuilding (Chapters 1-9)

#### Chapter 1: "Survey the Ruins"
- **Art:** `ch01-survey-the-ruins.png` — Figure surveying damage by torchlight
- **What happens:** Ruler tours the wreckage with narrator commentary
- **Dialog:**
  - Narrator: "You stand amid the wreckage. Smoke still rises from the Forge."
  - Narrator describes checking foundations (OS), sending ravens (internet), checking treasury (disk)
  - [Fun visual: scroll with green ✓ / red ✗ checkmarks]
  - Narrator: "The foundations survived. We can rebuild on this."
- **Side Quest Available:** Merith offers to paint (optional content)

#### Chapter 2: "Gather the Materials"
- **Art:** `ch02-gather-materials.png` — Bustling marketplace
- **What happens:** Ruler visits the marketplace to gather supplies
- **Dialog:**
  - Narrator: "Every great Kingdom needs raw materials."
  - Narrator describes each vendor: The Brewer's Guild (Homebrew), Royal Scribes (Git), Runestone of Node (Node.js), YAML Alchemist (yq), Leak Hunter (gitleaks)
  - Each vendor gets a brief comic exchange
  - Narrator: "All materials gathered. The crafting can begin."
- **Side Quest:** Merith paints the marketplace bustle

#### Chapter 3: "Raise the Gateway"
- **Art:** `ch03-raise-the-gateway.png` — Massive gateway being magically raised
- **What happens:** The great communication arch is restored
- **Dialog:**
  - Narrator: The Gateway is the heart — all commands flow through it
  - [Visual: Gateway lighting up with cyan energy]
  - Narrator: "The Gateway rises from the ashes!"
- **Side Quest:** Merith paints the gateway's restoration

#### Chapter 4: "Reclaim the Throne Room"
- **Art:** `ch04-throne-room.png` — Throne room illuminated by sigils
- **What happens:** Setting up the royal sigils (API keys, credentials)
- **Dialog:**
  - Narrator: "The Gateway stands, but it's dark and empty."
  - Narrator: Two sigils needed — Anthropic (powers Anna) and Gemini (powers Merith)
  - Merith: "I promise to be more careful."
  - [Visual: Sigils glowing, systems spring to life]
- **Side Quest:** Merith paints his first successful painting in the new kingdom

#### Chapter 5: "Unseal the Royal Archives"
- **Art:** `ch05-royal-archives.png` — Underground archive vault
- **What happens:** Retrieving the Kingdom's blueprints from the vault
- **Dialog:**
  - Narrator: "Before the fire, every blueprint was stored in the Royal Archives"
  - [Visual: Enormous doors swinging open, golden light]
  - Narrator: "The blueprints are safe. Every spell, every schematic."
- **Side Quest:** Merith paints the wonder of the archives

#### Chapter 6: "Relight the Forge"
- **Art:** `ch06-relight-the-forge.png` — The dramatic relighting
- **What happens:** THE turning point — the Forge burns again
- **Dialog:**
  - Narrator: "The Forge was the heart of the Kingdom"
  - [Visual: Ruler thrusts torch into furnace → FLAMES ROAR]
  - Narrator: "The furnace roars back to life. The anvil rings."
  - Narrator: "The Forge burns bright once more."
- **This is the emotional peak of Act II**
- **Side Quest:** Merith's most passionate painting

#### Chapter 7: "Polish the Scrying Glass"
- **Art:** `ch07-scrying-glass.png` — Crystalline dome being restored
- **What happens:** The kingdom's window to the world is repaired
- **Dialog:**
  - Narrator: Scrying Glass spotted trends and threats before anyone else knew
  - [Visual: Swirling images in the glass — tools, technologies]
  - Narrator: "The Glass clears. Shapes begin to form."
- **Side Quest:** Merith captures the mystical shimmer

#### Chapter 8: "Awaken the Wizard"
- **Art:** `ch08-awaken-merith.png` — Merith's study in the Pale Tower
- **What happens:** The ruler visits Merith in his tower — the emotional heart
- **Dialog:**
  - Merith: "Fireball. FIREBALL. Come on, just one little—"
  - [A painting appears]
  - Merith: "...painting. Yes. Another painting. Wonderful."
  - Merith: "Oh! You're here. I was just... practicing."
  - Merith: "I keep trying to cast spells, but the brush just... paints things."
  - Merith: "Beautiful things, admittedly. But I miss my wand."
  - Merith: "The Council says I can have one supervised Pyroblast per day. ONE."
  - Merith: "...a wizard who blew up an entire kingdom. Right. Fair enough."
- **This is the character moment — Merith is funny, sad, endearing**
- **Side Quest:** Merith paints a self-portrait (meta!)

#### Chapter 9: "Set the Royal Schedule"
- **Art:** `ch09-royal-schedule.png` — Grand astronomical clock
- **What happens:** Establishing the Kingdom's daily routines
- **Dialog:**
  - Narrator: "A Kingdom without routine is just a collection of buildings."
  - [Visual: Clock mechanism showing different daily activities]
  - Show the full schedule: dawn scans, morning patrols, water cooler, pyroblast at night
  - Narrator: "The heralds take their positions. The schedule is set."
- **Side Quest:** Merith paints time itself

---

### ACT III: The Coronation (Chapter 10)

#### Scene F-1: "The Kingdom Restored"
- **Art:** `ch10-kingdom-restored.png` — Aerial view of rebuilt kingdom at sunset
- **Dialog:**
  - Narrator: "The Forge burns bright. The Scrying Glass shimmers."
  - Narrator: "Knights stand at attention. The Wizard watches from his tower."
  - Narrator: "The Kingdom breathes again."
  - [Long, emotional beat]

#### Scene F-2: "The Coronation"
- **Art:** `ch10-the-coronation.png` — Grand ceremony in the great hall
- **Dialog:**
  - [Crown ASCII → animated crown placement in Ren'Py]
  - Narrator: "Long live [RULER_NAME]! Ruler of the Forge Kingdom!"
  - Anna: "Welcome back. I've missed having someone competent in charge."
  - Merith: "I'll be watching. ...Carefully. Very carefully this time."
- **Final Merith Beat:**
  - Narrator: "The Kingdom awaits your first command."
  - Narrator: "If the Wizard asks for his wand back, just hand him a paintbrush."
  - Merith: "I can HEAR you. And for the record, I've almost figured out how to cast fireball with oil paints. Almost."
  - Narrator: "He has not almost figured it out."
- **Credits roll with all art displayed as gallery**

---

## SIDE QUEST SYSTEM

Side quests are **optional bonus content**, not branching paths. At the end of each chapter, the player can choose to:

1. **"Let Merith paint"** → Shows Merith attempting magic, producing art instead. Brief comic scene + the painting displayed full-screen. Unlocks the art in the Gallery.
2. **"Continue"** → Skip to next chapter. Art NOT unlocked (incentivizes doing side quests).

### Side Quest Template (per chapter):
```
[Chapter ends]
Merith: "Ooh, ooh! Let me paint this moment!"
Choice: [Let him paint] / [Maybe later]
→ If yes: Brief scene of Merith waving paintbrush, art appears
→ Art displayed full screen with prompt text
→ "Painting added to the Gallery!"
```

### The Gallery
- Unlockable from the main menu after completing the game
- Shows all paintings the player unlocked during their playthrough
- Each painting shows the prompt that generated it
- Completionist incentive: "Collect all 14 paintings"

---

## CHARACTERS

### The Narrator
- **Role:** Omniscient, campy, pseudo-serious
- **Tone:** Fantasy epic narrator who can't quite keep a straight face
- **No sprite** — text only, distinct font/color
- **Examples:** "He has not almost figured it out." / "The paintbrush does not comfort him."

### Anna (The Empress)
- **Role:** AI orchestrator, lightning-powered empress
- **Appearance:** Regal, purple/gold, lightning crackling, confident
- **Sprite needed:** Yes (2-3 expressions: neutral, amused, commanding)
- **Appears:** Prologue mention, Ch4 (systems wake), Ch10 (coronation line)
- **Key line:** "Welcome back. I've missed having someone competent in charge."

### Merith (The Wizard)
- **Role:** Comic relief, heart of the story, the lovable disaster
- **Appearance:** Elderly, singed hat, paint-stained robes, paintbrush in hand
- **Sprite needed:** Yes (4-5 expressions: embarrassed, excited, sad, determined, painting)
- **Appears:** Prologue, Ch8 (major), side quests (all), Ch10 (coronation)
- **Key trait:** Every attempt at magic produces art. Means well. Always means well.

### The Ruler (Player)
- **No sprite** (first-person perspective)
- **Named by player** at start
- **Silent protagonist** — narrator and other characters react to implied choices

---

## ART REQUIREMENTS

### Existing (14 paintings — campaign backgrounds):
| ID | File | Chapter | Description |
|----|------|---------|-------------|
| 1 | ch00-the-kingdom-before.png | 0 | Kingdom in glory days |
| 2 | ch00-the-fireball.png | 0 | Merith's catastrophic fireball |
| 3 | ch00-the-aftermath.png | 0 | Ruins with dawn breaking |
| 4 | ch01-survey-the-ruins.png | 1 | Figure surveying damage |
| 5 | ch02-gather-materials.png | 2 | Bustling marketplace |
| 6 | ch03-raise-the-gateway.png | 3 | Gateway being raised |
| 7 | ch04-throne-room.png | 4 | Throne room illuminated |
| 8 | ch05-royal-archives.png | 5 | Underground archive vault |
| 9 | ch06-relight-the-forge.png | 6 | The great relighting |
| 10 | ch07-scrying-glass.png | 7 | Crystalline dome |
| 11 | ch08-awaken-merith.png | 8 | Merith's study |
| 12 | ch09-royal-schedule.png | 9 | Astronomical clock |
| 13 | ch10-the-coronation.png | 10 | Grand coronation |
| 14 | ch10-kingdom-restored.png | 10 | Aerial view restored |

### Additional Art Needed:
| # | Type | Description | Priority |
|---|------|-------------|----------|
| 15 | **Title Screen BG** | Forge Kingdom logo over dramatic landscape | HIGH |
| 16 | **Main Menu BG** | Soft version of kingdom-before or kingdom-restored | HIGH |
| 17 | **Character: Anna** | Empress portrait (2-3 expressions) | HIGH |
| 18 | **Character: Merith** | Wizard portrait (4-5 expressions) | HIGH |
| 19 | **Character: Narrator** | (none needed — text only) | — |
| 20 | **UI: Crown icon** | For choices/menus | MEDIUM |
| 21 | **UI: Paintbrush icon** | For side quest prompts | MEDIUM |
| 22 | **Credits BG** | Twilight kingdom panorama | LOW |
| 23 | **Gallery BG** | Art gallery/museum hall | LOW |

### Character Sprite Strategy
For a VN, we need character sprites. Options:
- **A)** Generate with Gemini (consistent style challenging but possible)
- **B)** Commission ($$$ but consistent)
- **C)** Silhouette/portrait style (easier to generate consistently)
- **Recommendation:** Start with generated portraits in ornate frames (like portrait paintings) — fits the "Merith paints everything" lore perfectly. Each character IS a painting.

---

## AUDIO REQUIREMENTS

| Type | Count | Source |
|------|-------|--------|
| BGM - Title/Menu | 1 | Royalty-free fantasy |
| BGM - Exploration (calm) | 1 | Royalty-free medieval |
| BGM - Dramatic/Epic | 1 | Royalty-free orchestral |
| BGM - Emotional/Merith | 1 | Royalty-free gentle |
| BGM - Coronation/Triumph | 1 | Royalty-free fanfare |
| SFX - Fireball explosion | 1 | Free SFX library |
| SFX - Page turn | 1 | Free SFX |
| SFX - Paintbrush swish | 1 | Free SFX |
| SFX - Forge igniting | 1 | Free SFX |
| SFX - Gateway activating | 1 | Free SFX |
| SFX - Crown placement | 1 | Free SFX |

---

## TECHNICAL SPECS

### Engine: Ren'Py 8.x
- **Language:** Python + Ren'Py script
- **Resolution:** 1920x1080 (16:9)
- **Platforms:** Windows, macOS, Linux (Steam)
- **Steam SDK:** Built-in Ren'Py integration
- **Achievements:** Yes (see below)

### File Structure
```
forge-the-kingdom-vn/
├── game/
│   ├── script.rpy          # Main game script
│   ├── screens.rpy         # UI screens (customized)
│   ├── options.rpy         # Game config
│   ├── gui.rpy             # GUI customization
│   ├── gallery.rpy         # Unlockable gallery system
│   ├── images/
│   │   ├── bg/             # Background art (14 existing + new)
│   │   ├── char/           # Character sprites
│   │   └── ui/             # UI elements
│   ├── audio/
│   │   ├── bgm/            # Background music
│   │   └── sfx/            # Sound effects
│   └── fonts/              # Custom fonts (fantasy themed)
└── README.md
```

### Steam Achievements (13 total)
| Achievement | Trigger | Icon |
|-------------|---------|------|
| 👑 Crown Accepted | Accept the crown in prologue | Crown |
| 🏚️ Ruin Inspector | Complete Chapter 1 | Torch |
| 🛒 Material Girl | Complete Chapter 2 | Shopping bag |
| 🚪 Gateway Keeper | Complete Chapter 3 | Arch |
| 🔑 Keeper of Sigils | Complete Chapter 4 | Key |
| 📜 Archivist | Complete Chapter 5 | Scroll |
| 🔥 Forge Master | Complete Chapter 6 (the turning point) | Anvil |
| 🔮 Glass Polisher | Complete Chapter 7 | Crystal ball |
| 🧙 Wizard Whisperer | Complete Chapter 8 | Hat |
| ⏰ Timekeeper | Complete Chapter 9 | Clock |
| 👑 Ruler of the Forge Kingdom | Complete the game | Crown (gold) |
| 🎨 Art Collector | Unlock all 14 paintings | Paintbrush |
| 😢 Merith's Regret | Choose "No" at the crown prompt | Broken crown |

---

## DEVELOPMENT PHASES

### Phase 1: Skeleton (Tonight) ✨
- [x] Game design document (this file)
- [ ] Install Ren'Py SDK
- [ ] Create project structure
- [ ] Write complete script.rpy (all dialog, all scenes)
- [ ] Place existing 14 paintings as backgrounds
- [ ] Implement name input + basic choices
- [ ] Side quest unlock system
- [ ] Gallery screen
- [ ] Playable start-to-finish

### Phase 2: Polish (Morning Review)
- [ ] Review script flow / fix pacing
- [ ] Generate additional art (title screen, menu, character portraits)
- [ ] Add placeholder audio (royalty-free)
- [ ] Custom UI theme (purple/gold kingdom aesthetic)
- [ ] Transitions and effects (screen shake, fades, etc.)

### Phase 3: Steam-Ready
- [ ] Steam SDK integration
- [ ] Achievement system
- [ ] Store page assets (capsule images, screenshots, trailer)
- [ ] Windows build testing
- [ ] Store description + tags
- [ ] $100 Steamworks fee

### Phase 4: Release
- [ ] Beta testing
- [ ] Final art pass
- [ ] Music licensing verification
- [ ] Submit for Steam review
- [ ] Launch!

---

## ESTIMATED TIMELINE
| Phase | Time |
|-------|------|
| Phase 1 (Skeleton) | Tonight |
| Phase 2 (Polish) | 2-3 days |
| Phase 3 (Steam-Ready) | 1 week |
| Phase 4 (Release) | 1-2 weeks |
| **Total to Steam** | **~3 weeks** |

---

*"He has not almost figured it out."*
