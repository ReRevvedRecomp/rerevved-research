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

## Calls of the name builder

Nine recorded slot `+0x1A0` sites in `0x82CF0000..0x82D80000` use the object at `0x8314F76C` or a register that was not traced. Six of the nine pass `r5` = 1. Three pass `r5` = 1 when a compared register value equals a value read through the object pointed to by the word at `0x8314EFE0`, or when a bit of a signed byte in the table at `0x83129988` is set, and `r5` = 0 otherwise. Five of the six call slot `+0x1A4` of the same object first, and the sixth is a loop over records from `0x830F2BF0`. The `nameBuilderCalls` section of the manifest lists the sites, the tests and the direct callers.

Interpretation: the three sites that compute `r5` create units with the body loaded for the local player or on a tile that player sees, and the six sites that pass 1 rebuild the group of an existing unit.

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

## When the attachment table is read

Slot `+0x18` of the member table is called by `0x82C63820` at two sites, each after the word at member `+0x14` is not 0, and by `0x82C631D0`, which is slot `+0xA4`. The body load `0x82D9CF30` calls `0x82C63820` at `0x82D9D1DC` with `flags | 2`. Two paths of `0x82C63820` return without calling slot `+0x18`: the path at `0x82C638D8` when flags bit `0x200` is set, and the path at `0x82C63974`. After the path at `0x82C63974`, `0x82C631D0` can make the call when it is called and its checks pass. On the name builder route with a zero low byte of `r5`, `0x82D7FE40` passes flags `0x200`, or `0x210` for type `0x18`. After the group call returns a nonzero low byte, it calls `0x82D9B080` on each nonzero entry of the list at group `+0x78` to `+0x7C`. The function `0x82D9B080` calls slot `+0x0` of the object at member `+0x14` with r4 = 1 and stores 0 to member `+0x14`, and it also runs the steps for the objects at member `+0xA0`, `+0x80` and the list object at member `+0x70`, whose start and end pointers are at `+0x74` and `+0x78`. A later load of such a member was not found. That the list holds the members made by `0x82D99EB8` is an assumption from the layout. The object that the loader creates at member `+0x34` on the path at `0x82C63974` has the function table `0x82164E00`. Its slot `+0x4`, `0x82C5FA78`, calls slot `+0xA4` of the member with r4 = 1 when the low byte of its r4 is not 0. The function `0x82D9CF30` stores the civilization argument to member byte `+0x8C` at `0x82D9D1F0`, after its call of `0x82C63820`, so a slot `+0x18` call made inside `0x82C63820` reads the earlier byte `+0x8C`, which the constructor initializes to -1. See the `memberSlot0x18` section of the manifest.

Interpretation: the attachment table is read as part of the body load, after the body file is loaded. On the routes recorded the civilization argument is -1 as well, so the key is the same. A zero low byte of `r5` asks for the group to be created without keeping its body in memory, and `0x82D9B080` unloads a member. For a body of its own for Chinese or Spanish Archers, a unit created with the zero low byte holds no body until a later load that was not found.

A load call on a member that already exists was not found in the searches listed. Each located load call is on a member constructed just before it, in the member loop `0x82D99EB8` and in `0x82D99CE8`. The name builder `0x82D7FE40` constructs a new group with `0x82D99BB0` on each call, before it builds the name. Slot `+0x1A4` of the table `0x82138768`, `0x82D7D9B0`, calls slot `+0xC` of a record's group with r4 = 1 and stores 0 to the group word of the records that hold that group. Five recorded sites call slot `+0x1A4` and then slot `+0x1A0` with r5 = 1. Interpretation: a body is brought back by removing the group of the unit and building a new one through the name builder, so a name chosen there applies on each body load found. See the `memberReloadSearch` section of the manifest.

## The function 0x82DC4F68

The function `0x82DC4F68` builds `<asset name>.XML` from the unit type row: the type is the word at object `+0x30` and the name is row `+0x20`. It is slot `+0x20` of the function table at `0x8212FFD0`, and `0x82DC5270`, which loads the file, is slot `+0x1C`.

The words from `0x8212FF9C` to `0x82130038` are five function tables in a row: a four word table at `0x8212FF9C` and nine word tables at `0x8212FFAC`, `0x8212FFD0`, `0x8212FFF4` and `0x82130018`. Each address is stored to word `+0x0` of an object by located code, which gives the split.

In the scans run, the address of each nine word table is stored in functions that release the object, and no constructor was found. The address of `0x8212FFD0` is stored at `0x821C7B24` and `0x82DC4C60`. No direct call to `0x82DC4F68` or `0x82DC5270` was found.

The scans find an address formed by `lis` with `addi` or `ori`. A constructor that forms the address another way, or loads it from memory, would be missed. A copy of a whole object was not searched. The manifest section `function0x82DC4F68` lists the scans and the stores.

Interpretation: the four nine word tables are one parent class and three child classes that look like model viewers, and this code looks unused in this image. The body name of a unit on the map does not pass through `0x82DC4F68`.

## What is not established

- No unit creation or file load was observed.
- No direct caller of `0x82D7FE40` was found. It is slot `+0x1A0` of the function table `0x82138768`. That the object at `0x8314F76C` holds this table at unit creation rests on a cited record in `ai-options-boundaries.json`, which also notes a second table store.
- The functions `0x82E80120`, `0x82D9B9F0` and `0x82D9C4B8`, and the `.kfm` branch were not read. `0x82C92950` was read at its head. The byte scan covered direct displacements in `0x82C50000..0x82DD0000`.
- The contents of any `_Attachments.xml` file were not examined, and no attachment table was read at run time.
- What `0x82D32BA8` does when the attribute is missing was not established. The attribute read `0x8230A118` returns 0 then.
- Which path of `0x82C63820` a unit takes at run time was not established.
- The scan of slot `+0x1A0` calls finds one instruction pattern. At five of the nine sites in `0x82CF0000..0x82D80000` the object was not traced to `0x8314F76C`, so that those sites call `0x82D7FE40` is not established.
- What the table at `0x83129988` holds, what the object pointed to by the word at `0x8314EFE0` is, and what the compared registers hold were not established.
- The 14 sites of the scan outside `0x82CF0000..0x82D80000` were not read and may use other tables.
- Of the 40 other indirect call sites through member slot `+0xB0` or `+0xB4`, 39 were not read. The other 14 direct call sites of the loader `0x82C63820` were not examined. A load call on an existing member could be in one of them.
- What a unit created with a zero low byte of `r5` shows when its tile bit is set later was not established. No code was found that calls slot `+0x1A4` and slot `+0x1A0` after a change of the table at `0x83129988`.
- What calls slot `+0x4` of the table `0x82164E00` was not established. `0x82C55BA0`, which holds the one direct call of `0x82C631D0`, has no direct caller found.
- Whether a constructor for the table `0x8212FFD0` exists that forms its address in a way the scans miss was not established.
- What the objects built by `0x82E72008` and `0x82E72108` are was not established. They store the table `0x8212FF9C`.
- The worker name functions `0x82D95A30` and the constructor containing the string use at `0x82E7A698` are not on the creation route read here. What they build names for was not established.
- The meaning of the words at `0x830ECD08` and `0x8312E670` and of the table at `0x82F6F2F0` was not established. The manifest's `interpretation` key holds the readings of these words.
