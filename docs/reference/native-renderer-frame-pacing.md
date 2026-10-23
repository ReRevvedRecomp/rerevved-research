# Native renderer guest frame pacing

The
[frame-pacing manifest](../../manifests/native-renderer-guest-frame-pacing.json)
bounds static timing/waits from playable callback to presentation; it
establishes neither simulation ownership, fixed tick nor rendering on every
timing update. Callback `0x82E87D18` calls `0x82C7DF58`, dispatching timing slot
`+0x8` at `0x82C7DF84`, then manager work. Entry r4 low byte nonzero permits
`0x82C7E104 -> 0x82C71A00`; zero reaches `0x82C7E118`. Both return `1`.

## Callback inputs and ownership

The
[scheduling manifest](../../manifests/native-renderer-frame-callback-scheduling.json)
records these inputs:

| Edge | State |
| --- | --- |
| `0x82E87D28` | Entry r4 -> r30, controlling manager-byte test |
| `0x82E87D2C`, `0x82E87D78`, `0x82E87D80` | Entry r5 -> r28 -> driver r4 -> call |
| `0x82E87D54`, `0x82E87D60` | Load manager `0x8314F28C`; store `+4` as `1` for zero r30 low byte, otherwise `0` |
| Registration | `0x82E2AF20` registers table `0x82120D2C` slot 0 = `0x82E87D18`. Vector `+0x80`, start/end/capacity `+0x84`/`+0x88`/`+0x8C`. Null callback exits; nonnull start with capacity stores/advances; otherwise `0x821B4450` has unbound insertion/return/retention. |

The
[owner-slot boundary](../../manifests/native-renderer-callback-owner-slot-boundary.json)
binds `0x82D83C7C`: owner from `0x82FFD624`, retaining vptr `0x82121100`, uses
`0x82121128` = no-op `0x821D5678`. Application service `+0x28` therefore neither
visits `+0x84/+0x88/+0x8C` nor produces r5; timing-owner `+0x28` is separate.
Vector invoker/r5 producer remain unknown, establishing no tick, frame counter,
simulation step, render cadence or presentation decision.

## Timing arithmetic and waits

`0x82C7EB68` dispatches at `0x82C7EB88` through `+0x14` (retained target
`0x82C5F790`). Nonzero owner `+0x18` selects `f1 - f0`; zero retains zero. Then:

1. Multiplies by owner `+0x28`.
2. Stores owner `+0x10`.
3. Clamps that value against exact double bits `0x3FC999999999999A` (decoded as
   `0.2`).
4. Increments `+0x30`.
5. Accumulates `+0x08`.
6. Stores the incoming value at `+0x18`.

The clamp is not an FPS limiter.

| Wait or limiter address | Condition | Interval or default | CPU/GPU | Role |
| --- | --- | --- | --- | --- |
| `0x826ABF38`, `0x826ABFCC` | Worker `0x826ABEA8` enters the first wait only when `[r26+0x3C] == [r26+0x38]`; status 258 selects or repeats the critical block, and the second wait follows it even when the device gate skips the pair | `KeWaitForSingleObject` uses r4=`3`, r5=`1`, r6=`0`; r27 points to stack `+0x50` when `[r25+0x178] == [r26+0x4]`, otherwise null. Pinned SDK maps `-300000` guest ticks to 30 guest milliseconds before optional scaling; actual host duration is unknown | CPU | Worker event and counter coordination |
| `0x826A4150` | Wrapper `0x826A4630` passes r4=`0` | PM4 `WAIT_REG_MEM` packet interval `0x100`, references `1` then `0`, device `+0x2A94+4`; not a time value | GPU | Pre-swap system command-buffer handshake |
| `0x8269E520` | Late Resolve command path reaches its wait packet | Register `0xA31`, reference r28, mask `0x80000000`, packet interval `8`; not a time value | GPU | Resolve command synchronization |
| `0x8269BE70` | The lock core selects `+0x0C` only when lock flags `& 0x1010`; callers pass a scalar fence in r4 and zero returns immediately | No fixed interval; compares fence and ring state and invokes bounded helpers | CPU/GPU | Resource lifetime fence wait, not a guest frame limiter |

## Presentation order and selector inputs

Status 258 plus device `+0x2ABE & 2` admits worker `0x826ABEA8` calls:
`0x826ABF80` -> `0x826A4630`, then `0x826ABF90` -> VdSwap owner `0x826A4638`.
Alternate `0x82517E38` uses `0x82517E58`/`0x82517E88`.

