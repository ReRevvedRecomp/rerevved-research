# Spaceship part presentation

When a city finishes a spaceship part, the game does more than record the part.
It credits a component, may show an advisor notice, plays a rocket over the
city while the game waits, and then shows the shared spaceship screen that can
start the launch. This page explains each step for a mod that wants to skip or
shorten the presentation, lists what such a mod must keep, and gives every
hook point with its address. The exact ranges, byte digests and limits live in
[spaceship-part-presentation.json](../../manifests/spaceship-part-presentation.json)
(`RVA-F-0382`); this page explains them.

Every claim here comes from static reading of the supported image. It holds
only when the mappings, tables, return values and frames are the ones the image
sets up. No game was run, so nothing here is a runtime observation. No option
below is shown to be safe for a multiplayer game or for saves.

## What happens when a part is built

There are four parts, items 119 to 122. Three separate things follow
completion, and they are easy to confuse.

| Step | Kind | What it does |
|---|---|---|
| Part state | Gameplay | Debits the production, marks the city with a pending flag and writes the item |
| Pending pass | Gameplay and presentation | Credits the component, may show a notice, plays the rocket, then shows the shared screen |
| Launch and arrival | Gameplay and presentation | A separate screen call that publishes a launch and a later arrival result |

In game terms the pending pass does this, in order, for each city with the
flag set:

1. It adds 1 to the owner's count for that part.
2. If the part belongs to a player other than the local player, it shows an
   advisor notice about it.
3. It starts a rocket and flame over the city, then keeps running the game
   until the rocket finishes. This is the interruption a player sees when an AI
   city builds a part.
4. It removes the rocket and shows the shared spaceship screen. A positive
   result from that screen sends a launch command.
5. It clears the pending flag.

The rocket is a unit of type 24, the unit type labeled Space Station in its
definition. It is a real record in the unit table, not a separate effect. That
is why skipping it is harder than hiding a picture.

### Worked example

Player 3 is an AI player. Player 0 is the local player. Player 3 finishes its
first part, item 119, in the city at index 5.

1. The city record is at `0x8314FE28 + 0xBC * 5`, which is `0x831501D4`. Item
   119 is normalized index 19. Because the arrival word for player 3 at
   `0x830ECC0C + 8 * 3` is still -1, the game sets bit 0x100 in the city word at
   `+0x24`, which is `0x831501F8`.
2. At the pending pass the game sees the flag, sees that the item is in
   119 to 122, and adds 1 to the word at `0x830ECC48 + 16 * 3 + 4 * 0`, which is
   `0x830ECC78`.
3. Player 3 is not the local player, so the game requests the foreign advisor
   notice at `0x82D1DEBC`. The local player gets no notice about their own
   part.
4. Both cases then request the rocket at `0x82D1DED8`, a call to `0x82D11750`
   with owner 3, type 24 and the city coordinates. The game finds a free row in
   player 3's unit table, sets the busy bit, and runs the game loop until the
   rocket updater clears the busy bit.
5. The updater moves the camera focus to the city. The rocket finishes when a
   time test passes, then the game retires the row and shows the shared screen.
6. The shared screen returns a signed result. A positive result requests command
   32. The pass then clears bit 0x100 in the city word.

A mod that wants to hide step 3 and step 4 must still do step 1, step 2, step 6
and the flag clear. The sections below say which parts of steps 3 to 5 can be
changed and what each change costs.

## What a mod that skips the cutscene must keep

### State writes

| Keep | Where | Why |
|---|---|---|
| Invested production debit | `0x82D16150` | It runs before the part state writer |
| Part state writer and its flag | `0x82D02090`, flag at `0x82D020EC` | The pending pass reads that flag |
| Component credit | `0x82D1DDFC` to `0x82D1DE04` | It is gameplay and is not part of any notice |
| First building achievement submission | `0x82D161B4` | It follows the state writer and precedes the later notices |
| Launch command 32 | `0x82D1DFA4`, `0x82D1E000` | A positive screen result sends it |
| Pending flag clear | `0x82D1E00C` | Clearing early loses the credit. Never publishing the flag skips the credit |
| The shared screen's signed result | `0x82D5C8A0` | Refusing it can stop the launch for AI and human players |
| Visibility and discovery writes of the notice helper | `0x82D076D8` | They change real map planes at `0x83129FC8` and `0x83129988` |

