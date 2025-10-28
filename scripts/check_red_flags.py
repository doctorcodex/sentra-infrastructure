# Architected by doctorcodex/ drferdiiskandar
# Developed by doctorcodex/ drferdiiskandar
# Architected by doctorcodex/ drferdiiskandarndar
# Developed by doctorcodex/ drferdiiskandarndar
"""
Red-Flag Checker (manual, zero-deps)
- Cek: version mismatch (hub/version.json vs latest session)
- Cek: missing daily log per agent (berdasar header "# log — YYYY-MM-DD")
- Cek: NOTAM hari ini
- Hitung completion rate (opsional) dari checklist "- [x]" vs "- [ ]" jika ada
- Tulis ringkasan ke ops/health/daily.md (append)

Pakai:
  python3 scripts/check_red_flags.py [--date YYYY-MM-DD]
"""
import os, re, json, sys, argparse, datetime

AGENTS = ["dexton","kade","rex","atlas","nova","aurora"]

def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def list_dir(path):
    try:
        return sorted(os.listdir(path))
    except FileNotFoundError:
        return []

def get_today_date(base_dir, date_override=None):
    if date_override:
        return date_override
    sessions_dir_probe = os.path.join(base_dir, "hub", "sessions")
    try:
        sess = sorted([s for s in os.listdir(sessions_dir_probe) if re.match(r"\d{4}-\d{2}-\d{2}\.md$", s)])
    except FileNotFoundError:
        sess = []
    if sess:
        return sess[-1].replace(".md","")
    else:
        return datetime.date.today().strftime("%Y-%m-%d")

def check_version_mismatch(base_dir):
    version_path = os.path.join(base_dir, "hub", "version.json")
    version_json = {}
    if os.path.exists(version_path):
        try:
            with open(version_path, "r", encoding="utf-8") as f:
                version_json = json.load(f)
        except Exception:
            version_json = {}
    version_str = version_json.get("version", "")

    sessions_dir = os.path.join(base_dir, "hub", "sessions")
    sessions = [s for s in list_dir(sessions_dir) if re.match(r"\d{4}-\d{2}-\d{2}\.md$", s)]
    latest_session = sessions[-1] if sessions else None
    latest_session_date = latest_session.replace(".md","") if latest_session else ""

    if version_str and latest_session_date and version_str != latest_session_date:
        return "Version mismatch."
    return None

def check_missing_logs(base_dir, today, agents):
    missing = []
    for a in agents:
        p = os.path.join(base_dir, "agents", a, "log.md")
        txt = read_text(p)
        if not txt:
            missing.append(a)
            continue
        headers = [f"# log — {today}", f"# log - {today}"]
        if not any(h in txt for h in headers):
            missing.append(a)
    return [f"Missing log: {m}." for m in missing]

def check_notam_entries(base_dir, today):
    notam_dir = os.path.join(base_dir, "ops", "notam")
    today_notams = [n for n in list_dir(notam_dir) if (today in n)]
    if today_notams:
        return "Incidents detected: " + ", ".join(today_notams) + "."
    return None

def calculate_completion_rate(base_dir, agents):
    rates = []
    for a in agents:
        p = os.path.join(base_dir, "agents", a, "log.md")
        txt = read_text(p)
        if not txt:
            continue
        checked = len(re.findall(r"(?m)^\s*-\s*\[x\]", txt, flags=re.IGNORECASE))
        unchecked = len(re.findall(r"(?m)^\s*-\s*\[\s\]", txt))
        total = checked + unchecked
        if total > 0:
            rate = round(100.0 * checked / total, 1)
            rates.append(rate)
    return round(sum(rates)/len(rates), 1) if rates else None

def check_completion_rate(avg_rate):
    if avg_rate is not None and avg_rate < 50.0:
        return "Low completion."
    return None

def write_health_report(health_path, today, avg_rate, red_flags):
    lines = []
    lines.append("Architected by doctorcodex/ drferdiiskandarndar")
    lines.append("Developed by doctorcodex/ drferdiiskandarndar")
    lines.append("")
    lines.append(f"# health — {today}")
    lines.append(f"- completion_rate: {avg_rate if avg_rate is not None else '-'}")
    if red_flags:
        for rf in red_flags:
            lines.append(f"- {rf}")
    else:
        lines.append("- no red flags.")
    lines.append("- notes: -")
    lines.append("")

    try:
        exists = os.path.exists(health_path) and os.path.getsize(health_path) > 0
    except Exception:
        exists = False
    with open(health_path, "a", encoding="utf-8") as f:
        if exists:
            f.write("\n---\n\n")
        f.write("\n".join(lines))

def print_summary(today, red_flags, avg_rate):
    print(f"[{today}] red-flags:")
    if red_flags:
        for rf in red_flags:
            print(f"- {rf}")
    else:
        print("- none")
    if avg_rate is not None:
        print(f"avg completion: {avg_rate}%")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Override tanggal (YYYY-MM-DD) untuk pengecekan")
    args = parser.parse_args()

    base = os.getcwd()
    today = get_today_date(base, args.date)

    red_flags = []

    version_mismatch = check_version_mismatch(base)
    if version_mismatch:
        red_flags.append(version_mismatch)

    missing_logs = check_missing_logs(base, today, AGENTS)
    red_flags.extend(missing_logs)

    notam_entries = check_notam_entries(base, today)
    if notam_entries:
        red_flags.append(notam_entries)

    avg_rate = calculate_completion_rate(base, AGENTS)
    low_completion = check_completion_rate(avg_rate)
    if low_completion:
        red_flags.append(low_completion)

    health_path = os.path.join(base, "ops", "health", "daily.md")
    write_health_report(health_path, today, avg_rate, red_flags)

    print_summary(today, red_flags, avg_rate)

if __name__ == "__main__":
    main()
