"""Integrazione dei metodi esatti AMPL nella pipeline sperimentale."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from time import perf_counter
from typing import Iterable

from ..core.instance import ProblemInstance


_SAFE_AMPL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class AmplSolveResult:
    """Risultato normalizzato restituito da una esecuzione AMPL."""

    method: str
    status: str
    solve_result_num: int
    feasible: bool
    objective_value: float | None
    runtime_seconds: float
    solver_time_seconds: float | None
    open_sites: tuple[str, ...]
    error: str


@dataclass(frozen=True)
class ExactExperimentResult:
    """Risultato di un metodo esatto su una singola istanza."""

    instance_id: str
    class_id: str
    size: str
    distribution: str
    capacity_level: str
    seed: int
    method: str
    status: str
    solve_result_num: int
    feasible: bool
    objective_value: float | None
    runtime_seconds: float
    solver_time_seconds: float | None
    open_sites: str
    error: str


def _normalize_seed(value: object) -> int:
    if value is None or value == "":
        return -1
    return int(value)


def _format_number(value: float) -> str:
    return format(float(value), ".15g")


def _validate_identifier(identifier: str) -> None:
    if not _SAFE_AMPL_IDENTIFIER.fullmatch(identifier):
        raise ValueError(
            f"Identificativo non compatibile con AMPL: {identifier!r}"
        )


def write_ampl_data(
    instance: ProblemInstance,
    output_path: Path,
) -> None:
    """Esporta una istanza nel formato dati AMPL usato dai modelli."""

    instance.validate()

    for community in instance.communities:
        _validate_identifier(community.id)
    for site in instance.sites:
        _validate_identifier(site.id)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    community_ids = [community.id for community in instance.communities]
    site_ids = [site.id for site in instance.sites]
    distances = instance.distance_matrix()

    lines: list[str] = [
        "data;",
        "",
        "set COMMUNITIES := " + " ".join(community_ids) + ";",
        "set SITES := " + " ".join(site_ids) + ";",
        "",
        f"param p := {instance.p};",
        "",
        "param demand :=",
    ]

    lines.extend(
        f"{community.id} {_format_number(community.demand)}"
        for community in instance.communities
    )
    lines.extend([";", "", "param capacity :="])
    lines.extend(
        f"{site.id} {_format_number(site.capacity)}"
        for site in instance.sites
    )

    lines.extend(
        [
            ";",
            "",
            "param distance:",
            "    " + " ".join(site_ids) + " :=",
        ]
    )

    for community_id in community_ids:
        row = " ".join(
            _format_number(distances[community_id][site_id])
            for site_id in site_ids
        )
        lines.append(f"{community_id} {row}")

    lines.extend([";", "", "end;", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _ampl_path(path: Path) -> str:
    """Converte un percorso Windows in forma leggibile da AMPL."""

    return path.resolve().as_posix()


def _compact_run_text(
    project_root: Path,
    data_path: Path,
    solver: str,
    time_limit_seconds: int,
) -> str:
    model_path = project_root / "models/compact.mod"

    return f"""reset;
model "{_ampl_path(model_path)}";
data "{_ampl_path(data_path)}";

option solver {solver};
option solver_msg 0;
option {solver}_options 'timelim={time_limit_seconds} mipgap=0';

solve;

printf "CMMOFLP_RESULT|method=compact|status=%s|code=%d|objective=%.17g|solver_time=%.17g\\n",
    solve_result, solve_result_num, z, _solve_elapsed_time;
printf "CMMOFLP_OPEN";
for {{j in SITES: y[j] > 0.5}} {{
    printf "|%s", j;
}}
printf "\\n";
"""


def _threshold_run_text(
    project_root: Path,
    data_path: Path,
    solver: str,
    time_limit_seconds: int,
) -> str:
    model_path = project_root / "models/threshold.mod"

    return f"""reset;
model "{_ampl_path(model_path)}";
data "{_ampl_path(data_path)}";

option solver {solver};
option solver_msg 0;
option {solver}_options 'timelim={time_limit_seconds}';