The notice helper `0x82D076D8` and the text formatter `0x82CFB620` run before the
advisor request. Dropping them to remove camera motion can change gameplay.

Do not skip the whole pending branch, do not clear the pending flag before the
credit, and do not refuse every call to `0x82D5C8A0`. The same screen class also
serves the manual launch caller `0x82D2A07C` and the arrival wrapper
`0x82D5C7D0`, which are not part notices.

### Saves

The rocket row lives in the same unit table the game saves. The save routine
`0x82CC1DA0` walks all 2048 raw rows of 84 bytes with no exclusion for type 24.
It requests the owner byte at `0x82CC1DE4` and the word at `+0xC` at
`0x82CC2024`; the matching load requests are at `0x82CC1DC8` and `0x82CC2008`.
The rocket marker at `+0x22` is also saved, by the requests at `0x82CC2208` and
`0x82CC2224`.

A mod that never creates the row leaves a different logical record from one that
creates and retires it: a retired rocket row keeps its owner and a marked state,
while an omitted row stays free. Both rows are excluded by a reader that needs
an owner other than 0xFF and a clear dead bit. The save routine would write the
difference only if a save happens before the deferred cleanup and the stream
delivers the requests; neither was shown, so neither guaranteed save divergence
nor save independence follows. Whether a game can be saved while the rocket
plays was not shown. A save made while a part is being built, or while the
pending flag is set, is the first case to test.

### Peers

The checksum scalar at `0x82CD4CF0` sums every unit row whose owner is not 0xFF
and whose dead bit (bit 31 of the word at `+0xC`) is clear. It does not read the
marker at `+0x22`. A retired rocket row therefore leaves the sum; a live row
stays in it. For slot `j` the row adds:

```text
j * sign8(type) + sign16(X) + 2 * sign16(Y) + sign16(U+0x52) + sign8(rank)
```

Example: a type 24 row with rank 1, slot 1, zero coordinates and zero `+0x52`
adds 1 * 24 + 1, which is 25, while live and 0 after retirement. If two peers
take the checksum on opposite sides of the retirement, their scalars differ by
25. This is built from supplied values. It does not show that a real game
reaches such a mismatch, and equal scalars would not prove equal state.

Two sample points exist, and they are different phases:

- The outer sample. The AI turn command (type 48, handler `0x82CDE79C`) calls
  the pending pass at `0x82CDE838`, may wait in a loop at `0x82CDE888`, then
  samples the scalar at `0x82CDE8B8`. This is after the rocket row is retired.
- The nested sample. While the rocket waits, the pump can run the session
  drain, which can reach command 55 and sample the scalar at `0x82CDEC64`, while
  the rocket row is still live. This needs the session info byte (below) to be
  nonzero, and a network byte at `0x8314F10B` to be nonzero.

Matching preferences on two peers do not make a skip safe, and no peer authority
was established. A skip that differs between peers has no support in the
evidence.

## Mod options compared

| Option | What it changes | Verdict |
|---|---|---|
| Show everything | Nothing | Native behavior |
| Skip the advisor notice only | Jumps from `0x82CE83A8` to `0x82CE87A8` | Closed for the notice. It leaves the rocket and the wait |
| Skip the rocket creation | Jumps from `0x82D1DED8` to `0x82D1DF60` | The row is not the same as after a native rocket. Needs more research |
| Camera only | Skips the focus stores | The wait remains. Does not remove the rocket |
| Late native finish | Redirects `0x82D5E868` to `0x82D5E888` | Ready for a default off control flow test. Not shown safe for a complete setting |

The advisor notice can be skipped on its own. The request at `0x82D1DEBC` has
return address `0x82D1DEC0`. A hook that matches the call must compare the call
site plus 4 with the saved link register, not a raw link register with
`0x82D1DEBC`. The cleanup entry `0x82CE87A8` clears the buffers and the status
bits the notice set. Jumping to the other destination, `0x82CE87F8`, returns
without that cleanup and is not equivalent.

