# Retail achievements

[Achievement data](../../data/achievements.json) is the canonical catalog of the
50 English retail achievement entries for the supported title image. It keeps
the original achievement IDs, names, unlocked and locked descriptions,
gamerscore, and icon image IDs. The IDs run from 5 through 54; they are not row
numbers. Their combined retail gamerscore is 1000G.

## Source and field meanings

The image is pinned by [the image manifest](../../manifests/image.json).
ReXGlue `init achievements` loaded that XEX and applied its matching update,
then read the title's XDBF achievement metadata in English (language ID 1).
The catalog records title ID `0x545407E5` and the extractor version and digest.
The source XEX and update digests were checked against the manifest before
extraction. No icon pixels or executable data are included.

`description` is the text shown after unlocking. `unachievedDescription` is the
locked description, which normally states the player-facing requirement.
Both preserve the extracted strings verbatim, including the trailing CRLF in
achievement 48's locked description. The rendered table displays line breaks
without changing the canonical text. `imageId` identifies a title XDBF image;
it is independent of the achievement ID.

The English names and descriptions in this catalog are the scoped display
metadata exception described by the [evidence model](../evidence-model.md).
They retain their retail provenance and do not establish a license for the
original game artwork or text.

## Unlock trigger coverage

The [native trigger family](../../manifests/achievement-unlock-triggers.json)
records each retail ID's ordinal, exact submit sites, predicate, player identity
and relevant history/reset machinery. The internal ordinal is not the retail
ID: ordinals 43..49 use an explicit reordered conversion.

`mapped` means that bounded static connection has resolving evidence locators.
It does not establish natural runtime acceptance, complete caller coverage,
successful command delivery, asynchronous file completion or durable SDK unlock
storage. `needs_mapping` retains a missing native join; partial evidence can
still be linked while that status remains. No natural runtime unlock was
validated by this mapping pass.

The aggregate victory, civilization and Great Person predicates use a shared
profile bank. Its loader clears 680 bytes before optional restoration; it is
not a new-game progress reset. Great Person history serializes presence bits
and reloads 1/0 values. File-write admission remains conditional. The history
finding records those qualifications alongside the exact cells and keys.

The catalog covers retail metadata and trigger-research status. Custom
recompilation achievements use their own IDs and are outside its 50 entries.
The [ordinary combat boundary](ordinary-combat.md) explains why an observed
combat or presentation pass cannot be assumed to be a unique unit defeat.

## Custom achievement seams

The family also records the three requested adaptations and their remaining
acceptance gates:

- **200% Concentrated Power of Will:** reuse the reached local-win handler
  `0x82D052C8` and signed Deity difficulty >=4. The title must separately retain
  all five handicap values staying at 200% for the whole game.
- **One To Rule:** use that local Deity win and the actual enabled OCC policy.
  Retail 49 checks saved founding history flags; it does not read the custom
  OCC setting or compare current city count.
- **Their Rage Is Within Your Control:** four selected combat retirement calls
  expose original defeated ownership and the opposite winner. A live-to-dead
  guard can reject repeated retirement, while allowing a reused live slot.
  Full attack/defense, normal/Fast and command-42 delivery still need acceptance.
  Retail 48 counts one unit's wins and cannot supply a saved per-game tally of
  50 Barbarian units defeated by the local player.

## Native gameplay events

The [event boundary family](../../manifests/achievement-event-boundaries.json)
records additional conditional static observations. Each finding retains its
input, lifetime, route and delivery limits. None establishes complete runtime
coverage or durable per-game history.

