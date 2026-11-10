# Native renderer guest frame pacing

The
[frame-pacing manifest](../../../manifests/native-renderer-guest-frame-pacing.json)
records static timing and waits from the playable callback to presentation.
It establishes neither that the callback controls simulation, a fixed tick nor
rendering on every timing update. Callback `0x82E87D18` calls `0x82C7DF58`,
which dispatches timing slot `+0x8` at `0x82C7DF84` and then runs manager work.
When the low byte of entry r4 is nonzero, the path `0x82C7E104 -> 0x82C71A00` is
permitted. When it is zero, the path reaches `0x82C7E118`. Both return `1`.

## Callback inputs and registration

The
[scheduling manifest](../../../manifests/native-renderer-frame-callback-scheduling.json)
records these inputs:

| Edge | State |
| --- | --- |
| `0x82E87D28` | Entry r4 goes to r30, which controls the manager-byte test |
| `0x82E87D2C`, `0x82E87D78`, `0x82E87D80` | Entry r5 goes to r28, then to driver r4, then into the call |
| `0x82E87D54`, `0x82E87D60` | Load manager `0x8314F28C`; store `+4` as `1` when the low byte of r30 is zero, otherwise `0` |
| Registration | `0x82E2AF20` registers table `0x82120D2C` slot 0 = `0x82E87D18`. The vector is at `+0x80`, with start, end and capacity at `+0x84`, `+0x88` and `+0x8C`. A null callback exits. When the start pointer is nonnull and capacity remains, the callback is stored and the end advances. Otherwise `0x821B4450` does the insertion, and its insertion, return and whether the result stays valid are not yet established. |

The
[callback slot boundary](../../../manifests/native-renderer-callback-owner-slot.json)
covers `0x82D83C7C`. It takes the object from `0x82FFD624`, with its vptr
`0x82121100` unchanged, and uses the table entry `0x82121128`, which is the no-op
`0x821D5678`. Application service `+0x28` therefore neither visits `+0x84`,
`+0x88` and `+0x8C` nor produces r5. The `+0x28` field of the timing object is
separate. The vector invoker and the producer of r5 remain unknown. The path
establishes no tick, frame counter, simulation step, render cadence or
presentation decision.

## Timing arithmetic and waits

`0x82C7EB68` dispatches at `0x82C7EB88` through `+0x14` (target `0x82C5F790`). A
nonzero `+0x18` on the timing object selects `f1 - f0`; zero keeps zero. Then:

1. Multiplies the result by timing object `+0x28`.
2. Stores it at timing object `+0x10`.
3. Clamps that value against exact double bits `0x3FC999999999999A` (decoded as
   `0.2`).
4. Increments `+0x30`.
5. Accumulates `+0x08`.
6. Stores the incoming value at `+0x18`.

The clamp is not an FPS limiter.

| Wait or limiter address | Condition | Interval or default | Processor | Role |
| --- | --- | --- | --- | --- |
| `0x826ABF38`, `0x826ABFCC` | Worker `0x826ABEA8` enters the first wait only when `[r26+0x3C] == [r26+0x38]`; status 258 selects or repeats the critical block, and the second wait follows it even when the device check skips the pair | `KeWaitForSingleObject` uses r4=`3`, r5=`1`, r6=`0`; r27 points to stack `+0x50` when `[r25+0x178] == [r26+0x4]`, otherwise null. Pinned SDK maps `-300000` guest ticks to 30 guest milliseconds before optional scaling; actual host duration is unknown | CPU | Worker event and counter coordination |
| `0x826A4150` | Wrapper `0x826A4630` passes r4=`0` | PM4 `WAIT_REG_MEM` command with interval `0x100`, references `1` then `0`, device `+0x2A94+4`; not a time value | GPU | Pre-swap system command-buffer handshake |
| `0x8269E520` | Late Resolve command path reaches its wait command | Register `0xA31`, reference r28, mask `0x80000000`, command interval `8`; not a time value | GPU | Resolve command synchronization |
| `0x8269BE70` | The lock core selects `+0x0C` only when lock flags `& 0x1010`; callers pass a scalar fence in r4 and zero returns immediately | No fixed interval; compares fence and ring state and invokes the helpers selected for inspection | CPU and GPU | Resource lifetime fence wait, not a guest frame limiter |

## Presentation order and selector inputs

Status 258 plus device `+0x2ABE & 2` permits worker `0x826ABEA8` calls:
`0x826ABF80` -> `0x826A4630`, then `0x826ABF90` -> VdSwap function `0x826A4638`.
The alternate `0x82517E38` uses `0x82517E58` and `0x82517E88`.

The VdSwap function calls VdGetSystemCommandBuffer at `0x826A4820` (LR
`0x826A4824`), then tests `+0x541C` at `0x826A4828`. A nonzero value copies stack
`+0x74` to `[device +0x2A90] + 8` and jumps to `0x826A4890`, skipping
reservation and import. A zero value calls import `0x82E92454` at `0x826A4884`.

Pre-swap device `+0x351C` maps:

| Selector | Mapped value |
| --- | --- |
| `0` and `1` | `1` |
| `2` | `2` |
| `4` | `3` |
| `0x80000000` | `0` |
| Other values | Stack `+0x50` |

The mapped value `<<8` combines `+0x2E4C` bits and incoming-r4 state into `r7`
for `0x8269BF40`. r6 holds callback `0x826A3FB8` at `0x826A4298` (LR
`0x826A429C`). A search limited to the selected code found setter `0x8268EF68`.
Three initial callers and five remainder callers have static producer origins.

