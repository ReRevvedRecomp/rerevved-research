<#
.SYNOPSIS
    Checks the combat retry bounds for the native combat random number generator.

.DESCRIPTION
    Scans every state of the unfolded 32-bit step behind the guest's combat
    generator (multiplier 214013, increment 2531011). The game folds each
    output below 4294954991, so it never visits every 32-bit state. It follows
    the unfolded step until a value reaches the folded range, and the fold
    lands on a state that ends the adverse run, so runs measured over the
    full unfolded period bound the game's runs. It reports the longest run of adverse results and of ordinal misses for
    one loss threshold. From those runs it derives the rejection, attempt and draw
    bounds and fails if the rejection bound does not stay below the native
    retry cap of 1000.

    -Case above-three-to-one uses the conservative strict-above-3x threshold.
    -Case exact-four-to-one uses the exact 4:1 threshold.
    -SelfTest runs only the small-width and constant checks.
    -Out writes the JSON result to a new file; an existing file is refused.

    Requires PowerShell 7 or later. A full scan visits 2^32 states.
#>
[CmdletBinding()]
param(
    [switch]$SelfTest,
    [ValidateSet('exact-four-to-one', 'above-three-to-one')]
    [string]$Case = 'above-three-to-one',
    [string]$Out
)
$ErrorActionPreference = 'Stop'
if ($Out -and (Test-Path -LiteralPath $Out)) { throw 'Output already exists.' }

$source = @'
using System;

public sealed class CombatPeriodResult
{
    public ulong States { get; set; }
    public ulong EligibleStates { get; set; }
    public ulong AdverseEligibleStates { get; set; }
    public ulong MaxAdverseReturnRun { get; set; }
    public ulong MaxOrdinalMissRun { get; set; }
    public uint EndState { get; set; }
}

public static class CombatRngPeriodAudit
{
    static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    static ulong Period(int bits) { return 1UL << bits; }
    static uint Step(uint state, uint a, uint c, uint mask)
    {
        return unchecked(state * a + c) & mask;
    }

    static void CheckDomain(int bits, uint a, uint c, uint m, uint b, uint h)
    {
        Require(bits >= 2 && bits <= 32, "Unsupported state width.");
        ulong n = Period(bits), mask = n - 1;
        Require((a & 3) == 1 && (c & 1) == 1, "Full-period preconditions fail.");
        Require(b < h && h < m && m < n && m > n / 2, "Invalid intervals.");
        ulong foldedMax = n - m - 1;
        Require(foldedMax <= b && (ulong)a * foldedMax + c < h, "Fold does not force a GOOD endpoint.");
        ulong jumpA = a & mask, jumpC = c & mask;
        for (int k = 0; k < bits; ++k)
        {
            ulong submask = (1UL << (k + 1)) - 1;
            Require((jumpA & submask) == 1 && (jumpC & submask) == (1UL << k), "Affine period certificate fails.");
            jumpC = jumpC * (jumpA + 1) & mask;
            jumpA = jumpA * jumpA & mask;
        }
        Require(jumpA == 1 && jumpC == 0, "Final affine jump is not identity.");
    }

    static CombatPeriodResult Scan(int bits, uint a, uint c, uint m, uint b, uint h, bool progress)
    {
        CheckDomain(bits, a, c, m, b, h);
        ulong n = Period(bits), eligible = 0, bad = 0, badRun = 0, maxBad = 0, misses = 0, maxMisses = 0;
        uint mask = (uint)(n - 1), state = 0;
        for (ulong i = 0; i < n; ++i)
        {
            uint next = Step(state, a, c, mask);
            if (state <= b)
            {
                eligible++;
                misses = 0;
                if (next >= h && next < m)
                {
                    bad++; badRun++;
                    if (badRun > maxBad) maxBad = badRun;
                }
                else badRun = 0;
            }
            else
            {
                misses++;
                if (misses > maxMisses) maxMisses = misses;
            }
            state = next;
            if (progress && (i & 0x0fffffffUL) == 0x0fffffffUL)
                Console.WriteLine("Scanned states: " + (i + 1));
        }
        Require(state == 0 && eligible == (ulong)b + 1, "Cycle coverage invariant fails.");
        return new CombatPeriodResult { States = n, EligibleStates = eligible, AdverseEligibleStates = bad,
            MaxAdverseReturnRun = maxBad, MaxOrdinalMissRun = maxMisses, EndState = state };
    }

    static ulong CountBad(uint a, uint c, uint m, uint b, uint h, ulong n)
    {
        ulong count = 0, last = ((ulong)a * b + c) / n;
        for (ulong q = 0; q <= last; ++q)
        {
            long lowerNumerator = (long)(q * n + h) - c;
            long upperNumerator = (long)(q * n + m - 1) - c;
            long lo = lowerNumerator >= 0 ? (lowerNumerator + a - 1) / a : lowerNumerator / a;
            long hi = upperNumerator >= 0 ? upperNumerator / a : (upperNumerator - a + 1) / a;
            lo = Math.Max(0, lo); hi = Math.Min(b, hi);
            if (lo <= hi) count += (ulong)(hi - lo + 1);
        }
        return count;
    }

