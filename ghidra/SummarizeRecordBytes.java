// Ghidra post-script. Counts nonzero bytes in bounded stride-sized records.
// Environment:
//   REREVVED_RECORD_BASE    first guest VA
//   REREVVED_RECORD_STRIDE  bytes per record, 1 through 1024
//   REREVVED_RECORD_COUNT   records to inspect, 1 through 64
//   REREVVED_DUMP_PATH      output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;

public class SummarizeRecordBytes extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address base = toAddr(Long.decode(requireEnv("REREVVED_RECORD_BASE")));
        int stride = parseBound("REREVVED_RECORD_STRIDE", 1024);
        int count = parseBound("REREVVED_RECORD_COUNT", 64);
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Memory memory = currentProgram.getMemory();

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.printf("Program: %s%n", currentProgram.getName());
            out.printf("Base: 0x%08X stride: 0x%X count: %d%n",
                base.getOffset(), stride, count);
            for (int index = 0; index < count && !monitor.isCancelled(); index++) {
                Address start = base.add((long) index * stride);
                int nonzero = 0;
                int first = -1;
                int last = -1;
                for (int offset = 0; offset < stride; offset++) {
                    Address address = start.add(offset);
                    if (!memory.contains(address)) {
                        throw new IllegalArgumentException("unmapped byte at " + address);
                    }
                    if (memory.getByte(address) != 0) {
                        if (first < 0) {
                            first = offset;
                        }
                        last = offset;
                        nonzero++;
                    }
                }
                out.printf("%d 0x%08X..0x%08X nonzero=%d first=%s last=%s%n",
                    index, start.getOffset(), start.add(stride - 1).getOffset(), nonzero,
                    first < 0 ? "none" : String.format("+0x%X", first),
                    last < 0 ? "none" : String.format("+0x%X", last));
            }
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private int parseBound(String name, int maximum) {
        int value = Integer.parseInt(requireEnv(name));
        if (value < 1 || value > maximum) {
            throw new IllegalArgumentException(name + " must be 1 through " + maximum);
        }
        return value;
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }
}
