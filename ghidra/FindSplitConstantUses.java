// Ghidra post-script. Finds bounded PowerPC split-constant constructions.
// Environment:
//   REREVVED_TARGET_VAS   comma-separated exact 32-bit values, max 8
//   REREVVED_LOOKAHEAD    optional instruction limit, default 8
//   REREVVED_MAX_MATCHES  optional distinct-function cap, default 8
//   REREVVED_DUMP_PATH    output path
//@category ReRevved

import java.io.FileWriter;
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

public class FindSplitConstantUses extends GhidraScript {
    @Override
    public void run() throws Exception {
        Set<Long> targets = new LinkedHashSet<>(
            parseValues(requireEnv("REREVVED_TARGET_VAS"), 8));
        int lookahead = parseBound(System.getenv("REREVVED_LOOKAHEAD"), 8, 1, 32,
                                   "REREVVED_LOOKAHEAD");
        int maxMatches = parseBound(System.getenv("REREVVED_MAX_MATCHES"), 8, 1, 64,
                                    "REREVVED_MAX_MATCHES");
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Listing listing = currentProgram.getListing();
        BasicBlockModel blocks = new BasicBlockModel(currentProgram);
        Set<Long> matchedFunctions = new LinkedHashSet<>();
        boolean truncated = false;

        try (PrintWriter out = new PrintWriter(new FileWriter(outPath))) {
            out.println("Program: " + currentProgram.getName());
            out.println("Targets: " + formatValues(new ArrayList<>(targets)));
            out.println("Lookahead: " + lookahead);

            InstructionIterator instructions = listing.getInstructions(true);
            outer:
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction high = instructions.next();
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
                long highValue = lisValue(high);
                Instruction current = listing.getInstructionAfter(high.getAddress());
                for (int index = 0; current != null && index < lookahead; index++) {
                    if (!function.getBody().contains(current.getAddress()) ||
                        !block.contains(current.getAddress())) {
                        break;
                    }
                    LowPart low = splitLow(current, highRegister);
                    if (low != null) {
                        long value = (low.add ? highValue + low.value
                                              : highValue | low.value) & 0xFFFFFFFFL;
                        if (targets.contains(value)) {
                            long entry = function.getEntryPoint().getOffset();
                            if (!matchedFunctions.contains(entry)) {
                                if (matchedFunctions.size() >= maxMatches) {
                                    truncated = true;
                                    break outer;
                                }
                                matchedFunctions.add(entry);
                                out.printf("%n=== function 0x%08X %s value 0x%08X ===%n",
                                           entry, function.getName(), value);
                                out.printf("0x%08X: %s%n", high.getAddress().getOffset(), high);
                                out.printf("0x%08X: %s%n", current.getAddress().getOffset(),
                                           current);
                            }
                            break;
                        }
                    }
                    if (writesRegister(current, highRegister)) {
                        break;
                    }
                    current = listing.getInstructionAfter(current.getAddress());
                }
            }
            out.println("Matches: " + matchedFunctions.size());
            out.println("Truncated: " + truncated);
        }
        println("WROTE: " + outPath);
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

    private LowPart splitLow(Instruction instruction, Register highRegister) {
        String mnemonic = instruction.getMnemonicString();
        if ((!mnemonic.equalsIgnoreCase("addi") && !mnemonic.equalsIgnoreCase("ori")) ||
            !operandIsRegister(instruction, 1, highRegister)) {
            return null;
        }
        Scalar scalar = operandScalar(instruction, 2);
        if (scalar == null) {
            return null;
        }
        return mnemonic.equalsIgnoreCase("addi")
            ? new LowPart(scalar.getSignedValue(), true)
            : new LowPart(scalar.getUnsignedValue() & 0xFFFFL, false);
    }

    private boolean writesRegister(Instruction instruction, Register register) {
        for (Object object : instruction.getResultObjects()) {
            if (object instanceof Register &&
                ((Register) object).getName().equalsIgnoreCase(register.getName())) {
                return true;
            }
        }
        return false;
    }

    private boolean operandIsRegister(Instruction instruction, int operand,
                                      Register register) {
        Object[] objects = instruction.getOpObjects(operand);
        return objects.length == 1 && objects[0] instanceof Register &&
               ((Register) objects[0]).getName().equalsIgnoreCase(register.getName());
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

    private static final class LowPart {
        private final long value;
        private final boolean add;

        private LowPart(long value, boolean add) {
            this.value = value;
            this.add = add;
        }
    }
}