| Event | Recorded boundary |
|---|---|
| [Unit production](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0354) | Selected post-creator completion and unit-rush joins, including alternate ship coordinates and partial-output guards. |
| [City founding](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0355) | Successful founding-only origin and current-turn observation, separate from current-city or first-capital history. |
| [ICBM action](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0356) | Two source-consumption receipts; selector/address search limits and the exact early-SDI live admission probe. |
| [Knights Templar](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0357) | Artifact selector identity and same-tile artifact-bit clearing, separate from mounted-unit grants. |
| [Water depth](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0358) | Native cache semantics, derived read-only current-terrain equivalent, conditional save/load transfer and selected committed-movement origins. |
| [Combat strength](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0359) | Final operative pair joined conditionally to the local decisive-defensive result through exact queue record/cursor lineage. |
| [Battle participation](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0360) | Opposed mode0 decision/RNG publication, checked mode2 evaluation exclusions and the later Normal/Fast presentation boundary. |
| [City capture](../../manifests/achievement-event-boundaries.json#/findings/RVA-F-0361) | Current-owner transfer with retained old owner and Palace identity, without a Boolean success return. |

## Catalog

This table is generated from the canonical JSON. Run
`python tools/reference_data.py --write` after editing the data; the regular
verification gate rejects a stale table.

<!-- achievement-catalog:begin -->
| ID | Name | Unlocked description | Locked description | G | Icon ID | Trigger mapping |
| ---: | --- | --- | --- | ---: | ---: | --- |
| 5 | Napalm in the Morning | You have won a battle! | Defeat an enemy unit | 3 | 21 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0350/triggers/5 |
| 6 | Buy the Ticket, Take the Ride | You have met with another civilization! | Make contact with another civilization. | 3 | 23 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0347/triggers/6 |
| 7 | Scientia Potentia Est | You have developed a new technology! | Complete development of any technology. | 3 | 25 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0347/triggers/7 |
| 8 | Home is Where One Starts From | You have constructed a building! | Construct a special building. | 3 | 20 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0347/triggers/8 |
| 9 | The Fruit of Labor | You have built your second city! | Build a second city in a game. | 5 | 30 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0347/triggers/9 |
| 10 | Before all Else, Be Armed | You have earned a special unit ability! | Earn a special unit ability in combat. | 5 | 24 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0350/triggers/10 |
| 11 | Once More Unto the Breach | You have created an army! | Combine three identical units into an army. | 5 | 18 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0350/triggers/11 |
| 12 | 80% of Success is Showing Up | You have unlocked a great person! | Accumulate culture to unlock a great person. | 5 | 22 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0348/triggers/12 |
| 13 | Good Afternoon, Doctor Jones. | You have discovered an ancient artifact! | Discover an ancient artifact. | 9 | 19 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0347/triggers/13 |
| 14 | Culture is Worth a Little Risk | You have built a Wonder of the World! | Build a Wonder of the World. | 9 | 26 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0347/triggers/14 |
| 15 | Veni Vidi Vici | You have won as a Roman civilization! | Win as a Roman civilization. | 15 | 35 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/15 |
| 16 | I Will Not Be Triumphed Over | You have won as an Egyptian civilization! | Win as an Egyptian civilization. | 15 | 36 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/16 |
| 17 | A Short Life of Glory | You have won as a Greek civilization! | Win as a Greek civilization. | 15 | 37 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/17 |
| 18 | Fair and Softly Goes Far | You have won as a Spanish civilization! | Win as a Spanish civilization. | 15 | 38 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/18 |
| 19 | Blood and Iron | You have won as a German civilization! | Win as a German civilization. | 15 | 39 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/19 |
| 20 | A Great Wind is Blowing | You have won as a Russian civilization! | Win as a Russian civilization. | 15 | 40 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/20 |
| 21 | Let a Hundred Flowers Bloom | You have won as a Chinese civilization! | Win as a Chinese civilization. | 15 | 41 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/21 |
| 22 | We the People | You have won as an American civilization! | Win as an American civilization. | 15 | 42 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/22 |
| 23 | Victory Over Lesser Men | You have won as a Japanese civilization! | Win as a Japanese civilization. | 15 | 43 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/23 |
| 24 | Imagination Rules the World | You have won as a French civilization! | Win as a French civilization. | 15 | 44 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/24 |
| 25 | An Indomitable Will | You have won as an Indian civilization! | Win as an Indian civilization. | 15 | 45 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/25 |
| 26 | A Knight Without Fear or Blame | You have won as an Arab civilization! | Win as an Arab civilization. | 15 | 46 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/26 |
| 27 | Flower and Song | You have won as an Aztec civilization! | Win as an Aztec civilization. | 15 | 47 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/27 |
| 28 | This World is a Harsh Place | You have won as an African civilization! | Win as an African civilization. | 15 | 48 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/28 |
| 29 | All Others Must Fail | You have won as a Mongolian civilization! | Win as a Mongolian civilization. | 15 | 49 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/29 |
| 30 | One Mistress and No Master | You have won as an English civilization! | Win as an English civilization. | 15 | 50 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/30 |
| 31 | Have Fun Storming the Castle | You have won a Domination Victory! | Win a Domination Victory. | 20 | 12 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/31 |
| 32 | Ideas Control the World | You have won a Technology Victory! | Win a Technology Victory. | 20 | 31 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/32 |
| 33 | A Revelation of Man | You have won with a Cultural Victory! | Win a Cultural Victory. | 20 | 8 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/33 |
| 34 | A Penny Saved is a Penny Earned | You have won an Economic Victory! | Win an Economic Victory. | 20 | 15 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/34 |
| 35 | Destroyer of Worlds | You have won all types of victories! | Win all types of victories (Domination, Technology, Cultural, and Economic). | 30 | 4 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/35 |
| 36 | Difficulties Mastered | You have won as all civilizations! | Win a victory with each civilization. | 30 | 34 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0346/triggers/36 |
| 37 | Vi Victa Vis | You have won a Domination Victory as King or higher! | Win a Domination Victory on at least King difficulty. | 30 | 14 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/37 |
| 38 | 640K Ought to be Enough | You have won a Technology Victory as King or higher! | Win a Technology Victory on at least King difficulty. | 30 | 33 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/38 |
| 39 | Embiggens the Smallest Man | You have won a Cultural Victory as King or higher! | Win a Cultural Victory on at least King difficulty. | 30 | 10 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/39 |
| 40 | The Guy Who Signs the Checks | You have won an Economic Victory as King or higher! | Win an Economic Victory on at least King difficulty. | 30 | 17 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/40 |
| 41 | Here's Looking at You, Kid | You have unlocked all Great Persons! | Unlock all Great Persons. | 45 | 3 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0348/triggers/41 |
| 42 | Such Joy Ambition Finds | You have won a Domination Victory on Deity difficulty! | Win a Domination victory on Deity difficulty. | 45 | 13 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/42 |
| 43 | Indistinguishable From Magic | You have won a Technology Victory on Deity difficulty! | Win a Technology victory on Deity difficulty. | 45 | 32 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/43 |
| 44 | Citizen of the World | You have won a Cultural Victory on Deity difficulty! | Win a Cultural victory on Deity difficulty. | 45 | 9 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/44 |
| 45 | Playing the Game | You have won an Economic Victory on Deity difficulty! | Win an Economic victory on Deity difficulty. | 45 | 16 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/45 |
| 46 | That We May Live in Peace | You have won the game by year 1000 AD on King difficulty or higher! | Win the game by year 1000 AD on King difficulty or higher. | 25 | 51 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/46 |
| 47 | Absolute Power is Kind of Neat | You have won without changing governments on King difficulty or higher | Win without changing governments on King difficulty or higher. | 25 | 11 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/47 |
| 48 | The Will to Win is Everything | Your unit has had 20 wins in battle! | Win 20 battles with one unit.<br> | 25 | 1 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0350/triggers/48 |
| 49 | Power Never Takes a Back Step | You have won with only one city on King difficulty or higher! | Win with only one city on at least King difficulty. | 25 | 5 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0345/triggers/49 |
| 50 | What is the City But the People? | Your city has grown to size 20! | Grow a city to size 20. | 25 | 6 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0349/triggers/50 |
| 51 | Organized Knowledge | Your city has achieved 200 science production! | Develop a city to produce 200 science per turn. | 25 | 29 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0349/triggers/51 |
| 52 | The Root of All Evil | Your city has achieved 200 gold production! | Develop a city to produce 200 gold per turn. | 25 | 27 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0349/triggers/52 |
| 53 | Curse of the Drinking Class | Your city has achieved 200 resource production! | Develop a city to produce 200 resources per turn. | 25 | 28 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0349/triggers/53 |
| 54 | The Universal Brotherhood of Man | Your city has achieved 200 culture production! | Develop a city to produce 200 culture per turn. | 25 | 7 | mapped<br>../manifests/achievement-unlock-triggers.json#/findings/RVA-F-0349/triggers/54 |
<!-- achievement-catalog:end -->
