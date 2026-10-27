// Raw bounded exact-global store discovery; every candidate needs confirmation.
// Environment:
//   REREVVED_TARGET_VAS   selected word addresses, maximum 8
//   REREVVED_MAX_MATCHES  output cap, default 16, maximum 64
//   REREVVED_LOOKAHEAD    words after each lis, default 32, maximum 128
//   REREVVED_DUMP_PATH    output file
// No program mutations. No assumed SDA base or control-flow analysis.
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryBlock;

public class FindRawGlobalStoreChains extends GhidraScript {
    @Override
    public void run() throws Exception {
        String rawTargets = requireEnv("REREVVED_TARGET_VAS");
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Set<Long> targets = new LinkedHashSet<>();
        for (String token : rawTargets.split(",", -1)) {
            long target = Long.decode(token.trim());
            if (target < 0 || target > 0xFFFFFFFFL) {
                throw new IllegalArgumentException("target must be unsigned 32-bit");
            }
            if (target > 0xFFFFFFFCL) {
                throw new IllegalArgumentException("target word range crosses 2^32");
            }
            targets.add(target);
        }
        if (targets.isEmpty() || targets.size() > 8) {
            throw new IllegalArgumentException("REREVVED_TARGET_VAS requires 1 through 8 targets");
        }
        int cap = parseBound("REREVVED_MAX_MATCHES", 16, 1, 64);
        int lookahead = parseBound("REREVVED_LOOKAHEAD", 32, 1, 128);
        Set<String> emitted = new LinkedHashSet<>();
        int candidates = 0;
        boolean truncated = false;

        try (PrintWriter out = new PrintWriter(new FileWriter(outPath))) {
            out.println("Program: " + currentProgram.getName());
            out.println("Targets: " + rawTargets);
            out.println("Lookahead: " + lookahead + " words; cap: " + cap);
            out.println("Raw candidates only. Register writes/control flow are unchecked; " +
                "seed/chain/owner must be confirmed.");
            out.println("Target ranges are four bytes; no fixed SDA/register base is assumed.");

            outer:
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                if (!block.isInitialized() || !block.isExecute()) {
                    continue;
                }
                Address seed = block.getStart().add((4 - (block.getStart().getOffset() & 3)) & 3);
                for (; seed.add(3).compareTo(block.getEnd()) <= 0; seed = seed.add(4)) {
                    monitor.checkCancelled();
                    int first = getInt(seed);
                    if ((first & 0xFC1F0000) != 0x3C000000) {
                        continue;
                    }
                    int register = (first >>> 21) & 31;
                    if (register == 0) {
                        continue;
                    }
                    Long[] known = new Long[32];
                    known[register] = (first & 0xFFFFL) << 16;
                    for (int step = 1; step <= lookahead &&
                            seed.add(4L * step + 3).compareTo(block.getEnd()) <= 0; step++) {
                        Address at = seed.add(4L * step);
                        int word = getInt(at);
                        int opcode = word >>> 26;
                        int rt = (word >>> 21) & 31;
                        int ra = (word >>> 16) & 31;
                        int rb = (word >>> 11) & 31;
                        long displacement = (short) word;
                        int width = dFormStoreWidth(opcode, rt);
                        Long effective = null;
                        if (width > 0 && (ra == 0 || known[ra] != null)) {
                            long offset = opcode == 62 ? (short) (word & 0xFFFC) : displacement;
                            effective = ((ra == 0 ? 0 : known[ra]) + offset) & 0xFFFFFFFFL;
                        }
                        if (opcode == 31) {
                            int indexedWidth = indexedStoreWidth((word >>> 1) & 1023);
                            if (indexedWidth > 0 && (ra == 0 || known[ra] != null) &&
                                    known[rb] != null) {
                                width = indexedWidth;
                                effective = ((ra == 0 ? 0 : known[ra]) + known[rb]) & 0xFFFFFFFFL;
                            }
                        }
                        if (effective != null) {
                            for (long target : targets) {
                                if (effective < target + 4 && target < effective + width &&
                                        emitted.add(at + ":" + target)) {
                                    if (candidates == cap) {
                                        truncated = true;
                                        break outer;
                                    }
                                    out.printf("target=0x%08X seed=0x%08X word=0x%08X " +
                                        "store=0x%08X word=0x%08X EA=0x%08X width=%d distance=%d%n",
                                        target, seed.getOffset(), first, at.getOffset(), word,
                                        effective, width, step);
                                    candidates++;
                                }
                            }
                        }
                        if (opcode == 18 && (word & 1) != 0) {
                            for (long target : targets) {
                                for (int argument = 3; argument <= 10; argument++) {
                                    if (known[argument] != null && known[argument] == target &&
                                            emitted.add("call:" + at + ":" + target + ":" + argument)) {
                                        if (candidates == cap) {
                                            truncated = true;
                                            break outer;
                                        }
                                        out.printf("target=0x%08X seed=0x%08X word=0x%08X " +
                                            "call=0x%08X word=0x%08X exactPointerArg=r%d distance=%d%n",
                                            target, seed.getOffset(), first, at.getOffset(), word,
                                            argument, step);
                                        candidates++;
                                    }
                                }
                            }
                        }

                        // This raw candidate model deliberately leaves other writes unchecked.
                        if (opcode == 15 && ra == 0) {
                            known[rt] = (word & 0xFFFFL) << 16;
                        } else if (opcode == 14) {
                            if (ra == 0) {
                                known[rt] = displacement & 0xFFFFFFFFL;
                            } else if (known[ra] == null) {
                                known[rt] = null;
                            } else {
                                known[rt] = (known[ra] + displacement) & 0xFFFFFFFFL;
                            }
                        } else if (opcode == 24) {
                            known[ra] = known[rt] == null ? null :
                                (known[rt] | (word & 0xFFFFL)) & 0xFFFFFFFFL;
                        } else if (opcode == 31 && ((word >>> 1) & 1023) == 444 && rt == rb) {
                            known[ra] = known[rt];
                        } else if (opcode == 31 && ((word >>> 1) & 1023) == 266) {
                            known[rt] = known[ra] == null || known[rb] == null ? null :
                                (known[ra] + known[rb]) & 0xFFFFFFFFL;
                        }
                    }
                }
            }
            out.println("Candidates: " + candidates);
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
            if (out.checkError()) {
                throw new IOException("failed while writing output: " + outPath);
            }
        }
    }

    private int dFormStoreWidth(int opcode, int source) {
        switch (opcode) {
            case 36: case 37: case 52: case 53:
                return 4;
            case 38: case 39:
                return 1;
            case 44: case 45:
                return 2;
            case 54: case 55: case 62:
                return 8;
            case 47:
                return 4 * (32 - source);
            default:
                return 0;
        }
    }

    private int indexedStoreWidth(int extendedOpcode) {
        switch (extendedOpcode) {
            case 151: case 183: case 663: case 695:
                return 4;
            case 215: case 247:
                return 1;
            case 407: case 439:
                return 2;
            case 149: case 181: case 727: case 759:
                return 8;
            default:
                return 0;
        }
    }

    private int parseBound(String key, int fallback, int minimum, int maximum) {
        String raw = System.getenv(key);
        int value = raw == null || raw.isBlank() ? fallback : Integer.parseInt(raw);
        if (value < minimum || value > maximum) {
            throw new IllegalArgumentException(key + " must be " + minimum + " through " + maximum);
        }
        return value;
    }

    private String requireEnv(String key) {
        String value = System.getenv(key);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(key + " is required");
        }
        return value;
    }
}
