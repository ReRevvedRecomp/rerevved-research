// Ghidra post-script. Finds decoded PowerPC vtable calls across bounded CFG paths.
// Environment:
//   REREVVED_VTABLE_SLOT_DISPLACEMENTS  comma-separated positive 16-bit displacements, max 8
//   REREVVED_MAX_CALLSITES              optional result cap, default 64
//   REREVVED_DUMP_PATH                  output path
//@category ReRevved

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class FindVtableSlotCallsCfg extends GhidraScript {
    private static final int MAX_PATH_INSTRUCTIONS = 16;
    private static final int MAX_BRANCH_EDGES = 2;
    private static final int MAX_STATES_PER_LOAD = 256;

    @Override
    public void run() throws Exception {
        Set<Long> displacements = parseDisplacements(
            requireEnv("REREVVED_VTABLE_SLOT_DISPLACEMENTS"));
        int maxCallsites = parseMaxCallsites(System.getenv("REREVVED_MAX_CALLSITES"));
        String outPath = requireEnv("REREVVED_DUMP_PATH");
        int callsites = 0;
        long scanned = 0;
        long loadCandidates = 0;
        long exploredStates = 0;
        long stateCaps = 0;
        Set<Long> straightLineCallsites = new LinkedHashSet<>();
        boolean truncated = false;

        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        try (out) {
            out.println("Program: " + currentProgram.getName());
            out.println("Slot displacements: " + formatDisplacements(displacements));
            out.println("Callsite cap: " + maxCallsites);
            out.println("CFG path limit: " + MAX_PATH_INSTRUCTIONS + " instructions");
            out.println("Branch-edge limit: " + MAX_BRANCH_EDGES);
            out.println("State limit per load: " + MAX_STATES_PER_LOAD);
            out.println("Alias copies: exact register copies only");

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
                SearchResult result = findCallsites(function, load, candidate.destination);
                exploredStates += result.exploredStates;
                straightLineCallsites.addAll(result.straightLineCallsites);
                if (result.stateCapHit) {
                    stateCaps++;
                }
                for (Match match : result.matches) {
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
                    out.println("Branch edges: " + match.branchEdges);
                    out.println("Alias copies: " + match.aliasCopies);
                    out.println("Path: " + formatPath(match.path));
                    callsites++;
                }
                if (truncated) {
                    break;
                }
            }
            out.println();
            out.println("Scanned instructions: " + scanned);
            out.println("Decoded slot-load candidates: " + loadCandidates);
            out.println("Explored path states: " + exploredStates);
            out.println("Loads reaching state cap: " + stateCaps);
            List<Long> sortedControls = new ArrayList<>(straightLineCallsites);
            Collections.sort(sortedControls);
            StringBuilder controlText = new StringBuilder();
            for (long address : sortedControls) {
                if (controlText.length() > 0) {
                    controlText.append(',');
                }
                controlText.append(String.format("0x%08X", address));
            }
            out.println("Recognized straight-line callsites: "
                + straightLineCallsites.size());
            out.println("Straight-line controls: " + controlText);
            out.println("Total: " + callsites);
            out.println("Truncated: " + truncated);
            out.println("Cancelled: " + monitor.isCancelled());
        }
        if (out.checkError()) {
            throw new IOException("failed while writing output: " + outPath);
        }
        println("WROTE: " + outPath);
    }

    private SearchResult findCallsites(
            Function function, Instruction load, Register destination) {
        SearchResult result = new SearchResult();
        Instruction first = instructionAt(load.getFallThrough(), function);
        if (first == null) {
            return result;
        }
        Set<String> initialAliases = new LinkedHashSet<>();
        initialAliases.add(registerName(destination));
        Deque<PathState> pending = new ArrayDeque<>();
        pending.add(new PathState(first, initialAliases, false, null, 0, 0, 1,
            List.of(load.getAddress())));
        Set<String> visited = new HashSet<>();
        Set<Long> recognizedCallsites = new HashSet<>();

        while (!pending.isEmpty() && !monitor.isCancelled()) {
            if (result.exploredStates >= MAX_STATES_PER_LOAD) {
                result.stateCapHit = true;
                break;
            }
            PathState state = pending.removeFirst();
            if (state.distance > MAX_PATH_INSTRUCTIONS) {
                continue;
            }
            String stateKey = stateKey(state);
            if (!visited.add(stateKey)) {
                continue;
            }
            result.exploredStates++;

            Instruction instruction = state.instruction;
            List<Address> path = new ArrayList<>(state.path);
            path.add(instruction.getAddress());
            if (isBctrl(instruction)) {
                if (state.ctrLive
                    && recognizedCallsites.add(instruction.getAddress().getOffset())) {
                    if (state.branchEdges == 0 && state.aliasCopies == 0) {
                        result.straightLineCallsites.add(
                            instruction.getAddress().getOffset());
                    } else {
                        result.matches.add(new Match(state.mtctr, instruction,
                            state.branchEdges, state.aliasCopies, path));
                    }
                }
                continue;
            }
            if (instruction.getFlowType().isCall()
                || instruction.getFlowType().isTerminal()) {
                continue;
            }

            Set<String> aliases = new LinkedHashSet<>(state.aliases);
            int aliasCopies = updateAliases(instruction, aliases, state.aliasCopies);
            boolean ctrLive = state.ctrLive;
            Instruction mtctr = state.mtctr;
            if (isMtctr(instruction)) {
                Register source = mtctrSource(instruction);
                ctrLive = source != null && aliases.contains(registerName(source));
                mtctr = ctrLive ? instruction : null;
            } else if (writesCtr(instruction)) {
                ctrLive = false;
                mtctr = null;
            }

            boolean branch = instruction.getFlowType().isJump();
            int branchEdges = state.branchEdges + (branch ? 1 : 0);
            if (branchEdges > MAX_BRANCH_EDGES) {
                continue;
            }
            for (Instruction successor : successors(function, instruction, branch)) {
                pending.addLast(new PathState(successor, aliases, ctrLive, mtctr,
                    branchEdges, aliasCopies, state.distance + 1, path));
            }
        }
        return result;
    }

    private List<Instruction> successors(
            Function function, Instruction instruction, boolean branch) {
        LinkedHashSet<Address> addresses = new LinkedHashSet<>();
        Address fallThrough = instruction.getFallThrough();
        if (fallThrough != null) {
            addresses.add(fallThrough);
        }
        if (branch) {
            for (Address flow : instruction.getFlows()) {
                addresses.add(flow);
            }
        }
        List<Instruction> result = new ArrayList<>();
        for (Address address : addresses) {
            Instruction successor = instructionAt(address, function);
            if (successor != null) {
                result.add(successor);
            }
        }
        return result;
    }

    private Instruction instructionAt(Address address, Function function) {
        if (address == null || !function.getBody().contains(address)) {
            return null;
        }
        return currentProgram.getListing().getInstructionAt(address);
    }

    private int updateAliases(
            Instruction instruction, Set<String> aliases, int aliasCopies) {
        Copy copy = exactCopy(instruction);
        boolean sourceLive = copy != null && aliases.contains(registerName(copy.source));
        Set<String> written = resultRegisterNames(instruction);
        aliases.removeAll(written);
        if (copy != null && sourceLive) {
            boolean identity = sameRegister(copy.destination, copy.source);
            if (aliases.add(registerName(copy.destination))) {
                if (!identity) aliasCopies++;
            }
        }
        return aliasCopies;
    }

    private Copy exactCopy(Instruction instruction) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        List<Register> operandRegisters = operandGeneralRegisters(instruction);
        if (mnemonic.equals("mr") && operandRegisters.size() == 2) {
            return new Copy(operandRegisters.get(0), operandRegisters.get(1));
        }
        if (mnemonic.equals("or") && operandRegisters.size() == 3
            && sameRegister(operandRegisters.get(1), operandRegisters.get(2))) {
            return new Copy(operandRegisters.get(0), operandRegisters.get(1));
        }
        if (mnemonic.equals("addi") && operandRegisters.size() == 2
            && !registerName(operandRegisters.get(1)).equals("r0")
            && hasZeroScalar(instruction)) {
            return new Copy(operandRegisters.get(0), operandRegisters.get(1));
        }
        if (mnemonic.equals("ori") && operandRegisters.size() == 2
            && hasZeroScalar(instruction)) {
            return new Copy(operandRegisters.get(0), operandRegisters.get(1));
        }
        if (mnemonic.equals("rlwinm") && operandRegisters.size() == 2
            && hasScalars(instruction, 0, 0, 31)) {
            return new Copy(operandRegisters.get(0), operandRegisters.get(1));
        }
        return null;
    }

    private boolean hasZeroScalar(Instruction instruction) {
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Scalar && ((Scalar) object).getSignedValue() == 0) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean hasScalars(Instruction instruction, long... expected) {
        List<Long> scalars = new ArrayList<>();
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Scalar) {
                    scalars.add(((Scalar) object).getSignedValue());
                }
            }
        }
        if (scalars.size() != expected.length) {
            return false;
        }
        for (int index = 0; index < expected.length; index++) {
            if (scalars.get(index) != expected[index]) {
                return false;
            }
        }
        return true;
    }

    private Set<String> resultRegisterNames(Instruction instruction) {
        Set<String> result = new HashSet<>();
        for (Object object : instruction.getResultObjects()) {
            if (object instanceof Register && isGeneralRegister((Register) object)) {
                result.add(registerName((Register) object));
            }
        }
        return result;
    }

    private List<Register> operandGeneralRegisters(Instruction instruction) {
        List<Register> result = new ArrayList<>();
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Register && isGeneralRegister((Register) object)) {
                    result.add((Register) object);
                }
            }
        }
        return result;
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

    private Register resultRegister(Instruction instruction) {
        Register result = null;
        for (Object object : instruction.getResultObjects()) {
            if (!(object instanceof Register) || !isGeneralRegister((Register) object)) {
                continue;
            }
            if (result != null) {
                return null;
            }
            result = (Register) object;
        }
        return result;
    }

    private Register mtctrSource(Instruction instruction) {
        Register source = null;
        for (Register register : operandGeneralRegisters(instruction)) {
            if (source != null) {
                return null;
            }
            source = register;
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

    private String registerName(Register register) {
        return register.getName().toLowerCase();
    }

    private boolean sameRegister(Register first, Register second) {
        return registerName(first).equals(registerName(second));
    }

    private boolean isVtableBase(Register register) {
        String name = registerName(register);
        return !name.equals("r0") && !name.equals("r1");
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
                if (object instanceof Register
                    && ((Register) object).getName().equalsIgnoreCase("CTR")) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean isBctrl(Instruction instruction) {
        return instruction.getMnemonicString().equalsIgnoreCase("bctrl");
    }

    private boolean writesCtr(Instruction instruction) {
        for (Object object : instruction.getResultObjects()) {
            if (object instanceof Register
                && ((Register) object).getName().equalsIgnoreCase("CTR")) {
                return true;
            }
        }
        return false;
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

    private String formatPath(List<Address> path) {
        StringBuilder result = new StringBuilder();
        for (Address address : path) {
            if (result.length() > 0) {
                result.append(" -> ");
            }
            result.append(String.format("0x%08X", address.getOffset()));
        }
        return result.toString();
    }

    private String stateKey(PathState state) {
        List<String> aliases = new ArrayList<>(state.aliases);
        Collections.sort(aliases);
        return state.instruction.getAddress() + "|" + aliases + "|" + state.ctrLive
            + "|" + state.branchEdges + "|" + state.aliasCopies;
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

    private static final class Copy {
        private final Register destination;
        private final Register source;

        private Copy(Register destination, Register source) {
            this.destination = destination;
            this.source = source;
        }
    }

    private static final class PathState {
        private final Instruction instruction;
        private final Set<String> aliases;
        private final boolean ctrLive;
        private final Instruction mtctr;
        private final int branchEdges;
        private final int aliasCopies;
        private final int distance;
        private final List<Address> path;

        private PathState(Instruction instruction, Set<String> aliases, boolean ctrLive,
                Instruction mtctr, int branchEdges, int aliasCopies, int distance,
                List<Address> path) {
            this.instruction = instruction;
            this.aliases = new LinkedHashSet<>(aliases);
            this.ctrLive = ctrLive;
            this.mtctr = mtctr;
            this.branchEdges = branchEdges;
            this.aliasCopies = aliasCopies;
            this.distance = distance;
            this.path = path;
        }
    }

    private static final class Match {
        private final Instruction mtctr;
        private final Instruction bctrl;
        private final int branchEdges;
        private final int aliasCopies;
        private final List<Address> path;

        private Match(Instruction mtctr, Instruction bctrl, int branchEdges,
                int aliasCopies, List<Address> path) {
            this.mtctr = mtctr;
            this.bctrl = bctrl;
            this.branchEdges = branchEdges;
            this.aliasCopies = aliasCopies;
            this.path = path;
        }
    }

    private static final class SearchResult {
        private final List<Match> matches = new ArrayList<>();
        private final Set<Long> straightLineCallsites = new LinkedHashSet<>();
        private long exploredStates;
        private boolean stateCapHit;
    }
}
