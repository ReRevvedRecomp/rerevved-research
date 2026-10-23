// Ghidra post-script. Finds raw PowerPC direct branch-and-link callers.
// Environment:
//   REREVVED_TARGET_VAS   comma-separated guest VAs, max 8
//   REREVVED_MAX_MATCHES  optional matches per target, default 32
//   REREVVED_DUMP_PATH    output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedHashMap;
import java.util.Map;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class FindDirectCallers extends GhidraScript {
    @Override
    public void run() throws Exception {
        Map<Long, Integer> targets = parseTargets(requireEnv("REREVVED_TARGET_VAS"));
        int maxMatches = parseMaxMatches(System.getenv("REREVVED_MAX_MATCHES"));
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Memory memory = currentProgram.getMemory();
        FunctionManager functions = currentProgram.getFunctionManager();
        boolean truncated = false;

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            out.println("Targets: " + formatTargets(targets));
            out.println("Match cap per target: " + maxMatches);
            out.println("Scope: initialized executable memory, aligned raw words");

            for (MemoryBlock block : memory.getBlocks()) {
                if (!block.isInitialized() || !block.isExecute() || monitor.isCancelled()) {
                    continue;
                }
                Address current = align(block.getStart());
                Address end = block.getEnd();
                while (current.compareTo(end) <= 0 && !monitor.isCancelled()) {
                    if (current.add(3).compareTo(end) > 0) {
                        break;
                    }
                    long word = Integer.toUnsignedLong(memory.getInt(current));
                    if (isDirectCall(word)) {
                        long target = branchTarget(current.getOffset(), word);
                        Integer count = targets.get(target);
                        if (count != null) {
                            if (count < maxMatches) {
                                emitMatch(out, current, word, target, functions);
                                targets.put(target, count + 1);
                            } else {
                                truncated = true;
                            }
                        }
                    }
                    current = current.add(4);
                }
            }

            out.println();
            for (Map.Entry<Long, Integer> entry : targets.entrySet()) {
                out.printf("Matches for 0x%08X: %d%n", entry.getKey(), entry.getValue());
            }
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private boolean isDirectCall(long word) {
        return (word >>> 26) == 18 && (word & 1) != 0;
    }

    private long branchTarget(long source, long word) {
        long displacement = word & 0x03FFFFFCL;
        if ((displacement & 0x02000000L) != 0) {
            displacement |= ~0x03FFFFFFL;
        }
        long base = (word & 2) != 0 ? 0 : source;
        return (base + displacement) & 0xFFFFFFFFL;
    }

    private void emitMatch(PrintWriter out, Address source, long word, long target,
                           FunctionManager functions) {
        Instruction instruction = currentProgram.getListing().getInstructionAt(source);
        Function function = functions.getFunctionContaining(source);
        String owner = function == null
            ? "<undefined>"
            : function.getName() + " @ " + function.getEntryPoint();
        out.printf("0x%08X word=0x%08X target=0x%08X decoded=%s owner=%s%n",
            source.getOffset(), word, target, instruction != null, owner);
    }

    private Map<Long, Integer> parseTargets(String raw) {
        Map<Long, Integer> targets = new LinkedHashMap<>();
        for (String token : raw.split(",")) {
            if (!token.isBlank()) {
                long value = Long.decode(token.trim()) & 0xFFFFFFFFL;
                targets.put(value, 0);
            }
        }
        if (targets.isEmpty() || targets.size() > 8) {
            throw new IllegalArgumentException(
                "REREVVED_TARGET_VAS must contain 1 through 8 values");
        }
        return targets;
    }

    private int parseMaxMatches(String raw) {
        int value = raw == null || raw.isBlank() ? 32 : Integer.parseInt(raw);
        if (value < 1 || value > 256) {
            throw new IllegalArgumentException(
                "REREVVED_MAX_MATCHES must be 1 through 256");
        }
        return value;
    }

    private String formatTargets(Map<Long, Integer> targets) {
        StringBuilder builder = new StringBuilder();
        for (long target : targets.keySet()) {
            if (builder.length() > 0) {
                builder.append(',');
            }
            builder.append(String.format("0x%08X", target));
        }
        return builder.toString();
    }

    private Address align(Address address) {
        long offset = address.getOffset();
        return address.add((4 - (offset & 3)) & 3);
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }
}
