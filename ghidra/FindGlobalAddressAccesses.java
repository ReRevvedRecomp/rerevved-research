// Ghidra post-script. Finds bounded decoded PowerPC global-address materializers.
// Environment:
//   REREVVED_TARGET_VAS   comma-separated exact 32-bit values, max 8
//   REREVVED_LOOKAHEAD    optional split-constant window, default 8
//   REREVVED_USE_WINDOW   optional first-use window, default 16
//   REREVVED_MAX_MATCHES  optional materializer cap, default 64
//   REREVVED_DUMP_PATH    output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.block.BasicBlockModel;
import ghidra.program.model.block.CodeBlock;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;

public class FindGlobalAddressAccesses extends GhidraScript {
    private static final int MAX_TARGETS = 8;
    private static final int DEFAULT_LOOKAHEAD = 8;
    private static final int DEFAULT_USE_WINDOW = 16;
    private static final int DEFAULT_MAX_MATCHES = 64;

    @Override
    public void run() throws Exception {
        Set<Long> targets = new LinkedHashSet<>(parseValues(
            requireEnv("REREVVED_TARGET_VAS"), MAX_TARGETS));
        int lookahead = parseBound(System.getenv("REREVVED_LOOKAHEAD"),
            DEFAULT_LOOKAHEAD, 1, 32, "REREVVED_LOOKAHEAD");
        int useWindow = parseBound(System.getenv("REREVVED_USE_WINDOW"),
            DEFAULT_USE_WINDOW, 1, 64, "REREVVED_USE_WINDOW");
        int maxMatches = parseBound(System.getenv("REREVVED_MAX_MATCHES"),
            DEFAULT_MAX_MATCHES, 1, 256, "REREVVED_MAX_MATCHES");
        String outPath = requireEnv("REREVVED_DUMP_PATH");

        Listing listing = currentProgram.getListing();
        BasicBlockModel blocks = new BasicBlockModel(currentProgram);
        int matches = 0;
        long scanned = 0;
        boolean truncated = false;

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            out.println("Targets: " + formatValues(targets));
            out.println("Split-constant lookahead: " + lookahead);
            out.println("First-use window: " + useWindow);
            out.println("Materializer cap: " + maxMatches);
            out.println("Decoded instructions only; undefined bytes are excluded.");

            InstructionIterator instructions = listing.getInstructions(true);
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction high = instructions.next();
                scanned++;
                Register highRegister = lisDestination(high);
                if (highRegister == null) {
                    continue;
                }
                Function function = currentProgram.getFunctionManager()
                    .getFunctionContaining(high.getAddress());
                CodeBlock block = blocks.getFirstCodeBlockContaining(high.getAddress(), monitor);
                if (function == null || block == null) {
                    continue;
                }

                Instruction current = listing.getInstructionAfter(high.getAddress());
                for (int distance = 1; current != null && distance <= lookahead; distance++) {
                    if (current.getAddress().getOffset() !=
                            high.getAddress().getOffset() + distance * 4 ||
                        !function.getBody().contains(current.getAddress()) ||
                        !block.contains(current.getAddress())) {
                        break;
                    }
                    SplitPart low = splitPart(current, highRegister);
                    if (low != null) {
                        long value = (low.add ? lisValue(high) + low.value
                                              : lisValue(high) | low.value) & 0xFFFFFFFFL;
                        if (targets.contains(value)) {
                            if (matches >= maxMatches) {
                                truncated = true;
                                break;
                            }
                            FunctionUse use = findFirstUse(function, current, low.destination,
                                useWindow);
                            writeMatch(out, matches + 1, value, function, high, current,
                                low.destination, use);
                            matches++;
                            if (use.cancelled) {
                                break;
                            }
                        }
                    }
                    if (writesRegister(current, highRegister) || hasControlFlow(current)) {
                        break;
                    }
                    current = listing.getInstructionAfter(current.getAddress());
                }
                if (truncated || monitor.isCancelled()) {
                    break;
                }
            }

            out.println();
            out.println("Decoded instructions scanned: " + scanned);
            out.println("Materializers emitted: " + matches);
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private void writeMatch(PrintWriter out, int ordinal, long value, Function function,
                            Instruction high, Instruction low, Register materializedRegister,
                            FunctionUse use) {
        out.printf("%n=== materializer %d ===%n", ordinal);
        out.printf("Target: 0x%08X%n", value);
        out.printf("Function: 0x%08X %s%n", function.getEntryPoint().getOffset(),
            function.getName());
        out.printf("Materializer high: 0x%08X %s%n",
            high.getAddress().getOffset(), high);
        out.printf("Materializer low: 0x%08X %s%n",
            low.getAddress().getOffset(), low);
        out.println("Materialized register: " + materializedRegister.getName());
        if (use.instruction == null) {
            out.println("First relevant use: <none within window>");
            out.println("Use status: " + (use.cancelled ? "CANCELLED" : "EXHAUSTED"));
        } else {
            out.printf("First relevant use: 0x%08X %s %s%n",
                use.instruction.getAddress().getOffset(), use.kind, use.instruction);
            out.println("Use register: " + use.register);
            out.println("Use status: FOUND");
        }
    }

