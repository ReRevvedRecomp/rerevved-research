// Ghidra post-script. Records bounded canonical-image observations as private scratch.
// Environment:
//   REREVVED_CANONICAL_OBSERVATIONS_OUT  private JSON output path
//@category ReRevved

import java.io.BufferedInputStream;
import java.io.BufferedWriter;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.scalar.Scalar;

public class ObserveCanonicalImageEvidence extends GhidraScript {
    private static final long FUNCTION_ENTRY = 0x821B3BB8L;
    private static final long FIELD_VALUE_SITE = 0x821B3BE8L;
    private static final long FIELD_STORE_SITE = 0x821B3BF4L;
    private static final long VTABLE_HIGH_SITE = 0x821B3BE0L;
    private static final long VTABLE_LOW_SITE = 0x821B3BECL;
    private static final long VTABLE_STORE_SITE = 0x821B3BF8L;

    @Override
    public void run() throws Exception {
        String output = requireEnv("REREVVED_CANONICAL_OBSERVATIONS_OUT");
        Path source = executablePath(currentProgram.getExecutablePath());
        long sourceSize = Files.size(source);
        String sourceSha256 = sha256(source);

        Address entry = toAddr(FUNCTION_ENTRY);
        Function function = currentProgram.getFunctionManager().getFunctionAt(entry);
        Instruction entryInstruction = requireInstruction(FUNCTION_ENTRY);

        Instruction fieldValue = requireInstruction(FIELD_VALUE_SITE);
        Instruction fieldStore = requireInstruction(FIELD_STORE_SITE);
        long fieldImmediate = scalar(fieldValue, 1).getSignedValue();

        Instruction vtableHigh = requireInstruction(VTABLE_HIGH_SITE);
        Instruction vtableLow = requireInstruction(VTABLE_LOW_SITE);
        Instruction vtableStore = requireInstruction(VTABLE_STORE_SITE);
        long high = scalar(vtableHigh, 1).getUnsignedValue() & 0xFFFFL;
        long low = scalar(vtableLow, 2).getSignedValue();
        long vtableAddress = ((high << 16) + low) & 0xFFFFFFFFL;

        String document = String.format(
            "{\n" +
            "  \"schemaVersion\": 1,\n" +
            "  \"program\": {\n" +
            "    \"name\": %s,\n" +
            "    \"imageBase\": %s,\n" +
            "    \"imageSize\": %d,\n" +
            "    \"processor\": %s,\n" +
            "    \"sourceSize\": %d,\n" +
            "    \"sourceSha256\": %s\n" +
            "  },\n" +
            "  \"function\": {\n" +
            "    \"id\": \"RVA-SYM-0223\",\n" +
            "    \"address\": \"0x821B3BB8\",\n" +
            "    \"present\": %s,\n" +
            "    \"entryMnemonic\": %s\n" +
            "  },\n" +
            "  \"fieldAccess\": {\n" +
            "    \"fieldId\": \"RVA-FLD-0121\",\n" +
            "    \"relationId\": \"RVA-REL-0290\",\n" +
            "    \"constantAddress\": \"0x821B3BE8\",\n" +
            "    \"constantMnemonic\": %s,\n" +
            "    \"constantRegister\": %s,\n" +
            "    \"value\": %d,\n" +
            "    \"storeAddress\": \"0x821B3BF4\",\n" +
            "    \"storeMnemonic\": %s,\n" +
            "    \"sourceRegister\": %s,\n" +
            "    \"baseRegister\": %s,\n" +
            "    \"offset\": %d\n" +
            "  },\n" +
            "  \"relation\": {\n" +
            "    \"id\": \"RVA-REL-0293\",\n" +
            "    \"from\": \"RVA-SYM-0223\",\n" +
            "    \"to\": \"RVA-VTBL-0025\",\n" +
            "    \"highAddress\": \"0x821B3BE0\",\n" +
            "    \"highMnemonic\": %s,\n" +
            "    \"highRegister\": %s,\n" +
            "    \"lowAddress\": \"0x821B3BEC\",\n" +
            "    \"lowMnemonic\": %s,\n" +
            "    \"lowTargetRegister\": %s,\n" +
            "    \"lowBaseRegister\": %s,\n" +
            "    \"storeAddress\": \"0x821B3BF8\",\n" +
            "    \"storeMnemonic\": %s,\n" +
            "    \"sourceRegister\": %s,\n" +
            "    \"baseRegister\": %s,\n" +
            "    \"offset\": %d,\n" +
            "    \"valueAddress\": %s\n" +
            "  }\n" +
            "}\n",
            json(currentProgram.getName()),
            json(address(currentProgram.getMemory().getMinAddress().getOffset())),
            currentProgram.getMemory().getSize(),
            json(currentProgram.getLanguageID().getIdAsString()),
            sourceSize,
            json(sourceSha256),
            function != null,
            json(entryInstruction.getMnemonicString()),
            json(fieldValue.getMnemonicString()),
            json(register(fieldValue, 0).getName()),
            fieldImmediate,
            json(fieldStore.getMnemonicString()),
            json(register(fieldStore, 0).getName()),
            json(register(fieldStore, 1).getName()),
            scalar(fieldStore, 1).getSignedValue(),
            json(vtableHigh.getMnemonicString()),
            json(register(vtableHigh, 0).getName()),
            json(vtableLow.getMnemonicString()),
            json(register(vtableLow, 0).getName()),
            json(register(vtableLow, 1).getName()),
            json(vtableStore.getMnemonicString()),
            json(register(vtableStore, 0).getName()),
            json(register(vtableStore, 1).getName()),
            scalar(vtableStore, 1).getSignedValue(),
            json(address(vtableAddress))
        );

        Path destination = Paths.get(output);
        try (BufferedWriter writer = Files.newBufferedWriter(
                destination, StandardCharsets.US_ASCII)) {
            writer.write(document);
        }
        println("WROTE canonical-image observations");
    }

    private Instruction requireInstruction(long value) {
        Instruction instruction = getInstructionAt(toAddr(value));
        if (instruction == null) {
            throw new IllegalStateException("Required observation site is not decoded");
        }
        return instruction;
    }

    private Register register(Instruction instruction, int operand) {
        for (Object value : instruction.getOpObjects(operand)) {
            if (value instanceof Register) return (Register) value;
        }
        throw new IllegalStateException("Required register operand is unavailable");
    }

    private Scalar scalar(Instruction instruction, int operand) {
        for (Object value : instruction.getOpObjects(operand)) {
            if (value instanceof Scalar) return (Scalar) value;
        }
        throw new IllegalStateException("Required scalar operand is unavailable");
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " is required");
        }
        return value;
    }

    private Path executablePath(String value) {
        if (value.matches("^/[A-Za-z]:/.*")) value = value.substring(1);
        return Paths.get(value);
    }

    private String sha256(Path path) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (InputStream input = new BufferedInputStream(Files.newInputStream(path))) {
            byte[] buffer = new byte[64 * 1024];
            int count;
            while ((count = input.read(buffer)) >= 0) digest.update(buffer, 0, count);
        }
        StringBuilder value = new StringBuilder();
        for (byte item : digest.digest()) value.append(String.format("%02X", item & 0xFF));
        return value.toString();
    }

    private String address(long value) {
        return String.format("0x%08X", value & 0xFFFFFFFFL);
    }

    private String json(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }
}
