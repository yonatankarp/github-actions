#!/usr/bin/env python3
"""Writes a version's release notes from the pull requests merged since the last version.

    release_notes.py 0.8.0               # the notes for tag v0.8.0
    release_notes.py 0.8.0 origin/main   # a preview, before the tag exists

Options:
    --override PATH      a file published instead, word for word, when it exists, e.g.
                         release-notes/{version}.md ({version} is the version without the v)
    --footer FILE        a file appended after the generated notes
    --scope-section S=H  pull requests with scope S (`feat(S): ...`) go under their own heading H,
                         e.g. 'cli=⌨️ In Terminal'. Repeat it for more than one.
    --dependencies H     list dependency upgrades (`chore(deps): ...`) under heading H,
                         e.g. '📦 Dependencies'. Without it they're left out like other chores.

Each pull request's title says what kind of change it is, which picks its heading: `feat: ...` is a
new feature, `change: ...` an improvement and `fix: ...` a bug fix. Other kinds (docs, chore, ci,
test, refactor) are left out. Any other scope is only a label and changes nothing. A line on top
counts what the version brings. The entry is the first paragraph under the PR's `## Release note`,
or its title when it has none; `none` leaves it out. Links and HTML are taken out of it (a link
keeps its text), and it's read when the notes are made, at tag time, so preview them before
tagging: an edit to a merged PR's description still changes them.

Needs `git` with the tags fetched, and `gh` signed in (GH_TOKEN on CI). A commit with no pull
request number is left out with a warning, and a failed command stops it with one line.
"""
import argparse
import json
import re
import subprocess
import sys

HEADINGS = {"feat": "✨ New features", "change": "🔧 Improvements", "fix": "🐞 Bug fixes"}
KINDS = set(HEADINGS) | {"docs", "chore", "ci", "test", "refactor"}
TITLE = re.compile(r"^(?P<kind>[a-z]+)(\((?P<scope>[^)]*)\))?!?: (?P<text>.+)$")
COUNTED = {"feat": ("new feature", "new features"), "change": ("improvement", "improvements"),
           "fix": ("bug fix", "bug fixes"), "deps": ("dependency update", "dependency updates")}


def run(*args, failed=None):
    """A command's output. When it fails, stops with one line: `failed`, or the command, then why."""
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True).stdout
    except FileNotFoundError:
        sys.exit(f"{args[0]} isn't installed: the release notes need git and gh.")
    except subprocess.CalledProcessError as error:
        why = error.stderr.strip().splitlines()
        sys.exit(f"{failed or ' '.join(args)}: {why[0] if why else f'exit {error.returncode}'}")


def release_note(body):
    """The first paragraph under the PR's `## Release note`, or None when it has none."""
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    match = re.search(r"^##\s*Release notes?\s*$(.*?)(?=^##\s|\Z)", body, flags=re.M | re.S | re.I)
    if not match:
        return None
    return plain(re.split(r"\n\s*\n", match.group(1).strip())[0]) or None


def plain(note):
    """The note with no links or HTML, since anyone can write or edit a PR's description: a link
    `[text](url)` or image `![text](url)` keeps its text, a tag or comment goes, and a bare URL loses
    its `https://` and `www.` so nothing autolinks it. Bold, lists and `code` stay as they are."""
    note = re.sub(r"!?\[((?:[^\[\]]|\[[^\]]*\])*)\]\([^)]*\)", r"\1", note)
    parts = re.split(r"(`[^`\n]*`)", note)  # code spans are left alone: `<name>` isn't a tag
    for i in range(0, len(parts), 2):
        text = re.sub(r"<!--.*?(-->|\Z)", "", parts[i], flags=re.S)
        text = re.sub(r"<((?:https?|ftp)://[^>\s]*)>", r"\1", text)
        text = re.sub(r"</?[A-Za-z][^>]*>", "", text)
        text = re.sub(r"\b(?:https?|ftp)://(?:www\.)?|\bwww\.", "", text, flags=re.I)
        parts[i] = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", text)
    return "\n".join(line.rstrip() for line in "".join(parts).strip().splitlines())


def bullets(note):
    """A note that is already a list stays one; a paragraph becomes one bullet."""
    lines = [line.rstrip() for line in note.splitlines() if line.strip()]
    if lines[0].startswith(("- ", "* ")):
        return ["- " + line[2:] if line.startswith("* ") else line for line in lines]
    return ["- " + " ".join(line.strip() for line in lines)]