Skipping the rocket creation matches native failure, which already jumps to
`0x82D1DF60` with slot -1. But native failure and a chosen skip are different:
after a normal rocket the row keeps its owner and has the dead bit set, while
a skipped rocket leaves the free row with owner 0xFF. Both rows fail the active
unit test, but only the free row can be allocated again. Do not fake slot -1
after calling the creator. That omits the retirement the caller needs.

Camera suppression alone cannot work. The caller's wait at `0x82D1DF30` to
`0x82D1DF4C` runs while the busy bit is set, and the updater sets the bit again
while the marker at `+0x22` is below 0x8000.

Late finish keeps the allocation, registration, selector 37, descriptor lookup,
normal selector 14, the object callback and the retirement. It runs after the
focus work, so a camera pull is not avoided, and it never gives a strict zero
wait because the caller still pumps once. Its effect on queued input is the
next section.

## How the code does it

### Completion and the pending flag

`CityUpdate` debits invested production at `0x82D16150`, then calls the part
state writer `0x82D02090` at `0x82D16158`. At `0x82D020A0` to `0x82D020EC`, items
119 to 122 select normalized indices 19 to 22. When `0x830ECC0C + 8 * owner` is
-1, the writer sets bit 0x100 of city word `+0x24`. The common item write and
the completion list follow. `0x82D161B4` can submit the first building
achievement after a fresh check that the city owner is the current player.
`0x82D161CC` copies the current item to `+0x3A`, `0x82D161D4` clears bit 0x400,
and mode dependent cleanup of the current item at `0x82D1629C` runs after the
generic completion presentation.

The writer `0x82D02090` has four direct callers: `0x82D16158` (city completion),
`0x82D0A200`, `0x82CE0DCC` and `0x82CE1144`. The last three are separate reward
and dispatcher completion paths. Direct calls do not cover indirect producers.

How far a flag reader reaches is open. Two limited searches (see
[spaceship-part-city-flag.json](../../manifests/spaceship-part-city-flag.json),
`RVA-F-0208` and `RVA-F-0211`) found no direct read of city `+0x24` outside the
pending pass, in the city gameplay range and in eight more city table
functions. That is not proof that nothing else reads it.

### The pending pass

`0x82D1D3BC` forms the city table `0x8314FE28`, `0x82D1D6FC` starts at city
index 0 with a pointer at table + 0x7C, and `0x82D1E014` advances by 0xBC.
`0x82D1DD64` reads city `+0x24` and tests bit 0x100. The pass continues only
when `0x830ECC0C + 8 * owner` is -1, when the item at `+0x3A` minus 119 is 0 to
3, and when the low byte of the `0x82DA9768` result is nonzero. `0x82D1D794`
forms `0x830ECC48`, and `0x82D1DDFC` to `0x82D1DE04` adds 1 to the word at
`0x830ECC48 + 16 * owner + 4 * part`.

| Site | What it does |
|---|---|
| `0x82D1DE10` | Calls the local player resolver `0x82D8A3A0` |
| `0x82D1DE14` to `0x82D1DE1C` | Reads the city owner and compares. Equal skips the notice. This is an owner test, not an AI test |
| `0x82D1DE4C` | Requests `0x82D076D8` before formatting at `0x82D1DE84` |
| `0x82D1DE90` | Calls `0x82CFB620(32, 0)` |
| `0x82D1DEB8` | Sets `0x82FFE7C4` bit 0x01000000 |
| `0x82D1DEBC` | Requests `0x82CE8338` with `r3 = 400`, `r4` to `r7 = 0` and `r8 = 1`. The result is not used |
| `0x82D1DEC0` to `0x82D1DED8` | Both paths meet; request `0x82D11750(owner, 24, cityX, cityY)` |
| `0x82D1DEE0`, `0x82D1DEE4` | Returned slot of exactly -1 jumps to `0x82D1DF60` |
| `0x82D1DF08`, `0x82D1DF14` | Write unit `+0x22` as 0, set `0x82FFE7C4` bit 0x02000000 |
| `0x82D1DF20` to `0x82D1DF4C` | Pump `0x82E2A838(application, 0, 1)` until its low byte is 0 or the busy bit clears |
| `0x82D1DF5C` | Request `0x82D02390(owner, slot, 0)`, then continue at `0x82D1DF60` |
| `0x82D1DF88`, `0x82D1DFCC` | Shared screen calls. The first needs the classifier low byte to be 0, the second needs a current player equality. Positive results request command 32 |
| `0x82D1E00C` | Clears bit 0x100 of the city word |

