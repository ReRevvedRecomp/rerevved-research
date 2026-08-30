// Ghidra post-script. Finds bounded decoded instruction uses of exact scalar values.
// Environment:
//   REREVVED_SCALAR_VALUES  comma-separated exact values, max 8
//   REREVVED_MNEMONICS      optional comma-separated mnemonic allowlist
//   REREVVED_MAX_FUNCTIONS  optional distinct-function cap, default 8
//   REREVVED_DUMP_PATH      output path
//@category ReRevved

import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class FindScalarUses extends GhidraScript {
    @Override
    public void run() throws Exception {
        Set<Long> values = parseValues(requireEnv("REREVVED_SCALAR_VALUES"));
        Set<String> mnemonics = parseMnemonics(System.getenv("REREVVED_MNEMONICS"));
        int maxFunctions = parseLimit(System.getenv("REREVVED_MAX_FUNCTIONS"));
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        Set<Long> matchedFunctions = new LinkedHashSet<>();
        int matchedInstructions = 0;
        boolean truncated = false;

        try (PrintWriter out = new PrintWriter(new FileWriter(outPath))) {
            out.println("Program: " + currentProgram.getName());
            out.println("Values: " + formatValues(values));
            out.println("Mnemonics: " + (mnemonics.isEmpty() ? "<all>" : String.join(",", mnemonics)));
            out.println("Function cap: " + maxFunctions);

            InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction instruction = instructions.next();
                if (!mnemonics.isEmpty() &&
                    !mnemonics.contains(instruction.getMnemonicString().toLowerCase())) {
                    continue;
                }
                Long matchedValue = matchingValue(instruction, values);
                if (matchedValue == null) {
                    continue;
                }
                Function function = currentProgram.getFunctionManager()
                    .getFunctionContaining(instruction.getAddress());
                if (function == null) {
                    continue;
                }
                long entry = function.getEntryPoint().getOffset();
                if (!matchedFunctions.contains(entry) && matchedFunctions.size() >= maxFunctions) {
                    truncated = true;
                    break;
                }
                if (matchedFunctions.add(entry)) {
                    out.printf("%n=== function 0x%08X %s ===%n", entry, function.getName());
                }
                out.printf("0x%08X value=0x%08X %s%n",
                    instruction.getAddress().getOffset(), matchedValue, instruction);
                matchedInstructions++;
            }
            out.println("Functions: " + matchedFunctions.size());
            out.println("Instructions: " + matchedInstructions);
            out.println("Truncated: " + truncated);
        }
        println("WROTE: " + outPath);
    }

    private Long matchingValue(Instruction instruction, Set<Long> values) {
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (!(object instanceof Scalar)) {
                    continue;
                }
                Scalar scalar = (Scalar) object;
                long unsigned = scalar.getUnsignedValue() & 0xFFFFFFFFL;
                long signed = scalar.getSignedValue() & 0xFFFFFFFFL;
                if (values.contains(unsigned)) {
                    return unsigned;
                }
                if (values.contains(signed)) {
                    return signed;
                }
            }
        }
        return null;
    }

    private Set<Long> parseValues(String raw) {
        Set<Long> values = new LinkedHashSet<>();
        for (String token : raw.split(",")) {
            if (!token.isBlank()) {
                values.add(Long.decode(token.trim()) & 0xFFFFFFFFL);
            }
        }
        if (values.isEmpty() || values.size() > 8) {
            throw new IllegalArgumentException("REREVVED_SCALAR_VALUES must contain 1 through 8 values");
        }
        return values;
    }

    private Set<String> parseMnemonics(String raw) {
        Set<String> values = new LinkedHashSet<>();
        if (raw == null || raw.isBlank()) {
            return values;
        }
        for (String token : raw.split(",")) {
            String value = token.trim().toLowerCase();
            if (!value.isEmpty()) {
                values.add(value);
            }
        }
        if (values.size() > 16) {
            throw new IllegalArgumentException("REREVVED_MNEMONICS accepts at most 16 values");
        }
        return values;
    }

    private int parseLimit(String raw) {
        int value = raw == null || raw.isBlank() ? 8 : Integer.parseInt(raw);
        if (value < 1 || value > 64) {
            throw new IllegalArgumentException("REREVVED_MAX_FUNCTIONS must be 1 through 64");
        }
        return value;
    }

    private String formatValues(Set<Long> values) {
        StringBuilder builder = new StringBuilder();
        for (long value : values) {
            if (builder.length() > 0) {
                builder.append(',');
            }
            builder.append(String.format("0x%08X", value));
        }
        return builder.toString();
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }
}
