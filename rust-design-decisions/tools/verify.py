#!/usr/bin/env python3
"""
Machine verification for the Rust Design Decisions site.

Every <pre data-verify="..."> code block on every page is extracted with the
SAME HTML scanner the contract checker uses (tools/check.py), compiled and
run with the pinned toolchain, and the outcome is written to the verify
report that tools/check.py cross-checks (E_VERIFY).

Modes:
  rust  ok    compiles, runs, exits 0            (data-expect optional, stdout)
  rust  fail  compilation fails                  (data-error required, e.g. E0382;
                                                  data-expect optional, stderr)
  rust  run   compiles, runs, exits 0            (data-expect optional, stdout)
  rust  panic compiles, runs, panics             (data-expect optional, stderr)
  rust  cont  appended to the previous rust chain head; verified jointly
  rust  skip  not verified                       (data-reason required)
  c     c-ok    compiles (gcc preferred), runs, exits 0
  c     c-asan  clang -fsanitize=address -g; run must trip the report
  c     c-tsan  clang -fsanitize=thread -g (via setarch -R); run must trip
               the ThreadSanitizer warning

All C compiles are -O0 (plain -g): optimization runs before sanitizer
instrumentation and can delete the bug being verified. Sanitizer runs execute
under setarch -R: under full ASLR this clang's ASan and TSan runtimes can die
before producing a report.

Rust fragments without `fn main` are wrapped in one automatically. Results
are content-hash cached under /tmp/opencode so repeat runs are fast; the
cache never substitutes for a first real run of changed code.

Usage:
  python3 tools/verify.py [--root DIR] [--pages a.html ...] [--report PATH] [--jobs N]

Default root: parent of tools/. Default report: manifest "verify_report".
--pages re-verifies only the named pages and preserves other pages' entries.
Exit code: 0 when every verified block passed, 1 otherwise.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

import check  # same directory: shared scanning, single source of truth

CACHE_DIR = "/tmp/opencode/rdd-verify-cache"
# Bump when verification behavior (compilers, flags, expectations) changes,
# so stale cached results can never mask a runner change.
CACHE_VERSION = "4"
SCRATCH_ROOT = "/tmp/opencode"
RUST_EDITION = "2021"
COMPILE_TIMEOUT = 120
RUN_TIMEOUT = 30
SAN_RUN_TIMEOUT = 120


# -- toolchain -------------------------------------------------------------------

def find_tool(env_var, names, extra=()):
    cand = os.environ.get(env_var)
    if cand and os.path.exists(cand):
        return cand
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    for x in extra:
        xp = os.path.expanduser(x)
        if os.path.exists(xp):
            return xp
    return None


def tool_version(path):
    if not path:
        return None
    try:
        p = subprocess.run([path, "--version"], capture_output=True,
                           text=True, timeout=30)
        return (p.stdout or p.stderr).strip().splitlines()[0]
    except Exception:
        return None


# -- subprocess helper -----------------------------------------------------------

def run_cmd(cmd, timeout, env=None):
    """Returns (returncode, stdout, stderr, timed_out)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.returncode, p.stdout or "", p.stderr or "", False
    except subprocess.TimeoutExpired:
        return None, "", "", True
    except FileNotFoundError:
        return None, "", f"executable not found: {cmd[0]}", False


def first_error_line(stderr):
    for line in stderr.splitlines():
        if line.startswith("error"):
            return line.strip()
    return (stderr.strip().splitlines() or ["?"])[0][:120]


# -- cache -------------------------------------------------------------------------