The wait is a synchronous pump of application work. It is not a proven input
lock, an AI pause or a network barrier.

### The advisor notice and its cleanup

Before the call at `0x82CE83A8`, `0x82CE8390` sets `r27 = 0x83000000` and
`0x82CE8398` saves `0x82FFE7C4` in `r31`. Cleanup at `0x82CE87A8` does this:

1. `0x82CE87B8` and `0x82CE87CC` clear the buffers at `0x830EE988` (length 1980)
   and `0x830EE7F8` (length 396) with value 0.
2. `0x82CE87D4` masks the saved status with 0xFE7FFFFF and `0x82CE87E0` stores it,
   clearing bits 0x01800000, including the 0x01000000 the caller set.
3. `0x82CE87F0` resets the float at `0x8314F1A8` to 0.0, and `0x82CE87F4` clears
   bit 0x200 of `0x82FFE7C0`.
4. `0x82CE87F8` returns -1, `0x82CE87FC` restores the 1280 byte frame and
   `0x82CE8800` tails to the register restore at `0x827F7CB8`.

The foreign caller drops the return value. This is a local contract only. It is
not a general advisor suppression, and the helper and thunk returns must be
normal.

### The rocket row

`0x82D11750` scans up to 256 slots in the owner's bank at `0x830F2BF0`, each row
84 bytes. A slot is free when its owner byte and byte `+7` are both 0xFF
(`0x82D1179C` to `0x82D117B0`); an exhausted bank returns -1 at `0x82D117C4`.
The row address is `U = 0x830F2BF0 + 84 * (256 * owner + slot)`.

| Site | Write |
|---|---|
| `0x82D11820` | Zero fill of 84 bytes |
| `0x82D1182C`, `0x82D118B0` | Owner and type 24 |
| Direct writes | Owner mask at `+0x18`, coordinates at `+0x1C` and `+0x1E`, slot at `+0x30`, movement at `+2`, rank at `+5`, life word at `+0xC`, sentinels at `+0x22`, `+0x28`, `+0x2E` and `+0x50` |
| `0x82D119B0` to `0x82D119B8` | `+7 = 0xFF`, `+0x26 = 0xFFFF`, `+0x14 = 0`, after the registration requests |

Registration at `0x82D11980` requests slot `+0x1A0` of the root at
`0x8314F76C`, and `0x82D1199C` requests `+0x1B4`. In the initialized table
`0x82138768` these select `0x82D7FE40` and a return only function `0x821D5678`.
`0x82D801E4` adds flag 0x10 for type 24 before `0x82D80208` initializes the model.
Registration can fail after a logical slot exists.

The type 24 definition is at `0x82F70EB8`, with the definition table stride 148.
Its flags word at `0x82F70F08` holds 8, which excludes the alternate creator
route at `0x82D117DC` to `0x82D117E4` and the optional arm at `0x82D11A00` to
`0x82D11A08`.

Mode 0 retirement `0x82D02390` ORs `0x80000000` into `+0xC` at `0x82D023F0` and
writes `+0x26 = 0xFFFF` at `0x82D02434`. It never writes owner 0xFF. The flags
word skips the first dependent scan at `0x82D02438`, but a second scan of 256
rows can clear another unit's link at `+0x50` when it matches the retired slot,
and can retire a matching type 30 row at `0x82D0250C`. So retirement is not
purely cosmetic, and complete destruction before the caller resumes is not
shown.

### The rocket frame

