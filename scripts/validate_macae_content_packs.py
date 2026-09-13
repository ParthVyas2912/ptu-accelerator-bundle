"""MCAPS continuation lab: MACAE content-pack conformance validator.

Zero model calls, zero infrastructure. Validates the three continuation-relevant
content packs against the rules the repository's own content_packs/README.md
declares as upload-blocking, plus the four-file knowledge-base wiring chain:

    pack.json  ->  seed_knowledge_bases.py  ->  agent_teams/*.json
                                            ->  Selecting-Team-Config-And-Data.ps1

Findings are reported as FAIL (documented as upload-blocking / 400 by the repo),
WARN (inconsistent but not documented as blocking) or PASS.
"""
import json
import os
import re
import sys

REPO = os.environ.get("MACAE_REPO", r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\repo\continuation\macae")
PACKS = ["contract_compliance", "rfp_evaluation", "hr_onboarding"]

HEX_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

TEAM_REQUIRED = ["id", "team_id", "name", "status", "deployment_name"]
AGENT_REQUIRED = ["input_key", "type", "name"]
TASK_REQUIRED = ["id", "name", "prompt", "created", "creator", "logo"]

findings = []


def add(pack, level, check, detail):
    findings.append({"pack": pack, "level": level, "check": check, "detail": detail})


def seed_kb_names():
    path = os.path.join(REPO, "infra", "scripts", "post-provision", "seed_knowledge_bases.py")
    if not os.path.exists(path):
        return None, None, path
    txt = open(path, encoding="utf8", errors="ignore").read()
    kbs = set(re.findall(r'^\s{4}"([a-z0-9\-]+-kb)":', txt, re.M))
    indexes = set(re.findall(r'"index_name"\s*:\s*"([^"]+)"', txt))
    return kbs, indexes, path


def selecting_script_text():
    path = os.path.join(REPO, "infra", "scripts", "post-provision", "Selecting-Team-Config-And-Data.ps1")
    if not os.path.exists(path):
        return None, path
    return open(path, encoding="utf8", errors="ignore").read(), path


def main():
    kbs, seeded_indexes, kb_path = seed_kb_names()
    sel_txt, sel_path = selecting_script_text()

    if kbs is None:
        add("*", "FAIL", "seed_knowledge_bases.py present", f"missing: {kb_path}")
        kbs, seeded_indexes = set(), set()
    if sel_txt is None:
        add("*", "FAIL", "Selecting-Team-Config-And-Data.ps1 present", f"missing: {sel_path}")
        sel_txt = ""

    for pack in PACKS:
        root = os.path.join(REPO, "content_packs", pack)
        if not os.path.isdir(root):
            add(pack, "FAIL", "pack directory exists", root)
            continue

        # ---- pack.json ---------------------------------------------------
        pack_json_path = os.path.join(root, "pack.json")
        pack_json = None
        declared_indexes = []
        if os.path.exists(pack_json_path):
            try:
                pack_json = json.load(open(pack_json_path, encoding="utf8"))
                add(pack, "PASS", "pack.json parses", "valid JSON")
            except Exception as exc:
                add(pack, "FAIL", "pack.json parses", str(exc))
            if pack_json:
                for key in ("search_indexes", "blob_indexes", "blob_uploads"):
                    for entry in pack_json.get(key, []) or []:
                        if entry.get("index_name"):
                            declared_indexes.append((key, entry["index_name"]))
                        src = entry.get("source")
                        if src:
                            abs_src = os.path.join(root, src.replace("/", os.sep))
                            if not os.path.isdir(abs_src):
                                add(pack, "FAIL", f"{key} source exists", f"{src} -> missing")
                            elif not os.listdir(abs_src):
                                add(pack, "FAIL", f"{key} source non-empty", src)
                            else:
                                add(pack, "PASS", f"{key} source exists", f"{src} ({len(os.listdir(abs_src))} files)")

        # ---- agent team configs -----------------------------------------
        teams_dir = os.path.join(root, "agent_teams")
        team_files = [f for f in os.listdir(teams_dir) if f.lower().endswith(".json")] if os.path.isdir(teams_dir) else []
        if not team_files:
            add(pack, "FAIL", "agent_teams has >=1 JSON team config", teams_dir)

        referenced_kbs = []
        for tf in team_files:
            tpath = os.path.join(teams_dir, tf)
            try:
                team = json.load(open(tpath, encoding="utf8"))
            except Exception as exc:
                add(pack, "FAIL", f"{tf} parses", str(exc))
                continue

            missing = [k for k in TEAM_REQUIRED if k not in team]
            if missing:
                add(pack, "FAIL", f"{tf} team-level required fields", f"missing {missing}")
            else:
                add(pack, "PASS", f"{tf} team-level required fields", "all present")

            tid = str(team.get("team_id", ""))
            if not HEX_UUID.match(tid):
                add(pack, "FAIL", f"{tf} team_id is hex UUID", f"team_id={tid!r}")
            else:
                add(pack, "PASS", f"{tf} team_id is hex UUID", tid)

            if team.get("status") != "visible":
                add(pack, "FAIL", f"{tf} status == visible", f"status={team.get('status')!r} (team will not appear in UI)")
            else:
                add(pack, "PASS", f"{tf} status == visible", "visible")

            agents = team.get("agents", []) or []
            if not agents:
                add(pack, "WARN", f"{tf} has agents", "no agents array")
            keys = []
            for ag in agents:
                amiss = [k for k in AGENT_REQUIRED if k not in ag]
                if amiss:
                    add(pack, "FAIL", f"{tf} agent required fields", f"{ag.get('name', '?')}: missing {amiss}")
                keys.append(ag.get("input_key"))
                if ag.get("use_knowledge_base"):
                    kbname = ag.get("knowledge_base_name")
                    if not kbname:
                        add(pack, "FAIL", f"{tf} KB agent has knowledge_base_name",
                            f"{ag.get('name')}: use_knowledge_base true but no knowledge_base_name")
                    else:
                        referenced_kbs.append((tf, ag.get("name"), kbname))
            dupes = {k for k in keys if keys.count(k) > 1}
            if dupes:
                add(pack, "FAIL", f"{tf} unique agent input_key", f"duplicates {sorted(dupes)}")
            elif keys:
                add(pack, "PASS", f"{tf} unique agent input_key", f"{len(keys)} agents")

            tasks = team.get("starting_tasks", []) or []
            if not tasks:
                add(pack, "FAIL", f"{tf} has >=1 starting_tasks", "none")
            else:
                bad = []
                for t in tasks:
                    tm = [k for k in TASK_REQUIRED if k not in t]
                    if tm:
                        bad.append(f"{t.get('name', '?')}: missing {tm}")
                if bad:
                    add(pack, "FAIL", f"{tf} starting_tasks required fields", "; ".join(bad))
                else:
                    add(pack, "PASS", f"{tf} starting_tasks required fields", f"{len(tasks)} task(s)")

        # ---- KB wiring chain --------------------------------------------
        for tf, agent, kbname in referenced_kbs:
            if kbname in kbs:
                add(pack, "PASS", "agent KB registered in seed_knowledge_bases.py", f"{agent} -> {kbname}")
            else:
                add(pack, "FAIL", "agent KB registered in seed_knowledge_bases.py",
                    f"{agent} -> {kbname!r} not found in KNOWLEDGE_BASES")

        for key, idx in declared_indexes:
            if idx in seeded_indexes:
                add(pack, "PASS", "pack index referenced by a knowledge source", idx)
            else:
                add(pack, "WARN", "pack index referenced by a knowledge source",
                    f"{idx} declared in pack.json ({key}) but no knowledge source references it")

        # ---- deployment script registration ------------------------------
        if sel_txt:
            if pack in sel_txt:
                add(pack, "PASS", "pack registered in Selecting-Team-Config-And-Data.ps1", "referenced")
            else:
                add(pack, "FAIL", "pack registered in Selecting-Team-Config-And-Data.ps1",
                    "pack name not referenced; post-provision menu will not deploy it")

    out = os.environ.get("OUT", "macae-content-pack-validation.json")
    json.dump(findings, open(out, "w", encoding="utf8"), indent=2)

    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    for f in sorted(findings, key=lambda x: (x["pack"], order[x["level"]], x["check"])):
        print(f"{f['level']:4} | {f['pack']:20} | {f['check']:52} | {f['detail']}")
    counts = {lv: sum(1 for f in findings if f["level"] == lv) for lv in ("PASS", "WARN", "FAIL")}
    print(f"\nPASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    print(f"written: {os.path.abspath(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