    static void CheckSmall(int bits, uint a, uint c, uint m, uint b, uint h)
    {
        CombatPeriodResult scan = Scan(bits, a, c, m, b, h, false);
        uint mask = (uint)(Period(bits) - 1);
        Require(scan.AdverseEligibleStates == CountBad(a, c, m, b, h, Period(bits)), "Independent interval count differs.");
        for (uint seed = 0; seed < Period(bits); ++seed)
        {
            uint state = seed;
            ulong attempts = 0, draws = 0;
            bool loss;
            do
            {
                attempts++;
                state = Step(state, a, c, mask) % m; draws++;
                loss = state >= h;
                ulong ordinalDraws = 0;
                do
                {
                    state = Step(state, a, c, mask) % m; draws++; ordinalDraws++;
                    Require(ordinalDraws <= scan.MaxOrdinalMissRun + 1, "Ordinal bound violated.");
                } while (state > b);
                Require(attempts <= scan.MaxAdverseReturnRun + 2, "Attempt bound violated.");
            } while (loss);
            state = Step(state, a, c, mask) % m; draws++;
            Require(draws <= (scan.MaxAdverseReturnRun + 2) * (scan.MaxOrdinalMissRun + 2) + 1, "Draw bound violated.");
        }
    }

    public static int Tests()
    {
        CheckSmall(6, 5, 1, 63, 7, 48);
        CheckSmall(8, 13, 1, 253, 28, 204);
        CheckSmall(10, 21, 5, 1019, 112, 800);
        bool rejected = false;
        try { CheckDomain(6, 5, 1, 50, 7, 48); } catch (InvalidOperationException) { rejected = true; }
        Require(rejected, "Unsafe fold domain was accepted.");
        rejected = false;
        try { CheckDomain(6, 3, 1, 63, 7, 48); } catch (InvalidOperationException) { rejected = true; }
        Require(rejected, "Short-period multiplier was accepted.");
        double q = BitConverter.Int64BitsToDouble(0x3df0000301109066L);
        Require(Math.Truncate((477217221.0 * q) * 9.0) == 0 && Math.Truncate((477217222.0 * q) * 9.0) == 1, "Ordinal threshold differs.");
        Require(Math.Truncate((1500.0 * 3435963992.0) * q) < 1200 && Math.Truncate((1500.0 * 3435963993.0) * q) >= 1200, "Comparison threshold differs.");
        Require(Math.Truncate((4294954990.0 * q) * 9.0) == 8, "Ordinal upper bound differs.");
        Require(CountBad(214013, 2531011, 4294954991, 477217221, 3435963993, 1UL << 32) == 95442550, "Independent full-width count differs.");
        const decimal numerator = 2251806265067571M, denominator = 9671406556917033397649408M;
        Require(3221216243M * numerator <= 0.75M * denominator && 3221216244M * numerator > 0.75M * denominator, "Conservative three-times threshold differs.");
        Require((0x3df0000301109066UL & ((1UL << 52) - 1)) + (1UL << 52) == 2UL * 2251806265067571UL, "Scale significand differs.");
        Require(((0x3df0000301109066UL >> 52) & 0x7ff) == 991, "Scale exponent differs.");
        return 10;
    }

    public static CombatPeriodResult Full(uint h)
    {
        CombatPeriodResult result = Scan(32, 214013, 2531011, 4294954991, 477217221, h, true);
        Require(result.AdverseEligibleStates == CountBad(214013, 2531011, 4294954991, 477217221, h, 1UL << 32), "Full scan and interval count differ.");
        return result;
    }
}
'@
$null = Add-Type -TypeDefinition $source -Language CSharp
$checks = [CombatRngPeriodAudit]::Tests()
$result = [ordered]@{
    SourceSha256   = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash
    SelfTestGroups = $checks
    Case           = $Case
}
if (-not $SelfTest) {
    $threshold = if ($Case -eq 'exact-four-to-one') { [uint32]3435963993 } else { [uint32]3221216243 }
    $result.LossThreshold = $threshold
    $scan = [CombatRngPeriodAudit]::Full($threshold)
    $result.Scan = $scan
    $result.RejectionBound = $scan.MaxAdverseReturnRun + 1
    $result.AttemptBound = $scan.MaxAdverseReturnRun + 2
    $result.DrawBound = ($scan.MaxAdverseReturnRun + 2) * ($scan.MaxOrdinalMissRun + 2) + 1
    if ($result.RejectionBound -ge 1000) { throw 'This bound does not exclude the native retry cap.' }
}
$json = $result | ConvertTo-Json -Depth 5
if ($Out) { [IO.File]::WriteAllText([IO.Path]::GetFullPath($Out), $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false)) }
$json
