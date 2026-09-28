// Ghidra post-script. Finds raw PowerPC displacement stores in one bounded VA band.
// Environment:
//   REREVVED_SCAN_START_VA  inclusive guest VA
//   REREVVED_SCAN_END_VA    exclusive guest VA
//   REREVVED_FIELD_OFFSETS  comma-separated signed D-form offsets, max 8
//   REREVVED_MAX_MATCHES    optional output cap, default 32
//   REREVVED_DUMP_PATH      output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class FindRawFieldStores extends GhidraScript {
    @Override
    public void run() throws Exception {
        long start = Long.decode(requireEnv("REREVVED_SCAN_START_VA"));
        long end = Long.decode(requireEnv("REREVVED_SCAN_END_VA"));
        Set<Integer> offsets = parseOffsets(requireEnv("REREVVED_FIELD_OFFSETS"));
        int cap = parseCap(System.getenv("REREVVED_MAX_MATCHES"));
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        if (start < 0 || end > 0x100000000L || start >= end ||
            (start & 3) != 0 || (end & 3) != 0 || end - start > 0x100000L) {
            throw new IllegalArgumentException("scan must be an aligned band of at most 0x100000 bytes");
        }

        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Memory memory = currentProgram.getMemory();
        int scanned = 0;
        int matches = 0;
        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.printf("Program: %s%nRange: [0x%08X,0x%08X)%nOffsets: %s%nCap: %d%n",
                currentProgram.getName(), start, end, offsets, cap);
            for (long value = start; value < end && !monitor.isCancelled(); value += 4) {
                Address address = space.getAddress(value);
                MemoryBlock block = memory.getBlock(address);
                if (block == null || !block.isInitialized() || !block.isExecute() ||
                    value + 3 > block.getEnd().getOffset()) {
                    continue;
                }
                scanned++;
                int word = memory.getInt(address);
                int opcode = word >>> 26;
                if (!isStore(opcode)) {
                    continue;
                }
                int displacement = (short) (word & (opcode == 62 ? 0xFFFC : 0xFFFF));
                if (!offsets.contains(displacement)) {
                    continue;
                }
                matches++;
                if (matches > cap) {
                    continue;
                }
                int source = (word >>> 21) & 31;
                int base = (word >>> 16) & 31;
                Function owner = currentProgram.getFunctionManager().getFunctionContaining(address);
                Instruction decoded = currentProgram.getListing().getInstructionAt(address);
                out.printf("0x%08X word=0x%08X opcode=%d rS=%d rA=%d offset=%d decoded=%s owner=%s%n",
                    value, word, opcode, source, base, displacement,
                    decoded == null ? "false" : decoded.toString(),
                    owner == null ? "<undefined>" : owner.getEntryPoint().toString());
            }
            out.printf("Scanned: %d%nMatches: %d%nTruncated: %s%nCancelled: %s%n",
                scanned, matches, matches > cap, monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private boolean isStore(int opcode) {
        return (opcode >= 36 && opcode <= 39) || opcode == 44 || opcode == 45 ||
            (opcode >= 52 && opcode <= 55) || opcode == 62;
    }

    private Set<Integer> parseOffsets(String raw) {
        Set<Integer> values = new LinkedHashSet<>();
        for (String token : raw.split(",")) {
            int value = Integer.decode(token.trim());
            if (value < Short.MIN_VALUE || value > Short.MAX_VALUE) {
                throw new IllegalArgumentException("offset is outside signed D-form range");
            }
            values.add(value);
        }
        if (values.isEmpty() || values.size() > 8) {
            throw new IllegalArgumentException("REREVVED_FIELD_OFFSETS requires 1 through 8 values");
        }
        return values;
    }

    private int parseCap(String raw) {
        int cap = raw == null || raw.isBlank() ? 32 : Integer.parseInt(raw);
        if (cap < 1 || cap > 256) {
            throw new IllegalArgumentException("REREVVED_MAX_MATCHES must be 1 through 256");
        }
        return cap;
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }
}
