"""Typer CLI for legal-agent-bench."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from legal_agent_bench.runner import run

app = typer.Typer(no_args_is_help=True, help="Benchmark for tool-using legal-research agents.")
console = Console()


@app.command()
def bench(
    out_dir: Path = typer.Option(Path("runs/latest")),
    n_per_kind: int = typer.Option(10, help="Tasks per task family"),
    seed: int = typer.Option(17),
) -> None:
    """Run the full benchmark."""
    result = run(out_dir, n_per_kind=n_per_kind, seed=seed)
    console.print_json(json.dumps(result["aggregate"], default=str))


@app.command()
def report(out_dir: Path = typer.Option(Path("runs/latest"))) -> None:
    """Print the headline aggregate metrics from the last run."""
    data = json.loads((out_dir / "summary.json").read_text())
    table = Table(title="Aggregate metrics")
    table.add_column("metric")
    table.add_column("value", justify="right")
    for k, v in data["aggregate"].items():
        table.add_row(k, f"{v:.4f}" if isinstance(v, float) else str(v))
    console.print(table)


if __name__ == "__main__":
    app()