    private FunctionUse findFirstUse(Function function, Instruction low, Register destination,
                                     int useWindow) {
        Set<String> live = new LinkedHashSet<>();
        live.add(normalize(destination));
        Instruction current = low;
        for (int distance = 1; distance <= useWindow; distance++) {
            if (monitor.isCancelled()) {
                return FunctionUse.cancelled();
            }
            Instruction next = currentProgram.getListing()
                .getInstructionAfter(current.getAddress());
            if (next == null || next.getAddress().getOffset() !=
                    current.getAddress().getOffset() + 4 ||
                !function.getBody().contains(next.getAddress()) ||
                currentProgram.getFunctionManager().getFunctionContaining(next.getAddress())
                    != function) {
                return FunctionUse.exhausted();
            }

            String direct = relevantMemoryUse(next, live);
            if (direct != null) {
                return FunctionUse.found(direct, next, firstLive(live));
            }
            String parameter = parameterUse(next, live);
            if (parameter != null) {
                return FunctionUse.found("PARAMETER", next, parameter);
            }

            Register copySource = copySource(next, live);
            Register result = resultRegister(next);
            for (String register : new ArrayList<>(live)) {
                if (writesRegister(next, register)) {
                    live.remove(register);
                }
            }
            if (copySource != null && result != null) {
                live.add(normalize(result));
            }
            if (live.isEmpty() || hasControlFlow(next)) {
                return FunctionUse.exhausted();
            }
            current = next;
        }
        return FunctionUse.exhausted();
    }

