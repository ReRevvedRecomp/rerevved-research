// Ghidra post-script. Finds decoded PowerPC indirect calls through vtable slots.
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
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class FindVtableSlotCalls extends GhidraScript {
    private static final int MAX_WINDOW_INSTRUCTIONS = 8;

    @Override
    public void run() throws Exception {
        Set<Long> displacements = parseDisplacements(
            requireEnv("REREVVED_VTABLE_SLOT_DISPLACEMENTS"));
        int maxCallsites = parseMaxCallsites(System.getenv("REREVVED_MAX_CALLSITES"));
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        int callsites = 0;
        long scanned = 0;
        long loadCandidates = 0;
        boolean truncated = false;

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            out.println("Slot displacements: " + formatDisplacements(displacements));
            out.println("Callsite cap: " + maxCallsites);
            out.println("Straight-line window: " + MAX_WINDOW_INSTRUCTIONS + " instructions");

            InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction load = instructions.next();
                scanned++;
                LoadCandidate candidate = matchLoad(load, displacements);
                if (candidate == null) {
                    continue;
                }
                loadCandidates++;
                Function function = currentProgram.getFunctionManager()
                    .getFunctionContaining(load.getAddress());
                if (function == null) {
                    continue;
                }
                Match match = findCallsite(function, load, candidate.destination);
                if (match == null) {
                    continue;
                }
                if (callsites >= maxCallsites) {
                    truncated = true;
                    break;
                }
                out.printf("%n=== callsite %d ===%n", callsites + 1);
                out.printf("Function: 0x%08X %s%n",
                    function.getEntryPoint().getOffset(), function.getName());
                out.printf("Slot displacement: +0x%X%n", candidate.displacement);
                out.printf("Vtable base: %s%n", candidate.base.getName());
                out.printf("Slot load: 0x%08X %s%n",
                    load.getAddress().getOffset(), load);
                out.printf("mtctr: 0x%08X %s%n",
                    match.mtctr.getAddress().getOffset(), match.mtctr);
                out.printf("bctrl: 0x%08X %s%n",
                    match.bctrl.getAddress().getOffset(), match.bctrl);
                callsites++;
            }
            out.println();
            out.println("Scanned instructions: " + scanned);
            out.println("Decoded slot-load candidates: " + loadCandidates);
            out.println("Total: " + callsites);
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private LoadCandidate matchLoad(Instruction instruction, Set<Long> displacements) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        if (!mnemonic.equals("lwz") && !mnemonic.equals("lwzu")) {
            return null;
        }
        Register destination = resultRegister(instruction);
        if (destination == null) {
            return null;
        }
        for (int operand = 1; operand < instruction.getNumOperands(); operand++) {
            Register base = null;
            Long displacement = null;
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Register && base == null) {
                    base = (Register) object;
                } else if (object instanceof Scalar && displacement == null) {
                    displacement = scalarDisplacement((Scalar) object);
                }
            }
            if (base != null && displacement != null && displacements.contains(displacement)
                && isVtableBase(base)) {
                return new LoadCandidate(base, destination, displacement);
            }
        }
        return null;
    }

    private Match findCallsite(Function function, Instruction load, Register destination) {
        Instruction current = load;
        Instruction mtctr = null;
        Register trackedSource = null;
        boolean sourceValueLive = false;
        for (int distance = 1; distance <= MAX_WINDOW_INSTRUCTIONS; distance++) {
            Instruction next = currentProgram.getListing()
                .getInstructionAfter(current.getAddress());
            if (next == null || next.getAddress().getOffset() != current.getAddress().getOffset() + 4
                || !function.getBody().contains(next.getAddress())
                || currentProgram.getFunctionManager().getFunctionContaining(next.getAddress()) != function) {
                return null;
            }
            if (isBctrl(next)) {
                return mtctr == null ? null : new Match(mtctr, next);
            }
            if (mtctr == null) {
                if (writesRegister(next, destination)) {
                    return null;
                }
                if (isMtctr(next)) {
                    Register source = mtctrSource(next);
                    if (source != null && sameRegister(source, destination)) {
                        mtctr = next;
                        trackedSource = source;
                        sourceValueLive = true;
                        current = next;
                        continue;
                    }
                }
            } else {
                if (isMtctr(next)) {
                    Register source = mtctrSource(next);
                    if (source == null || !sameRegister(source, trackedSource)
                        || !sourceValueLive) {
                        return null;
                    }
                    mtctr = next;
                    current = next;
                    continue;
                }
                if (writesRegister(next, trackedSource)) {
                    sourceValueLive = false;
                }
            }
            if (hasControlFlow(next)) {
                return null;
            }
            current = next;
        }
        return null;
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

    private boolean writesRegister(Instruction instruction, Register expected) {
        for (Object object : instruction.getResultObjects()) {
            if (object instanceof Register && sameRegister((Register) object, expected)) {
                return true;
            }
        }
        return false;
    }

    private Register mtctrSource(Instruction instruction) {
        Register source = null;
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (!(object instanceof Register)) {
                    continue;
                }
                Register register = (Register) object;
                if (!isGeneralRegister(register)) {
                    continue;
                }
                if (source != null) {
                    return null;
                }
                source = register;
            }
        }
        return source;
    }

    private boolean isGeneralRegister(Register register) {
        String name = register.getName();
        if (name.length() < 2 || (name.charAt(0) != 'r' && name.charAt(0) != 'R')) {
            return false;
        }
        for (int index = 1; index < name.length(); index++) {
            if (!Character.isDigit(name.charAt(index))) {
                return false;
            }
        }
        return true;
    }

    private boolean sameRegister(Register first, Register second) {
        return first.getName().equalsIgnoreCase(second.getName());
    }

    private boolean isVtableBase(Register register) {
        String name = register.getName();
        return !name.equalsIgnoreCase("r0") && !name.equalsIgnoreCase("r1");
    }

    private boolean isMtctr(Instruction instruction) {
        String mnemonic = instruction.getMnemonicString();
        if (mnemonic.equalsIgnoreCase("mtctr")) {
            return true;
        }
        if (!mnemonic.equalsIgnoreCase("mtspr")) {
            return false;
        }
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Register &&
                    ((Register) object).getName().equalsIgnoreCase("CTR")) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean isBctrl(Instruction instruction) {
        return instruction.getMnemonicString().equalsIgnoreCase("bctrl");
    }

    private boolean hasControlFlow(Instruction instruction) {
        return instruction.getFlowType().isJump() || instruction.getFlowType().isCall()
            || instruction.getFlowType().isTerminal();
    }

    private long scalarDisplacement(Scalar scalar) {
        long unsigned = scalar.getUnsignedValue();
        long signed = scalar.getSignedValue();
        return signed > 0 ? signed : unsigned;
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

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }

    private static final class LoadCandidate {
        private final Register base;
        private final Register destination;
        private final long displacement;

        private LoadCandidate(Register base, Register destination, long displacement) {
            this.base = base;
            this.destination = destination;
            this.displacement = displacement;
        }
    }

    private static final class Match {
        private final Instruction mtctr;
        private final Instruction bctrl;

        private Match(Instruction mtctr, Instruction bctrl) {
            this.mtctr = mtctr;
            this.bctrl = bctrl;
        }
    }
}
