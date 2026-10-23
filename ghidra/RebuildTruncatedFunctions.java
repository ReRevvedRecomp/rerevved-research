// Ghidra mutating post-script. Rebuilds functions truncated at a call.
// Run second through tools/bootstrap-ghidra.ps1 against a disposable project.
//@category ReRevved
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.SourceType;
import ghidra.framework.options.Options;
import ghidra.framework.options.OptionType;
import java.util.ArrayList;
import java.util.List;

public class RebuildTruncatedFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        requireBootstrapGuard();

        // Disable Non-Returning Functions analyzers before re-disassembly so
        // auto-analysis does not restore the thunk noreturn flags.
        disableNoReturnAnalyzers();

        // Snapshot entry points before mutating the function set.
        List<Address> entries = new ArrayList<>();
        Function f = getFirstFunction();
        while (f != null) { entries.add(f.getEntryPoint()); f = getFunctionAfter(f); }

        int examined = 0, rebuilt = 0, err = 0;
        for (Address entry : entries) {
            Function fn = getFunctionAt(entry);
            if (fn == null) continue;
            examined++;
            Address bodyMax = fn.getBody().getMaxAddress();
            Instruction last = getInstructionContaining(bodyMax);
            if (last == null || !last.getFlowType().isCall()) continue;
            boolean userNamed = fn.getSymbol() != null
                && fn.getSymbol().getSource() == SourceType.USER_DEFINED;
            String nm = userNamed ? fn.getName() : null;
            try {
                removeFunction(fn);
                clearListing(entry, bodyMax);
                disassemble(entry);
                Function nf = createFunction(entry, nm);
                if (nf == null) {
                    err++;
                } else {
                    if (nm != null) nf.setName(nm, SourceType.USER_DEFINED);
                    rebuilt++;
                }
            } catch (Exception e) { err++; }
            if ((examined % 5000) == 0) println("[rebuild] ... examined " + examined);
        }
        println("[rebuild] examined " + examined + " functions; rebuilt " + rebuilt
            + " thunk-truncated (errors " + err + "). Split-constant recovery runs last.");
        requireNoErrors(err);
    }

    static void requireNoErrors(int errors) {
        if (errors != 0) {
            throw new IllegalStateException("rebuild reported " + errors + " error(s)");
        }
    }

    // Match "Non-Returning" by name because option keys can vary.
    // The BOOLEAN_TYPE guard leaves numeric sub-options unchanged.
    private void disableNoReturnAnalyzers() {
        Options analyzers = currentProgram.getOptions("Analyzers");
        int off = 0;
        for (String opt : analyzers.getOptionNames()) {
            if (opt.contains("Non-Returning") && analyzers.getType(opt) == OptionType.BOOLEAN_TYPE) {
                analyzers.setBoolean(opt, false);
                off++;
            }
        }
        println("[rebuild] disabled " + off + " Non-Returning analyzer toggle(s).");
    }

    private void requireBootstrapGuard() {
        String guard = System.getenv("REREVVED_GHIDRA_MUTATION");
        if (!"ALLOW_DISPOSABLE_PROJECT".equals(guard)) {
            throw new IllegalStateException(
                "Repair scripts require tools/bootstrap-ghidra.ps1 and a disposable project.");
        }
    }
}