Owner calls VdGetSystemCommandBuffer at `0x826A4820` (LR `0x826A4824`), then
tests `+0x541C` at `0x826A4828`. Nonzero copies stack `+0x74` to
`[device +0x2A90] + 8` and jumps `0x826A4890`, skipping reservation/import; zero
calls import `0x82E92454` at `0x826A4884`.

Pre-swap device `+0x351C` maps:

| Selector | Mapped value |
| --- | --- |
| `0` and `1` | `1` |
| `2` | `2` |
| `4` | `3` |
| `0x80000000` | `0` |
| Other values | Stack `+0x50` |

Mapped value <<8 combines `+0x2E4C` bits and incoming-r4 state into `r7` for
`0x8269BF40`; r6 holds callback `0x826A3FB8` at `0x826A4298` (LR `0x826A429C`).
Bounded scan found setter `0x8268EF68`; three initial and five remainder callers
have static producer origins.

The
[setup-input manifest](../../manifests/native-renderer-presentation-setup-input.json)
traces caller two before template `+0x34`, retaining exact stack/mapping
details; helper mutation/final retention remain unresolved. The
[remainder manifest](../../manifests/native-renderer-presentation-selector-remainder.json)
locates five calls in `0x82C15240`, each reloading `[0x8314F300]` and passing
`U8(entry +0x0)`, `U8(entry +0x1)`, `U32(entry +0x4)`, `U32(entry +0x8)` or
`U32(entry +0xC)` as r4. Prologue indices `0`, `8`, `4`, `16`, `168` precede
unsigned compare `360`, yet setters occupy `case 336`. This mismatch leaves
entry/control/retention conditional. Runtime activation, default, interval
meaning and indirect/tail closure remain unknown.

## Callback arithmetic and clock units

Callback extracts low 8 bits/bits 8..11, choosing nonzero `[device +0x5434]` or
`60`. It computes `r11 = (timebase_delta * 100) / (frequency / divisor)`, then
`r7 = r11 + 1`, capped at `100`, with `twllei r29,0`/`twllei r11,0` guards.
Branches:

| Target | Condition |
| --- | --- |
| `0x826A4078` | `r8+r30 > r10`, `r30 == 0`, or `r7 <=` input low 8 bits |
| `0x826A40BC` | `r9 == 0` |
| `0x826A4100` | The subsequent `r10 == 1` |

Divisor, activation and interval meaning remain unknown; `60` is no proved FPS
setting. Clock target `0x82C5F790` lazily fills `+0x38` via `0x8280F0C8` and
`+0x40` via `0x8280F100`, returning (sample-baseline)/`+0x38`. Owner `+0x28`
meaning/values, scaling, samples, cadence and retail equivalence remain unknown.

Pinned SDK negative timeout `-timeout_ticks / 10000` maps `-300000` to 30 guest
milliseconds before `ScaleGuestDurationMillis`; null is unbounded.
`clock_no_scaling` true retains duration; otherwise `guest_time_scalar_` scales
and saturates. `REX_QUERY_TIMEBASE` returns guest ticks,
`KeQueryPerformanceFrequency` ticks/second: the pre-multiplier quotient is guest
seconds.

See:

- [threading.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/kernel/xboxkrnl/xboxkrnl_threading.cpp#L839-L848)
- [xobject.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/system/xobject.cpp#L189-L213)
- [clock.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/core/clock.cpp#L188-L203)
- [clock.h](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/include/rex/chrono/clock.h#L61-L73)
- [threading.cpp frequency path](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/kernel/xboxkrnl/xboxkrnl_threading.cpp#L371-L374)
- [runtime.cpp](https://github.com/ReRevvedRecomp/rerevved-sdk/blob/05e9bc372a66b651f05e2444f74bd5b31a90fc02/src/system/runtime.cpp#L150-L152)

Source initialization establishes intent, not observed settings, host duration,
event cadence, retail semantics or frame cap.

## Remaining limits

Generated `0x82C7DF58` has no direct kernel wait/sleep/VdSwap text; indirect and
unscanned dispatch remain open, including a guest cap below 60. No value proves
FPS, vsync or fixed simulation step. Only the pinned timeout conversion is
bounded in milliseconds; runtime scaling/duration remain unknown.
