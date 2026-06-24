#!/usr/bin/env python3
"""
cr3echrz.cli — Unified CLI module

Single interface for:
  • 7 mathematical theorem operationalizations (p3theorem engine)
  • 6 p4rakernel standalone modules (Burnside, Connes, Erdős–Straus, Goldbach, Landau, Three-Body)
  • 271 vault ob3ects (ob3ect_vault engine)
  • Structural analysis via CL8NK navigator
  • Frobenius verification across all domains

Usage:
    cr3 --help                       Show this help
    cr3 --list                       List all available (theorems + p4rakernel + ob3ects)
    cr3 --list-theorems              List theorems only (13 total)
    cr3 --list-ob3ects [domain]      List vault ob3ects (271)
    cr3 <name> [params...]           Run a theorem, p4rakernel module, or ob3ect
    cr3 p4ra <name> [params...]      Run a p4rakernel module (guaranteed p4ra engine)
    cr3 p4ra --list                  List p4rakernel modules
    cr3 p4ra --help                  Show p4rakernel-specific help
    cr3 <name> --help                Show per-command help with literal examples
    cr3 --analyze <name>             CL8NK structural analysis
    cr3 --version                    Show version

Author: Lando⊗⊙perator
Date: 2026-06-24
"""
import sys
import os
import json
import subprocess
from pathlib import Path

from cr3echrz.shared import OPCODES


# ═══════════════════════════════════════════════════════════════════════
#  ENGINE LOADERS
# ═══════════════════════════════════════════════════════════════════════

def load_theorem_engine():
    """Load the 7-theorem engine from code/unified_driver.py."""
    from cr3echrz.code.unified_driver import (
        THEOREM_REGISTRY, run_theorem, list_theorems
    )
    return THEOREM_REGISTRY, run_theorem, list_theorems


def load_vault_engine():
    """Load the 271 ob3ect vault engine."""
    from cr3echrz.ob3ect_vault.main import (
        bootstrap_ob3ect, list_all_ob3ects
    )
    from cr3echrz.ob3ect_vault import state as vault_state
    return bootstrap_ob3ect, list_all_ob3ects, vault_state


def load_p4rakernel_modules():
    """Load the 6 p4rakernel standalone theorem modules."""
    from cr3echrz.p4rakernel import P4RA_MODULES, P4RA_DESCRIPTIONS
    return P4RA_MODULES, P4RA_DESCRIPTIONS

# ═══════════════════════════════════════════════════════════════════════
#  PER-COMMAND HELP TEXTS
# ═══════════════════════════════════════════════════════════════════════

