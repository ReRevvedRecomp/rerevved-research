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