The updater `0x82D5FFC8` clears the busy bit at `0x82D60050`. Its type 24 arm
(`0x82D61498` to `0x82D615A4`) calls `0x82D5E660` at `0x82D61580`, and if the
marker at `+0x22` is below 0x8000 (unsigned) it sets the busy bit again at
`0x82D6159C`. The marker value 0xFFFF means finished.

`0x82D5E660` has two paths. The auxiliary record is
`A = 0x83024F18 + 292 * (256 * owner + slot)`.

| Path | Sites | Effect |
|---|---|---|
| Finished | `0x82D5E698`, `0x82D5E69C` | The marker equals 0xFFFF. It zeroes `A+8` and returns before any focus work |
| Active | `0x82D5E748` to `0x82D5E7C0` | Writes focus inputs `0x82F772D0` at `0x82D5E778` and `0x82F771C4` at `0x82D5E780`, `0x830E45B8 = 2`, `0x830E45B4 = 1`, bit 0x08000000 of `0x82FFE7C0`, view fields `+0x118` and `+0x11C` of the object at `0x8314F2C4`, and the float at `0x8314F1A8`. Then it requests selector 37 at `0x82D5E7C8` |

Timing. `0x82D60044` to `0x82D60084` multiplies the frame scalar by 1000 (float
at `0x8216A530`) and clamps the integer to 1 to 250, stored at `0x8314F04C`.
`0x82D5E7D4` asks the local player resolver, and if the row owner differs from
it, `0x82D5E7E0` doubles the delta, giving 2 to 500. This tests for a player
other than the local player, not for an AI. The finish test at `0x82D5E858` to
`0x82D5E868` compares the previous time with
`low32(L - delta - 2000)`, where `L` is the return of `0x82D5E568`. For type 24
the definition byte `+0x48` is 1, so the first child is used; request 3 maps to
1010 through `0x82D5CFD0` and the word at `0x82F793AC`, and `0x82E59F98` reads
child `+0x28` through the registries at `0x831560D0`, `0x831560D8` and
`0x831560E0`. The delivered values are not known, so do not invent a duration.

If that test fails and the previous time is above 1000, `0x82D5E87C` calls
`0x82E55518`. It pops the first word of the queue at `0x82F7AD28` (vector at
`+0xC` and `+0x10`), and only the value 1035 finishes. The value 1035 is an
abstract code. It is not shown to be the B or Start button.

Native finish stores 0xFFFF at `0x82D5E898`, writes a constant at `0x82D5E8A4`
(positive zero from `0x8211B944`, so not a saved earlier camera), requests
selector 14 at `0x82D5E8A8` and calls object `+0x80` at `0x82D5E8BC`. The
finish block never clears the shared busy bit itself. The next pump does that
when `0x82E2A838` finds mask 0x08000400 in application `+4`, and it also clears
`0x82FFE7C0` bits 0x00030000 and the word at `0x830E45BC`.

### Camera and view

`0x82D6B0A8` loads the focus inputs at `0x82D6B138` and `0x82D6B140` and can store
them to `0x83020D80` and `+4` at `0x82D6B268` and `0x82D6B270`. That copy needs
both bit 0x8000 and bit 0x08000000 of `0x82FFE7C0`, so skipping only the
coordinate stores can leave stale values eligible.

Past that, the code reaches a view object. `0x82D6B8D4` calls `0x821B1988` on the
wrapper at `0x8314EF84`. It returns wrapper `+8` only when the type descriptor
at `0x8314F488` is accepted. `0x82D6B8EC`, `0x82D6B8F0` and `0x82D6B8F4` write
object `+0x50`, `+0x54` and `+0x58`, and `0x82D6B910` calls object `+0x8C`.
`0x82D6BDC0` then forwards to `0x82E5A798`, which writes the same three words
at `0x82E5AA7C`, `0x82E5AA80` and `0x82E5AA84` and calls `+0x8C` again at
`0x82E5AAC4`. Other view code at `0x82D6B658` and `0x82D6B668` writes
`0x8314F1A8`.

