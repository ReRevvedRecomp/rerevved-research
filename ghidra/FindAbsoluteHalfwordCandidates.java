// Ghidra post-script. Finds raw lis followed by an absolute lhz/lha candidate.
// Environment: REREVVED_TARGET_VAS (1..8 exact VAs), REREVVED_MAX_MATCHES
// (optional, 1..128, default 32), REREVVED_DUMP_PATH.
// Register lifetimes and code ownership require separate verification.
//@category ReRevved
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryBlock;

public class FindAbsoluteHalfwordCandidates extends GhidraScript {
    @Override
    public void run() throws Exception {
        Set<Long> targets = new LinkedHashSet<>();
        for (String token : required("REREVVED_TARGET_VAS").split(",")) {
            long value = Long.decode(token.trim());
            if (value < 0 || value > 0xFFFFFFFFL) {
                throw new IllegalArgumentException("target must be an unsigned 32-bit VA");
            }
            targets.add(value);
        }
        if (targets.isEmpty() || targets.size() > 8) {
            throw new IllegalArgumentException("requires 1..8 targets");
        }
        String rawCap = System.getenv("REREVVED_MAX_MATCHES");
        int cap = rawCap == null || rawCap.isBlank() ? 32 : Integer.parseInt(rawCap);
        if (cap < 1 || cap > 128) {
            throw new IllegalArgumentException("cap must be 1..128");
        }
        int matches = 0;
        long scanned = 0;
        PrintWriter out = new PrintWriter(new FileWriter(required("REREVVED_DUMP_PATH")));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            out.println("Targets: " + targets + "; lookahead: 8 words; cap: " + cap);
            out.println("Raw candidates; intervening writes, paths and owners unchecked.");
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                if (!block.isInitialized() || !block.isExecute()) { continue; }
                Address first = block.getStart();
                first = first.add((4 - (first.getOffset() & 3)) & 3);
                for (Address at = first; at.add(3).compareTo(block.getEnd()) <= 0;
                     at = at.add(4)) {
                    monitor.checkCancelled();
                    scanned++;
                    int high = getInt(at);
                    if ((high & 0xFC1F0000) != 0x3C000000) { continue; }
                    int base = (high >>> 21) & 31;
                    if (base == 0) { continue; }
                    for (int distance = 1; distance <= 8; distance++) {
                        Address lowAt = at.add(4L * distance);
                        if (lowAt.add(3).compareTo(block.getEnd()) > 0) { break; }
                        int low = getInt(lowAt);
                        int opcode = low >>> 26;
                        if ((opcode != 40 && opcode != 42) ||
                            ((low >>> 16) & 31) != base) { continue; }
                        long value = (((high & 0xFFFFL) << 16) + (short) low) & 0xFFFFFFFFL;
                        if (!targets.contains(value)) { continue; }
                        matches++;
                        if (matches <= cap) {
                            out.printf("0x%08X + 0x%08X => 0x%08X words=%08X,%08X%n",
                                at.getOffset(), lowAt.getOffset(), value, high, low);
                        }
                    }
                }
            }
            out.printf("Scanned: %d%nMatches: %d%nTruncated: %s%n",
                scanned, matches, matches > cap);
        }
        if (out.checkError()) { throw new java.io.IOException("query output failed"); }
    }

    private String required(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("missing " + name);
        }
        return value;
    }
}