def pull_requests(since, ref):
    """The pull request numbers merged from `since` to `ref`, oldest first. `--first-parent` keeps
    to the main line, where a merge commit says `Merge pull request #12` and a squash ends `(#12)`."""
    subjects = run("git", "log", "--first-parent", "--format=%s", f"{since}..{ref}").splitlines()
    numbers = []
    for subject in reversed(subjects):  # oldest first, the order they landed in
        match = re.match(r"Merge pull request #(\d+)", subject) or re.search(r"\(#(\d+)\)$", subject)
        if not match:
            print(f"No pull request number, left out: {subject}", file=sys.stderr)
        elif match.group(1) not in numbers:
            numbers.append(match.group(1))
    return numbers


def render(prs, scope_sections, dependencies=None):
    """The notes for pull requests given as (number, title, body), or "" when none is for people.
    `scope_sections` maps a scope to its own heading, e.g. {"cli": "⌨️ In Terminal"}. `dependencies`
    is the heading for `chore(deps)` pull requests, which are left out without it."""
    sections = {heading: [] for heading in [*HEADINGS.values(), *scope_sections.values()]}
    if dependencies:
        sections[dependencies] = []
    counts = dict.fromkeys(COUNTED, 0)
    elsewhere = dict.fromkeys(scope_sections.values(), 0)
    for number, pr_title, body in prs:
        title = TITLE.match(pr_title)
        if not title or title["kind"] not in KINDS:
            print(f"#{number} has no kind in its title, left out: {pr_title}", file=sys.stderr)
            continue
        note = release_note(body)
        is_dependency = bool(dependencies) and title["kind"] == "chore" and title["scope"] == "deps"
        if (title["kind"] not in HEADINGS and not is_dependency) or (note or "").lower().rstrip(".") == "none":
            continue
        if not note:
            text = plain(title["text"])
            note = text[:1].upper() + text[1:]
        if not note:
            print(f"#{number} has nothing left in its title once the HTML is taken out, left out", file=sys.stderr)
            continue
        lines = bullets(note)
        if is_dependency:
            heading = dependencies
            counts["deps"] += len(lines)
        elif heading := scope_sections.get(title["scope"]):
            elsewhere[heading] += len(lines)
        else:
            heading = HEADINGS[title["kind"]]
            counts[title["kind"]] += len(lines)
        sections[heading] += lines
    body = "\n\n".join(f"### {heading}\n" + "\n".join(lines) for heading, lines in sections.items() if lines)
    return f"{summary(counts, elsewhere)}\n\n{body}" if body else ""


def summary(counts, elsewhere=None):
    """"This update has 7 new features, 2 improvements and 5 bug fixes, plus more in Terminal."
    `elsewhere` counts the entries under each scope's own heading, which reads without its emoji
    and with a small first letter: "⌨️ In Terminal" is "in Terminal"."""
    parts = [f"{n} {COUNTED[kind][n != 1]}" for kind, n in counts.items() if n]
    places = [re.sub(r"^\W+", "", h) for h, n in (elsewhere or {}).items() if n]
    places = and_list([p[:1].lower() + p[1:] for p in places])
    if not places:
        return f"This update has {and_list(parts)}." if parts else ""
    if not parts:
        return f"This update has changes {places}."
    return f"This update has {and_list(parts)}, plus more {places}."


def and_list(items):
    return ", ".join(items[:-1]) + " and " + items[-1] if len(items) > 1 else "".join(items)


def notes(version, ref, override=None, footer=None, scope_sections=None, dependencies=None):
    if override:
        try:
            return open(override.replace("{version}", version)).read().strip()
        except FileNotFoundError:
            pass
    since = run("git", "describe", "--tags", "--abbrev=0", "--match", "v*", f"{ref}^",
                failed=f"No earlier v* tag before {ref} to list the changes from").strip()
    prs = []
    for number in pull_requests(since, ref):
        pr = json.loads(run("gh", "pr", "view", number, "--json", "title,body",
                            failed=f"Couldn't read pull request #{number}"))
        prs.append((number, pr["title"], pr["body"]))
    text = render(prs, scope_sections or {}, dependencies)
    if not text:
        sys.exit(f"Nothing user-facing in {version}: no feat, fix or change pull request"
                 + (" and no dependency update." if dependencies else "."))
    return text + ("\n\n" + open(footer).read().strip() if footer else "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version")
    parser.add_argument("ref", nargs="?")
    parser.add_argument("--override")
    parser.add_argument("--footer")
    parser.add_argument("--scope-section", action="append", default=[], metavar="SCOPE=HEADING")
    parser.add_argument("--dependencies", metavar="HEADING")
    args = parser.parse_args()
    if bad := [s for s in args.scope_section if "=" not in s]:
        parser.error(f"--scope-section {bad[0]!r} isn't scope=heading")
    version = args.version.removeprefix("v")
    print(notes(version, args.ref or f"v{version}", args.override, args.footer,
                dict(s.split("=", 1) for s in args.scope_section), args.dependencies))