param best_threshold default -1;
param best_y {{SITES}} binary default 0;
param best_x {{COMMUNITIES, SITES}} binary default 0;

for {{candidate in SITES}} {{
    let threshold := safety[candidate];
    solve;

    if solve_result_num < 100 then {{
        if threshold > best_threshold then {{
            let best_threshold := threshold;
            let {{j in SITES}} best_y[j] := y[j];
            let {{i in COMMUNITIES, j in SITES}} best_x[i,j] := x[i,j];
        }}
    }}
}}

if best_threshold >= 0 then {{
    printf "CMMOFLP_RESULT|method=threshold|status=solved|code=0|objective=%.17g|solver_time=%.17g\\n",
        best_threshold, _total_solve_elapsed_time;
    printf "CMMOFLP_OPEN";
    for {{j in SITES: best_y[j] > 0.5}} {{
        printf "|%s", j;
    }}
    printf "\\n";
}}
else {{
    printf "CMMOFLP_RESULT|method=threshold|status=infeasible|code=200|objective=nan|solver_time=%.17g\\n",
        _total_solve_elapsed_time;
    printf "CMMOFLP_OPEN\\n";
}}
"""


def parse_ampl_output(
    output: str,
    expected_method: str,
    runtime_seconds: float,
) -> AmplSolveResult:
    """Estrae i marker macchina prodotti dagli script AMPL."""

    result_line = next(
        (
            line.strip()
            for line in output.splitlines()
            if line.startswith("CMMOFLP_RESULT|")
        ),
        None,
    )
    open_line = next(
        (
            line.strip()
            for line in output.splitlines()
            if line.startswith("CMMOFLP_OPEN")
        ),
        None,
    )

    if result_line is None:
        return AmplSolveResult(
            method=expected_method,
            status="error",
            solve_result_num=-1,
            feasible=False,
            objective_value=None,
            runtime_seconds=runtime_seconds,
            solver_time_seconds=None,
            open_sites=(),
            error="Marker CMMOFLP_RESULT non trovato nell'output AMPL.",
        )

    fields: dict[str, str] = {}
    for token in result_line.split("|")[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value

    method = fields.get("method", "")
    if method != expected_method:
        return AmplSolveResult(
            method=expected_method,
            status="error",
            solve_result_num=-1,
            feasible=False,
            objective_value=None,
            runtime_seconds=runtime_seconds,
            solver_time_seconds=None,
            open_sites=(),
            error=(
                f"Metodo inatteso nel marker AMPL: {method!r}; "
                f"atteso {expected_method!r}."
            ),
        )

    status = fields.get("status", "unknown")
    code = int(fields.get("code", "-1"))

    objective_raw = fields.get("objective", "nan")
    objective_value = (
        None
        if objective_raw.lower() in {"nan", "none", ""}
        else float(objective_raw)
    )

    solver_time_raw = fields.get("solver_time", "")
    solver_time = (
        float(solver_time_raw)
        if solver_time_raw not in {"", "nan"}
        else None
    )

    open_sites: tuple[str, ...] = ()
    if open_line is not None:
        parts = open_line.split("|")
        open_sites = tuple(part for part in parts[1:] if part)

    feasible = status in {"solved", "limit"} and objective_value is not None

    return AmplSolveResult(
        method=method,
        status=status,
        solve_result_num=code,
        feasible=feasible,
        objective_value=objective_value,
        runtime_seconds=runtime_seconds,
        solver_time_seconds=solver_time,
        open_sites=open_sites,
        error="",
    )


def solve_with_ampl(
    instance: ProblemInstance,
    method: str,
    project_root: Path,
    solver: str = "gurobi",
    time_limit_seconds: int = 300,
    ampl_command: str = "ampl",
) -> AmplSolveResult:
    """Esegue il modello compatto o il metodo a soglia tramite AMPL CLI."""

    if method not in {"compact", "threshold"}:
        raise ValueError("Il metodo deve essere 'compact' oppure 'threshold'.")
    if time_limit_seconds <= 0:
        raise ValueError("Il time limit deve essere positivo.")
    if shutil.which(ampl_command) is None:
        raise FileNotFoundError(
            f"Comando AMPL non trovato: {ampl_command!r}."
        )

    with tempfile.TemporaryDirectory(prefix="cmmoflp_ampl_") as temp_directory:
        temp_root = Path(temp_directory)
        data_path = temp_root / "instance.dat"
        run_path = temp_root / "solve.run"

        write_ampl_data(instance, data_path)

        if method == "compact":
            run_text = _compact_run_text(
                project_root,
                data_path,
                solver,
                time_limit_seconds,
            )
        else:
            run_text = _threshold_run_text(
                project_root,
                data_path,
                solver,
                time_limit_seconds,
            )

        run_path.write_text(run_text, encoding="utf-8")

        start = perf_counter()
        completed = subprocess.run(
            [ampl_command, str(run_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=max(time_limit_seconds * 2, time_limit_seconds + 30),
            check=False,
        )
        runtime_seconds = perf_counter() - start

        combined_output = completed.stdout + "\n" + completed.stderr
        parsed = parse_ampl_output(
            combined_output,
            expected_method=method,
            runtime_seconds=runtime_seconds,
        )

        if completed.returncode != 0 and parsed.status != "error":
            return AmplSolveResult(
                method=method,
                status="error",
                solve_result_num=parsed.solve_result_num,
                feasible=False,
                objective_value=None,
                runtime_seconds=runtime_seconds,
                solver_time_seconds=parsed.solver_time_seconds,
                open_sites=(),
                error=combined_output.strip(),
            )

        if parsed.status == "error":
            return AmplSolveResult(
                method=method,
                status="error",
                solve_result_num=parsed.solve_result_num,
                feasible=False,
                objective_value=None,
                runtime_seconds=runtime_seconds,
                solver_time_seconds=parsed.solver_time_seconds,
                open_sites=(),
                error=(parsed.error + "\n" + combined_output.strip()).strip(),
            )

        return parsed


def run_exact_manifest(
    project_root: Path,
    manifest_path: Path,
    output_path: Path,
    methods: Iterable[str] = ("compact", "threshold"),
    solver: str = "gurobi",
    time_limit_seconds: int = 300,
) -> list[ExactExperimentResult]:
    """Esegue i metodi esatti su tutte le istanze del manifest."""

    method_names = list(methods)
    if not method_names:
        raise ValueError("Specificare almeno un metodo esatto.")

    with manifest_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        manifest_rows = list(csv.DictReader(handle))

    results: list[ExactExperimentResult] = []

    for row in manifest_rows:
        instance = ProblemInstance.from_json(
            project_root / row["json_path"]
        )
        instance.metadata.update(
            {
                "class_id": row.get("class_id", ""),
                "size": row.get("size", ""),
                "distribution": row.get("distribution", ""),
                "capacity_level": row.get("capacity_level", ""),
                "seed": _normalize_seed(row.get("seed")),
            }
        )

        for method in method_names:
            solve_result = solve_with_ampl(
                instance=instance,
                method=method,
                project_root=project_root,
                solver=solver,
                time_limit_seconds=time_limit_seconds,
            )

            results.append(
                ExactExperimentResult(
                    instance_id=instance.name,
                    class_id=str(instance.metadata.get("class_id", "")),
                    size=str(instance.metadata.get("size", "")),
                    distribution=str(
                        instance.metadata.get("distribution", "")
                    ),
                    capacity_level=str(
                        instance.metadata.get("capacity_level", "")
                    ),
                    seed=_normalize_seed(instance.metadata.get("seed")),
                    method=method,
                    status=solve_result.status,
                    solve_result_num=solve_result.solve_result_num,
                    feasible=solve_result.feasible,
                    objective_value=solve_result.objective_value,
                    runtime_seconds=solve_result.runtime_seconds,
                    solver_time_seconds=solve_result.solver_time_seconds,
                    open_sites=";".join(solve_result.open_sites),
                    error=solve_result.error,
                )
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(result) for result in results]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)

    return results