def _cmd_help(name):
    """Return (header, body) help text for a named command, or None."""
    helps = {
        # ── META COMMANDS ──
        "--list": (
            "cr3 --list",
            "List ALL available commands — theorems, p4rakernel modules, and vault ob3ects.\n"
            "\n"
            "  cr3 --list\n"
            "\n"
            "Shows a categorized listing of everything available:\n"
            "  • 7 theorems (p3theorem engine)\n"
            "  • 6 p4rakernel standalone modules (also: cr3 p4ra --list)\n"
            "  • 271 vault ob3ects (with domain filters)\n"
            "\n"
            "Use --list-theorems or --list-ob3ects for filtered views.\n"
            "Use cr3 p4ra --list for p4rakernel-only listing."
        ),
        "--list-theorems": (
            "cr3 --list-theorems",
            "List all 13 mathematical theorems (7 p3theorem + 6 p4rakernel).\n"
            "\n"
            "  cr3 --list-theorems\n"
            "\n"
            "Then run any listed theorem:\n"
            "  cr3 collatz 27                       # p3theorem engine\n"
            "  cr3 p4ra burnside 2 5                # p4rakernel engine\n"
            "  cr3 p4ra goldbach 100                # p4rakernel engine\n"
            "  cr3 p4ra connes R                    # p4rakernel engine\n"
            "\n"
            "Note: burnside/goldbach/erdos_straus exist in BOTH engines.\n"
            "  cr3 <name>         → p3theorem engine (default)\n"
            "  cr3 p4ra <name>    → p4rakernel engine (Belnap+Frobenius)"
        ),
        "--list-ob3ects": (
            "cr3 --list-ob3ects [domain]",
            "List vault ob3ects, optionally filtered by domain.\n"
            "\n"
            "  cr3 --list-ob3ects                # all 271 ob3ects\n"
            "  cr3 --list-ob3ects mathematical   # math ob3ects only\n"
            "  cr3 --list-ob3ects magical        # magical ob3ects only\n"
            "  cr3 --list-ob3ects alchemical     # alchemical ob3ects only\n"
            "\n"
            "Domains: mathematical, magical, alchemical, divinatory,\n"
            "         computational, physical, biological, theological, ...\n"
            "\n"
            "Then run any listed ob3ect:\n"
            "  cr3 truth_machine\n"
            "  cr3 philosophers_stone"
        ),
        "--analyze": (
            "cr3 --analyze <name>",
            "Run CLINK L8 structural analysis on a theorem or system.\n"
            "\n"
            "  cr3 --analyze collatz             # Collatz CL8NK analysis\n"
            "  cr3 --analyze goldbach            # Goldbach CL8NK analysis\n"
            "  cr3 --analyze burnside            # Burnside CL8NK analysis\n"
            "  cr3 --analyze connes              # Connes CL8NK analysis\n"
            "  cr3 --analyze three_body          # Three-Body CL8NK analysis\n"
            "  cr3 --analyze erdos_straus        # Erdős–Straus CL8NK analysis\n"
            "  cr3 --analyze landau              # Landau CL8NK analysis\n"
            "  cr3 --analyze baum_connes         # Baum–Connes CL8NK analysis\n"
            "  cr3 --analyze inverse_galois      # Inverse Galois CL8NK analysis\n"
            "\n"
            "Reports: CLINK L8 entry decomposition, structural distance,\n"
            "         tier assessment, per-primitive deltas."
        ),
        "--version": (
            "cr3 --version",
            "Show cr3 version, author, and opcode inventory.\n"
            "\n"
            "  cr3 --version"
        ),

        # ── P4RA SUBCOMMAND ──
        "p4ra": (
            "cr3 p4ra <module> [args...]",
            "Run a p4rakernel standalone module — Belnap+Frobenius 13-step bootstrap.\n"
            "This subcommand guarantees the p4rakernel engine (never p3theorem).\n"
            "\n"
            "  cr3 p4ra --help                   # This help\n"
            "  cr3 p4ra --list                   # List all 6 p4rakernel modules\n"
            "\n"
            "  cr3 p4ra burnside 2 5             # B(2,5) — PARADOX\n"
            "  cr3 p4ra burnside 2 665 1 2 -1 -2 # B(2,665) — INFINITE (Adian 1979)\n"
            "  cr3 p4ra connes R                 # Connes: R EMBEDDABLE\n"
            "  cr3 p4ra connes \"L(F_2)\"           # Connes: L(F_2) NON-EMBEDDABLE\n"
            "  cr3 p4ra connes \"L(F_2)\" false     # Connes: L(F_2) PARADOX (pre-2020)\n"
            "  cr3 p4ra erdos_straus 73          # Erdős–Straus: 4/73\n"
            "  cr3 p4ra erdos_straus 5           # Erdős–Straus: 4/5 = 1/2+1/4+1/20\n"
            "  cr3 p4ra goldbach 100             # Goldbach: 100 = 3+97 = ... (6 pairs)\n"
            "  cr3 p4ra goldbach 30              # Goldbach: 30 = 7+23 = 11+19 = 13+17\n"
            "  cr3 p4ra landau Koebe             # Landau: Koebe omits -1/4\n"
            "  cr3 p4ra landau Dense             # Landau: Dense (unbounded)\n"
            "  cr3 p4ra landau Picard            # Landau: Essential singularity\n"
            "  cr3 p4ra threebody                # Three-Body: figure-8 Poincaré section\n"
            "\n"
            "All p4rakernel modules run the full 13-step IMASM bootstrap with\n"
            "Belnap FOUR state registers and Frobenius (μ∘δ=id) verification."
        ),

        # ── P3THEOREM ENGINE (7 theorems) ──
        "collatz": (
            "cr3 collatz <seed>",
            "Collatz Conjecture (3n+1 problem) — 14-phase operationalization.\n"
            "\n"
            "  cr3 collatz 27                    # classic: seed=27, 111 steps to 1\n"
            "  cr3 collatz 19                    # seed=19, 20 steps\n"
            "  cr3 collatz 871                   # seed=871, 178 steps\n"
            "  cr3 collatz 63728127              # large seed, >900 steps\n"
            "\n"
            "Default seed: 27"
        ),
        "goldbach": (
            "cr3 goldbach <n>",
            "Goldbach's Conjecture — every even n ≥ 4 is sum of two primes. 18-phase.\n"
            "Uses p3theorem engine. For p4rakernel Belnap+Frobenius version:\n"
            "  cr3 p4ra goldbach <n>\n"
            "\n"
            "  cr3 goldbach 100                  # 100 = 3+97 = 11+89 = ... (6 pairs)\n"
            "  cr3 goldbach 30                   # 30 = 7+23 = 11+19 = 13+17\n"
            "  cr3 goldbach 10                   # 10 = 3+7 = 5+5 (MULTIPLE)\n"
            "  cr3 goldbach 4                    # 4 = 2+2\n"
            "  cr3 goldbach 99999989             # large prime-adjacent\n"
            "\n"
            "Default n: 100"
        ),
        "three_body": (
            "cr3 three_body",
            "Three-Body Problem — Hamiltonian non-integrability. 19-phase.\n"
            "\n"
            "  cr3 three_body                    # Run with default parameters\n"
            "\n"
            "No parameters — runs the full 19-phase bootstrap with figure-8 orbit."
        ),
        "burnside": (
            "cr3 burnside <generators> <exponent> [seed...]",
            "Bounded Burnside Problem — B(m,n) group finiteness. 13-phase.\n"
            "Uses p3theorem engine. For p4rakernel Belnap+Frobenius version:\n"
            "  cr3 p4ra burnside <generators> <exponent> [seed...]\n"
            "\n"
            "  cr3 burnside 2 3                  # B(2,3): FINITE (order 27)\n"
            "  cr3 burnside 2 4                  # B(2,4): FINITE\n"
            "  cr3 burnside 2 5                  # B(2,5): PARADOX (KAM boundary)\n"
            "  cr3 burnside 2 665 1 2 -1 -2      # B(2,665): INFINITE (Adian 1979)\n"
            "  cr3 burnside 3 3 1 2 1 3 -1 -2    # B(3,3): with custom seed\n"
            "\n"
            "Arguments: generators (m), exponent (n), then seed word as integers.\n"
            "Default: B(2,5) with seed (1, 2, -1, -2)"
        ),

        "erdos_straus": (
            "cr3 erdos_straus <n>",
            "Erdős–Straus Conjecture — 4/n = 1/x + 1/y + 1/z. 27-phase.\n"
            "Uses p3theorem engine. For p4rakernel Belnap+Frobenius version:\n"
            "  cr3 p4ra erdos_straus <n>\n"
            "\n"
            "  cr3 erdos_straus 73               # 4/73 decomposition\n"
            "  cr3 erdos_straus 5                # 4/5 = 1/2 + 1/4 + 1/20\n"
            "  cr3 erdos_straus 17               # 4/17 congruence class analysis\n"
            "  cr3 erdos_straus 49               # 4/49 = 1/14 + 1/98 + 1/196\n"
            "  cr3 erdos_straus 97               # prime n analysis\n"
            "\n"
            "Default n: 73"
        ),
        "inverse_galois": (
            "cr3 inverse_galois <group_name>",
            "Inverse Galois Problem — every finite group as Galois group over Q. 24-phase.\n"
            "\n"
            "  cr3 inverse_galois Sn             # Symmetric group S_n\n"
            "  cr3 inverse_galois An             # Alternating group A_n\n"
            "  cr3 inverse_galois C5             # Cyclic group C_5\n"
            "\n"
            "Default group: Sn"
        ),
        "baum_connes": (
            "cr3 baum_connes <group_class>",
            "Baum–Connes Conjecture — assembly map isomorphism. 22-phase.\n"
            "\n"
            "  cr3 baum_connes a-T-menable       # a-T-menable groups (HK)\n"
            "  cr3 baum_connes hyperbolic        # Hyperbolic groups\n"
            "  cr3 baum_connes SL3Z              # SL(3,Z) — counterexample?\n"
            "\n"
            "Default class: a-T-menable"
        ),

        # ── P4RAKERNEL STANDALONE MODULES (6) ──
        # Each has its own --help. Also accessible via: cr3 p4ra <name>
        "connes": (
            "cr3 connes <factor_name> [use_2020]",
            "Connes Embedding Problem — II₁ factor embeddability in R^ω.\n"
            "Full Belnap+Frobenius 13-step bootstrap with JNVWY 2020 (MIP*=RE).\n"
            "Also accessible via: cr3 p4ra connes <factor_name> [use_2020]\n"
            "\n"
            "  cr3 connes R                      # R (hyperfinite): EMBEDDABLE\n"
            "  cr3 connes \"L(F_2)\"               # L(F_2): NON-EMBEDDABLE (post-2020)\n"
            "  cr3 connes \"L(F_2)\" true           # Same: use_2020=true (default)\n"
            "  cr3 connes \"L(F_2)\" false          # L(F_2) pre-2020: PARADOX\n"
            "  cr3 connes \"L(F_2)\" no             # Same: use_2020=false\n"
            "  cr3 connes \"L(F_n)\"                # Free group factor L(F_n)\n"
            "  cr3 connes M                       # Generic II₁ factor\n"
            "\n"
            "Arguments: factor_name (R, L(F_2), L(F_n), M, ...),\n"
            "           use_2020 = true/false (default true — JNVWY 2020 applies)."
        ),
        "landau": (
            "cr3 landau <case>",
            "Landau's Theorems — holomorphic functions on the unit disk.\n"
            "Full Belnap+Frobenius 13-step IMASM bootstrap (Landau 1904).\n"
            "Also accessible via: cr3 p4ra landau <case>\n"
            "\n"
            "  cr3 landau Koebe                  # f(z)=z/(1-z)²: omits -1/4 (BOUNDED)\n"
            "  cr3 landau Dense                  # f(z)=z+0.1z²: omits nothing (UNBOUNDED)\n"
            "  cr3 landau Picard                 # Essential singularity: entanglement case\n"
            "\n"
            "Cases:\n"
            "  Koebe  — Bounded omission (omits exactly -1/4)\n"
            "  Dense  — Unbounded (dense image on C)\n"
            "  Picard — Essential singularity (dialetheic/paradox boundary)"
        ),
        "threebody": (
            "cr3 threebody",
            "Three-Body Problem — Hamiltonian non-integrability (Poincaré 1890).\n"
            "Full Belnap+Frobenius bootstrap with KAM dialetheic boundary.\n"
            "Also accessible via: cr3 p4ra threebody\n"
            "\n"
            "  cr3 threebody                     # Run full 13-step bootstrap\n"
            "\n"
            "No arguments — runs the full operationalization with figure-8\n"
            "Poincaré section, Liouville integrability analysis, and Frobenius\n"
            "verification at every FSPLIT/FFUSE pair."
        ),

        # ── VAULT OB3ECTS (selected frequently-used) ──
        "truth_machine": (
            "cr3 truth_machine",
            "Truth Machine ob3ect — self-verifying paraconsistent truth evaluator.\n"
            "\n"
            "  cr3 truth_machine                 # Run with defaults\n"
            "  cr3 truth_machine 0.5 200         # dt=0.5, N_period=200"
        ),
        "philosophers_stone": (
            "cr3 philosophers_stone",
            "Philosopher's Stone (Lapis Philosophorum) — alchemical transmutation ob3ect.\n"
            "\n"
            "  cr3 philosophers_stone            # Run with defaults"
        ),
        "chaos_magic_servitor": (
            "cr3 chaos_magic_servitor",
            "Chaos Magic Servitor — self-imscribing magical ob3ect.\n"
            "\n"
            "  cr3 chaos_magic_servitor          # Run with defaults"
        ),
        "collatz_theorem": (
            "cr3 collatz_theorem [dt] [N]",
            "Collatz Theorem vault ob3ect — ob3ect_vault version.\n"
            "\n"
            "  cr3 collatz_theorem               # Run with defaults\n"
            "  cr3 collatz_theorem 0.1 500       # dt=0.1, N_period=500"
        ),
    }
    return helps.get(name)