def cache_key(lang, mode, error, expect, code):
    blob = json.dumps([CACHE_VERSION, lang, mode, error, expect, code],
                      ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def cache_get(key):
    p = os.path.join(CACHE_DIR, key + ".json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def cache_put(key, value):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        p = os.path.join(CACHE_DIR, key + ".json")
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        pass  # cache is best-effort


# -- rust verification --------------------------------------------------------------

def verify_rust(code, mode, error, expect, tools, workdir):
    if tools.rustc is None:
        return False, "rustc not found (install via rustup)"
    if "fn main" not in code:
        code = "fn main() {\n" + code + "\n}"
    src = os.path.join(workdir, "prog.rs")
    binary = os.path.join(workdir, "prog")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)
    rc, out, err, to = run_cmd(
        [tools.rustc, "--edition", RUST_EDITION, "-o", binary, src],
        COMPILE_TIMEOUT)
    if to:
        return False, "rustc timed out"
    if mode == "fail":
        if rc == 0:
            return False, "compiled successfully but the page claims rejection"
        if error and error not in err:
            return False, f"stderr does not contain {error}"
        if expect and expect not in err:
            return False, f"stderr does not contain {expect!r}"
        return True, f"rejected as expected ({first_error_line(err)})"
    if rc != 0:
        return False, f"compile failed: {first_error_line(err)}"
    rc, out, err, to = run_cmd([binary], RUN_TIMEOUT)
    if to:
        return False, "timed out while running"
    if mode == "ok":
        if rc != 0:
            return False, f"ran with exit code {rc}"
        return True, "compiled and ran (exit 0)"
    if mode == "run":
        if rc != 0:
            return False, f"ran with exit code {rc}"
        if expect and expect not in out:
            return False, f"stdout does not contain {expect!r}"
        return True, "compiled and ran (exit 0)"
    if mode == "panic":
        if rc == 0:
            return False, "exited 0 but the page claims a panic"
        if "panicked at" not in err:
            return False, "stderr contains no panic message"
        if expect and expect not in err:
            return False, f"stderr does not contain {expect!r}"
        return True, "panicked as expected"
    return False, f"unknown rust mode {mode!r}"


# -- c verification -------------------------------------------------------------------

def verify_c(code, mode, expect, tools, workdir):
    # Sanitizers need clang: gcc 11 folds the dangling-return pattern that the
    # stack-use-after-return check depends on. Plain runs use gcc to match the
    # captured corpus. -O0 everywhere: optimization runs before sanitizer
    # instrumentation and can delete the very bug being verified. Sanitizer
    # runs execute under setarch -R: this clang's ASan runtime segfaults under
    # full ASLR on this kernel (roughly a third of runs, with or without the
    # fake-stack option), so verdicts would be flaky without it.
    cc = (tools.gcc or tools.clang) if mode == "c-ok" else (tools.clang or tools.gcc)
    if cc is None:
        return False, "no C compiler found (clang or gcc)"
    src = os.path.join(workdir, "prog.c")
    binary = os.path.join(workdir, "prog")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)

    if mode == "c-ok":
        cmd = [cc, "-g", "-o", binary, src]
        rc, out, err, to = run_cmd(cmd, COMPILE_TIMEOUT)
        if to or rc != 0:
            return False, f"compile failed: {first_error_line(err)}"
        rc, out, err, to = run_cmd([binary], RUN_TIMEOUT)
        if to:
            return False, "timed out while running"
        if rc != 0:
            return False, f"ran with exit code {rc}"
        if expect and expect not in out:
            return False, f"stdout does not contain {expect!r}"
        return True, "compiled and ran (exit 0)"

    if mode == "c-asan":
        cmd = [cc, "-fsanitize=address", "-g", "-o", binary, src]
        rc, out, err, to = run_cmd(cmd, COMPILE_TIMEOUT)
        if to or rc != 0:
            return False, f"compile failed: {first_error_line(err)}"
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_stack_use_after_return=1"
        if tools.setarch:
            argv = [tools.setarch, platform.machine(), "-R", binary]
        else:
            argv = [binary]
        rc, out, err, to = run_cmd(argv, SAN_RUN_TIMEOUT, env=env)
        if to:
            return False, "timed out under AddressSanitizer"
        if rc == 0 or "ERROR: AddressSanitizer" not in err:
            return False, "AddressSanitizer reported nothing"
        if expect and expect not in err:
            return False, f"sanitizer output does not contain {expect!r}"
        return True, "AddressSanitizer caught the bug as expected"

    if mode == "c-tsan":
        cmd = [cc, "-fsanitize=thread", "-g", "-o", binary, src]
        rc, out, err, to = run_cmd(cmd, COMPILE_TIMEOUT)
        if to or rc != 0:
            return False, f"compile failed: {first_error_line(err)}"
        if tools.setarch:
            argv = [tools.setarch, platform.machine(), "-R", binary]
        else:
            argv = [binary]
        rc, out, err, to = run_cmd(argv, SAN_RUN_TIMEOUT)
        if to:
            return False, "timed out under ThreadSanitizer"
        if "WARNING: ThreadSanitizer" not in err:
            return False, "ThreadSanitizer reported no race"
        if expect and expect not in err:
            return False, f"sanitizer output does not contain {expect!r}"
        return True, "ThreadSanitizer caught the race as expected"

    return False, f"unknown c mode {mode!r}"


# -- job collection ---------------------------------------------------------------------

def collect_jobs(root, pages):
    """One job per chain head (cont blocks are folded into their head)."""
    jobs = []
    for fname in pages:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            print(f"warning: {fname} does not exist, skipping", file=sys.stderr)
            continue
        s, _ = check.scan_file(path)
        current = None
        for pre in s.pres:
            if not pre["has_code"]:
                continue
            lang = check.code_language(pre)
            mode = pre["verify"]
            if lang == "c":
                if mode in ("c-ok", "c-asan", "c-tsan"):
                    jobs.append({"page": fname, "line": pre["line"],
                                 "lang": "c", "mode": mode,
                                 "error": "", "expect": pre["expect"],
                                 "code": pre["text"]})
                continue
            if lang != "rust":
                continue
            if mode == "cont":
                if current is not None:
                    current["code"] += "\n" + pre["text"]
                continue
            if mode in check.CHAIN_HEAD_MODES:
                current = {"page": fname, "line": pre["line"],
                           "lang": "rust", "mode": mode,
                           "error": pre["error"], "expect": pre["expect"],
                           "code": pre["text"]}
                jobs.append(current)
            else:
                current = None  # skip / invalid: check.py flags those
    return jobs


