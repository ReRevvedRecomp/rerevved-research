# Advisor popup sites

The advisor popup is the framed message from one of the four advisors (Science,
Military, Domestic and Foreign), plus the tutorial cue. The game uses it for
news, reports, offers and some required choices. This page groups the 169 places
in the code that show one by what the popup says, and records which popups a
mod can drop without breaking the caller. The call target is `0x82CE8338`. The
exact data is in the
[caller inventory](../../manifests/advisor-show.json#/findings/RVA-F-0248) and
its [purpose groups](../../manifests/advisor-show.json#/findings/RVA-F-0248/advisorPopupPurposeGroups).

## What a mod can change

Popups fall into three kinds.

| Handling | Sites | What it means for a mod |
| --- | --- | --- |
| `notice` | 62 | A report with no answer. No explored code path reads the returned value, so the popup can be skipped. |
| `offer` | 3 | Save reminder, Trophy Room offer and new government prompt. The caller compares the answer once; skipping the popup takes the same path as declining. |
| `keep-native` | 102 | Player menus, refusals, diplomacy, required choices, tutorial, game end and multiplayer host. Leave these alone. |

A mod suppresses a popup by jumping from the call at `0x82CE83A8` to the cleanup
route `0x82CE87A8`, the game's own skip path. The route clears two buffers,
clears the status bits the caller set (including bit `0x01000000`), resets a
float and returns `-1` through `0x82CE87F8`. A bare `-1` return is not
equivalent, and neither is the entry check's direct return through `0x82CE87F8`,
because both omit that cleanup. The route also needs a valid frame: mapped
storage for the buffers, the saved status kept without incompatible changes,
normal helper and thunk returns, and the active 1280 byte frame. The steps are in
[the advisor notice and its cleanup](spaceship-part-presentation.md#the-advisor-notice-and-its-cleanup),
which proved them for the foreign notice at `0x82D1DEBC` only; the other sites
rest on the result evidence below. The three `offer` sites treat the returned
`-1` like any answer other than the one they test for, and the 62 `notice` sites
never read it.

A mod replaces a popup by showing its own message first and then taking the same
cleanup route, or by returning the answer it wants a `used` site to see. Both
are design options that follow from the result evidence below. No runtime run
has tried either.

### Identify the site

The table below uses the address of the call instruction. Code that runs on
entry to `0x82CE8338` sees the return address, which is the site plus 4. Subtract
4, look the site up in the group tables, and act by group. The cue index (the low
byte of the first argument) is not enough on its own, because many unrelated
popups share one cue.

### Worked example: rival peace news

The call at `0x82CC8A3C` reports that a rival civilization signed a peace
treaty. It sits in the group `rival-war-and-peace-news` with handling `notice`.
The producer returns the popup result to its caller, and a caller within 2
levels overwrites it without reading it. A hook that matches the return
address `0x82CC8A40` and takes the cleanup route above hides the report and
changes nothing else.

### Worked example: save reminder

The call at `0x82D1D3A0` is the save reminder, handling `offer`. The code
compares the result with 0. Only 0 reaches the call at `0x82D00550`. A
`-1` answer skips that call, as does any other nonzero answer. A mod that hides the
reminder therefore also skips whatever `0x82D00550` does; its purpose is not
identified here. A replacement that wants the same effect returns 0 instead.

The Trophy Room offer at `0x82D083E0` behaves the same way. Only 0 runs the
block at `0x82D083EC`; every other answer goes to `0x82D0844C`. The new
government prompt at `0x82CEB298` runs its block only for the answer 1; any
other answer, including `-1`, ends the function, and its only caller discards
the value.

## Groups by purpose

The groups below are shown in the order of the manifest. Site counts are in
parentheses.

| Group | Sites | Handling |
| --- | --- | --- |
| `rival-war-and-peace-news` | 2 | `notice` |
| `rival-government-changes` | 1 | `notice` |
| `city-capture-reports` | 5 | `notice` |
| `victory-race-warnings` | 8 | `notice` |
| `rival-great-people-and-wonders` | 2 | `notice` |
| `rankings-and-culture` | 3 | `notice` |
| `artifacts-and-ancient-sites` | 5 | `notice` |
| `combat-reports` | 13 | `notice` |
| `spy-reports` | 2 | `notice` |
| `city-status-reports` | 6 | `notice` |
| `discoveries-and-progress` | 11 | `notice` |
| `village-outcomes` | 4 | `notice` |
| `save-reminder` | 1 | `offer` |
| `trophy-room-offer` | 1 | `offer` |
| `new-government-available` | 1 | `offer` |
| `player-menus-and-confirmations` | 20 | `keep-native` |
| `refusals-of-a-player-action` | 11 | `keep-native` |
| `diplomacy` | 24 | `keep-native` |
| `required-choices` | 13 | `keep-native` |
| `tutorial-and-hints` | 19 | `keep-native` |
| `game-end-and-system` | 9 | `keep-native` |
| `multiplayer-host-controls` | 6 | `keep-native` |

Two more callers, `0x82D07B9C` and `0x82D07C9C` in the function `0x82D076D8`,
have no purpose group. They pass the Military cue and no text was recovered. The
manifest lists 169 callers; 167 are grouped. Treat the two as `keep-native`
until they are identified.

## Result use

Each site is labeled by what the code does with the returned value.

| Result | Meaning |
| --- | --- |
| `ignored` | The function that shows the popup overwrites the value without reading it. |
| `returned` | That function returns the value to its caller. For the 62 `notice` sites the native-word walk found that a caller overwrites it without reading it, within the stated depth of 1, 2 or 5 levels. For the other `returned` sites the walk stopped at the producer's return and no later discard is claimed. |
| `used` | The site or a function it calls reads the value. |
| `arg-to-call` | The value is passed to a call as an argument. The callee was not walked. |
| `dead` | The walk found no live use. Both sites sit in a jump table region, so the path through the table was not traced. |

The 65 suppressible sites come from a native-word walk of the supported image
([result consumers](../../manifests/advisor-show.json#/findings/RVA-F-0249)).
The other 102 sites come from a walk of the recompiled copy of each function and
are corroboration only. Where a label has two parts, such as `ignored or
returned`, the branch arms of the function differ.


### rival-war-and-peace-news

Reports that rival civilizations declared war or made peace.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CC89BC` | News that a rival civilization declared war | returned | 2 |
| `0x82CC8A3C` | News that a rival civilization signed a peace treaty | returned | 2 |

### rival-government-changes

Reports that a rival civilization changed government.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CDFF70` | News that a rival civilization changed government | ignored | 0 |

### city-capture-reports

Reports of cities taken or recaptured, with the rewards that come with a capture.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82D1CB44` | A rival civilization recaptured a city | returned | 1 |
| `0x82D1D0A8` | A rival civilization took a city | returned | 1 |
| `0x82D1D18C` | A rival civilization took a capital | returned | 1 |
| `0x82D1CE5C` | A technology learned during a city capture | returned | 1 |
| `0x82D1C48C` | Captive Settlers rescued during a city capture | returned | 1 |

### victory-race-warnings

Warnings that a rival civilization or we are close to a victory condition.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CE1640` | A rival civilization launched a Space Station | ignored | 0 |
| `0x82D0A938` | A rival civilization discovered Space Flight | ignored | 0 |
| `0x82D0CDA4` | Victory race warning with a Science cue | ignored | 0 |
| `0x82D0D3AC` | Victory race warning with a Foreign cue (text not recovered) | ignored | 0 |
| `0x82D0D5EC` | Victory race warning with a Military cue (text not recovered) | ignored | 0 |
| `0x82D0DAD0` | Victory race warning with a Domestic cue (text not recovered) | ignored | 0 |
| `0x82E66AE0` | Countdown of Great People and wonders still needed for a victory | ignored | 0 |
| `0x82D11370` | Victory warning sent through the tutorial cue (text not recovered) | ignored | 0 |

### rival-great-people-and-wonders

Reports of rival Great People and finished wonders.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CE1244` | A rival civilization used a Great Person to upgrade | ignored | 0 |
| `0x82D1775C` | A rival civilization completed a wonder | returned | 5 |

### rankings-and-culture

Reports of world rankings and culture results.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CC7414` | A rival civilization has the strongest economy | returned | 1 |
| `0x82D85B14` | A city became the greatest city in the world | ignored | 0 |
| `0x82D1B374` | Citizens of a city react to a culture result | returned | 1 |

### artifacts-and-ancient-sites

Reports of artifacts and ancient sites found or rumored.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82D18D7C` | Rumor that a rival civilization found an artifact | returned | 1 |
| `0x82D08E5C` | Villagers hint at an ancient site | ignored | 0 |
| `0x82D17FD8` | Lost City of Atlantis found | ignored | 0 |
| `0x82D186E0` | Terracotta Army found | ignored | 0 |
| `0x82D18B9C` | Tesla's Peace Ray found | ignored | 0 |

### combat-reports

Reports of combat results, captures and nuclear defense. See [combat](combat.md) and [nuclear actions](nuclear-actions.md).

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CD8F84` | A Great General appeared after combat | ignored | 0 |
| `0x82CD9814` | A Great General appeared after combat | ignored | 0 |
| `0x82CD91D0` | A unit defeated an upgraded enemy | ignored | 0 |
| `0x82CD9294` | Combat report (text not recovered) | ignored | 0 |
| `0x82CD9558` | Combat report (text not recovered) | ignored | 0 |
| `0x82CD960C` | Combat report (text not recovered) | ignored | 0 |
| `0x82CD7A38` | Combat report (text not recovered) | ignored | 0 |
| `0x82CDCBE8` | We captured an enemy Settler | ignored | 0 |
| `0x82CDCCD4` | A rival civilization captured our Settler | ignored | 0 |
| `0x82CDCE24` | Our Settlers were captured and taken to another city | ignored | 0 |
| `0x82CDCF94` | We captured an enemy unit | ignored | 0 |
| `0x82CDD0AC` | A rival civilization captured one of our units | ignored | 0 |
| `0x82CDF268` | An SDI Defense destroyed a nuclear weapon | ignored | 0 |

### spy-reports

Reports of enemy Spy actions and bribed Great People. See [Spy missions](spy-missions.md).

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CF6E6C` | An enemy Spy stole gold from a city | returned | 1 |
| `0x82CF7418` | A Great Person was bribed | returned | 1 |

### city-status-reports

Reports of city mood and blockades.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82D1DABC` | City status report (text not recovered) | ignored | 0 |
| `0x82D1DBA0` | City status report (text not recovered) | ignored | 0 |
| `0x82D1DCA4` | City status report (text not recovered) | ignored | 0 |
| `0x82D1D9B0` | City status report: positive mood change | ignored | 0 |
| `0x82D1E3A8` | People are becoming content | ignored | 0 |
| `0x82CF5134` | A unit could not be built because the city is blockaded | ignored | 0 |

### discoveries-and-progress

Reports of technologies, eras, milestones, taxes and routes.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CEAFC4` | Our civilization was first to discover a technology | returned | 1 |
| `0x82CEAE60` | Discovery report (text not recovered) | ignored | 0 |
| `0x82D076C4` | Our civilization advanced to a new era | returned | 1 |
| `0x82CF5D20` | Economic milestone reached | ignored | 0 |
| `0x82CF3DC4` | An import tax was collected | returned | 2 |
| `0x82D06FCC` | Engineers completed a route to a city | returned | 1 |
| `0x82D17470` | A Great Wonder revealed a technology | ignored | 0 |
| `0x82D1DEBC` | Discovery report (text not recovered) | ignored | 0 |
| `0x82CED234` | Turns remaining on the current research | ignored | 0 |
| `0x82D0AA70` | Progress report (text not recovered) | ignored | 0 |
| `0x82D0AD5C` | Progress report (text not recovered) | ignored | 0 |

### village-outcomes

Results of entering a village. See [friendly villages](friendly-villages.md) and [barbarians](barbarians.md).

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82D09098` | Villagers report a threat | ignored | 0 |
| `0x82D091E8` | Villagers mention a wealthy rival city nearby | ignored | 0 |
| `0x82D0EFB0` | Villagers react to a refused or failed approach | returned | 2 |
| `0x82D08448` | Villagers join the city | ignored | 0 |

### save-reminder

Reminder to save the game.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82D1D3A0` | Reminder to save the game | used |  |

### trophy-room-offer

Offer to view the Trophy Room.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82D083E0` | Offer to view the Trophy Room | used |  |

### new-government-available

Prompt to change government when a new one is available.

| Site | What it reports | Result | Depth |
| --- | --- | --- | --- |
| `0x82CEB298` | A new government is available to adopt | used |  |

### player-menus-and-confirmations

Menus and confirmations the player opened or must confirm.

| Site | Result |
| --- | --- |
| `0x82D06534` | used |
| `0x82D06610` | used |
| `0x82D2A498` | used |
| `0x82D2B22C` | used |
| `0x82D2CF98` | used |
| `0x82D2D06C` | used |
| `0x82D2D17C` | used |
| `0x82D853AC` | used |
| `0x82D2C0DC` | used |
| `0x82D2B4A8` | used |
| `0x82D2A000` | used |
| `0x82D28C60` | used |
| `0x82D28CF0` | used |
| `0x82CD49A8` | used |
| `0x82CF4248` | used |
| `0x82CF4554` | used |
| `0x82CF48C4` | used |
| `0x82CECB9C` | used |
| `0x82CECC74` | used |
| `0x82D6AC74` | ignored |

### refusals-of-a-player-action

Explanations that a requested action is refused.

| Site | Result |
| --- | --- |
| `0x82CD4858` | ignored |
| `0x82CD4A68` | ignored |
| `0x82CD4AD0` | ignored |
| `0x82CD4C50` | ignored |
| `0x82CCEA6C` | ignored |
| `0x82CCEBB4` | ignored or returned |
| `0x82CCEF9C` | returned |
| `0x82D2C068` | dead,jumptable |
| `0x82CDD55C` | used |
| `0x82CE0614` | ignored |
| `0x82CE12BC` | ignored |

### diplomacy

Diplomacy dialogs and answers.

| Site | Result |
| --- | --- |
| `0x82CC87FC` | returned |
| `0x82CCC1FC` | used |
| `0x82CCC2D8` | ignored |
| `0x82CCF108` | returned |
| `0x82CCF1A8` | returned |
| `0x82CC75A8` | returned |
| `0x82CFBB74` | used |
| `0x82CFBC74` | used |
| `0x82CFBD28` | ignored |
| `0x82CFBDC8` | ignored |
| `0x82CFBE38` | ignored |
| `0x82CFBEBC` | ignored |
| `0x82CFD858` | used |
| `0x82CFD9C4` | used |
| `0x82CFDAA4` | used |
| `0x82CFDB78` | used |
| `0x82CFDC40` | used |
| `0x82CFDD14` | used |
| `0x82CFDDC8` | used |
| `0x82CFDE80` | used |
| `0x82CFDF18` | used |
| `0x82CFDF70` | used |
| `0x82CFDFF0` | used |
| `0x82CFE2A4` | used |

### required-choices

Prompts that need a player decision.

| Site | Result |
| --- | --- |
| `0x82CED0CC` | used |
| `0x82D187EC` | returned,used |
| `0x82D1884C` | used |
| `0x82D1E6B0` | returned,used |
| `0x82D1E748` | used |
| `0x82CE9428` | used |
| `0x82D29A18` | dead,jumptable |
| `0x82D29A68` | used |
| `0x82D29ACC` | ignored |
| `0x82D194DC` | used |
| `0x82D0BF90` | used |
| `0x82D12858` | used |
| `0x82D116A0` | ignored |

### tutorial-and-hints

Tutorial and hint messages.

| Site | Result |
| --- | --- |
| `0x82DE3810` | returned |
| `0x82DE38D8` | used |
| `0x82DE3944` | used |
| `0x82DE39A8` | used |
| `0x82DE39F0` | ignored or returned |
| `0x82DE3C74` | used |
| `0x82DE3E1C` | used |
| `0x82DE4128` | ignored |
| `0x82DE41E8` | used |
| `0x82DE4418` | used |
| `0x82DE44D4` | ignored |
| `0x82DE4654` | used |
| `0x82DE46D4` | ignored |
| `0x82DE4890` | used |
| `0x82DE4910` | ignored |
| `0x82DE4974` | ignored |
| `0x82DE4A0C` | ignored |
| `0x82DE5030` | used |
| `0x82D2A8B4` | used |

### game-end-and-system

Game end, demo, Game of the Week and system messages. Game of the Week messages are described in [Game of the Week](game-of-the-week.md).

| Site | Result |
| --- | --- |
| `0x82D0E00C` | ignored |
| `0x82D1F288` | ignored |
| `0x82D1F304` | ignored |
| `0x82D25C80` | ignored |
| `0x82D270EC` | ignored |
| `0x82DDDE4C` | ignored |
| `0x82DF9958` | used |
| `0x82D20248` | ignored |
| `0x82D204AC` | ignored |

### multiplayer-host-controls

Host menu for removing or muting players.

| Site | Result |
| --- | --- |
| `0x82DED3BC` | used |
| `0x82DED4B0` | arg-to-call |
| `0x82DED764` | used |
| `0x82DED8FC` | arg-to-call,dead |
| `0x82DEDA58` | arg-to-call,dead |
| `0x82DEDB14` | arg-to-call,dead |

## How the code does it

Every site is a direct branch and link to `0x82CE8338`, spread over 52 functions.
The first argument carries the cue index in its low byte. 168 sites pass zero in
both force arguments, so the entry check returns `-1` before any presentation
when byte `0x8314EF9F` and byte `0x8314F10B` are both nonzero. Only
`0x82DF9958` can force the popup to show. Separate checks of the word at
`0x8314F1B8` and bit `0x40000000` of the word at `0x82FFE7C4` lead to the
cleanup early-out `0x82CE87A8`. The cue switch at `0x82CE852C` selects the
advisor name: index 0 Science, 1 Military, 2 Domestic and 3 Foreign, with 4
selecting none and 5 the tutorial cue pair. See the
[entry boundary](../../manifests/advisor-show.json#/findings/RVA-F-0242) and the
[frame and input](frontend-frame-and-input.md#advisor-presentation-entry) page.

## Limits and open questions

- The groups come from static reading of the text each site loads and of its
  producer. They show what each popup says, not when the producer shows it.
- No runtime run has shown any popup suppressed through these sites. The
  early-out is the game's own skip path, but whether skipping is safe in every
  game state is not established, and a safe advisor-off setting is not known.
- The meanings of bytes `0x8314EF9F` and `0x8314F10B` are not known.
- Purposes for text that loads through a table are taken from the producer
  strings. Sites with no recovered text carry a label that says so.
- The two ungrouped sites above remain unidentified.
- The result walk is tied to this image. Another build needs a new walk.
