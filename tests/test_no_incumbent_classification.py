"""Test della classificazione delle esecuzioni senza incumbent."""

from cmmoflp_nuclear_siting.experiments.grasp_vnd_runner import (
    classify_grasp_vnd_failure,
)


MESSAGE = "GRASP-VND non ha trovato alcuna soluzione ammissibile."


def test_missing_incumbent_at_deadline_is_not_software_error() -> None:
    classification = classify_grasp_vnd_failure(
        exception=ValueError(MESSAGE),
        runtime_seconds=19.99,
        time_limit_seconds=20.0,
    )

    assert classification.status == "limit"
    assert (
        classification.stop_reason
        == "time_limit_no_incumbent"
    )
    assert classification.error == ""


def test_unexpected_exception_remains_software_error() -> None:
    classification = classify_grasp_vnd_failure(
        exception=RuntimeError("errore inatteso"),
        runtime_seconds=1.0,
        time_limit_seconds=20.0,
    )

    assert classification.status == "error"
    assert classification.stop_reason == "error"
    assert classification.error == "errore inatteso"