# ═══════════════════════════════════════════════════════════════════════
#  CL8NK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

CATALOG_NAME_MAP = {
    "collatz": "collatz_conjecture",
    "goldbach": "goldbachs_conjecture",
    "three_body": "three_body_problem",
    "burnside": "bounded_burnside_problem",
    "erdos_straus": "erdos_straus_conjecture",
    "baum_connes": "baum_connes_conjecture",
    "inverse_galois": "inverse_galois_problem",
    "connes": "connes_embedding_problem",
    "landau": "landaus_theorems",
    "threebody": "three_body_problem",
}


def run_cl8nk_analysis(name: str):
    """Run CLINK L8 structural analysis via cl8nk_navigator."""
    catalog_name = CATALOG_NAME_MAP.get(name, name)

    search_paths = [
        Path(__file__).resolve().parent.parent.parent
        / "imscribing_grammar" / "navigators" / "cl8nk_navigator.py",
        Path("/home/mrnob0dy666/imsgct/imscribing_grammar/navigators/cl8nk_navigator.py"),
    ]
    nav_path = None
    for p in search_paths:
        if p.exists():
            nav_path = str(p)
            break

    if not nav_path:
        return "  CL8NK navigator not found (run from within imsgct tree)"

    for action in ["entry", "distance"]:
        try:
            result = subprocess.run(
                ["python3", nav_path, action, catalog_name],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            continue
    return None

# ═══════════════════════════════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════════════════════════════

BANNER = r"""
   ╔══════════════════════════════════════╗
   ║     cr3  —  unified framework       ║
   ║     Lando⊗⊙perator  ·  2026         ║
   ╚══════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════════════
#  P4RAKERNEL MODULE DISPATCH
# ═══════════════════════════════════════════════════════════════════════

def _run_p4rakernel_module(name: str, args: list):
    """Run a p4rakernel standalone module."""
    if name == "burnside":
        from cr3echrz.p4rakernel.burnside.main import run_burnside_protocol
        m = int(args[0]) if len(args) > 0 else 2
        n = int(args[1]) if len(args) > 1 else 5
        seed = tuple(int(x) for x in args[2:]) if len(args) > 2 else (1, 2, -1, -2)
        run_burnside_protocol(m=m, n=n, seed_word=seed)
    elif name == "connes":
        from cr3echrz.p4rakernel.connes.main import run_connes_protocol
        factor = args[0] if len(args) > 0 else "L(F_2)"
        use_2020 = args[1].lower() not in ("false", "0", "no") if len(args) > 1 else True
        run_connes_protocol(factor_name=factor, use_2020=use_2020)
    elif name == "erdos_straus":
        from cr3echrz.p4rakernel.erdos_straus.main import run_erdos_straus
        n = int(args[0]) if len(args) > 0 else 73
        run_erdos_straus(n=n)
    elif name == "goldbach":
        from cr3echrz.p4rakernel.goldbach.main import run_goldbach
        n = int(args[0]) if len(args) > 0 else 30
        run_goldbach(n=n)
    elif name == "landau":
        from cr3echrz.p4rakernel.landau.main import run_landau
        case = args[0] if len(args) > 0 else "Koebe"
        if case == "Koebe":
            run_landau(name="Koebe", description="f(z)=z/(1-z)^2", omits_finite=True,
                       omitted_value=complex(-0.25,0), is_essential=False)
        elif case == "Dense":
            run_landau(name="Dense", description="f(z)=z+0.1z^2", omits_finite=False,
                       omitted_value=None, is_essential=False)
        elif case == "Picard":
            run_landau(name="Picard", description="f near essential singularity",
                       omits_finite=None, omitted_value=None, is_essential=True)
        else:
            print(f"Unknown Landau case: {case}. Try: Koebe, Dense, Picard")
    elif name == "threebody":
        from cr3echrz.p4rakernel.threebody.main import main as threebody_main
        threebody_main()
    else:
        print(f"Unknown p4rakernel module: {name}")


# ═══════════════════════════════════════════════════════════════════════
#  HELP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def print_help():
    """Print comprehensive help with categorized literal examples."""
    print(BANNER)
    print("Usage:  cr3 [command] [args...]\n")
    print("Any command accepts --help to see its own detailed help with examples.\n")

    print("\u2554" + "\u2550"*62 + "\u2557")
    print("\u2551  META COMMANDS" + " "*45 + "\u2551")
    print("\u255a" + "\u2550"*62 + "\u255d")
    print()
    print("  cr3 --help                       This help")
    print("  cr3 --version                    Show version + opcodes")
    print("  cr3 --list                       List ALL available")
    print("  cr3 --list-theorems              List theorems (13)")
    print("  cr3 --list-ob3ects [domain]      List ob3ects (271)")
    print("  cr3 --analyze <name>             CL8NK structural analysis")
    print()

    print("\u2554" + "\u2550"*62 + "\u2557")
    print("\u2551  P3THEOREM ENGINE — 7 Theorems" + " "*30 + "\u2551")
    print("\u255a" + "\u2550"*62 + "\u255d")
    print()
    print("  cr3 collatz 27                   Collatz (3n+1), seed=27")
    print("  cr3 goldbach 100                 Goldbach, n=100")
    print("  cr3 three_body                   Three-Body, default params")
    print("  cr3 burnside 2 665 1 2 -1 -2     Bounded Burnside, B(2,665)")
    print("  cr3 erdos_straus 73              Erdos-Straus, 4/73")
    print("  cr3 inverse_galois Sn            Inverse Galois, S_n")
    print("  cr3 baum_connes a-T-menable      Baum-Connes, a-T-menable")
    print()

    print("\u2554" + "\u2550"*62 + "\u2557")
    print("\u2551  P4RAKERNEL MODULES — 6 Standalone (Belnap+Frobenius)" + " "*6 + "\u2551")
    print("\u255a" + "\u2550"*62 + "\u255d")
    print()
    print("  Use the 'p4ra' subcommand to guarantee p4rakernel engine dispatch:")
    print()
    print("  cr3 p4ra burnside 2 5            B(2,5) — PARADOX")
    print("  cr3 p4ra burnside 2 665 1 2 -1 -2  B(2,665) — INFINITE (Adian 1979)")
    print("  cr3 p4ra connes R                 Connes: R EMBEDDABLE")
    print("  cr3 p4ra connes \"L(F_2)\" true     Connes: L(F_2) NON-EMBEDDABLE")
    print("  cr3 p4ra connes \"L(F_2)\" false    Connes: L(F_2) PARADOX (pre-2020)")
    print("  cr3 p4ra erdos_straus 5           Erdos-Straus: 4/5 = 1/2+1/4+1/20")
    print("  cr3 p4ra goldbach 30              Goldbach: 30 = 7+23 = 11+19 = 13+17")
    print("  cr3 p4ra landau Koebe             Landau: Koebe omits -1/4")
    print("  cr3 p4ra landau Dense             Landau: Dense (unbounded)")
    print("  cr3 p4ra landau Picard            Landau: Essential singularity")
    print("  cr3 p4ra threebody                Three-Body: figure-8 Poincare section")
    print()
    print("  Unique p4ra modules (connes/landau/threebody) also work directly:")
    print("  cr3 connes R                      Same as cr3 p4ra connes R")
    print("  cr3 landau Koebe                  Same as cr3 p4ra landau Koebe")
    print("  cr3 threebody                     Same as cr3 p4ra threebody")
    print()
    print("  cr3 p4ra --list                   List all 6 p4rakernel modules")
    print("  cr3 p4ra --help                   P4rakernel-specific help")
    print()

    print("\u2554" + "\u2550"*62 + "\u2557")
    print("\u2551  VAULT OB3ECTS — 271 (sample)" + " "*28 + "\u2551")
    print("\u255a" + "\u2550"*62 + "\u255d")
    print()
    print("  cr3 truth_machine                Self-verifying truth evaluator")
    print("  cr3 philosophers_stone           Alchemical Lapis Philosophorum")
    print("  cr3 chaos_magic_servitor         Self-imscribing magical ob3ect")
    print("  cr3 collatz_theorem              Collatz vault ob3ect")
    print("  cr3 monad                        Category theory: monad")
    print("  cr3 topos                        Category theory: topos")
    print("  cr3 hopf                         Hopf algebra")
    print("  cr3 yoneda                       Yoneda embedding")
    print("  cr3 homotopytypetheory           HoTT ob3ect")
    print("  cr3 i_ching_hexagram_ob3ect      I Ching divination")
    print("  cr3 tarot_spread_ob3ect          Tarot divination")
    print("  cr3 goetic_seal_invocation       Goetic invocation")
    print()

    print("\u2554" + "\u2550"*62 + "\u2557")
    print("\u2551  PER-COMMAND HELP" + " "*43 + "\u2551")
    print("\u255a" + "\u2550"*62 + "\u255d")
    print()
    print("  Every command supports --help for detailed examples:")
    print()
    print("  cr3 p4ra --help                   P4rakernel subcommand help")
    print("  cr3 collatz --help                Collatz examples")
    print("  cr3 goldbach --help               Goldbach examples")
    print("  cr3 burnside --help               Burnside examples")
    print("  cr3 connes --help                 Connes examples")
    print("  cr3 erdos_straus --help           Erdos-Straus examples")
    print("  cr3 landau --help                 Landau examples")
    print("  cr3 threebody --help              Three-Body help")
    print("  cr3 --analyze --help              CL8NK analysis help")
    print("  cr3 --list --help                 List command help")
    print("  cr3 truth_machine --help          Truth Machine help")
    print()


def print_command_help(name: str):
    """Print per-command help with literal CLI examples."""
    info = _cmd_help(name)
    if info:
        header, body = info
        print(f"\n  {header}")
        sep = '─' * len(header)
        print(f"  {sep}")
        print()
        for line in body.split('\n'):
            print(f"  {line}")
        print()
    else:
        print(f"\n  No detailed help for '{name}'.")
        print(f"  Try: cr3 --list  to see all available commands.\n")

def print_p4ra_help():
    """Print p4rakernel subcommand help."""
    _, descriptions = load_p4rakernel_modules()

    print(f"\n{'='*60}")
    print(f"  cr3 p4ra — P4RAKERNEL MODULE DISPATCH")
    print(f"{'='*60}")
    print()
    print(f"  Usage:  cr3 p4ra <module> [args...]")
    print(f"          cr3 p4ra --list")
    print(f"          cr3 p4ra --help")
    print()
    print(f"  The p4ra subcommand guarantees dispatch to the p4rakernel engine")
    print(f"  — full Belnap+Frobenius 13-step IMASM bootstrap with μ∘δ=id verification.")
    print(f"  This is the ONLY way to reach p4rakernel versions of modules that also")
    print(f"  exist in the p3theorem engine (burnside, goldbach, erdos_straus).")
    print()

    print(f"  \u2500\u2500 Modules \u2500\u2500")
    print()
    for name, desc in descriptions.items():
        print(f"  cr3 p4ra {name:14s}  {desc}")
    print()
    print(f"  \u2500\u2500 Examples \u2500\u2500")
    print()
    print(f"  cr3 p4ra burnside 2 5             # B(2,5) — PARADOX")
    print(f"  cr3 p4ra burnside 2 665 1 2 -1 -2 # B(2,665) — INFINITE")
    print(f"  cr3 p4ra connes R                 # R: EMBEDDABLE")
    print(f"  cr3 p4ra connes \"L(F_2)\"           # L(F_2): NON-EMBEDDABLE")
    print(f"  cr3 p4ra connes \"L(F_2)\" false     # L(F_2) pre-2020: PARADOX")
    print(f"  cr3 p4ra erdos_straus 73          # 4/73 decomposition")
    print(f"  cr3 p4ra goldbach 100             # 100 = 3+97 = ... (6 pairs)")
    print(f"  cr3 p4ra landau Koebe             # Koebe omits -1/4")
    print(f"  cr3 p4ra landau Dense             # Dense (unbounded)")
    print(f"  cr3 p4ra landau Picard            # Essential singularity")
    print(f"  cr3 p4ra threebody                # Figure-8 Poincaré section")
    print()
    print(f"  \u2500\u2500 Per-module help \u2500\u2500")
    print(f"  cr3 burnside --help         # Burnside help (shows both engines)")
    print(f"  cr3 connes --help           # Connes help")
    print(f"  cr3 p4ra --help             # This help")
    print()


def print_ob3ect_help():
    """Print help for vault ob3ect usage."""
    print("""
  cr3 <ob3ect_name> [dt] [N_period]

  Vault ob3ects are self-verifying programs from the ob3ect/ pipeline.
  Each ob3ect runs a Belnap+Frobenius bootstrap and verifies its own
  algebraic closure (\u03bc\u2218\u03b4=id).

  Examples:
    cr3 truth_machine                  # default params
    cr3 truth_machine 0.5 200          # dt=0.5, N_period=200
    cr3 philosophers_stone             # default params
    cr3 chaos_magic_servitor 0.1 500   # dt=0.1, N_period=500
    cr3 collatz_theorem                # vault version of Collatz
    cr3 monad                          # category theory monad

  List all: cr3 --list-ob3ects
  Filter:   cr3 --list-ob3ects mathematical
""")

# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]

    # ── Global --help / -h ──
    if cmd in ("--help", "-h"):
        print_help()
        return

    # ── Version ──
    if cmd == "--version":
        from cr3echrz import __version__
        print(f"cr3 v{__version__} — Unified cr3echrz Framework")
        print(f"Author: Lando⊗⊙perator | Date: 2026-06-24")
        print(f"12 universal opcodes: {', '.join(OPCODES.values())}")
        return

    # ── Per-command --help: cr3 <name> --help or cr3 <name> -h ──
    # Check if the LAST argument is --help/-h (but NOT for 'p4ra' — handled below)
    if cmd != "p4ra" and len(sys.argv) >= 3 and sys.argv[-1] in ("--help", "-h"):
        subj = cmd
        print_command_help(subj)
        return

    # ═══════════════════════════════════════════════════════════════════
    #  P4RA SUBCOMMAND — guaranteed p4rakernel engine dispatch
    # ═══════════════════════════════════════════════════════════════════
    if cmd == "p4ra":
        p4ra_args = sys.argv[2:]

        # ── cr3 p4ra --help ──
        if not p4ra_args or p4ra_args[0] in ("--help", "-h"):
            print_p4ra_help()
            return

        # ── cr3 p4ra --list ──
        if p4ra_args[0] == "--list":
            try:
                _, descriptions = load_p4rakernel_modules()
                print(f"\n{'='*60}")
                print(f"  P4RAKERNEL STANDALONE MODULES (6)")
                print(f"{'='*60}")
                print()
                for i, (name, desc) in enumerate(descriptions.items(), 1):
                    print(f"  {i}. {name:14s}  {desc}")
                print()
                print(f"  ──── Usage ────")
                print(f"  cr3 p4ra <name> [args...]     run with args")
                print(f"  cr3 p4ra <name> --help        NOT YET — use cr3 <name> --help")
                print(f"  cr3 p4ra --help               this listing")
                print()
            except Exception as e:
                print(f"  p4rakernel: {e}")
            return

        # ── cr3 p4ra <module> [args...] ──
        p4ra_name = p4ra_args[0]
        p4ra_mod_args = p4ra_args[1:]

        # Check for --help on the module
        if p4ra_mod_args and p4ra_mod_args[-1] in ("--help", "-h"):
            print_command_help(p4ra_name)
            return

        try:
            p4ra_mods, p4ra_descs = load_p4rakernel_modules()
            if p4ra_name not in p4ra_mods:
                print(f"\n  Unknown p4rakernel module: '{p4ra_name}'")
                print(f"  Available: {', '.join(p4ra_mods.keys())}")
                print(f"  Try: cr3 p4ra --list\n")
                return

            print(f"\n{'='*60}")
            print(f"  cr3 — P4RAKERNEL MODULE (Belnap+Frobenius 13-step bootstrap)")
            print(f"  {p4ra_name}")
            print(f"  {p4ra_descs.get(p4ra_name, '')}")
            print(f"{'='*60}")
            _run_p4rakernel_module(p4ra_name, p4ra_mod_args)
            return
        except ImportError as e:
            print(f"  Failed to load p4rakernel: {e}")
            return

    # ── List commands ──
    if cmd == "--list-theorems":
        print(f"\n{'='*60}")
        print(f"  MATHEMATICAL THEOREMS")
        print(f"{'='*60}")

        # Unified driver theorems (7)
        print(f"\n  ── p3theorem engine (7 theorems) ──\n")
        try:
            _, _, list_theorems = load_theorem_engine()
            list_theorems()
        except Exception as e:
            print(f"  p3theorem engine: {e}")

        # p4rakernel standalone modules (6)
        print(f"\n  ── p4rakernel standalone modules (6) ──\n")
        try:
            _, descriptions = load_p4rakernel_modules()
            for i, (name, desc) in enumerate(descriptions.items(), 1):
                print(f"  {i}. {name:14s}  {desc}")
        except Exception as e:
            print(f"  p4rakernel: {e}")

        print(f"\n  ── Usage ──")
        print(f"  cr3 <name>              p3theorem engine (default)")
        print(f"  cr3 p4ra <name>         p4rakernel engine (Belnap+Frobenius)")
        print(f"  cr3 <name> --help       show examples\n")
        return

    if cmd == "--list-ob3ects":
        filter_domain = None
        args_after = sys.argv[2:]
        # Check if the user added --help
        if "--help" in args_after or "-h" in args_after:
            print_ob3ect_help()
            return
        if args_after:
            filter_domain = args_after[0]
        _, list_all_ob3ects, _ = load_vault_engine()
        list_all_ob3ects(filter_domain)
        print(f"\n  Usage: cr3 <ob3ect_name>          run an ob3ect")
        print(f"         cr3 <ob3ect_name> --help   show examples\n")
        return

    if cmd == "--list":
        # Check for --help
        if len(sys.argv) >= 3 and sys.argv[-1] in ("--help", "-h"):
            print_command_help("--list")
            return

        print(f"\n{'='*60}")
        print(f"  AVAILABLE — cr3echrz Unified Framework")
        print(f"{'='*60}")

        # Theorems
        print(f"\n  ── MATHEMATICAL THEOREMS (p3theorem engine) ──\n")
        try:
            _, _, list_theorems = load_theorem_engine()
            list_theorems()
        except Exception as e:
            print(f"  p3theorem engine: {e}")

        # p4rakernel modules
        print(f"\n  ── P4RAKERNEL STANDALONE MODULES (6) ──\n")
        try:
            _, descriptions = load_p4rakernel_modules()
            for name, desc in descriptions.items():
                print(f"  {name:14s}  {desc}")
            print(f"\n  Use: cr3 p4ra <name> [args...]")
            print(f"  List: cr3 p4ra --list")
        except Exception as e:
            print(f"  p4rakernel: {e}")

        # Ob3ects summary
        print(f"\n  ── VAULT OB3ECTS (ob3ect_vault engine) ──\n")
        try:
            _, list_all_ob3ects, vault_state = load_vault_engine()
            ob3ects = vault_state.discover_ob3ects()
            print(f"  {len(ob3ects)} ob3ects available")
            print(f"  Filter: cr3 --list-ob3ects [domain]")
            print(f"  Domains: mathematical, magical, alchemical, divinatory,")
            print(f"           computational, physical, biological, theological, ...")
        except Exception as e:
            print(f"  Vault: {e}")

        print(f"\n  ── Quick Start ──")
        print(f"  cr3 collatz 27              cr3 p4ra burnside 2 5")
        print(f"  cr3 goldbach 100             cr3 p4ra connes R")
        print(f"  cr3 erdos_straus 73          cr3 p4ra landau Koebe")
        print(f"  cr3 truth_machine            cr3 --analyze collatz")
        print(f"  cr3 <name> --help             show examples for <name>\n")
        return

    # ── Analyze ──
    if cmd == "--analyze":
        if len(sys.argv) < 3:
            print("Usage: cr3 --analyze <name>")
            print("Try:   cr3 --analyze --help")
            return
        name = sys.argv[2]
        # Check for --help on the target
        if name in ("--help", "-h"):
            print_command_help("--analyze")
            return
        print(f"\n  CL8NK Structural Analysis: {name}")
        print("  " + "─"*50)
        output = run_cl8nk_analysis(name)
        if output:
            print(output)
        else:
            print(f"  No CL8NK data for '{name}'")
        return

    # ── Run theorem/ob3ect ──
    name = cmd
    args = sys.argv[2:]

    # Check if the user asked for help on this command
    if "--help" in args or "-h" in args:
        print_command_help(name)
        return

    # Try theorem engine first (p3theorem)
    try:
        THEOREM_REGISTRY, run_theorem, _ = load_theorem_engine()
        if name in THEOREM_REGISTRY:
            entry = THEOREM_REGISTRY[name]
            kwargs = {}
            param_names = list(entry["params"].keys())
            for i, key in enumerate(param_names):
                if i < len(args):
                    try:
                        kwargs[key] = int(args[i])
                    except ValueError:
                        kwargs[key] = args[i]
            run_theorem(name, **kwargs)
            return
    except ImportError:
        pass

    # Try p4rakernel standalone modules (for modules unique to p4ra: connes, landau, threebody)
    try:
        p4ra_mods, p4ra_descs = load_p4rakernel_modules()
        if name in p4ra_mods:
            print(f"\n{'='*60}")
            print(f"  cr3 — P4RAKERNEL MODULE (Belnap+Frobenius 13-step bootstrap)")
            print(f"  {name}")
            print(f"  {p4ra_descs.get(name, '')}")
            print(f"  (Use 'cr3 p4ra {name}' for explicit p4rakernel dispatch)")
            print(f"{'='*60}")
            _run_p4rakernel_module(name, args)
            return
    except ImportError:
        pass

    # Try vault engine
    try:
        bootstrap_ob3ect, _, _ = load_vault_engine()
        print(f"\n{'='*60}")
        print(f"  cr3 — VAULT OB3ECT")
        print(f"  {name}")
        print(f"{'='*60}")
        result = bootstrap_ob3ect(name, **{
            "dt": float(args[0]) if args else 1.0,
            "N_period": int(args[1]) if len(args) > 1 else 100,
        })
        return
    except ImportError:
        pass

    print(f"Unknown: '{name}'")
    print(f"Use cr3 --list to see available theorems and ob3ects")
    print(f"Use cr3 --help for full usage\n")


if __name__ == "__main__":
    main()
