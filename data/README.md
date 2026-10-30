# Reference data

These files are the canonical player-facing labels and descriptions used by
the recovered game reference:

- `civilizations.csv` owns civilization display names, leaders, and Unique
  Ability (UA) descriptions. Its UA ID column remains blank because no shared
  UA ID storage has been recovered.
- `era-bonus-definitions.csv` owns one gameplay description for each recovered
  Unique Era Ability (UEA) ID.
- [`achievements.json`](achievements.json) owns the 50 retail achievement IDs,
  English names, unlocked/locked descriptions, gamerscore, icon image IDs and
  native trigger-mapping status. Its [reference page](../docs/reference/achievements.md)
  separates extracted display metadata from native unlock evidence.

Recovered civilization IDs, internal names, row order, and four UEA ID
assignments remain canonical in
[`civilization-bonus-storage.json`](../manifests/civilization-bonus-storage.json).
Run `python tools/reference_data.py --write` after changing these data files or
the manifest. The repository verification gate rejects a stale rendered table.

Player-facing civilization data was normalized from the [Civilization Wiki
list](https://civilization.fandom.com/wiki/Civilizations_%28CivRev%29) and
cross-checked against the [StrategyWiki civilization
reference](https://strategywiki.org/wiki/Civilization_Revolution/Civilizations).
External references help interpret the retail data. They do not override the
recovered image assignments.

## Image manifest

[`image-manifest.csv`](image-manifest.csv) records 1,130 images exported from
retail game content. Image payloads are not included. Each row names the
exported PNG and the original game archive and resource it came from.

| Column | Meaning |
|---|---|
| `category` | Export grouping for browsing related images. |
| `file` | Relative path of the exported PNG preview. |
| `width`, `height` | Exported image dimensions in pixels. |
| `source_archive` | Original game archive containing the resource. |
| `source_name` | Original resource name, with a character locator for a bitmap embedded in an SWF. |

For example, `Pregame.FPK` and `gfx_mainmenu_logo.dds` identify the game source
for `ui_external/gfx_mainmenu_logo.png`. In `gfx_groundarrow.swf#character_1`
the suffix is an export locator for an SWF character ID, not part of the
archive filename. The `misc` category holds icon and UI resources identified by
filename, `ui_external` holds images declared externally by GFx movies, and
`embedded_swf` holds bitmaps stored inside SWF movies. Categories and preview
filenames are export metadata; the source columns keep the game's names and
spelling.

The manifest was derived from the image export's `index.csv`. When refreshing
it, compare every row with the export index and preserve source names, dimensions,
SWF character locators and row order. An exported PNG path does not establish
a runtime loader key, payload format or fallback behavior.
