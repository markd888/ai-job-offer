import json
import subprocess
import sys
from pathlib import Path

GOLDEN = Path(__file__).resolve().parent / "golden" / "evaluate-position"


def run_grade(tmp_path, results):
    rf = tmp_path / "results.json"
    rf.write_text(json.dumps(results))
    proc = subprocess.run(
        [sys.executable, str(GOLDEN / "grade.py"), str(rf)],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout


def perfect_results():
    out = []
    for p in sorted((GOLDEN / "cases").glob("*.json")):
        case = json.loads(p.read_text())
        if "label" not in case:
            continue
        l = case["label"]
        out.append({"id": case["id"], "tier": l["tier"], "score": l["score"],
                    "matched_filter": l["hard_filter"]})
    return out


def test_perfect_run_passes(tmp_path):
    code, out = run_grade(tmp_path, perfect_results())
    assert code == 0
    assert "tier agreement: 9/9" in out


def test_two_tier_misses_fail_gate(tmp_path):
    results = perfect_results()
    flipped = 0
    for r in results:
        if r["tier"] in ("P0", "P1") and flipped < 2:
            r["tier"] = "P2"; flipped += 1
    code, out = run_grade(tmp_path, results)
    assert code == 1          # 7/9 = 0.78 < 0.8
    assert "FAIL" in out


def test_missed_filter_fails_even_with_perfect_tiers(tmp_path):
    results = perfect_results()
    for r in results:
        if r["matched_filter"]:
            r["matched_filter"] = None
            r["tier"] = "P1"
            break
    code, out = run_grade(tmp_path, results)
    assert code == 1
    assert "filter" in out.lower()


def test_wrong_filter_reported_fails_even_though_truthy(tmp_path):
    # A run that fires the WRONG hard filter (e.g. reports the crypto filter
    # on the relocation case) must still fail — matched_filter being merely
    # truthy is not enough, it must match the case's own label.
    results = perfect_results()
    filter_results = [r for r in results if r["matched_filter"]]
    assert len(filter_results) == 3  # sanity: three filter cases exist
    a, b = filter_results[0], filter_results[1]
    a["matched_filter"] = b["matched_filter"]  # a now reports b's filter, wrongly
    code, out = run_grade(tmp_path, results)
    assert code == 1
    assert "MISSED FILTER" in out


def test_missing_case_reported(tmp_path):
    code, out = run_grade(tmp_path, perfect_results()[:-1])
    assert code == 1
    assert "missing" in out.lower()


def run_grade_raw(tmp_path, text):
    rf = tmp_path / "results.json"
    rf.write_text(text)
    proc = subprocess.run(
        [sys.executable, str(GOLDEN / "grade.py"), str(rf)],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def test_non_json_results_file_fails_cleanly(tmp_path):
    code, out, err = run_grade_raw(tmp_path, "not json at all {{{")
    assert code == 2
    assert "results.json" in err
    assert "not valid JSON" in err


def test_non_list_json_results_fails_cleanly(tmp_path):
    code, out, err = run_grade_raw(tmp_path, json.dumps({"id": "p0-clean"}))
    assert code == 2
    assert "results.json" in err
    assert "dict" in err


# ---- scoring v2 runs ---------------------------------------------------------
QUOTE = "Designed and shipped the price-test framework"  # verbatim in the frozen profile


def perfect_v2():
    out = []
    for p in sorted((GOLDEN / "cases").glob("*.json")):
        case = json.loads(p.read_text())
        l = case["label_v2"]
        reqs = [{"requirement": f, "status": "FAIL", "jd_quote": "x"} for f in l["must_fail"]]
        reqs += [{"requirement": kw, "status": "UNKNOWN", "jd_quote": "not stated"} for kw in l["must_unknown"]]
        dims = {k: {"evidence_class": allowed[0],
                    "evidence": [] if allowed[0] == "MISSING" else [{"quote": QUOTE, "source": "profile"}]}
                for k, allowed in l["evidence"].items()}
        fit = None if not l["fit_range"] else sum(l["fit_range"]) / 2
        out.append({"id": case["id"], "eligibility": l["eligibility"], "requirements": reqs,
                    "dimensions": dims, "attractiveness": l["attractiveness"][0],
                    "fit_score": fit if fit is not None else 50, "tier": l["tier"]})
    return out


def test_v2_perfect_run_passes(tmp_path):
    code, out = run_grade(tmp_path, perfect_v2())
    assert code == 0, out
    assert "scoring v2 run" in out and "tier: 32/32" in out


def test_v2_unknown_reported_as_fail_fails(tmp_path):
    results = perfect_v2()
    r = next(r for r in results if any(q["status"] == "UNKNOWN" for q in r["requirements"]))
    for q in r["requirements"]:
        if q["status"] == "UNKNOWN":
            q["status"] = "FAIL"
    r["eligibility"] = "blocked"; r["tier"] = "P2"
    code, out = run_grade(tmp_path, results)
    assert code == 1 and "false blocks: 1" in out


def test_v2_invented_quote_fails(tmp_path):
    results = perfect_v2()
    d = next(d for r in results for d in r["dimensions"].values() if d["evidence"])
    d["evidence"][0]["quote"] = "Ran a 40-person payments org at a FTSE 100 bank"
    code, out = run_grade(tmp_path, results)
    assert code == 1 and "untraced quote" in out


def test_v2_missed_fail_fails(tmp_path):
    results = perfect_v2()
    r = next(r for r in results if r["eligibility"] == "blocked")
    r["requirements"] = []
    code, out = run_grade(tmp_path, results)
    assert code == 1 and "missed FAIL" in out
