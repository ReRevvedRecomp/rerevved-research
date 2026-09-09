// Ghidra post-script. Finds raw-only PowerPC vtable slot-call candidates.
// Environment:
//   REREVVED_VTABLE_SLOT_DISPLACEMENTS  comma-separated positive 16-bit displacements, max 8
//   REREVVED_MAX_CALLSITES              optional result cap, default 64
//   REREVVED_DUMP_PATH                  output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;

public class FindRawVtableSlotCalls extends GhidraScript {
    private static final int MAX_WINDOW_WORDS = 8;
    private static final long OPCODE_MASK = 0xFC000000L;
    private static final long LWZ_OPCODE = 0x80000000L;
    private static final long MTCTR_MASK = 0xFC1FFFFFL;
    private static final long MTCTR_PATTERN = 0x7C0903A6L;
    private static final long BCTRL_WORD = 0x4E800421L;
    private static final long BRANCH_FORM_MASK = 0xFC0007FEL;
    private static final long BCLR_FORM = 0x4C000020L;
    private static final long BCCTR_FORM = 0x4C000420L;

    @Override
    public void run() throws Exception {
        Set<Long> displacements = parseDisplacements(
            requireEnv("REREVVED_VTABLE_SLOT_DISPLACEMENTS"));
        int maxCallsites = parseMaxCallsites(System.getenv("REREVVED_MAX_CALLSITES"));
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Memory memory = currentProgram.getMemory();
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Long> decodedCandidates = collectDecodedCandidates(displacements);
        long scannedWords = 0;
        long rawCandidates = 0;
        long decodedRawCandidates = 0;
        long rawOnlyCandidates = 0;
        int callsites = 0;
        boolean truncated = false;

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            out.println("Slot displacements: " + formatDisplacements(displacements));
            out.println("Callsite cap: " + maxCallsites);
            out.println("Raw successor window: " + MAX_WINDOW_WORDS + " words");
            out.println("Scope: initialized executable memory, aligned raw words");
            out.println("Raw matches are syntactic and require register-lifetime confirmation.");

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
                    scannedWords++;
                    long word = Integer.toUnsignedLong(memory.getInt(current));
                    RawLoad load = matchRawLoad(word, displacements);
                    if (load != null) {
                        rawCandidates++;
                        if (decodedCandidates.contains(current.getOffset())) {
                            decodedRawCandidates++;
                        } else {
                            rawOnlyCandidates++;
                            RawMatch match = findRawCallsite(memory, block, current, load);
                            if (match != null) {
                                if (callsites >= maxCallsites) {
                                    truncated = true;
                                } else {
                                    emitMatch(out, functions, current, word, load, match,
                                        callsites + 1);
                                    callsites++;
                                }
                            }
                        }
                    }
                    current = current.add(4);
                }
            }

            out.println();
            out.println("Executable raw words scanned: " + scannedWords);
            out.println("Decoded slot-load candidates: " + decodedCandidates.size());
            out.println("Raw lwz slot-load candidates: " + rawCandidates);
            out.println("Raw candidates covered by decoded query: " + decodedRawCandidates);
            out.println("Raw-only slot-load candidates: " + rawOnlyCandidates);
            out.println("Total raw-only callsite candidates: " + callsites);
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private Set<Long> collectDecodedCandidates(Set<Long> displacements) {
        Set<Long> result = new LinkedHashSet<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext() && !monitor.isCancelled()) {
            Instruction instruction = instructions.next();
            if (matchDecodedLoad(instruction, displacements)) {
                result.add(instruction.getAddress().getOffset());
            }
        }
        return result;
    }

    private boolean matchDecodedLoad(Instruction instruction, Set<Long> displacements) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        if (!mnemonic.equals("lwz") && !mnemonic.equals("lwzu")) {
            return false;
        }
        if (resultRegister(instruction) == null) {
            return false;
        }
        for (int operand = 1; operand < instruction.getNumOperands(); operand++) {
            Register base = null;
            Long displacement = null;
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Register && base == null) {
                    base = (Register) object;
                } else if (object instanceof Scalar && displacement == null) {
                    Scalar scalar = (Scalar) object;
                    displacement = scalar.getSignedValue() > 0
                        ? scalar.getSignedValue() : scalar.getUnsignedValue();
                }
            }
            if (base != null && displacement != null
                && !base.getName().equalsIgnoreCase("r0")
                && !base.getName().equalsIgnoreCase("r1")
                && displacements.contains(displacement)) {
                return true;
            }
        }
        return false;
    }

    private Register resultRegister(Instruction instruction) {
        Register result = null;
        for (Object object : instruction.getResultObjects()) {
            if (!(object instanceof Register)) {
                continue;
            }
            if (result != null) {
                return null;
            }
            result = (Register) object;
        }
        return result;
    }

    private RawLoad matchRawLoad(long word, Set<Long> displacements) {
        if ((word & OPCODE_MASK) != LWZ_OPCODE) {
            return null;
        }
        int base = (int) ((word >>> 16) & 0x1F);
        if (base == 0 || base == 1) {
            return null;
        }
        long displacement = word & 0xFFFFL;
        if (!displacements.contains(displacement)) {
            return null;
        }
        int destination = (int) ((word >>> 21) & 0x1F);
        return new RawLoad(destination, base, displacement);
    }

    private RawMatch findRawCallsite(
            Memory memory, MemoryBlock block, Address loadAddress, RawLoad load)
            throws Exception {
        Address mtctr = null;
        for (int distance = 1; distance <= MAX_WINDOW_WORDS; distance++) {
            Address address = loadAddress.add(distance * 4L);
            if (address.compareTo(block.getEnd()) > 0
                || address.add(3).compareTo(block.getEnd()) > 0) {
                return null;
            }
            long word = Integer.toUnsignedLong(memory.getInt(address));
            if (word == BCTRL_WORD) {
                return mtctr == null ? null : new RawMatch(mtctr, address, distance);
            }
            if (isMtctr(word)) {
                int source = (int) ((word >>> 21) & 0x1F);
                if (source != load.destination) {
                    return null;
                }
                mtctr = address;
                continue;
            }
            if (isControlFlow(word)) {
                return null;
            }
        }
        return null;
    }

    private boolean isMtctr(long word) {
        return (word & MTCTR_MASK) == MTCTR_PATTERN;
    }

    private boolean isControlFlow(long word) {
        long opcode = word >>> 26;
        return opcode == 16 || opcode == 17 || opcode == 18
            || (word & BRANCH_FORM_MASK) == BCLR_FORM
            || (word & BRANCH_FORM_MASK) == BCCTR_FORM;
    }

    private void emitMatch(PrintWriter out, FunctionManager functions, Address loadAddress,
                           long loadWord, RawLoad load, RawMatch match, int index)
            throws Exception {
        Function function = functions.getFunctionContaining(loadAddress);
        String owner = function == null
            ? "<undefined>"
            : function.getName() + " @ " + function.getEntryPoint();
        out.printf("%n=== raw-only callsite %d ===%n", index);
        out.printf("Owner: %s%n", owner);
        out.printf("Slot displacement: +0x%X%n", load.displacement);
        out.printf("Raw slot load: 0x%08X word=0x%08X r%d,+0x%X(r%d)%n",
            loadAddress.getOffset(), loadWord, load.destination, load.displacement, load.base);
        out.printf("Raw mtctr: 0x%08X%n", match.mtctr.getOffset());
        out.printf("Raw bctrl: 0x%08X%n", match.bctrl.getOffset());
        out.printf("Window distance: %d words%n", match.distance);
        for (int distance = 0; distance <= match.distance; distance++) {
            Address address = loadAddress.add(distance * 4L);
            long word = Integer.toUnsignedLong(currentProgram.getMemory().getInt(address));
            Instruction decoded = currentProgram.getListing().getInstructionAt(address);
            out.printf("  0x%08X 0x%08X %s%n", address.getOffset(), word,
                decoded == null ? "<undefined>" : decoded.toString());
        }
    }

    private Set<Long> parseDisplacements(String raw) {
        Set<Long> values = new LinkedHashSet<>();
        for (String token : raw.split(",")) {
            if (!token.isBlank()) {
                long value = Long.decode(token.trim());
                if (value <= 0 || value > 0xFFFFL) {
                    throw new IllegalArgumentException(
                        "REREVVED_VTABLE_SLOT_DISPLACEMENTS must contain positive 16-bit values");
                }
                values.add(value);
            }
        }
        if (values.isEmpty() || values.size() > 8) {
            throw new IllegalArgumentException(
                "REREVVED_VTABLE_SLOT_DISPLACEMENTS must contain 1 through 8 values");
        }
        return values;
    }

    private int parseMaxCallsites(String raw) {
        int value = raw == null || raw.isBlank() ? 64 : Integer.parseInt(raw.trim());
        if (value < 1 || value > 256) {
            throw new IllegalArgumentException("REREVVED_MAX_CALLSITES must be 1 through 256");
        }
        return value;
    }

    private String formatDisplacements(Set<Long> values) {
        StringBuilder result = new StringBuilder();
        for (long value : values) {
            if (result.length() > 0) {
                result.append(',');
            }
            result.append(String.format("0x%04X", value));
        }
        return result.toString();
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

    private static final class RawLoad {
        private final int destination;
        private final int base;
        private final long displacement;

        private RawLoad(int destination, int base, long displacement) {
            this.destination = destination;
            this.base = base;
            this.displacement = displacement;
        }
    }

    private static final class RawMatch {
        private final Address mtctr;
        private final Address bctrl;
        private final int distance;

        private RawMatch(Address mtctr, Address bctrl, int distance) {
            this.mtctr = mtctr;
            this.bctrl = bctrl;
            this.distance = distance;
        }
    }
}
