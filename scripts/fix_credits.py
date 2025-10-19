Architected by doctorcodex/ drferdiiskandar\nDeveloped by doctorcodex/ drferdiiskandar\n\n
#!/usr/bin/env python3
# Architected by doctorcodex/ drferdiiskandarndar
# Developed by doctorcodex/ drferdiiskandarndar
"""
fix_credits.py — normalize branding & (optionally) lowercase filenames.

WHAT IT DOES
- Replaces any old branding with:
    Architected by doctorcodex/ drferdiiskandarndar
    Developed by doctorcodex/ drferdiiskandarndar
- Ensures the two credit lines exist at the top of every text file.
- (Optional) Lowercases filenames safely (skips .git/ and archives/).

USAGE
  # dry run (no file changes, report only)
  python3 scripts/fix_credits.py --check

  # apply text fixes only (recommended first step)
  python3 scripts/fix_credits.py --apply

  # also lowercase filenames (careful on case-sensitive FS)
  python3 scripts/fix_credits.py --apply --lowercase
"""
import os, re, sys, argparse, pathlib, shutil

ARCH_LINE = "Architected by doctorcodex/ drferdiiskandarndar"
DEV_LINE  = "Developed by doctorcodex/ drferdiiskandarndar"
HEADER    = ARCH_LINE + "\\n" + DEV_LINE + "\\n\\n"

TEXT_EXT = {".md",".mdx",".json",".ts",".tsx",".js",".mjs",".cjs",
            ".sh",".py",".yaml",".yml",".txt",".css",".html",".mts",".mtsx"}

SKIP_DIRS = {".git","node_modules","archives",".next","dist","build"}

def is_text_file(path: str) -> bool:
    ext = pathlib.Path(path).suffix.lower()
    return ext in TEXT_EXT

def normalize_credits(content: str) -> str:
    out = content
    # Normalize any 'Architected by doctorcodex/ drferdiiskandarNE
    out = re.sub(r'Architected by doctorcodex/ drferdiiskandar\\n]*', ARCH_LINE, out, flags=re.IGNORECASE)
    # Normalize any 'Developed by doctorcodex/ drferdiiskandarNE
    out = re.sub(r'Developed by doctorcodex/ drferdiiskandar\\n]*', DEV_LINE, out, flags=re.IGNORECASE)
    # Ensure header exists at top
    stripped = out.lstrip()
    if not stripped.startswith("Architected by doctorcodex/ drferdiiskandarnsure the first two lines exactly match
        lines = out.splitlines()
        i = 0
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i < len(lines):
            if lines[i].strip() != ARCH_LINE:
                lines[i] = ARCH_LINE
            # Ensure second line exists and matches
            if i+1 >= len(lines):
                lines.insert(i+1, DEV_LINE)
            else:
                if lines[i+1].strip() != DEV_LINE:
                    lines[i+1] = DEV_LINE
            out = "\\n".join(lines) + ("\n" if out.endswith("\\n") else "")
    return out

def walk_files(base):
    for dirpath, dirnames, filenames in os.walk(base):
        # prune skip dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="dry-run only")
    ap.add_argument("--apply", action="store_true", help="write changes to disk")
    ap.add_argument("--lowercase", action="store_true", help="also lowercase filenames (careful)")
    args = ap.parse_args()

    base = os.getcwd()
    changed = []
    renamed = []

    # Text normalization
    for path in walk_files(base):
        if not is_text_file(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        newc = normalize_credits(content)
        if newc != content:
            changed.append(path)
            if args.apply:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(newc)

    # Lowercase pass
    if args.lowercase:
        import shutil, pathlib
        for path in sorted(walk_files(base), key=len, reverse=True):
            rel = os.path.relpath(path, base)
            parts = rel.split(os.sep)
            if any(p in {".git","node_modules","archives",".next","dist","build"} for p in parts):
                continue
            new_rel = rel.lower()
            if rel != new_rel:
                new_abs = os.path.join(base, new_rel)
                os.makedirs(os.path.dirname(new_abs), exist_ok=True)
                if args.apply:
                    shutil.move(path, new_abs)
                renamed.append((rel, new_rel))

    # Report
    print("[fix_credits] files_changed:", len(changed))
    for p in changed[:20]:
        print("  ~", p)
    if len(changed) > 20:
        print("  ...")

    if args.lowercase:
        print("[fix_credits] files_renamed:", len(renamed))
        for a,b in renamed[:20]:
            print(f"  mv {a} -> {b}")
        if len(renamed) > 20:
            print("  ...")

    if not args.apply:
        print("\\nNOTE: this was a dry run. Use --apply to write changes.")

if __name__ == "__main__":
    main()