The
[setup-input manifest](../../../manifests/native-renderer-presentation-setup-input.json)
traces caller two before template `+0x34`, keeping the exact stack and mapping
details. Helper mutation and whether the final value stays unchanged remain
unresolved. The
[remainder manifest](../../../manifests/native-renderer-presentation-selector-other-values.json)
locates five calls in `0x82C15240`, each reloading `[0x8314F300]` and passing
`U8(entry +0x0)`, `U8(entry +0x1)`, `U32(entry +0x4)`, `U32(entry +0x8)` or
`U32(entry +0xC)` as r4. Prologue indices `0`, `8`, `4`, `16` and `168` come
before the unsigned compare `360`, yet the setters sit at `case 336`. This
mismatch leaves the entry, the control and whether values stay unchanged
dependent on conditions. Runtime activation, the default, the meaning of the
interval, and whether indirect and tail paths are covered remain unknown.

## Callback arithmetic and clock units

The callback extracts the low 8 bits and bits 8 to 11, and chooses a nonzero
`[device +0x5434]` or `60`. It computes
`r11 = (timebase_delta * 100) / (frequency / divisor)`, then `r7 = r11 + 1`,
capped at `100`, with `twllei r29,0` and `twllei r11,0` guards. The branches are:

| Target | Condition |
| --- | --- |
| `0x826A4078` | `r8+r30 > r10`, `r30 == 0`, or `r7 <=` input low 8 bits |
| `0x826A40BC` | `r9 == 0` |
| `0x826A4100` | The subsequent `r10 == 1` |

The divisor, the activation and the meaning of the interval remain unknown. The
value `60` is not shown to be an FPS setting. Clock target `0x82C5F790` lazily
fills `+0x38` through `0x8280F0C8` and `+0x40` through `0x8280F100`, and returns
(sample-baseline)/`+0x38`. The meaning and values of `+0x28` on the timing
object, the scaling, the samples, the cadence and the retail equivalence remain
unknown.

The pinned SDK maps a negative timeout through `-timeout_ticks / 10000`, so
`-300000` becomes 30 guest milliseconds before `ScaleGuestDurationMillis`. A
null timeout is unbounded. When `clock_no_scaling` is true, the duration is kept;
otherwise `guest_time_scalar_` scales and saturates it. `REX_QUERY_TIMEBASE`
returns guest ticks and `KeQueryPerformanceFrequency` returns ticks per second,
so the pre-multiplier quotient is guest seconds.

See:

- [threading.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/kernel/xboxkrnl/xboxkrnl_threading.cpp#L839-L848)
- [xobject.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/system/xobject.cpp#L189-L213)
- [clock.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/core/clock.cpp#L188-L203)
- [clock.h](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/include/rex/chrono/clock.h#L61-L73)
- [threading.cpp frequency path](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/kernel/xboxkrnl/xboxkrnl_threading.cpp#L371-L374)
- [runtime.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/system/runtime.cpp#L150-L152)

Source initialization establishes intent, not observed settings, host duration,
event cadence, retail semantics or frame cap.

## Simulation, interface and media timing

These notes keep four timing questions apart. None has an accepted consumer
that fixes a tick rate.

**Simulation updates.** The advance at `0x82C7EB68` multiplies the clock
difference by timing record `+0x28` and stores it at `+0x10`. The count at `+0x30`
rises once per reached advance. It counts advances, not driver calls, game
ticks or shown frames. The
[field `+0x10` finding](../../../manifests/frame-timing-field10-reader.json)
stops at 28 direct reader functions, above its limit of 6, so it names no
first reader. One later edge is accepted in
[the main frame finding](../../../manifests/gameplay-main-frame.json#/candidateFrameWork):
`0x82E43B50` loads the receiver from `0x8314F084` and calls `0x82D526A0`. That
shows where the receiver comes from, not what game state the call updates. The
function that writes simulation state from the timing value is open. More driver
entries with smaller elapsed values could change work that runs once per entry,
so a driver count is not a simulation rate. The limits of the one runtime
sample are in
[the same finding](../../../manifests/gameplay-main-frame.json#/runtimeProbe).

**Interface scripts.** The frontend step `0x82C5F680` loads the timing record
`0x8314F280`, calls its slot `+0x08` (target `0x82C7EB68`), and then uses the
accumulated time or frame delta in later update calls
([update finding](../../../manifests/gameplay-frame-timing-owner.json#/perFrameUpdate)).
The accepted records do not name the GFx advance call or the ActionScript
scheduling code that runs in a game. A smaller elapsed value might change
per-call script work or event order when updates run more often. That is not
yet shown. The same finding's query of `0x82C5F680` covered two instructions
and found no reader, which is not a no-reader result. The attract movie
finding rejects `0x82C5F680` as the frame boundary of a playable game. Drawing
is separate: see [GFx image rendering](gfx-image-rendering.md).

**Movies.** The movie draw reads frame data with no known clock link. See
[movie draw plane setup](movie-draw-binding.md).

**Audio.** The stream slot handle at `+0x4` in the audio manager is the result
of the Miles open wrapper. Nothing ties it to a render client index, a callback
argument or a sample pointer. No code that produces PCM callbacks, no cue clock
and no handle release is identified. See [audio script table](../content/audio-script-table.md)
and [the stream finding](../../../manifests/audio-initialization-stream-ownership.json#/streamOpen).

## Remaining limits

The recompiled copy of `0x82C7DF58` has no direct kernel wait, sleep or VdSwap
text. Indirect and unscanned dispatch remain open, including a guest cap below
60. No value shows an FPS, vsync or fixed simulation step. Only the pinned
timeout conversion gives a limit in milliseconds; runtime scaling and duration
remain unknown.
