// Ghidra post-script. Finds direct calls with a nearby 32-bit constant argument.
// Environment:
//   REREVVED_TARGET_VAS       comma-separated direct call target guest VAs, max 8
//   REREVVED_ARGUMENT_REG     argument register name, for example r4
//   REREVVED_ARGUMENT_VALUES  comma-separated constants, max 8
//   REREVVED_LOOKBACK         optional instruction limit, default 32
//   REREVVED_MAX_MATCHES      optional result cap, default 8
//   REREVVED_DUMP_PATH        output path
//@category ReRevved

import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.block.BasicBlockModel;
import ghidra.program.model.block.CodeBlock;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class FindCallSplitConstantArgs extends GhidraScript {
    @Override
    public void run() throws Exception {
        List<Long> targets = parseValues(requireEnv("REREVVED_TARGET_VAS"), 8);
        Set<Long> expectedValues = new LinkedHashSet<>(
            parseValues(requireEnv("REREVVED_ARGUMENT_VALUES"), 8));
        String registerName = requireEnv("REREVVED_ARGUMENT_REG");
        int lookback = parseBound(System.getenv("REREVVED_LOOKBACK"), 32, 1, 64,
                                  "REREVVED_LOOKBACK");
        int maxMatches = parseBound(System.getenv("REREVVED_MAX_MATCHES"), 8, 1, 64,
                                    "REREVVED_MAX_MATCHES");
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Listing listing = currentProgram.getListing();
        BasicBlockModel blocks = new BasicBlockModel(currentProgram);
        int matches = 0;
        boolean truncated = false;

        try (PrintWriter out = new PrintWriter(new FileWriter(outPath))) {
            out.println("Program: " + currentProgram.getName());
            out.println("Targets: " + formatValues(targets));
            out.println("Argument: " + registerName);
            out.println("Values: " + formatValues(new ArrayList<>(expectedValues)));
            outer:
            for (long targetValue : targets) {
                Address target = space.getAddress(targetValue);
                ReferenceIterator references =
                    currentProgram.getReferenceManager().getReferencesTo(target);
                while (references.hasNext()) {
                    Reference reference = references.next();
                    if (!reference.getReferenceType().isCall()) {
                        continue;
                    }
                    Instruction call = listing.getInstructionAt(reference.getFromAddress());
                    Match match = findNearestConstant(listing, blocks, call, registerName,
                                                      lookback);
                    if (match == null || !expectedValues.contains(match.value)) {
                        continue;
                    }
                    if (matches >= maxMatches) {
                        truncated = true;
                        break outer;
                    }
                    out.printf("%n=== call 0x%08X target 0x%08X value 0x%08X ===%n",
                               call.getAddress().getOffset(), targetValue, match.value);
                    for (Instruction instruction : match.window) {
                        out.printf("0x%08X: %s%n", instruction.getAddress().getOffset(),
                                   instruction);
                    }
                    matches++;
                }
            }
            out.println("Matches: " + matches);
            out.println("Truncated: " + truncated);
        }
        println("WROTE: " + outPath);
    }

    private Match findNearestConstant(Listing listing, BasicBlockModel blocks,
                                      Instruction call, String registerName,
                                      int lookback) throws Exception {
        Function function = currentProgram.getFunctionManager()
            .getFunctionContaining(call.getAddress());
        CodeBlock block = blocks.getFirstCodeBlockContaining(call.getAddress(), monitor);
        if (function == null || block == null) {
            return null;
        }
        List<Instruction> reverseWindow = new ArrayList<>();
        Instruction current = listing.getInstructionBefore(call.getAddress());
        for (int index = 0; current != null && index < lookback; index++) {
            if (!function.getBody().contains(current.getAddress()) ||
                !block.contains(current.getAddress())) {
                return null;
            }
            reverseWindow.add(current);
            if (!writesRegister(current, registerName)) {
                current = listing.getInstructionBefore(current.getAddress());
                continue;
            }
            Long immediate = directImmediate(current, registerName);
            if (immediate != null) {
                return makeMatch(reverseWindow, call, immediate);
            }
            SplitLow low = splitLow(current, registerName);
            if (low == null) {
                return null;
            }
            Instruction high = listing.getInstructionBefore(current.getAddress());
            for (int highIndex = index + 1;
                 high != null && highIndex < lookback; highIndex++) {
                if (!function.getBody().contains(high.getAddress()) ||
                    !block.contains(high.getAddress())) {
                    return null;
                }
                reverseWindow.add(high);
                if (writesRegister(high, registerName)) {
                    Long highValue = splitHigh(high, registerName);
                    if (highValue == null) {
                        return null;
                    }
                    long value = low.add ? highValue + low.value
                                         : highValue | low.value;
                    return makeMatch(reverseWindow, call, value);
                }
                high = listing.getInstructionBefore(high.getAddress());
            }
            return null;
        }
        return null;
    }

    private Match makeMatch(List<Instruction> reverseWindow, Instruction call, long value) {
        Collections.reverse(reverseWindow);
        reverseWindow.add(call);
        return new Match(reverseWindow, value & 0xFFFFFFFFL);
    }

    private boolean writesRegister(Instruction instruction, String registerName) {
        for (Object object : instruction.getResultObjects()) {
            if (object instanceof Register &&
                ((Register) object).getName().equalsIgnoreCase(registerName)) {
                return true;
            }
        }
        return false;
    }

    private Long directImmediate(Instruction instruction, String registerName) {
        if (!instruction.getMnemonicString().equalsIgnoreCase("li") ||
            !operandIsRegister(instruction, 0, registerName)) {
            return null;
        }
        Scalar scalar = operandScalar(instruction, 1);
        return scalar == null ? null : scalar.getSignedValue() & 0xFFFFFFFFL;
    }

    private SplitLow splitLow(Instruction instruction, String registerName) {
        String mnemonic = instruction.getMnemonicString();
        if ((!mnemonic.equalsIgnoreCase("ori") && !mnemonic.equalsIgnoreCase("addi")) ||
            !operandIsRegister(instruction, 0, registerName) ||
            !operandIsRegister(instruction, 1, registerName)) {
            return null;
        }
        Scalar scalar = operandScalar(instruction, 2);
        if (scalar == null) {
            return null;
        }
        return mnemonic.equalsIgnoreCase("addi")
            ? new SplitLow(scalar.getSignedValue(), true)
            : new SplitLow(scalar.getUnsignedValue() & 0xFFFFL, false);
    }

    private Long splitHigh(Instruction instruction, String registerName) {
        if (!instruction.getMnemonicString().equalsIgnoreCase("lis") ||
            !operandIsRegister(instruction, 0, registerName)) {
            return null;
        }
        Scalar scalar = operandScalar(instruction, 1);
        return scalar == null ? null : (scalar.getUnsignedValue() & 0xFFFFL) << 16;
    }

    private boolean operandIsRegister(Instruction instruction, int operand,
                                      String registerName) {
        Object[] objects = instruction.getOpObjects(operand);
        return objects.length == 1 && objects[0] instanceof Register &&
               ((Register) objects[0]).getName().equalsIgnoreCase(registerName);
    }

    private Scalar operandScalar(Instruction instruction, int operand) {
        Object[] objects = instruction.getOpObjects(operand);
        return objects.length == 1 && objects[0] instanceof Scalar
            ? (Scalar) objects[0] : null;
    }

    private List<Long> parseValues(String raw, int maximum) {
        List<Long> values = new ArrayList<>();
        for (String token : raw.split(",")) {
            if (!token.isBlank()) {
                values.add(Long.decode(token.trim()) & 0xFFFFFFFFL);
            }
        }
        if (values.isEmpty() || values.size() > maximum) {
            throw new IllegalArgumentException("value list must contain 1 through " + maximum);
        }
        return values;
    }

    private int parseBound(String raw, int defaultValue, int minimum, int maximum,
                           String name) {
        int value = raw == null || raw.isBlank() ? defaultValue : Integer.parseInt(raw);
        if (value < minimum || value > maximum) {
            throw new IllegalArgumentException(name + " must be " + minimum + " through " +
                                               maximum);
        }
        return value;
    }

    private String formatValues(List<Long> values) {
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

    private static final class Match {
        private final List<Instruction> window;
        private final long value;

        private Match(List<Instruction> window, long value) {
            this.window = window;
            this.value = value;
        }
    }

    private static final class SplitLow {
        private final long value;
        private final boolean add;

        private SplitLow(long value, boolean add) {
            this.value = value;
            this.add = add;
        }
    }
}