The constructed view table is `0x82123738`. Its `+8` cell (`0x82123740`) selects
`0x821B8950`, which returns exactly the requested descriptor, and its `+0x8C`
cell (`0x821237C4`) selects `0x82E0E4B8`. Both callers pass a delta of positive
zero. That is not a no-op: `0x82E0E4B8` can run `0x82E0DEC8`, which can read the
focus globals and call `0x82E0D370` and `0x82E0D7F8`, then `0x82E26C20`, which
writes the three words again, copies a matrix and requests `0x8234B2C0`.
`0x82E0EC1C` and `0x82E0EC34` set or clear bit 0x00020000 of `0x82FFE7C4` from
view byte `+0x131`. That bit is not the rocket busy bit and not the focus flag.
Do not suppress this update as a zero delta repair.

Output of the transform path, in order:

- `0x82E0D7F8` (mode 0) clears `+0x324` and `+0x328`, sets byte `+0x131`, calls
  `0x82E0D3E0`, clears a shared byte at `+0x88D`, calls `0x82E0D168` when `+0x13A`
  is 0, calls `0x82C776C0`, stores mode 0 at `+0x320` and writes three words at
  `+0x230`, `+0x234` and `+0x238`.
- The view's `+0x68` cell (`0x821237A0`) selects `0x8234C1B0`, which can call
  `0x8234BE70`. That function can visit two object lists and call each object's
  `+0x4C` or `+0x50` method.
- Cells `0x821237B4` and `0x821237B8` select `0x8234E460` and `0x8234D6A0`.
  `0x8234E460` calls `0x82D7A8A8`, then `0x8234DF90`, which writes all 16 floats at
  view `+0xB0` to `+0xEC`. `0x8234D6A0` can store view `+0x90`, `+0x94` and `+0x98`
  into the record at `[+0xA0]`.

The destination, its first engine reader, `0x82D7A8A8` and the child callbacks
are not known.

### Child state and finish

`0x82D99690` forwards selectors 37 and 14 to child `+8`. The child table is
`0x82135C90`. Its `+8` cell (`0x82135C98`) selects `0x821B3B60`, which stores the
selector value at child `+0x6C`; that is real state, but whether anything then
processed it is not known. `0x82D99FF8` appends through the descriptor at
`+0x6C`. `0x82D99518`, the `+0x80` cell of the object table `0x82135DB0`, forwards
to each child's `+0x80`. The child `+0x80` cell (`0x82135D10`) selects `0x82C61950`,
which calls `0x82C7FA80` on the manager at `0x8314F27C`.

That manager call selects entries through `0x82C7F458` by the result of each node's
`+0xB4` method, which is not shown to be the same child. For each delivered
match, `0x82C7FACC` clears node `+0x78`, releases and clears `+0x7C`, clears byte
`+0x84` and can set entry `+0x24` to 6. This is a cleanup request. It does not
show that the child is destroyed, that rendering or audio stopped, or that the
scene is idle.

### Queued input

The queue is at `0x82F7AD28` with table `0x82138B4C`. Its event method
(`0x82138B50` cell) is `0x82E555A0`. Registration of the queue
(`0x82D79760`, `0x82C7A488`) does not add events. In `0x82E555A0`, a nonzero
mapped code from `0x82D319A8`, with event `+8` equal to 1, is appended at
`0x82E55640`. Another arm copies 24 event bytes and appends the original code at
`0x82E55710`. Both use `0x821B0C98`, which stores the word at the end and moves
`+0x10` by 4. Initial capacity is 0, so the first append needs growth that was
not followed. Codes 1038 to 1040 take other paths.

Input reaches the queue in the same pump. If the top callback is the table at
`0x82120D2C`, `0x82E87D18` calls `0x82C7DF58`; `0x82C7DFD0` polls `0x82C7A608`,
then calls the interface cell `+0x7C` (`0x82E10680`) and `+0x10` (`0x82E10690`)
of the table at `0x82120EB0`. `0x82E10690` drains its 24 byte event vector through
`0x82C7A190`, which visits recipients in reverse order, before it calls the
updater at `0x82E107AC`. The updater needs application `+0x70` child `+4` equal
to 2, a valid local player resolver, and clear bits 0x800, 0x04000000 and 0x400 in
application `+4`. So an event can be appended before this updater reaches its
possible pop.

