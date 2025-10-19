Architected by doctorcodex/ drferdiiskandar\nDeveloped by doctorcodex/ drferdiiskandar\n\n
# Architected by doctorcodex/ drferdiiskandarndar
# Developed by doctorcodex/ drferdiiskandarndar
"""
Memory Helper (manual, zero-deps)
Menyimpan "memori" sebagai file yang terbaca manusia:
  - discussions/<YYYY-MM-DD>.md  (notes, decisions, issues)
  - hub/version.json              (context updates + bump revision)

Pakai:
  python3 scripts/mem.py note "isi catatan"
  python3 scripts/mem.py decision "isi keputusan"
  python3 scripts/mem.py issue "deskripsi isu/ketergantungan"
  python3 scripts/mem.py context key "value baru"

Opsional set tanggal (override):
  MEM_DATE=2025-10-19 python3 scripts/mem.py note "isi"
"""
import os, sys, json, datetime

def today_str():
    d = os.environ.get("MEM_DATE")
    if d:
        return d
    return datetime.date.today().strftime("%Y-%m-%d")

BASE = os.getcwd()
DISCUSS_DIR = os.path.join(BASE, "hub", "discussions")
VERSION_PATH = os.path.join(BASE, "hub", "version.json")

def ensure_discussion_file(date_str):
    os.makedirs(DISCUSS_DIR, exist_ok=True)
    path = os.path.join(DISCUSS_DIR, f"{date_str}.md")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                "Architected by doctorcodex/ drferdiiskandarndar\n"
                "Developed by doctorcodex/ drferdiiskandarndar\n\n"
                f"# discussion — {date_str}\n\n"
                "## notes\n\n"
                "## decisions\n\n"
                "## issues\n\n"
            )
    return path

def append_under_section(md_path, section, line):
    # Simple text append: ensure section exists; append under it.
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    if f"## {section}\n" not in content:
        content += f"\n## {section}\n\n"

    # Append at end (ke sederhanaan). Tidak melakukan reflow isi lama.
    if not content.endswith("\n"):
        content += "\n"
    content += f"- {line}\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

def load_version():
    if os.path.exists(VERSION_PATH):
        try:
            with open(VERSION_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_version(obj):
    with open(VERSION_PATH, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def cmd_note(msg):
    d = today_str()
    p = ensure_discussion_file(d)
    append_under_section(p, "notes", msg)
    print(f"[mem] note saved to {p}")

def cmd_decision(msg):
    d = today_str()
    p = ensure_discussion_file(d)
    append_under_section(p, "decisions", msg)
    print(f"[mem] decision saved to {p}")

def cmd_issue(msg):
    d = today_str()
    p = ensure_discussion_file(d)
    append_under_section(p, "issues", msg)
    print(f"[mem] issue saved to {p}")

def cmd_context(key, value):
    d = today_str()
    v = load_version()
    # ensure credits persist
    v.setdefault("_credit_architect", "Architected by doctorcodex/ drferdiiskandarndar")
    v.setdefault("_credit_developed", "Developed by doctorcodex/ drferdiiskandarndar")
    # bump revision counter & set version date to latest discussion date
    rev = int(v.get("revision", 0)) + 1
    v["revision"] = rev
    v["version"] = d
    # save key/value under "context"
    ctx = v.get("context", {})
    ctx[key] = value
    v["context"] = ctx
    # also log the change for traceability
    updates = v.get("context_updates", [])
    updates.append({"date": d, "key": key, "value": value, "rev": rev})
    v["context_updates"] = updates
    save_version(v)
    # mirror to discussions as a decision
    p = ensure_discussion_file(d)
    append_under_section(p, "decisions", f'context update: {key} = "{value}" (rev {rev})')
    print(f"[mem] context updated: {key} = {value}; version.json revision {rev}")

def main():
    if len(sys.argv) < 3:
        print("usage: mem.py [note|decision|issue|context] <args...>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "note":
        cmd_note(" ".join(sys.argv[2:]))
    elif cmd == "decision":
        cmd_decision(" ".join(sys.argv[2:]))
    elif cmd == "issue":
        cmd_issue(" ".join(sys.argv[2:]))
    elif cmd == "context":
        if len(sys.argv) < 4:
            print("usage: mem.py context <key> <value>", file=sys.stderr)
            sys.exit(1)
        cmd_context(sys.argv[2], " ".join(sys.argv[3:]))
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