    private String relevantMemoryUse(Instruction instruction, Set<String> live) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        boolean load = mnemonic.startsWith("l");
        boolean store = mnemonic.startsWith("s");
        if (!load && !store) {
            return null;
        }
        boolean hasMemoryOperand = false;
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            boolean hasRegister = false;
            boolean hasScalar = false;
            for (Object object : instruction.getOpObjects(operand)) {
                hasRegister |= object instanceof Register;
                hasScalar |= object instanceof Scalar;
            }
            if (hasRegister && hasScalar) {
                hasMemoryOperand = true;
                break;
            }
        }
        if (!hasMemoryOperand) {
            return null;
        }
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Register && live.contains(normalize((Register) object))) {
                    return store ? "STORE" : "LOAD";
                }
            }
        }
        return null;
    }

    private String parameterUse(Instruction instruction, Set<String> live) {
        if (!instruction.getFlowType().isCall()) {
            return null;
        }
        for (String register : live) {
            if (isParameterRegister(register)) {
                return register;
            }
        }
        return null;
    }

    private Register copySource(Instruction instruction, Set<String> live) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        if (!mnemonic.equals("mr") && !mnemonic.equals("or") &&
            !mnemonic.equals("addi") && !mnemonic.equals("subi")) {
            return null;
        }
        if ((mnemonic.equals("addi") || mnemonic.equals("subi")) &&
            !hasZeroImmediate(instruction)) {
            return null;
        }
        Register source = null;
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (!(object instanceof Register)) {
                    continue;
                }
                Register candidate = (Register) object;
                if (live.contains(normalize(candidate))) {
                    if (source != null && !sameRegister(source, candidate)) {
                        return null;
                    }
                    source = candidate;
                }
            }
        }
        return source;
    }

    private boolean hasZeroImmediate(Instruction instruction) {
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Scalar &&
                    (((Scalar) object).getUnsignedValue() & 0xFFFFFFFFL) == 0) {
                    return true;
                }
            }
        }
        return false;
    }

    private Register lisDestination(Instruction instruction) {
        if (!instruction.getMnemonicString().equalsIgnoreCase("lis")) {
            return null;
        }
        Object[] objects = instruction.getOpObjects(0);
        return objects.length == 1 && objects[0] instanceof Register
            ? (Register) objects[0] : null;
    }

    private long lisValue(Instruction instruction) {
        Scalar scalar = operandScalar(instruction, 1);
        return (scalar.getUnsignedValue() & 0xFFFFL) << 16;
    }

    private SplitPart splitPart(Instruction instruction, Register highRegister) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        if (!mnemonic.equals("addi") && !mnemonic.equals("subi") &&
            !mnemonic.equals("ori")) {
            return null;
        }
        if (!operandIsRegister(instruction, 1, highRegister)) {
            return null;
        }
        Scalar scalar = operandScalar(instruction, 2);
        Register destination = resultRegister(instruction);
        if (scalar == null || destination == null) {
            return null;
        }
        if (mnemonic.equals("ori")) {
            return new SplitPart(destination, scalar.getUnsignedValue() & 0xFFFFL, false);
        }
        long immediate = scalar.getSignedValue();
        if (mnemonic.equals("subi")) {
            immediate = -immediate;
        }
        return new SplitPart(destination, immediate, true);
    }

    private Register resultRegister(Instruction instruction) {
        Register result = null;
        for (Object object : instruction.getResultObjects()) {
            if (!(object instanceof Register)) {
                continue;
            }
            Register candidate = (Register) object;
            if (!isGeneralRegister(candidate)) {
                continue;
            }
            if (result != null) {
                return null;
            }
            result = candidate;
        }
        return result;
    }

    private boolean writesRegister(Instruction instruction, Register expected) {
        return writesRegister(instruction, normalize(expected));
    }

    private boolean writesRegister(Instruction instruction, String expected) {
        for (Object object : instruction.getResultObjects()) {
            if (object instanceof Register && normalize((Register) object).equals(expected)) {
                return true;
            }
        }
        return false;
    }

    private boolean operandIsRegister(Instruction instruction, int operand,
                                      Register register) {
        Object[] objects = instruction.getOpObjects(operand);
        return objects.length == 1 && objects[0] instanceof Register &&
               sameRegister((Register) objects[0], register);
    }

    private Scalar operandScalar(Instruction instruction, int operand) {
        Object[] objects = instruction.getOpObjects(operand);
        return objects.length == 1 && objects[0] instanceof Scalar
            ? (Scalar) objects[0] : null;
    }

    private boolean hasControlFlow(Instruction instruction) {
        return instruction.getFlowType().isJump() || instruction.getFlowType().isCall()
            || instruction.getFlowType().isTerminal();
    }

    private boolean isGeneralRegister(Register register) {
        String name = normalize(register);
        if (name.length() < 2 || name.charAt(0) != 'R') {
            return false;
        }
        for (int index = 1; index < name.length(); index++) {
            if (!Character.isDigit(name.charAt(index))) {
                return false;
            }
        }
        return true;
    }

    private boolean isParameterRegister(String register) {
        if (!register.startsWith("R")) {
            return false;
        }
        try {
            int number = Integer.parseInt(register.substring(1));
            return number >= 3 && number <= 10;
        } catch (NumberFormatException exception) {
            return false;
        }
    }

    private String normalize(Register register) {
        return register.getName().toUpperCase();
    }

    private boolean sameRegister(Register first, Register second) {
        return normalize(first).equals(normalize(second));
    }

    private String firstLive(Set<String> live) {
        return live.isEmpty() ? "<unknown>" : live.iterator().next();
    }

    private List<Long> parseValues(String raw, int maximum) {
        List<Long> values = new ArrayList<>();
        for (String token : raw.split(",")) {
            if (!token.isBlank()) {
                long value = Long.decode(token.trim());
                if (value < 0 || value > 0xFFFFFFFFL) {
                    throw new IllegalArgumentException("target must be a 32-bit unsigned value");
                }
                values.add(value);
            }
        }
        if (values.isEmpty() || values.size() > maximum) {
            throw new IllegalArgumentException("target list must contain 1 through " + maximum);
        }
        return values;
    }

    private int parseBound(String raw, int defaultValue, int minimum, int maximum,
                           String name) {
        int value = raw == null || raw.isBlank() ? defaultValue : Integer.parseInt(raw.trim());
        if (value < minimum || value > maximum) {
            throw new IllegalArgumentException(name + " must be " + minimum + " through " + maximum);
        }
        return value;
    }

    private String formatValues(Set<Long> values) {
        List<String> formatted = new ArrayList<>();
        for (long value : values) {
            formatted.add(String.format("0x%08X", value));
        }
        return String.join(",", formatted);
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }

    private static final class SplitPart {
        private final Register destination;
        private final long value;
        private final boolean add;

        private SplitPart(Register destination, long value, boolean add) {
            this.destination = destination;
            this.value = value;
            this.add = add;
        }
    }

    private static final class FunctionUse {
        private final String kind;
        private final Instruction instruction;
        private final String register;
        private final boolean cancelled;

        private FunctionUse(String kind, Instruction instruction, String register,
                             boolean cancelled) {
            this.kind = kind;
            this.instruction = instruction;
            this.register = register;
            this.cancelled = cancelled;
        }

        private static FunctionUse found(String kind, Instruction instruction, String register) {
            return new FunctionUse(kind, instruction, register, false);
        }

        private static FunctionUse exhausted() {
            return new FunctionUse(null, null, null, false);
        }

        private static FunctionUse cancelled() {
            return new FunctionUse(null, null, null, true);
        }
    }
}
