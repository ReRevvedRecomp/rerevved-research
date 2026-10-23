import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

// Minimal input objects for production queries; no query logic is reproduced here.
record Address(long getOffset) implements Comparable<Address> {
    Address add(long amount) { return new Address(getOffset + amount); }
    public int compareTo(Address other) { return Long.compare(getOffset, other.getOffset); }
    public String toString() { return String.format("0x%08X", getOffset); }
}
record Register(String getName) {}
record Scalar(long getSignedValue) {
    long getUnsignedValue() { return getSignedValue & 0xFFFFL; }
}
record FlowType(boolean isJump, boolean isCall, boolean isTerminal) {}
class Instruction {
    final Address address;
    final String mnemonic;
    final Object[][] operands;
    final Object[] results;
    Address fallThrough;
    Address[] flows = {};
    Instruction(long address, String mnemonic, Object[] results, Object[]... operands) {
        this.address = new Address(address);
        this.mnemonic = mnemonic;
        this.results = results;
        this.operands = operands;
        fallThrough = this.address.add(4);
    }
    Address getAddress() { return address; }
    String getMnemonicString() { return mnemonic; }
    Object[] getResultObjects() { return results; }
    int getNumOperands() { return operands.length; }
    Object[] getOpObjects(int index) { return operands[index]; }
    Address getFallThrough() { return fallThrough; }
    Address[] getFlows() { return flows; }
    FlowType getFlowType() {
        return new FlowType(mnemonic.equals("b"), mnemonic.equals("bctrl") || mnemonic.equals("bl"), mnemonic.equals("blr"));
    }
    public String toString() { return mnemonic; }
}
class InstructionIterator implements Iterator<Instruction> {
    final Iterator<Instruction> iterator;
    InstructionIterator(Collection<Instruction> values) { iterator = values.iterator(); }
    public boolean hasNext() { return iterator.hasNext(); }
    public Instruction next() { return iterator.next(); }
}
class Listing {
    final TreeMap<Long, Instruction> instructions = new TreeMap<>();
    void add(Instruction instruction) { instructions.put(instruction.address.getOffset(), instruction); }
    Instruction getInstructionAt(Address address) { return instructions.get(address.getOffset()); }
    Instruction getInstructionAfter(Address address) {
        var next = instructions.higherEntry(address.getOffset());
        return next == null ? null : next.getValue();
    }
    InstructionIterator getInstructions(boolean forward) { return new InstructionIterator(instructions.values()); }
    InstructionIterator getInstructions(Address start, boolean forward) {
        return new InstructionIterator(instructions.tailMap(start.getOffset()).values());
    }
}
class CodeBlock {
    boolean contains(Address address) { return address.getOffset() >= 0 && address.getOffset() < 0x10000; }
}
class Function {
    CodeBlock getBody() { return new CodeBlock(); }
    Address getEntryPoint() { return new Address(0); }
    String getName() { return "fixture"; }
}
class FunctionManager {
    final Function function = new Function();
    Function getFunctionContaining(Address address) { return function.getBody().contains(address) ? function : null; }
}
record MemoryBlock(long start, int[] words, boolean isInitialized, boolean isExecute) {
    Address getStart() { return new Address(start); }
    Address getEnd() { return new Address(start + words.length * 4L - 1); }
}
class Memory {
    final List<MemoryBlock> blocks = new ArrayList<>();
    MemoryBlock[] getBlocks() { return blocks.toArray(MemoryBlock[]::new); }
    int getInt(Address address) {
        for (MemoryBlock block : blocks) {
            long index = (address.getOffset() - block.start()) / 4;
            if (address.getOffset() >= block.start() && index < block.words().length) return block.words()[(int) index];
        }
        throw new AssertionError("unmapped address " + address);
    }
}
class Program {
    final Listing listing = new Listing();
    final FunctionManager functions = new FunctionManager();
    final Memory memory = new Memory();
    Listing getListing() { return listing; }
    FunctionManager getFunctionManager() { return functions; }
    Memory getMemory() { return memory; }
    String getName() { return "synthetic"; }
}
class Monitor { boolean isCancelled() { return false; } }
class BasicBlockModel {
    BasicBlockModel(Program program) {}
    CodeBlock getFirstCodeBlockContaining(Address address, Monitor monitor) { return new CodeBlock(); }
}
class GhidraScript {
    Program currentProgram;
    final Monitor monitor = new Monitor();
    public void run() throws Exception {}
    Address toAddr(long offset) { return new Address(offset); }
    void println(String value) {}
}

public class QueryInstructionFixture {
    static final Register R3 = new Register("r3"), R12 = new Register("r12"), CTR = new Register("CTR");
    static Instruction op(long address, String mnemonic, Object[] results, Object[]... operands) {
        return new Instruction(address, mnemonic, results, operands);
    }
    static Instruction load(long address) {
        return op(address, "lwz", new Object[] {R12}, new Object[] {R12}, new Object[] {new Scalar(0x34), R3});
    }
    static Instruction mtctr(long address, Register source) {
        return op(address, "mtctr", new Object[] {CTR}, source == null ? new Object[] {} : new Object[] {source});
    }
    static Instruction plain(long address, String name) { return op(address, name, new Object[] {}); }