Example. If native code would pop a word `W` and a late finish skips that pop,
the native queue is empty while the modified queue still holds `W`. The
previous time at or below 1000 avoids only this pop. Another consumer
(`0x82DA5ADC` pops, `0x82DA5AE8` passes the word to `0x82DA3EF0`) is not shown to
be the next reader. Do not add a blanket flush or a made up pop.

### Session info byte

The nested multiplayer sample needs the info byte at `+0x1E`. The session child
construction calls `0x82CA2AB0` at `0x82CA5F1C` and stores the result at child
`+0x1C` at `0x82CA5F28`; a failed allocation stores 0. `0x82CA2AFC` installs table
`0x8215FE18`, `0x82CA2B04` sets `+0x1D` to 1 and `0x82CA2B08` sets `+0x1E` to 0.

The drain predicate is `0x82CA49A8` (cell `0x8215FA8C`). It calls the `+0x108`
getter `0x82219D70` twice, and returns the byte at `+0x1E` of the second result.
The setter is `0x82CA4A18` (cell `0x8215FA88`, child virtual `+0x10`). It calls
the getter at `0x82CA4A40`, returns if the result is zero, calls it again at
`0x82CA4A5C` and writes the low byte of its second argument at `+0x1E`
(`0x82CA4A60`), with no second null check. With a nonzero info pointer both
getter results are the same. Whether anything calls the setter with a nonzero
value, and in what order against the read, is not known. See
[xbox-network-message-root.json](../../manifests/xbox-network-message-root.json)
for the retry queue that clears and sets the byte.

### The shared spaceship screen

The constructor `0x82DD9198` registers the screen name at `0x8212D05C` through
`0x82C7C3D0`, installs table `0x8212D348` and sets the result words at `+0x42C`
and `+0x43C` to -1. Table cells select update `0x82DDAD40`, init `0x82C7BCC0`,
close `0x82C7BD50` and callbacks `0x82DDAB48` and `0x82DD8D38`. `0x82DDAEB4`
and `0x82DDAEBC` keep the player and a second argument; `0x82DDAF34` stores the
second at `+0x444` and `0x82DDB01C` stores the player at `+0x438`. `0x82DDAF68`
to `0x82DDAF84` store whether the current child result differs from the
player in byte `+0x44C`.

`0x82DDB3D0` calls `0x82DDA288` and `0x82DDB3D4` stores its signed result at
`+0x43C`. The callbacks copy it to `+0x42C`, and the modal `0x82E40738` returns
`+0x42C`. `0x82DDAA40` tests byte `+0x44C`, result `+0x43C` and mode `+0x448`: a
nonzero byte with a result that is not -1 and a mode that is not 2 requests
`0x82DD8E40(this, 0)` and sets the mode to 2; other arms schedule a timer with
callback `0x82DD9230`, which branches to `0x82DD8F50`. So cancelling is phased and
is not a close now. `0x82E40738` saves and restores the interface byte `+5` and
child byte `+0x29`, manages the modal depth at `0x83156368`, calls the current
object `+0xC` and returns the result.

Scene and audio lookups are separate: `0x82DAAD94` to `0x82DAADA8` pass the
scene node name at `0x821343F8` to `0x82C62B98` and keep the result at object
`+0x48`; `0x82DD8E9C` to `0x82DD8EAC` pass the stats tone name at `0x8212D328` to
`0x821B6168`, `0x82DD8EDC` requests `0x82E42DA0` and keeps a handle at `+0x454`,
and `0x82DD8F24` requests `0x82E428E0` to stop it. These are lookup names and
requests. Delivered media, the actual sound and camera restoration are not
shown. No spaceship specific movie file name was found, and no link from these
requests to the intro movie entry (`0x82E551D8` and test `0x82E5522C`). The
intro skip pattern, which filters the frontend tables at `0x82131A18` and
`0x82121320`, does not carry over to this screen.

