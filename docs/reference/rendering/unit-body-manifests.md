# Unit body manifests

When a unit is created, the function `0x82D7FE40` builds the name of the body file from the asset name in the unit type row and appends `.xml` unless the name contains `.kfm`. The unit group creates up to three members, and each member loads that file in `0x82D9CF30`. A second file, `<name>_Attachments.xml`, is tested and read for the pieces of each member, and its rows are selected by a four letter civilization key. This page is a static reading. No unit creation or file load was observed. The record is the [unit body manifest load manifest](../../../manifests/unit-body-manifest-load.json).

## Body name at creation

The unit type row at `0x82F700D8 + 0x94 * type` holds the asset name at `+0x20`. Byte `+0x48` of the row is a mask of members. The function `0x82D7FE40` starts from the asset name. The sections `typeRows` and `nameBuilder` of the manifest list the rows read and the steps.

- Type 0 uses the civilization word at `0x830ECD28 + 4 * player`. When it is in 0 through `0xF`, a 16 entry switch picks `settler_rom` through `settler_eng`.
- Type `0x1E` picks `Great_General_Ind`, `Great_General_Mod` or `GreatGeneral_Medieval` by the word at `0x830ECD08 + 4 * player`.
- Type `0x1D` picks `Caravan_Mod` when that word is 3.
- Types `0x1F` and `0x20` pick `GreatSci_F` and `GreatArtist_F` under a byte test at `0x82F6F2F0`.
- Types 2 and 7 keep `worker_rom_m`.

Then `.xml` is appended unless `.kfm` is already in the name. The name goes to slot `+0x14` of the group.

Interpretation: `0x82D7FE40` is the place where the body file of a unit is chosen. The player and civilization are at hand there, so a body of its own for the unit of one civilization and one type could be chosen at the same point, before `.xml` is appended.

## Members and the load

The group function `0x82D99EB8` tests bits 0, 1 and 2 of row byte `+0x48`. For each set bit it creates a member with `0x82D9B6E0` and calls member slot `+0xB0` with the name. That slot jumps to slot `+0xB4`, which is `0x82D9CF30`. A second route, `0x82D99CE8`, creates members for i = 3 to 8. See the `groupAndMembers` section.

The function `0x82D9CF30` copies the name to member `+0x10`, then calls `0x82D9C748`, `0x82D9BE28`, `0x82D9C4B8` and `0x82C63820`. The `.kfm` branch was not read.

## Name replacement

At `0x82D9D0E8` the name is tested with `0x82E80120`. A nonzero low byte of the result skips the replacement. Otherwise the name `Numidian_Cavalry.xml` becomes `Knight.xml`, and any other name becomes `Legion.xml`. The function `0x82E80120` was not read.

Interpretation: `0x82E80120` tests whether the file exists, and `Legion.xml` is the stand-in body for a missing file.

## Attachment table and civilization key

The function `0x82D9BE28` derives a four letter key from the player of the unit record. It reads the civilization word at `0x830ECD28 + 4 * player`, clamps it to 0 through `0xF` and takes the first four characters of the name at `0x82F7A348 + 4 * civ`. The function `0x82D9C748` appends `_Attachments.xml` to the name and tests the result with `0x82E80120`. When the test fails, it clears bit `0x10000000` of member word `+0x4`.

The function `0x82D9C050` opens the table through `0x82C92950` and selects rows with the key `civ`. For a row it reads `file` and `bone`, loads the file, and looks for `helmet`, `weapon` and `shield` in the bone name. It stores each piece count minus 1 in member bytes `+0x89` to `+0x8B`. The loads of those bytes found in the scan are in `0x82D9B9F0` and `0x82D9A3F8`. See the `civilizationKey`, `attachmentTable` and `memberBytes` sections.

The selection `0x821D0BD0` walks each node below the node it is given, at any depth, and collects each node of kind 1 whose `civ` attribute equals the whole four letter key. The key is the first four characters of the civilization name string, such as `Roma` for index 0 and `Engl` for index `0xF`. The compare `0x827F27B0` ignores the case of ASCII letters. The function `0x82D9C050` attempts one piece load for each collected node, and a load that fails skips the node. When no node is collected it loads nothing and stores nothing to member bytes `+0x89` to `+0x8B`, and it has no default row. A later node whose piece loads overwrites a byte when that byte's word is the first of the three found in its bone string. The reader is called at `0x82D9CBF4` in `0x82D9C7F0`, which is slot `+0x18` of the member table `0x82135C90`. See the `rowSelection` part of the `attachmentTable` section.

Interpretation: the attachment pieces differ by civilization through the `civ` rows of `<name>_Attachments.xml`, not through the body name. A unit of a civilization with no row gets no attachment pieces and no default set. Attachment pieces for Chinese or Spanish Archers can be chosen with rows keyed `Chin` and `Span` in the table for the body name the unit loads.

## The function 0x82DC4F68

The function `0x82DC4F68` builds `<asset name>.XML` from the unit type row: the type is the word at object `+0x30` and the name is row `+0x20`. It is slot `+0x20` of the function table at `0x8212FFD0`, and `0x82DC5270`, which loads the file, is slot `+0x1C`.

The words from `0x8212FF9C` to `0x82130038` are five function tables in a row: a four word table at `0x8212FF9C` and nine word tables at `0x8212FFAC`, `0x8212FFD0`, `0x8212FFF4` and `0x82130018`. Each address is stored to word `+0x0` of an object by located code, which gives the split.

In the scans run, the address of each nine word table is stored in functions that release the object, and no constructor was found. The address of `0x8212FFD0` is stored at `0x821C7B24` and `0x82DC4C60`. No direct call to `0x82DC4F68` or `0x82DC5270` was found.

The scans find an address formed by `lis` with `addi` or `ori`. A constructor that forms the address another way, or loads it from memory, would be missed. A copy of a whole object was not searched. The manifest section `function0x82DC4F68` lists the scans and the stores.

Interpretation: the four nine word tables are one parent class and three child classes that look like model viewers, and this code looks unused in this image. The body name of a unit on the map does not pass through `0x82DC4F68`.

## What is not established

- No unit creation or file load was observed.
- No direct caller of `0x82D7FE40` was found. It is slot `+0x1A0` of the function table `0x82138768`. That the object at `0x8314F76C` holds this table at unit creation rests on a cited record in `ai-options-boundaries.json`, which also notes a second table store.
- The functions `0x82E80120`, `0x82D9B9F0` and `0x82D9C4B8`, and the `.kfm` branch were not read. `0x82C92950` was read at its head. `0x82C63820` was not read, and the byte scan covered direct displacements in `0x82C50000..0x82DD0000`.
- The contents of any `_Attachments.xml` file were not examined, and no attachment table was read at run time.
- What `0x82D32BA8` does when the attribute is missing was not established. The attribute read `0x8230A118` returns 0 then.
- When slot `+0x18` of the member table `0x82135C90` runs, and so when the reader runs relative to the body load in `0x82D9CF30`, was not established.
- Whether a constructor for the table `0x8212FFD0` exists that forms its address in a way the scans miss was not established.
- What the objects built by `0x82E72008` and `0x82E72108` are was not established. They store the table `0x8212FF9C`.
- The worker name functions `0x82D95A30` and the constructor containing the string use at `0x82E7A698` are not on the creation route read here. What they build names for was not established.
- The meaning of the words at `0x830ECD08` and `0x8312E670` and of the table at `0x82F6F2F0` was not established. The manifest's `interpretation` key holds the readings of these words.
