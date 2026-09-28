// Ghidra post-script. Classifies register-plus-displacement field accesses in
// selected functions and an optional bounded caller closure.
// Environment:
//   REREVVED_FIELD_OFFSETS  comma-separated hex offsets
//   REREVVED_SEED_VAS       optional comma-separated function or interior VAs
//   REREVVED_CALLER_DEPTH   optional non-negative integer, default 0
//   REREVVED_CALLEE_DEPTH   optional non-negative integer, default 0
//   REREVVED_BASE_REGS      optional comma-separated register names
//   REREVVED_ACCESS_TYPES   optional READ,WRITE,READ_WRITE,ADDRESS filter
//   REREVVED_MAX_HITS       optional positive result cap; zero means no cap
//   REREVVED_SCAN_START_VA  optional inclusive instruction-address lower bound
//   REREVVED_SCAN_END_VA    optional exclusive instruction-address upper bound
//   REREVVED_DUMP_PATH      output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.RefType;

public class FindFieldAccesses extends GhidraScript {
    private static final class FunctionAtDepth {
        final Function function;
        final int depth;

        FunctionAtDepth(Function function, int depth) {
            this.function = function;
            this.depth = depth;
        }
    }

    @Override
    public void run() throws Exception {
        Set<Long> offsets = parseHexSet(requireEnv("REREVVED_FIELD_OFFSETS"));
        String seedRaw = System.getenv("REREVVED_SEED_VAS");
        Set<Long> seedVas = parseHexSet(seedRaw);
        boolean explicitSeeds = seedRaw != null && !seedRaw.isBlank();
        Set<String> baseRegisters = parseUpperSet(System.getenv("REREVVED_BASE_REGS"));
        Set<String> accessTypes = parseUpperSet(System.getenv("REREVVED_ACCESS_TYPES"));
        int callerDepth = parseDepth(System.getenv("REREVVED_CALLER_DEPTH"));
        int calleeDepth = parseDepth(System.getenv("REREVVED_CALLEE_DEPTH"));
        int maxHits = parseMaxHits(System.getenv("REREVVED_MAX_HITS"));
        long scanStart = parseAddressBound(System.getenv("REREVVED_SCAN_START_VA"), 0);
        long scanEnd = parseAddressBound(System.getenv("REREVVED_SCAN_END_VA"), 0x100000000L);
        if (scanStart >= scanEnd) {
            throw new IllegalArgumentException("scan start must be below scan end");
        }
        String outPath = requireEnv("REREVVED_DUMP_PATH");

        FunctionManager functions = currentProgram.getFunctionManager();
        Map<Long, Integer> functionDepths = buildClosure(
            functions, seedVas, callerDepth, calleeDepth, explicitSeeds);
        long scanned = 0;
        long hits = 0;
        boolean truncated = false;

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Offsets: " + System.getenv("REREVVED_FIELD_OFFSETS"));
            out.println("Seeds: " + System.getenv("REREVVED_SEED_VAS"));
            out.println("Caller depth: " + callerDepth);
            out.println("Callee depth: " + calleeDepth);
            out.println("Access filter: " + System.getenv("REREVVED_ACCESS_TYPES"));
            out.println("Max hits: " + maxHits);
            out.printf("Scan range: [0x%08X, 0x%08X)%n", scanStart, scanEnd);
            if (!functionDepths.isEmpty()) {
                out.println("Functions in scope:");
                for (Map.Entry<Long, Integer> entry : functionDepths.entrySet()) {
                    Function function = functions.getFunctionAt(toAddress(entry.getKey()));
                    String name = function == null ? "<missing>" : function.getName();
                    out.printf("  depth=%d 0x%08X %s%n", entry.getValue(), entry.getKey(), name);
                }
            }

            InstructionIterator instructions = currentProgram.getListing().getInstructions(
                toAddress(scanStart), true);
            scan:
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction instruction = instructions.next();
                if (instruction.getAddress().getOffset() >= scanEnd) break;
                Function function = functions.getFunctionContaining(instruction.getAddress());
                if (function == null) continue;
                long entry = function.getEntryPoint().getOffset();
                if (!functionDepths.isEmpty() && !functionDepths.containsKey(entry)) continue;
                scanned++;

                for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                    Long displacement = null;
                    String base = null;
                    for (Object object : instruction.getOpObjects(operand)) {
                        if (object instanceof Scalar) {
                            long value = ((Scalar) object).getUnsignedValue();
                            if (offsets.contains(value)) displacement = value;
                        } else if (object instanceof Register && base == null) {
                            base = ((Register) object).getName().toUpperCase();
                        }
                    }
                    if (displacement == null || base == null) continue;
                    if (baseRegisters.isEmpty()) {
                        if (base.equals("R1")) continue;
                    } else if (!baseRegisters.contains(base)) {
                        continue;
                    }

                    String access = classifyAccess(instruction, operand);
                    if (!accessTypes.isEmpty() && !accessTypes.contains(access)) continue;
                    hits++;
                    int depth = functionDepths.isEmpty() ? -1 : functionDepths.get(entry);
                    out.printf(
                        "0x%08X\t%s\tdepth=%d\t0x%08X\t%s\top%d\t%s\t+0x%X\t%s%n",
                        entry, function.getName(), depth, instruction.getAddress().getOffset(),
                        access, operand, base, displacement, instruction.toString());
                    if (maxHits > 0 && hits >= maxHits) {
                        truncated = instructions.hasNext();
                        break scan;
                    }
                }
            }
            out.printf("Scanned %d instructions; found %d accesses.%n", scanned, hits);
            out.println("Truncated: " + truncated);
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private Map<Long, Integer> buildClosure(
            FunctionManager functions, Set<Long> seedVas, int callerDepth, int calleeDepth,
            boolean explicitSeeds) {
        Set<Function> seeds = new HashSet<>();
        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        boolean unresolved = false;

        for (long seedVa : seedVas) {
            Address address = space.getAddress(seedVa);
            Function function = functions.getFunctionAt(address);
            if (function == null) function = functions.getFunctionContaining(address);
            if (function == null) {
                printerr(String.format("No function contains seed 0x%08X", seedVa));
                unresolved = true;
                continue;
            }
            long entry = function.getEntryPoint().getOffset();
            if (seeds.stream().noneMatch(item ->
                    item.getEntryPoint().getOffset() == entry)) seeds.add(function);
        }
        if (explicitSeeds && unresolved) {
            throw new IllegalArgumentException("one or more requested seeds do not resolve");
        }

        Map<Long, Integer> callerDepths = new TreeMap<>();
        Map<Long, Integer> calleeDepths = new TreeMap<>();
        for (Function seed : seeds) {
            long entry = seed.getEntryPoint().getOffset();
            callerDepths.put(entry, 0);
            calleeDepths.put(entry, 0);
        }
        addDirectionalClosure(callerDepths, seeds, callerDepth, true);
        addDirectionalClosure(calleeDepths, seeds, calleeDepth, false);

        Map<Long, Integer> depths = new TreeMap<>(callerDepths);
        for (Map.Entry<Long, Integer> entry : calleeDepths.entrySet()) {
            depths.merge(entry.getKey(), entry.getValue(), Math::min);
        }
        return depths;
    }

    private void addDirectionalClosure(Map<Long, Integer> depths, Set<Function> seeds,
            int maxDepth, boolean callers) {
        ArrayDeque<FunctionAtDepth> queue = new ArrayDeque<>();
        for (Function seed : seeds) queue.add(new FunctionAtDepth(seed, 0));

        while (!queue.isEmpty() && !monitor.isCancelled()) {
            FunctionAtDepth current = queue.remove();
            if (current.depth >= maxDepth) continue;
            Set<Function> adjacent = callers
                ? current.function.getCallingFunctions(monitor)
                : current.function.getCalledFunctions(monitor);
            for (Function function : adjacent) {
                long entry = function.getEntryPoint().getOffset();
                int depth = current.depth + 1;
                Integer knownDepth = depths.get(entry);
                if (knownDepth != null && knownDepth <= depth) continue;
                depths.put(entry, depth);
                queue.add(new FunctionAtDepth(function, depth));
            }
        }
    }

    private Address toAddress(long value) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
    }

    private String classifyAccess(Instruction instruction, int operand) {
        RefType refType = instruction.getOperandRefType(operand);
        if (refType != null && refType.isRead() && refType.isWrite()) return "READ_WRITE";
        if (refType != null && refType.isWrite()) return "WRITE";
        if (refType != null && refType.isRead()) return "READ";
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        if (mnemonic.startsWith("st") || mnemonic.equals("dcbz")) return "WRITE";
        if (mnemonic.startsWith("l")) return "READ";
        return "ADDRESS";
    }

    private int parseDepth(String value) {
        if (value == null || value.isBlank()) return 0;
        int depth = Integer.parseInt(value.trim());
        if (depth < 0 || depth > 8) {
            throw new IllegalArgumentException("closure depth must be between 0 and 8");
        }
        return depth;
    }

    private int parseMaxHits(String value) {
        if (value == null || value.isBlank()) return 0;
        int limit = Integer.parseInt(value.trim());
        if (limit < 0 || limit > 10000) {
            throw new IllegalArgumentException("REREVVED_MAX_HITS must be between 0 and 10000");
        }
        return limit;
    }

    private long parseAddressBound(String value, long defaultValue) {
        if (value == null || value.isBlank()) return defaultValue;
        long address = Long.decode(value.trim());
        if (address < 0 || address > 0x100000000L) {
            throw new IllegalArgumentException("scan bound must fit the 32-bit address space");
        }
        return address;
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }

    private Set<Long> parseHexSet(String value) {
        Set<Long> result = new HashSet<>();
        if (value == null || value.isBlank()) return result;
        for (String token : value.split(",")) result.add(Long.decode(token.trim()));
        return result;
    }

    private Set<String> parseUpperSet(String value) {
        Set<String> result = new HashSet<>();
        if (value == null || value.isBlank()) return result;
        for (String token : value.split(",")) result.add(token.trim().toUpperCase());
        return result;
    }
}
