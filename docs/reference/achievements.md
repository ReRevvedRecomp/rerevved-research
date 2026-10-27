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

`needs_mapping` means Research has not yet joined that achievement ID to its
native unlock submission, exact predicate, relevant counter and identity, and
save/reset behavior where applicable. A description or a mapped gameplay
mechanic alone does not establish this connection. Related combat, victory,
city and technology findings remain usable leads.

`mapped` requires resolving evidence locators for the native achievement-specific
connection. It does not by itself establish natural runtime acceptance.
The `unlockTrigger.evidence` array is empty while no such connection is
promoted. Mark a partially investigated trigger `needs_mapping` until the
required joins are complete; record supported partial evidence alongside it.

The catalog covers retail metadata and trigger-research status. Custom
recompilation achievements use their own IDs and are outside its 50 entries.
The [ordinary combat boundary](ordinary-combat.md) explains why an observed
combat or presentation pass cannot be assumed to be a unique unit defeat.

## Catalog

This table is generated from the canonical JSON. Run
`python tools/reference_data.py --write` after editing the data; the regular
verification gate rejects a stale table.

<!-- achievement-catalog:begin -->
| ID | Name | Unlocked description | Locked description | G | Icon ID | Trigger mapping |
| ---: | --- | --- | --- | ---: | ---: | --- |
| 5 | Napalm in the Morning | You have won a battle! | Defeat an enemy unit | 3 | 21 | needs_mapping |
| 6 | Buy the Ticket, Take the Ride | You have met with another civilization! | Make contact with another civilization. | 3 | 23 | needs_mapping |
| 7 | Scientia Potentia Est | You have developed a new technology! | Complete development of any technology. | 3 | 25 | needs_mapping |
| 8 | Home is Where One Starts From | You have constructed a building! | Construct a special building. | 3 | 20 | needs_mapping |
| 9 | The Fruit of Labor | You have built your second city! | Build a second city in a game. | 5 | 30 | needs_mapping |
| 10 | Before all Else, Be Armed | You have earned a special unit ability! | Earn a special unit ability in combat. | 5 | 24 | needs_mapping |
| 11 | Once More Unto the Breach | You have created an army! | Combine three identical units into an army. | 5 | 18 | needs_mapping |
| 12 | 80% of Success is Showing Up | You have unlocked a great person! | Accumulate culture to unlock a great person. | 5 | 22 | needs_mapping |
| 13 | Good Afternoon, Doctor Jones. | You have discovered an ancient artifact! | Discover an ancient artifact. | 9 | 19 | needs_mapping |
| 14 | Culture is Worth a Little Risk | You have built a Wonder of the World! | Build a Wonder of the World. | 9 | 26 | needs_mapping |
| 15 | Veni Vidi Vici | You have won as a Roman civilization! | Win as a Roman civilization. | 15 | 35 | needs_mapping |
| 16 | I Will Not Be Triumphed Over | You have won as an Egyptian civilization! | Win as an Egyptian civilization. | 15 | 36 | needs_mapping |
| 17 | A Short Life of Glory | You have won as a Greek civilization! | Win as a Greek civilization. | 15 | 37 | needs_mapping |
| 18 | Fair and Softly Goes Far | You have won as a Spanish civilization! | Win as a Spanish civilization. | 15 | 38 | needs_mapping |
| 19 | Blood and Iron | You have won as a German civilization! | Win as a German civilization. | 15 | 39 | needs_mapping |
| 20 | A Great Wind is Blowing | You have won as a Russian civilization! | Win as a Russian civilization. | 15 | 40 | needs_mapping |
| 21 | Let a Hundred Flowers Bloom | You have won as a Chinese civilization! | Win as a Chinese civilization. | 15 | 41 | needs_mapping |
| 22 | We the People | You have won as an American civilization! | Win as an American civilization. | 15 | 42 | needs_mapping |
| 23 | Victory Over Lesser Men | You have won as a Japanese civilization! | Win as a Japanese civilization. | 15 | 43 | needs_mapping |
| 24 | Imagination Rules the World | You have won as a French civilization! | Win as a French civilization. | 15 | 44 | needs_mapping |
| 25 | An Indomitable Will | You have won as an Indian civilization! | Win as an Indian civilization. | 15 | 45 | needs_mapping |
| 26 | A Knight Without Fear or Blame | You have won as an Arab civilization! | Win as an Arab civilization. | 15 | 46 | needs_mapping |
| 27 | Flower and Song | You have won as an Aztec civilization! | Win as an Aztec civilization. | 15 | 47 | needs_mapping |
| 28 | This World is a Harsh Place | You have won as an African civilization! | Win as an African civilization. | 15 | 48 | needs_mapping |
| 29 | All Others Must Fail | You have won as a Mongolian civilization! | Win as a Mongolian civilization. | 15 | 49 | needs_mapping |
| 30 | One Mistress and No Master | You have won as an English civilization! | Win as an English civilization. | 15 | 50 | needs_mapping |
| 31 | Have Fun Storming the Castle | You have won a Domination Victory! | Win a Domination Victory. | 20 | 12 | needs_mapping |
| 32 | Ideas Control the World | You have won a Technology Victory! | Win a Technology Victory. | 20 | 31 | needs_mapping |
| 33 | A Revelation of Man | You have won with a Cultural Victory! | Win a Cultural Victory. | 20 | 8 | needs_mapping |
| 34 | A Penny Saved is a Penny Earned | You have won an Economic Victory! | Win an Economic Victory. | 20 | 15 | needs_mapping |
| 35 | Destroyer of Worlds | You have won all types of victories! | Win all types of victories (Domination, Technology, Cultural, and Economic). | 30 | 4 | needs_mapping |
| 36 | Difficulties Mastered | You have won as all civilizations! | Win a victory with each civilization. | 30 | 34 | needs_mapping |
| 37 | Vi Victa Vis | You have won a Domination Victory as King or higher! | Win a Domination Victory on at least King difficulty. | 30 | 14 | needs_mapping |
| 38 | 640K Ought to be Enough | You have won a Technology Victory as King or higher! | Win a Technology Victory on at least King difficulty. | 30 | 33 | needs_mapping |
| 39 | Embiggens the Smallest Man | You have won a Cultural Victory as King or higher! | Win a Cultural Victory on at least King difficulty. | 30 | 10 | needs_mapping |
| 40 | The Guy Who Signs the Checks | You have won an Economic Victory as King or higher! | Win an Economic Victory on at least King difficulty. | 30 | 17 | needs_mapping |
| 41 | Here's Looking at You, Kid | You have unlocked all Great Persons! | Unlock all Great Persons. | 45 | 3 | needs_mapping |
| 42 | Such Joy Ambition Finds | You have won a Domination Victory on Deity difficulty! | Win a Domination victory on Deity difficulty. | 45 | 13 | needs_mapping |
| 43 | Indistinguishable From Magic | You have won a Technology Victory on Deity difficulty! | Win a Technology victory on Deity difficulty. | 45 | 32 | needs_mapping |
| 44 | Citizen of the World | You have won a Cultural Victory on Deity difficulty! | Win a Cultural victory on Deity difficulty. | 45 | 9 | needs_mapping |
| 45 | Playing the Game | You have won an Economic Victory on Deity difficulty! | Win an Economic victory on Deity difficulty. | 45 | 16 | needs_mapping |
| 46 | That We May Live in Peace | You have won the game by year 1000 AD on King difficulty or higher! | Win the game by year 1000 AD on King difficulty or higher. | 25 | 51 | needs_mapping |
| 47 | Absolute Power is Kind of Neat | You have won without changing governments on King difficulty or higher | Win without changing governments on King difficulty or higher. | 25 | 11 | needs_mapping |
| 48 | The Will to Win is Everything | Your unit has had 20 wins in battle! | Win 20 battles with one unit.<br> | 25 | 1 | needs_mapping |
| 49 | Power Never Takes a Back Step | You have won with only one city on King difficulty or higher! | Win with only one city on at least King difficulty. | 25 | 5 | needs_mapping |
| 50 | What is the City But the People? | Your city has grown to size 20! | Grow a city to size 20. | 25 | 6 | needs_mapping |
| 51 | Organized Knowledge | Your city has achieved 200 science production! | Develop a city to produce 200 science per turn. | 25 | 29 | needs_mapping |
| 52 | The Root of All Evil | Your city has achieved 200 gold production! | Develop a city to produce 200 gold per turn. | 25 | 27 | needs_mapping |
| 53 | Curse of the Drinking Class | Your city has achieved 200 resource production! | Develop a city to produce 200 resources per turn. | 25 | 28 | needs_mapping |
| 54 | The Universal Brotherhood of Man | Your city has achieved 200 culture production! | Develop a city to produce 200 culture per turn. | 25 | 7 | needs_mapping |
<!-- achievement-catalog:end -->
