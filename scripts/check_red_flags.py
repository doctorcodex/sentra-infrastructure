Architected by doctorcodex/ drferdiiskandar\nDeveloped by doctorcodex/ drferdiiskandar\n\n
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Override tanggal (YYYY-MM-DD) untuk pengecekan")
    args = parser.parse_args()

    today = None
        if args.date:
            today = args.date
        else:
            sessions_dir_probe = os.path.join(base, "hub", "sessions")
            try:
                sess = sorted([s for s in os.listdir(sessions_dir_probe) if re.match(r"\d{4}-\d{2}-\d{2}\.md$", s)])
            except FileNotFoundError:
                sess = []
            if sess:
                today = sess[-1].replace(".md","")
            else:
                today = datetime.date.today().strftime("%Y-%m-%d")
    base = os.getcwd()

    # 1) Version mismatch
    version_path = os.path.join(base, "hub", "version.json")
    version_json = {}
    if os.path.exists(version_path):
        try:
            version_json = json.load(open(version_path, "r", encoding="utf-8"))
        except Exception:
            version_json = {}
    version_str = version_json.get("version", "")

    sessions_dir = os.path.join(base, "hub", "sessions")
    sessions = [s for s in list_dir(sessions_dir) if re.match(r"\d{4}-\d{2}-\d{2}\.md$", s)]
    latest_session = sessions[-1] if sessions else None
    latest_session_date = latest_session.replace(".md","") if latest_session else ""

    red_flags = []
    if version_str and latest_session_date and version_str != latest_session_date:
        red_flags.append("Version mismatch.")

    # 2) Missing daily logs
    missing = []
    for a in AGENTS:
        p = os.path.join(base, "agents", a, "log.md")
        txt = read_text(p)
        if not txt:
            missing.append(a)
            continue
        # cari header "# log — YYYY-MM-DD" (em dash)
        headers = [f"# log — {today}", f"# log - {today}"]
        if not any(h in txt for h in headers):
            missing.append(a)
    if missing:
        for m in missing:
            red_flags.append(f"Missing log: {m}.")

    # 3) NOTAM entries today
    notam_dir = os.path.join(base, "ops", "notam")
    today_notams = [n for n in list_dir(notam_dir) if (today in n)]
    if today_notams:
        red_flags.append("Incidents detected: " + ", ".join(today_notams) + ".")

    # 4) Completion rates (optional heuristic)
    # Hitung rata-rata jika ada checkbox di log
    rates = []
    for a in AGENTS:
        p = os.path.join(base, "agents", a, "log.md")
        txt = read_text(p)
        if not txt:
            continue
        # Ambil hanya blok untuk hari ini jika pengguna memisah per hari, jika tidak ya pakai seluruh file
        # Heuristik sederhana
        checked = len(re.findall(r"(?m)^\s*-\s*\[x\]", txt, flags=re.IGNORECASE))
        unchecked = len(re.findall(r"(?m)^\s*-\s*\[\s\]", txt))
        total = checked + unchecked
        if total > 0:
            rate = round(100.0 * checked / total, 1)
            rates.append(rate)
    avg_rate = round(sum(rates)/len(rates), 1) if rates else None

    if avg_rate is not None and avg_rate < 50.0:
        red_flags.append("Low completion.")

    # 5) Tulis ke ops/health/daily.md (append)
    health_path = os.path.join(base, "ops", "health", "daily.md")
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

    # append separator jika file sudah ada dan tidak kosong
    try:
        exists = os.path.exists(health_path) and os.path.getsize(health_path) > 0
    except Exception:
        exists = False
    with open(health_path, "a", encoding="utf-8") as f:
        if exists:
            f.write("\n---\n\n")
        f.write("\n".join(lines))

    # stdout ringkas
    print(f"[{today}] red-flags:")
    if red_flags:
        for rf in red_flags:
            print(f"- {rf}")
    else:
        print("- none")
    if avg_rate is not None:
        print(f"avg completion: {avg_rate}%")

if __name__ == "__main__":
    main()