    public static void main(String[] args) throws Exception {
        String scenario = args[0];
        Program program = new Program();
        Listing listing = program.listing;
        GhidraScript query;
        if (scenario.startsWith("ctr-")) {
            query = new FindVtableSlotCalls();
            listing.add(load(0));
            listing.add(mtctr(4, R12));
            if (!scenario.equals("ctr-live")) listing.add(op(8, "li", new Object[] {R12}));
            else listing.add(plain(8, "nop"));
            if (scenario.equals("ctr-overwrite")) listing.add(plain(12, "bctrl"));
            else {
                Register source = scenario.equals("ctr-wrong") ? R3 : scenario.equals("ctr-missing") ? null : R12;
                listing.add(mtctr(12, source));
                listing.add(plain(16, "bctrl"));
            }
        } else if (scenario.startsWith("cfg-")) {
            query = new FindVtableSlotCallsCfg();
            listing.add(load(0));
            if (scenario.equals("cfg-state-cap")) {
                Instruction branch = plain(4, "b");
                branch.fallThrough = null;
                branch.flows = new Address[257];
                for (int index = 0; index < 257; index++) {
                    long offset = 0x1000 + index * 4L;
                    branch.flows[index] = new Address(offset);
                    Instruction leaf = plain(offset, "nop");
                    leaf.fallThrough = null;
                    listing.add(leaf);
                }
                listing.add(branch);
            } else if (scenario.startsWith("cfg-distance-")) {
                int distance = Integer.parseInt(args[1]);
                listing.add(mtctr(4, R12));
                for (int index = 2; index < distance; index++) listing.add(plain(index * 4L, "nop"));
                listing.add(plain(distance * 4L, "bctrl"));
            } else if (scenario.startsWith("cfg-branches-")) {
                int branches = Integer.parseInt(args[1]);
                for (int index = 1; index <= branches; index++) listing.add(plain(index * 4L, "b"));
                listing.add(mtctr((branches + 1) * 4L, R12));
                listing.add(plain((branches + 2) * 4L, "bctrl"));
            } else if (scenario.equals("cfg-r0") || scenario.equals("cfg-alias")) {
                Register target = new Register(scenario.equals("cfg-r0") ? "r0" : "r11");
                Register finalTarget = new Register("r10");
                listing.add(op(4, "mr", new Object[] {target}, new Object[] {target}, new Object[] {R12}));
                listing.add(op(8, "addi", new Object[] {finalTarget}, new Object[] {finalTarget}, new Object[] {target}, new Object[] {new Scalar(0)}));
                listing.add(mtctr(12, finalTarget));
                listing.add(plain(16, "bctrl"));
            } else {
                listing.add(mtctr(4, R12));
                listing.add(scenario.equals("cfg-clobber") ? op(8, "other", new Object[] {CTR}) : plain(8, "bl"));
                listing.add(plain(12, "bctrl"));
            }
        } else if (scenario.startsWith("raw-")) {
            query = new FindRawVtableSlotCalls();
            int distance = scenario.equals("raw-window") ? Integer.parseInt(args[1]) : scenario.equals("raw-control") ? 3 : 2;
            int[] words = new int[distance + 1];
            Arrays.fill(words, 0x60000000);
            words[0] = 0x81830034;
            words[1] = 0x7D8903A6;
            words[distance] = 0x4E800421;
            if (scenario.equals("raw-control")) words[2] = 0x4E800020;
            program.memory.blocks.add(new MemoryBlock(0, words, true, true));
            if (scenario.equals("raw-decoded")) {
                listing.add(load(0));
                program.memory.blocks.add(new MemoryBlock(0x100, words, true, true));
                program.memory.blocks.add(new MemoryBlock(0x200, words, true, false));
                program.memory.blocks.add(new MemoryBlock(0x300, words, false, true));
            }
        } else if (scenario.equals("global-continue")) {
            query = new FindGlobalAddressAccesses();
            listing.add(op(0, "lis", new Object[] {R12}, new Object[] {R12}, new Object[] {new Scalar(0x1234)}));
            listing.add(op(4, "addi", new Object[] {R3}, new Object[] {R3}, new Object[] {R12}, new Object[] {new Scalar(1)}));
            listing.add(op(8, "addi", new Object[] {R3}, new Object[] {R3}, new Object[] {R12}, new Object[] {new Scalar(2)}));
        } else throw new AssertionError("unknown scenario " + scenario);
        query.currentProgram = program;
        query.run();
        System.out.print(Files.readString(Path.of(System.getenv("REREVVED_DUMP_PATH"))));
    }
}
