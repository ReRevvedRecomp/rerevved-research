# Xbox command callback tables

This is a reference appendix. No known mod uses it yet. It records two small
tables of function pointers that the Xbox build of Civilization Revolution
(version 1.3) installs in a stack object while the type 53 command checks
other players, and the helper code those tables reach. The helpers end in a
shared fallback, `0x827F5780`, that the connection code also uses.

A modder needs this page for one reason: to know what a hook on one of these
functions would see. Code outside the tables also calls `0x82D3D9F0`: the height
file buffer release, the audio script table and socket cleanup. `0x827F5780` is
its fallback and is also the initial target of a pointer table in the connection
code. A hook on either function sees those calls too, whenever those paths run.
Everything on this page is read from the guest code. No run has observed a
table slot being called, a command being sent or a value changing.

## A worked example

The second scan of the type 53 command, described in
[Xbox turn command flow](xbox-turn-command-flow.md#second-scan-which-players-get-a-resync-prompt),
picks every peer whose stored scalar differs from a fresh sample. For each one
it builds an object on the stack at `r1+0xA0`, and the first word of that
object is the address of a table.

1. **The object starts with table `0x82136930`.** The body stores that address
   at object offset `+0x00` at `0x82CDEB84`. It also fills the rest of the
   object (the full store list is in the turn command flow page).
2. **A manager child may be called.** When the field at manager offset `+0x10`
   is not null, the code calls that child's virtual slot `+0x44` with the child,
   the object and the literal 1 as arguments 1 through 3. The target of that
   slot is not identified.
3. **The object then points at table `0x8211EC1C`.** The word at `+0x00` is
   rewritten at `0x82CDEBDC`. The same rewrite happens when the call is skipped.

If anything later called slot `+0x08` of the first table, it would write the
32 byte base envelope and then the 4 byte word at object offset `+0x34`. Slot
`+0x0C` would read 28 bytes of envelope and then the same 4 byte word. Those
sizes come from [Xbox command serialization](xbox-command-serialization.md#the-base-envelope).
No code on the scan path is shown to call either slot, so this is what the
slots do if reached, not what the game is observed to do.

## The two tables

A table here is a run of function pointers in initialized memory. Each row
below was read from the supported image and shows only what the pointers and
their targets show. Neither table has a recovered class name, constructor or
destructor identity, or slot name.

### Table `0x82136930`

Five slots, `[0x82136930,0x82136944)`. The word at `0x82136944` starts a
different pointer sequence that begins with the same two targets, which is why
the extent ends there.

| Offset | Target | What the code does |
| ---: | --- | --- |
| `+0x00` | `0x821D3D30` | Keeps `arg1`, installs table `0x8211EC1C` at offset zero, calls `0x82D3D9F0` when bit zero of `arg2` is set, returns `arg1` |
| `+0x04` | `0x821D5678` | Returns at once |
| `+0x08` | `0x82D90EC8` | Calls the base envelope write helper `0x82CB1F78`, then the 32 bit write `0x821D3EA0` on object `+0x34` |
| `+0x0C` | `0x82D90E80` | Calls the base envelope read helper `0x82CB1EC8`, then the 32 bit read `0x822D93E8` on object `+0x34` |
| `+0x10` | `0x82D91BD0` | Passes manager pointer `0x8314EFDC` and object `+0x34` to `0x82D8FCC8`, then returns 1 |

Ghidra stops decompiling `0x82D90EC8` and `0x82D90E80` at known bad
instruction data. The recompiled copy of each function corroborates the two
calls, and it adds no other function to the set. The slot at `+0x10` is not the
command object consume target `0x82D91C58`.

A second path builds the same table in heap memory. `0x821D3A98` requests
`0x38` bytes, installs `0x82136930` and initializes the same observed offsets,
but stores zero at `+0x34` where the stack path stores its loop index. The
number `0x38` is an argument to one allocation request. It is not a proven heap
size or a general size for the stack object. The Ghidra reference model records
one data reference to the table, at `0x821D3AE8` inside `0x821D3A98`. It omits
the case 53 store, so it is not a list of every installer.

### Table `0x8211EC1C`

Six slots, `[0x8211EC1C,0x8211EC34)`.

| Offset | Target | What the code does |
| ---: | --- | --- |
| `+0x00` | `0x821D3D30` | Same shared target as in the first table |
| `+0x04` | `0x821D5678` | Same shared target as in the first table |
| `+0x08` | `0x82CB1F78` | Base envelope write helper |
| `+0x0C` | `0x82CB1EC8` | Base envelope read helper |
| `+0x10` | `0x822DF8A0` | Returns zero. Ghidra reports far more than 8 callers, and none is followed |
| `+0x14` | `0x821B14B0` | Keeps `arg1` across one call to `0x82E2EFF0`, makes a second call to `0x82D3D9F0` when bit zero of `arg2` is set, returns `arg1`. It reads no object field |

Three functions install it besides the case 53 store:

| Installer | What it does |
| --- | --- |
| `0x82CB1B80` | Fills a caller provided object with `0x8211EC1C` at offset zero, a parameter at `+0x10` and the base fields except `+0x10` and `+0x34` (data reference at `0x82CB1BA0`) |
| `0x82CCE708` | Builds a command object through `0x82D90A18`, calls the manager child `+0x44` slot when the child is not null, then replaces the leading word (references at `0x82CCE810` and `0x82CCE814`) |
| `0x82CEDF90` | Does the same as `0x82CCE708` (references at `0x82CEE090` and `0x82CEE094`) |

Those five references in three functions are what the Ghidra reference model
records. It also omits the case 53 store, so the list is not complete.

The slot at `+0x14` sits at `0x8211EC30`. The model records no direct
reference to that address. The target `0x821B14B0` appears twice in aligned
initialized memory: at `0x8211EC30` and at `0x8216B900`. The second occurrence
lies inside the executable wide table of 8 byte function entries
`[0x8216B800,0x8218A050)` described in the
[serialization page](xbox-command-serialization.md#the-factory-row-and-the-function-table).
It is a row in that table and not a table comparison.

### The table after it

A zero word at `0x8211EC34` separates the six pointers from five more. The
seven words from `0x8211EC30` are:

| Address | Word |
| --- | --- |
| `0x8211EC30` | `0x821B14B0` (slot `+0x14` of the table above) |
| `0x8211EC34` | `0x00000000` |
| `0x8211EC38` | `0x821B1630` |
| `0x8211EC3C` | `0x821B1640` |
| `0x8211EC40` | `0x821D5678` |
| `0x8211EC44` | `0x822DF8A0` |
| `0x8211EC48` | `0x821B1628` |

These words do not form a repeated shape of 8 byte pointer and descriptor
pairs, which rejects reading them as more rows of the function entry table
above. The Ghidra model records one
data reference to `0x8211EC38`, at `0x82E2EC38` inside `0x82E2EBD8`. That
function initializes a caller provided object, stores `0x8211EC38` at offset
zero and touches fields up to `+0x64`. So `0x8211EC38` is a separately
installed table start. The page records it as a structural limit only. The
extent of that table, its slots and its other installers are not recovered,
and no catalog entry covers it.

## The shared leading targets

Both tables begin with `0x821D3D30` and `0x821D5678`. A shared target does
not mean a shared meaning.

- `0x821D3D30` keeps its first argument, installs `0x8211EC1C` at offset zero,
  calls `0x82D3D9F0` when bit zero of `arg2` is set, and returns `arg1`. Ghidra
  stops decompiling it at known bad data, and the recompiled copy corroborates
  the body. The scan itself also rewrites the leading word to `0x8211EC1C`
  (see the worked example), so that rewrite does not depend on this slot.
- `0x821D5678` is a single instruction return.

Neither function is shown to construct, destroy, release or own anything.

## The router and the fallback chain

`0x82D3D9F0` is the helper that both `0x821D3D30` and `0x821B14B0` call. It
routes a pointer `P` through four callees. Ghidra stops decompiling it at known
bad data and reports callers outside the one function set. This page does not
count or follow them.

1. It keeps `P` and calls `0x82D3DA78`.
2. When that call returns a nonnull base pointer `B`, it queries `B+0x1080`
   through `0x82D2E3D0`.
3. A nonzero low byte from the query passes `B`, `P` and a local word loaded
   after the query to `0x82D2E960`.
4. Otherwise it passes `P` to the fallback `0x827F5780`.

A nonzero query return does not by itself show that the query wrote the word in
step 3. The [manifest](../../manifests/xbox-network-message-root.json#/turnAndSyncAnchors/case55/case53Producers/stackObjectTable/sharedLeadingHelper/followupBoundary/queryOutputBoundary)
records one exact case where it is, and the conditions that case needs.

### The fallback `0x827F5780`

The fallback is a null checked, return checked pointer helper. In order:

1. A null `P` returns at once.
2. Otherwise it calls `0x82812B20`, which returns the word at `0x831580F8`.
3. It passes that value, zero and `P` to the return check `0x82811F48`.
4. A nonzero return from the check ends the helper.
5. A zero return calls `0x827F6910`, then `0x8280DD30`, then `0x827F68A8`, and
   stores the last result at offset zero of the pointer that `0x827F6910`
   returned.

Ghidra stops decompiling `0x827F5780` at known bad data and reports callers
outside the one function set. The recompiled copy corroborates the order.

| Function | Local behavior |
| --- | --- |
| `0x82811F48` | Returns 1 when `arg3` is null. For a nonnull `arg3` it reads and writes values at addresses derived from `arg1` and `arg3`, tests bits, stores paired pointers and updates counters. One path calls `NtFreeVirtualMemory` on a pointer value derived from `arg3` and changes the result of 1 to 0 only when that import returns a negative value. Its process guard path can call `KeBugCheckEx`. The check reaches the known save and restore thunk `0x827F7C7C`, which the configured Ghidra project misclassifies as not returning |
| `0x827F6910` | Calls `0x827FE4E8`. Returns the static address `0x82F2E9A8` when that call returns zero, otherwise the returned value plus 8 |
| `0x827FE4E8` | See the next table |
| `0x8280DD30` | Returns the word at `*(r13+0x100)+0x160` when the word at `r13+0x150` is zero, otherwise zero. It has no callee. Ghidra reports 6 callers, including `0x827FE4E8`, and omits the call from `0x827F5780` |
| `0x827F68A8` | Scans 45 entries of 8 bytes (key, then value) from `0x82F2E840`, returns the value on a key match. On a miss, keys `0x13` through `0x24` return `0xD`, keys `0xBC` through `0xCA` return 8, and every other key returns `0x16` |

The function `0x827FE4E8` does this:

1. It keeps the return from `0x8280DD30` for a final call to `0x82819F18`.
2. It loads the word at `0x82F2EE28`, gets an indirect target from `0x827FE3F0`
   and calls it with the loaded word.
3. An initial nonzero result other than 1 comes back unchanged. An initial
   result of 1 becomes zero.
4. An initial zero enters indirect calls through the pointer at `0x82FA1644`.
   They may pass 1 and `0xC4` to `0x827F9628`. A returned pointer is passed
   through the same indirect call.
5. When the second indirect call returns zero, the function passes the pointer to
   `0x827F5780` and returns zero. When it returns nonzero, the function stores 1
   at `+0x14`, `0x82F2F080` at `+0x5C`, the return from `0x8280DA68` at `+0`
   and -1 at `+4`, then returns the pointer. Other zero result paths return zero.

Ghidra stops decompiling `0x827FE4E8` at known bad data. It reports 3 callers and
7 direct targets outside the one function set, and none is followed. The
recompiled copy corroborates the local control flow only.

The 45 entry table ends at `0x82F2E9A8` (`0x82F2E840 + 45 * 8`), the same
address that `0x827F6910` returns when its call returns zero. This is
arithmetic. No use of the match is established.

None of these dataflows shows an allocator or deallocator, construction or
destruction, release or any function that holds the data, a class, object or field, a meaning for a
return value, or any runtime or transport role. The fallback calls
`NtFreeVirtualMemory` on one path, which makes release plausible, but the page
does not rely on that.

### The value at `0x831580F8`

`0x82812B20` is three instructions:

```text
0x82812B20  lis  r11,-0x7CEA
0x82812B24  lwz  r3,-0x7F08(r11)
0x82812B28  blr
```

The pair resolves to `0x831580F8`. The canonical flat image stores
`0x00000000` there. This is the only value read, and no adjacent word was
read.

What the searches show, and what they do not:

- The Ghidra reference model records one read, at `0x82812B24`, and no writer
  or data reference. The same model omits the call from `0x827F5780` and
  reports the other callers `0x82800DE8`, `0x827F9550` and `0x827F57E0`, so
  its caller list is incomplete and no count is claimed.
- A scan of all 462,689 defined instructions for the 16 bit unsigned form
  `0x80F8` and for the signed form `-0x7F08` finds no hit, even though the load
  at `0x82812B24` exists. A miss in that scan form is not evidence of absence.
- The same scan for the 32 bit form `0xFFFF80F8` finds exactly one hit, the load
  at `0x82812B24`.
- A search of aligned initialized memory finds no word that equals
  `0x831580F8`.

Unaligned patterns, split constants, indexed or indirect access, runtime values,
code built addresses and other ways to build the address are outside these
searches. So there is no unique reader, no list of writers, no initialization
code and no live value. The zero is a value in the image, not a runtime value.

### Other users of the router

The same helpers appear outside this command code:

- The audio script table passes nonzero backing storage to `0x82D3D9F0` and
  then clears fields. See [Audio script table](audio-script-table.md).
- The height file override calls `0x82D3D9F0` to release a buffer on both the
  failure and success paths. What `0x827F5780` and `0x82D2E960` free, and
  whether they can free a substituted buffer, is unknown. See
  [Height file override](heights-file-override.md).
- Socket cleanup passes a registry node to `0x82D3D9F0`. See the next section.

## The same fallback in connection code

The connection code reaches `0x827F5780` through a different route. A pointer
table at `0x82F32D5C` holds four function pointers, and three helpers call
through it.

| Word | Initial value | Called by | Request |
| --- | --- | --- | --- |
| `0x82F32D5C` | `0x827F57E0` | `0x82A17250`, at `0x82A17274` | Allocation. A census of raw direct calls to `0x82A17250` finds 21 sites (capped at 64, not truncated) |
| `0x82F32D60` | `0x827F5780` | `0x82A172C8` | Retirement. Returns its argument unchanged when null |
| `0x82F32D64` | `0x827F55E0` | `0x82A17288`, at `0x82A172B4` | Growth of a container backing |
| `0x82F32D68` | `0x82A171C8` | none recorded here | Role not established |

`0x82A171F8` stores four arguments into these four words with no check and no
atomic update. A raw direct call census of initialized executable memory
(capped at 64, not truncated, not cancelled) finds no call to it, and the
Ghidra model records no reference to it. That does not show the table is
unchanging, that the writer is unused or that no other writer exists. The
initial words do not show that `0x827F5780` stays selected. A pointer shaped
return from these helpers is not a status and should not be treated as one.

### Socket cleanup

The cleanup routine for a network object, started from the destructor path at
`0x82C9FFE8`, does three separate things. In each name below, `Sock` is the
socket object and `C` is the stored connection value.

| Function | What it does |
| --- | --- |
| `0x82C9FE80` | Treats `Sock` as a key into the map at `0x83155F44`. On a match it unlinks the node, requests `0x82D3D9F0` on the node (`0x82C9FF3C`, `0x82C9FF40`) and decrements the count at `+0x0C`. It does not call a destructor on the node or clear callback fields on `Sock` |
| `0x82A08948` | Loads the container at `Sock+0x0C` and calls `0x82A16B08` with callback `0x82A08980`. That function visits each element, calling `0x82A16230` on it, and the callback forwards to `0x82A088B0` |
| `0x82A10F10` | Reads `Sock+0x1C`. When it is nonzero, stores 1 at `Sock+0x14` and returns without the calls below. When it is zero, calls `0x827F1248(U32[Sock])`, `0x82A166F8(U32[Sock+0x0C])`, `0x82A15A88(U32[Sock+0x10])` and `0x82A172C8(Sock)` in that order, then `0x82A0F4F8`. It does not test the close result. Its final result is the later cleanup helper's, not the close result |

`0x827F1248` is a wrapper for the import `NetDll_closesocket` (ordinal 4). The
pinned SDK returns 0 from it without checking the close or handle release
results, and a failed socket lookup returns -1 with error `0x2736`. So neither
the wrapper result nor the later helper result shows that the operating system
closed the socket, that the caller's handle was removed or that the object was
destroyed.

### Callbacks and the retirement target

`0x82A16230` walks a container `H` from the last index down to 0. For each
index it calls `0x82A15C10` to get the address of the slot, and passes that
address to a saved callback with a saved context. It never checks the slot
result before the callback. The slot address is not the stored value: for the
selected callback, `E` is the slot address and the stored connection value is
`C = U32[E]`. The element callback `0x82A15AF8` also passes `E` and not `C`.

`0x82A088B0` overwrites its second argument with 1 and calls `0x82A14BF8(C, 1)`.
That function skips its helper sequence when `C+0x0C` is 7 or more, leaving raw
`C` in `r3`. Below 7 it calls `0x82A14C78`, `0x82A14218`, `0x82A15268` (with
second argument 0) and `0x82A11268` in order. It writes no result of its own.

With the table word at `0x82F32D60` still selecting `0x827F5780`, the target
behaves as the fallback chain above. It skips its calls for a null input, calls
`0x82812B20` at `0x827F579C` and `0x82811F48` at `0x827F57A8`. Its three further
calls are at `0x827F57B4`, `0x827F57BC` and `0x827F57C0`.

The return check works on a pointer, and for a nonnull one it derives a header
16 bytes before the pointer. It can enter a critical section, then take one of
two routes. The virtual memory route unlinks its header, leaves any entered
lock, requests `NtFreeVirtualMemory` (`0x82812198`, `0x8281219C`) and clears
the frame result at `F+0x58` on a negative return. That word starts at 1. The
other route calls `0x82810D48`, `0x82810230` or `0x8280FE08`, whose own effects
are not recovered. Both routes then call the exit helper `0x828121E8`
(`0x828121B0`, `0x828121B4`) before the frame word is loaded into `r3`.

The exit helper keeps its own frame. It saves `r31`, `r30`, `r25` and the link
register, makes a 112 byte frame, leaves the critical section
`U32[r30+1408]` only when `r25` is nonzero, and restores its registers. Under
valid separate stack and lock storage and normal returns it does not change
`F+0x58`. So the returned value of the selected nonnull path is 1, or 0 after a
negative `NtFreeVirtualMemory`, provided the unrecovered header helpers do not
write that word. That is a result word, not a proof that the header, the
payload or the connection were freed.

### Forced connection retirement

`0x82A14C78` skips its work when `C+0x0C` is already 7. Otherwise it writes 7,
then requests `0x82A168F0` (a delete request on bucket container `B`) and
`0x82A15C60` (an append request on list `L = U32[Sock+0x10]`), without testing
either result. The first request can reach the bucket element callback before the
second. `0x82A15268` returns 1 when `C` or the callback at `C+0x30` is null.
Otherwise it increments `C+0x24` and `Sock+0x1C`, calls the callback with `C`
and one argument, then decrements both. The callback result is discarded. When
`Sock+0x14` is then nonzero and `Sock+0x1C` is zero it requests `0x82A10F10`
and returns 0.

The forced path calls `0x82A15268` and then `0x82A11268` without testing the
first result. A result of 0 therefore means a socket retirement was requested,
and the later requests still run. `0x82A11268` skips its removals when `C+0x14`
or `C+0x24` is nonzero. This is a lifetime requirement, not a stale access or a
fix. Safe continuation needs `C`, `Sock`, the list and bucket containers and the
slot being walked to stay valid through every later use. Which callbacks are
installed, and whether any retires them, is not recovered.

### Container changes and growth

The selected container code changes counts and slots in a fixed order. `V`
below is any container with count at `+0`, capacity at `+4`, element size at
`+8`, growth step at `+0x0C`, element callback at `+0x10` and backing at
`+0x14`.

| Step | Function | Order |
| --- | --- | --- |
| Search | `0x82A16068` with `0x82A16430` | Linear search from index 0, calling the comparator with the key and the slot address. Returns -1 on a miss. A binary route through `0x82A164D8` exists and `0x82A168F0` does not select it |
| Insert | `0x82A15CA8` | Calls growth only when count equals capacity. Reloads the count, adds 1 and stores it, then, when the index is below the last slot, shifts elements through `0x827F5520`, then copies through `0x82A15DF0` and `0x827F8550`. The count is published before the bytes are copied |
| Growth | `0x82A15D88` | Stores capacity plus the growth step at `V+4`, calls `0x82A17288`, then stores the returned low word at `V+0x14` with no zero test. Capacity is published before the backing call |
| Erase | `0x82A15F98` | Calls the element callback, then `0x82A15EE8`, which shifts and stores count minus 1. It validates no index and calls no payload destructor |
| Copy | `0x827F5520` | Equal addresses return. A destination below the source (signed) goes forward through `0x827F8550`. Otherwise it copies backward in byte and word loops |

`0x82A17288` stores its two arguments as 32 bit words, loads the target from
`0x82F32D64` and calls it. The initial target is `0x827F55E0`. Its first branch
tests the old backing pointer `P`:

- `P` is zero. The request goes to `0x827F57E0` (allocation) and its result is
  forwarded, also when the size `N` is zero.
- `P` is nonzero and `N` is zero. It requests `0x827F5780(P)` (`0x827F5614`),
  then sets `r3` to 0 at `0x827F5690`. That zero is the wrapper result after a
  retirement request, not a successful free.
- `P` and `N` both nonzero. It obtains the context through `0x82812B20`, calls
  `0x82812238` (`0x827F5648`), and keeps a nonzero low word. A zero low word
  tests a retry word. With retry enabled it can call `0x82801348(N)` and repeat,
  or request storage through `0x827F6910`, `0x8280DD30` and `0x827F68A8` before
  returning 0. With retry disabled it also requests that storage but forwards
  the zero. A size above `0xFFFFF000` takes a handler path that ends in 0.

When growth returns 0 normally for a nonempty request, `0x82A15D88` stores 0 at
`V+0x14` after it has already published the new capacity. `0x82A15CA8` then
continues with its count before copy sequence and tests no result. So a
positive size alone does not give a nonnull backing. Whether any real container
reaches this is not shown, and no allocation failure has been observed. The
source paths do support a guard that handles failure before it commits capacity,
backing, count and slot state, and that preserves the old storage and `C`. A
guard at the copy alone would leave a partial state. `0x82A14C78` has already
requested the bucket deletion before the list insertion, so a complete change
covers both.

The forward copy `0x827F8550` saves `r3` at stack offset -8 and restores it
through five return paths (`0x827F8624`, `0x827F8640`, `0x827F8664`,
`0x827F87E8`, `0x827F88F4`). It copies from lower to higher offsets in groups of
128, 8, 4 or 1 bytes by alignment, and returns the original destination. It
checks no capacity and calls nothing. Two reached paths load unaligned words
(`0x827F85A4`, `0x827F8630`), which needs the platform's unaligned access
behavior to be as expected. The selected word copy, from `0x82A15DF0`, requests
4 bytes.

### Container construction

The code that builds these containers sets the element size, comparison and
callbacks.

| Function | What it builds |
| --- | --- |
| `0x82A159C0` | A 24 byte container header: count 0, capacity (8 when the input is 0), element size, growth step equal to the capacity, callback, and a backing of capacity times element size bytes. It stores the backing result with no null test, and returns the header |
| `0x82A16620` | A 20 byte bucket container header, a pointer array of bucket count times 4 bytes, and one `0x82A159C0` container per bucket. No allocation result is tested |
| `0x82A17250` | Truncates its argument to 32 bits and calls the allocation word at `0x82F32D5C` |
| `0x82A10B28` | Builds a 76 byte object `O` for a socket. It requests startup through `0x82A0F460` without testing the result, then a bucket container through `0x82A16620(4, 32, 2, 0x82A10E30, 0x82A10E70, 0)` stored at `O+0x0C`, then a list through `0x82A159C0(4, 4, 0x82A10EE0)` stored at `O+0x10`. It tests only the returned header pointers. A null header requests retirement of what was acquired and returns 1 |

Under the selected arguments the bucket container has 32 buckets, each with
element size 4, capacity and growth 2 and no element callback. The list has
element size 4, capacity and growth 4 and the element callback `0x82A10EE0`.
So when `B` and a bucket `K` come from this constructed object, the element
callback check in `0x82A15AF8` sees 0 and skips the payload callback. That does
not say `K` equals the `H` that the traversal saved.

The hash `0x82A10E30` takes a pointer to a stored `C`, computes `U32[C]` times
`U16[C+4]` in low 32 bits, and returns that value modulo the bucket count. The
comparison `0x82A10E70` returns the 16 bit difference of `U16[C+4]` when the
two `U32[C]` words are equal, and the word difference otherwise. A result of 0
means those two fields match. It does not show pointer identity, a player
identity or which code holds the data. The list callback `0x82A10EE0` loads `C` from the slot
address and calls `0x82A14CE0(C)`.

After building the children, `0x82A10B28` requests `0x827F1230` (arguments 2, 2,
254 for mode 2, otherwise 2, 2, 17), stores the result at `O+0`, and on a
failed result requests retirement of the bucket container, the list and `O`
and returns 3. Unless the mode is 3 it also requests `0x827F12C8`. A failed
result from that request first requests `0x827F1248(U32[O])` and then the same
three retirements, which makes four requests, not three. A final `0x827F12B0`
request is not tested. The routine stores `O` through the original
output pointer at `0x82A10E18` and returns 0. Its early failure exits do not
request `0x82A0F4F8`, so startup reference pairing is handled by the outer
code, which is not recovered here.

### Conditions behind these facts

Everything in this section holds only while the actual table words stay as the image
initializes them, the valid storage, frames and locks the code needs are in
place, helper calls return normally, and nothing else changes the data.
Changing the word at `0x82F32D60` would need a matching allocation and context
pair for the same lifetime, not only a new final function.

## Addresses

| Address | Role |
| --- | --- |
| `0x82136930`, `0x82136944` | First table and the end of its extent |
| `0x8211EC1C`, `0x8211EC34` | Second table and the end of its extent |
| `0x8211EC38` | Start of the five pointer sequence after the zero word at `0x8211EC34` |
| `0x821D3D30`, `0x821D5678` | Shared leading targets |
| `0x82D90EC8`, `0x82D90E80`, `0x82D91BD0` | Slots 2 to 4 of the first table |
| `0x82CB1F78`, `0x82CB1EC8`, `0x822DF8A0`, `0x821B14B0` | Slots 2 to 5 of the second table |
| `0x82CB1B80`, `0x82CCE708`, `0x82CEDF90` | Installers of the second table |
| `0x821D3A98` | Heap path that requests `0x38` bytes and installs the first table |
| `0x82E2EBD8` | Stores `0x8211EC38` at offset zero of a caller provided object |
| `0x82D3D9F0`, `0x82D3DA78`, `0x82D2E3D0`, `0x82D2E960` | Router and its three other callees |
| `0x827F5780`, `0x82811F48`, `0x82812B20` | Fallback, return check and value source |
| `0x827F6910`, `0x827FE4E8`, `0x8280DD30`, `0x827F68A8` | Calls on the zero return path |
| `0x831580F8` | Word that `0x82812B20` returns |
| `0x82F2E840`, `0x82F2E9A8` | Start of the 45 entry lookup and the address `0x827F6910` returns when its call returns zero |
| `0x82F32D5C` | Four word pointer table; `0x82A171F8` is its writer |
| `0x82A172C8`, `0x82A17250`, `0x82A17288` | Retirement, allocation and growth callers |
| `0x827F55E0`, `0x827F57E0` | Initial growth and allocation targets |
| `0x827F8550`, `0x827F5520` | Forward copy and the direction sensitive move |

## Limits and open questions

- Nothing here shows a slot being called, a command being sent or a table
  being read in a live match. The tables are not tied to a delivery, ordering,
  readiness, completion, lockstep or checksum meaning.
- Original class, slot and function names are unknown. The tables are not
  shown to be vtables of a named class, and `0x82D3D9F0` and `0x827F5780` are
  not shown to allocate or free anything.
- The extent of the table at `0x8211EC38`, its slots and its installers are
  not recovered. The extents of the first two tables are structural only.
- Ghidra stops decompiling several of these functions at known bad data and
  reports caller lists that omit calls proved elsewhere, so no caller count,
  caller list or reader list is complete.
- The meaning of the 45 entry lookup keys and values, the word at
  `0x831580F8`, the address `0x82F2E9A8` and the stores in `0x827FE4E8` is not
  recovered. The writers of `0x831580F8` are not found.
- What the installed callbacks in the connection containers do, and whether
  any of them retires a container that is still being walked, is open. No
  stale access, allocation failure or operating system close failure has been
  observed.
- A mod that hooks or replaces any of these functions has no tested pattern to
  follow.

## Evidence

- [Callback table record](../../manifests/xbox-network-message-root.json#/turnAndSyncAnchors/case55/case53Producers/stackObjectTable),
  with the shared helper, fallback and value source records below it
- [Socket unwind helpers](../../manifests/xbox-network-message-root.json#/nativeSocketUnwindHelperBoundary)
- [Callback and configured target](../../manifests/xbox-network-message-root.json#/nativeSocketCallbackTargetBoundary)
- [Configured return](../../manifests/xbox-network-message-root.json#/nativeSocketConfiguredReturnBoundary)
- [Forced connection retirement](../../manifests/xbox-network-message-root.json#/nativeForcedConnectionRetirementBoundary)
- [Container mutation](../../manifests/xbox-network-message-root.json#/nativeConnectionContainerMutationBoundary)
- [Growth and copy](../../manifests/xbox-network-message-root.json#/nativeConnectionGrowthCopyBoundary)
- [Container construction](../../manifests/xbox-network-message-root.json#/nativeConnectionContainerConstructionBoundary)
- [Xbox turn command flow](xbox-turn-command-flow.md)
- [Xbox command serialization](xbox-command-serialization.md)
- [Xbox network messages](xbox-network-messages.md)
