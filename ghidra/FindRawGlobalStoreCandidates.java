// Ghidra post-script. Finds raw lis/D-form integer-store address candidates.
// Candidates need instruction, register-lifetime, and ownership confirmation.
// Environment:
//   REREVVED_TARGET_VAS   comma-separated exact 32-bit addresses, max 8
//   REREVVED_MAX_MATCHES  optional total output cap, default 32, max 128
//   REREVVED_DUMP_PATH    output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class FindRawGlobalStoreCandidates extends GhidraScript {
    private static final int MAX_TARGETS = 8;
    private static final int LOOKAHEAD_WORDS = 8;
    private static final int DEFAULT_CAP = 32;
    private static final int MAX_CAP = 128;

    @Override
    public void run() throws Exception {
        Set<Long> targets = new LinkedHashSet<>();
        for (String token : requireEnv("REREVVED_TARGET_VAS").split(",")) {
            long value = Long.decode(token.trim());
            if (value < 0 || value > 0xFFFFFFFFL) {
                throw new IllegalArgumentException("target must be a 32-bit unsigned address");
            }
            targets.add(value);
        }
        if (targets.isEmpty() || targets.size() > MAX_TARGETS) {
            throw new IllegalArgumentException("target list must contain 1 through " +
                MAX_TARGETS + " addresses");
        }
        String capValue = System.getenv("REREVVED_MAX_MATCHES");
        int cap = capValue == null || capValue.isBlank() ? DEFAULT_CAP : Integer.parseInt(capValue);
        if (cap < 1 || cap > MAX_CAP) {
            throw new IllegalArgumentException("REREVVED_MAX_MATCHES must be 1 through " + MAX_CAP);
        }
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Memory memory = currentProgram.getMemory();
        int matches = 0;
        boolean truncated = false;
        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            for (long target : targets) {
                out.printf("Target: 0x%08X%n", target);
            }
            out.println("Lookahead: " + LOOKAHEAD_WORDS + " words; candidate cap: " + cap);
            out.println("Initialized executable memory only; stw/stwu/stb/stbu/sth/sthu only.");
            out.println("Lookahead stays within one memory block; cross-block pairs are excluded.");
            out.println("Intervening writes, branches, code ownership, and aliases are unchecked.");
            outer:
            for (MemoryBlock block : memory.getBlocks()) {
                if (!block.isInitialized() || !block.isExecute()) {
                    continue;
                }
                Address at = block.getStart();
                at = at.add((4 - (at.getOffset() & 3)) & 3);
                for (; at.add(3).compareTo(block.getEnd()) <= 0; at = at.add(4)) {
                    if (monitor.isCancelled()) {
                        break outer;
                    }
                    int high = memory.getInt(at);
                    if ((high & 0xFC1F0000) != 0x3C000000) {
                        continue;
                    }
                    int register = (high >>> 21) & 31;
                    if (register == 0) {
                        continue;
                    }
                    long highValue = (high & 0xFFFFL) << 16;
                    for (int distance = 1; distance <= LOOKAHEAD_WORDS; distance++) {
                        Address storeAt = at.add(distance * 4);
                        if (storeAt.add(3).compareTo(block.getEnd()) > 0) {
                            break;
                        }
                        int store = memory.getInt(storeAt);
                        int opcode = store >>> 26;
                        if (!isIntegerStore(opcode) || ((store >>> 16) & 31) != register) {
                            continue;
                        }
                        long value = (highValue + (short) store) & 0xFFFFFFFFL;
                        if (!targets.contains(value)) {
                            continue;
                        }
                        if (matches == cap) {
                            truncated = true;
                            break outer;
                        }
                        out.printf("0x%08X + 0x%08X => 0x%08X words=0x%08X,0x%08X%n",
                            at.getOffset(), storeAt.getOffset(), value, high, store);
                        matches++;
                    }
                }
            }
            out.println("Candidates: " + matches);
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private boolean isIntegerStore(int opcode) {
        return (opcode >= 36 && opcode <= 39) || opcode == 44 || opcode == 45;
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }
}