# -- execution -----------------------------------------------------------------------------

def execute_job(job, tools):
    key = cache_key(job["lang"], job["mode"], job["error"], job["expect"],
                    job["code"])
    hit = cache_get(key)
    if hit is not None:
        return job, hit["ok"], hit["detail"], True
    workdir = tempfile.mkdtemp(prefix="rdd-verify-", dir=SCRATCH_ROOT)
    try:
        if job["lang"] == "rust":
            ok, detail = verify_rust(job["code"], job["mode"], job["error"],
                                     job["expect"], tools, workdir)
        else:
            ok, detail = verify_c(job["code"], job["mode"], job["expect"],
                                  tools, workdir)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    cache_put(key, {"ok": ok, "detail": detail})
    return job, ok, detail, False


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify every claimed code block")
    ap.add_argument("--root", default=None, help="site root (default: parent of tools/)")
    ap.add_argument("--pages", nargs="*", default=None,
                    help="re-verify only these pages (entries for others are kept)")
    ap.add_argument("--report", default=None, help="report path override")
    ap.add_argument("--jobs", type=int, default=4, help="parallel workers")
    args = ap.parse_args(argv)

    os.makedirs(SCRATCH_ROOT, exist_ok=True)
    root = os.path.abspath(args.root or os.path.join(os.path.dirname(__file__), ".."))
    manifest = check.load_json(os.path.join(root, "manifest.json"))
    report_rel = args.report or manifest.get("verify_report", "tools/verify-report.json")
    report_path = os.path.normpath(os.path.join(root, report_rel))
    if args.report and not os.path.isabs(args.report):
        report_path = os.path.normpath(os.path.join(os.getcwd(), args.report))

    if args.pages is not None:
        page_list = args.pages
    else:
        page_list = sorted(f for f in os.listdir(root)
                           if f.endswith(".html") and os.path.isfile(os.path.join(root, f)))

    tools = type("Tools", (), {})()
    tools.rustc = find_tool("RUSTC", ["rustc"], ["~/.cargo/bin/rustc"])
    tools.clang = find_tool("CLANG", ["clang"])
    tools.gcc = find_tool("GCC", ["gcc"])
    tools.setarch = find_tool("SETARCH", ["setarch"])

    jobs = collect_jobs(root, page_list)
    print(f"verifying {len(jobs)} block(s) across {len(page_list)} page(s) "
          f"(rustc: {tools.rustc or 'MISSING'}, cc: {tools.clang or tools.gcc or 'MISSING'})")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = [ex.submit(execute_job, j, tools) for j in jobs]
        for fut in concurrent.futures.as_completed(futs):
            job, ok, detail, cached = fut.result()
            status = "ok  " if ok else "FAIL"
            src = " (cached)" if cached else ""
            print(f"  [{status}] {job['page']}:{job['line']} {job['mode']:<6} {detail}{src}")
            results.append((job, ok, detail))

    # merge: keep other pages' entries, replace re-verified pages' entries
    old_entries = []
    reverified = set(page_list)
    if os.path.exists(report_path) and not args.report:
        try:
            old = check.load_json(report_path)
            old_entries = [e for e in old.get("entries", [])
                           if e.get("page") not in reverified]
        except Exception:
            old_entries = []

    entries = old_entries + [
        {"page": job["page"], "line": job["line"], "mode": job["mode"],
         "ok": ok, "detail": detail,
         "expect": (job["error"] if job["mode"] == "fail"
                    else (job["expect"] or None))}
        for (job, ok, detail) in results
    ]
    entries.sort(key=lambda e: (e["page"], e["line"]))

    report = {
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .isoformat(timespec="seconds"),
        "toolchain": {
            "rustc": tool_version(tools.rustc),
            "clang": tool_version(tools.clang),
            "gcc": tool_version(tools.gcc),
        },
        "entries": entries,
    }
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    tmp = report_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, report_path)

    failures = [r for r in results if not r[1]]
    print(f"\nreport: {report_path} ({len(entries)} entries)")
    if failures:
        print(f"VERIFY FAIL: {len(failures)} of {len(results)} block(s) failed")
        return 1
    print(f"VERIFY PASS: {len(results)} block(s) verified, 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
