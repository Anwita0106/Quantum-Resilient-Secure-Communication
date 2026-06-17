"""
CLI entry point: runs the normal and attack scenarios and writes the
logs + comparison chart into results/ (this is what actually produces
the files the README describes — the original main.py only printed to
the console).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from secure_communication import run_secure_communication
from intrusion_detection import DEFAULT_QBER_THRESHOLD
from visualization import plot_error_rate_comparison

DEFAULT_MESSAGE = "Hello Bob, this is a quantum-resilient secure message"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantum-Resilient Secure Communication demo")
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="Message to send")
    parser.add_argument("--key-length", type=int, default=256, help="Number of raw qubits (n)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_QBER_THRESHOLD,
        help="QBER threshold above which intrusion is flagged",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible runs")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent.parent / "results"),
        help="Directory to write logs and the comparison chart to",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("===== CASE 1: NORMAL COMMUNICATION =====")
    no_attack = run_secure_communication(
        args.message, eve=False, n=args.key_length, threshold=args.threshold, seed=args.seed
    )
    (output_dir / "no_attack_output.txt").write_text(
        "CASE: Normal Communication (No Attack)\n\n" + no_attack["log"] + "\n"
    )

    print("\n===== CASE 2: ATTACK SCENARIO =====")
    seed_for_attack = None if args.seed is None else args.seed + 1
    attack = run_secure_communication(
        args.message, eve=True, n=args.key_length, threshold=args.threshold, seed=seed_for_attack
    )
    (output_dir / "attack_output.txt").write_text(
        "CASE: Attack Scenario (Eavesdropper Present)\n\n" + attack["log"] + "\n"
    )

    chart_path = plot_error_rate_comparison(
        {"No Attack": no_attack["error_rate"], "Attack": attack["error_rate"]},
        output_dir / "error_rate_comparison.png",
    )
    print(f"\nLogs and chart written to: {output_dir}")
    print(f"Chart: {chart_path}")


if __name__ == "__main__":
    main()
