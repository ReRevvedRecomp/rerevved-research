// Ghidra post-script. Finds raw PowerPC lis/addi or lis/ori candidates.
// Unlike FindSplitConstantUses, this also covers undefined or truncated code.
// Matches require instruction and register-lifetime confirmation by the caller.
// Environment:
//   REREVVED_TARGET_VAS   comma-separated exact 32-bit values, max 8
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

public class FindSplitConstantCandidates extends GhidraScript {
    @Override
    public void run() throws Exception {
        Set<Long> targets = new LinkedHashSet<>();
        for (String token : requireEnv("REREVVED_TARGET_VAS").split(",")) {
            long value = Long.decode(token.trim());
            if (value < 0 || value > 0xFFFFFFFFL) {
                throw new IllegalArgumentException("target must be a 32-bit unsigned value");
            }
            targets.add(value);
        }
        if (targets.isEmpty() || targets.size() > 8) {
            throw new IllegalArgumentException("target list must contain 1 through 8 values");
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
            out.println("Lookahead: 8 words; candidate cap: 8");
            out.println("Raw candidates only; intervening writes and code ownership are unchecked.");
            outer:
            for (MemoryBlock block : memory.getBlocks()) {
                if (!block.isInitialized()) {
                    continue;
                }
                Address start = block.getStart();
                start = start.add((4 - (start.getOffset() & 3)) & 3);
                for (Address at = start; at.add(3).compareTo(block.getEnd()) <= 0;
                     at = at.add(4)) {
                    monitor.checkCancelled();
                    int high = memory.getInt(at);
                    // addis rD,0,imm (lis).
                    if ((high & 0xFC1F0000) != 0x3C000000) {
                        continue;
                    }
                    int register = (high >>> 21) & 31;
                    long highValue = (high & 0xFFFFL) << 16;
                    for (int distance = 1; distance <= 8; distance++) {
                        Address lowAt = at.add(distance * 4);
                        if (lowAt.add(3).compareTo(block.getEnd()) > 0) {
                            break;
                        }
                        int low = memory.getInt(lowAt);
                        int opcode = low >>> 26;
                        boolean add = opcode == 14 && register != 0 &&
                                      ((low >>> 16) & 31) == register;
                        boolean or = opcode == 24 && ((low >>> 21) & 31) == register;
                        if (!add && !or) {
                            continue;
                        }
                        long value = (add ? highValue + (short) low :
                                           highValue | (low & 0xFFFFL)) & 0xFFFFFFFFL;
                        if (!targets.contains(value)) {
                            continue;
                        }
                        if (matches == 8) {
                            truncated = true;
                            break outer;
                        }
                        out.printf("0x%08X + 0x%08X => 0x%08X%n",
                                   at.getOffset(), lowAt.getOffset(), value);
                        matches++;
                    }
                }
            }
            out.println("Candidates: " + matches);
            out.println("Truncated: " + truncated);
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }
}