The launch wiring is covered by
[spaceship-launch-arrival-year.json](../../manifests/spaceship-launch-arrival-year.json)
(`RVA-F-0322`) and [science.md](science.md): the launch caller accepts only a
positive result, which excludes valid BC dates and year zero. The arrival
wrapper `0x82D5C7D0` is called from `0x82D115E8` and `0x82D11604` in `0x82D10FD8`.
These are not part notice calls.

## Hook points

| Address | What a hook can do there | What it must keep |
|---|---|---|
| `0x82CE83A8` (to `0x82CE87A8`) | Hide the foreign advisor notice | The following caller instructions, the status snapshot and the 1280 byte frame |
| `0x82D1DED8` to `0x82D1DF60` | Skip the rocket | Matches the native `-1` allocation failure, which also rejoins at `0x82D1DF60`, but not successful creation followed by retirement: the row stays free instead of retired. Needs the later reader order |
| `0x82D5E748` to `0x82D5E7C0` | Skip individual focus stores | Every register assignment, selector 37 at `0x82D5E7C8`, the descriptor call and the timing stores |
| `0x82D5E868` to `0x82D5E888` | Finish early | `r25 = 84 * I`, `r21 = 0x830F2C12`, `r24 = 0x830F2C2C`, `r23` as `0x83150000` sign extended, readable `U+0x3C`, the 192 byte frame and the register save and restore state. `I = low32((owner << 8) + slot)` |
| `0x82D5E898` to `0x82D5E8BC` | Native finish | Marker, constant, selector 14 and `+0x80` request |
| `0x82D1DF5C` | Retirement | The caller's retirement, which a skip must not omit after a creator call |

At `0x82D5E868` a hook leaves the original branch for a false policy and
redirects only a chosen row. An earlier jump from `0x82D5E6C0` to `0x82D5E888`
skips the setup at `0x82D5E74C` and `0x82D5E758` and is not equivalent. Do not
write 0xFFFF into an active row (the finished path omits selector 14 and the
`+0x80` request), do not use 0x8000 (it still runs the active body), do not
create a failure after the creator ran, and do not clear the busy bit
globally.

## Limits and open questions

- Runtime behavior has not been observed. Everything here comes from the
  image's code, tables, frames and return values.
- No physical button was tied to the code 1035, to the callback modes 1, 2 and 3,
  or to the screen result. No retail skip option or cheat was found. The two
  spaceship setting names in the image, an effect flag and an engine count, are
  not enough to identify one.
- The delivered media, audio, camera restoration and the full effect of the
  child, manager and view callbacks are not known. A late finish keeps the
  native requests, but a request is not a completed cleanup, a camera free
  first frame, unchanged queued input or a zero wait.
- Eventual equivalence of a skipped rocket needs a later comparison point: the
  code that frees the retired row, and the first allocator, save or peer reader of
  that same row.
- Save timing and delivered bytes for the marker, owner byte and life word were
  not shown. Whether a save can be made while the rocket plays is open.
- Which of the outer sample at `0x82CDE8B8` and the nested sample at
  `0x82CDEC64` a peer reaches, the value of the info byte at that time and the
  order of its writer against its reader are open.
- The state flag at city `+0x24` has no known reader besides the pending pass.
  The reader searches covered only direct operand forms.
- The pending state is also written by three other completion paths
  (`0x82D0A200`, `0x82CE0DCC`, `0x82CE1144`). Their natural triggers were not
  followed.
- Items 119 to 122 are the only initialized part records. See
  [building and wonder storage limits](building-wonder-storage-limits.md) for
  what extending the building table needs.

## Evidence

- [spaceship-part-presentation.json](../../manifests/spaceship-part-presentation.json),
  `RVA-F-0382`: every range, digest, guard and the remaining questions.
- [spaceship-launch-arrival-year.json](../../manifests/spaceship-launch-arrival-year.json),
  `RVA-F-0322`: the launch result and arrival.
- [spaceship-part-city-flag.json](../../manifests/spaceship-part-city-flag.json),
  `RVA-F-0208` and `RVA-F-0211`: the flag and its reader searches.
- [science.md](science.md): the launch result and a summary of the presentation.
