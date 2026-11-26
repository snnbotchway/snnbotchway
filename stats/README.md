# How these numbers are counted

Every day a script counts the pull requests I authored that were merged, in public and private repositories, from November 2025 on. Only totals are published: [`stats.json`](stats.json) holds no repository names, titles or code.

## Pull requests

A merged PR counts once. These are left out because they carry work already counted, or none of mine:

- PRs from one long-lived branch to another (`staging` to `main`, back-merges)
- PRs that sync a fork with its upstream project
- reverts and dependency bumps

## Lines shipped

A PR's size is the lines it added plus the lines it removed, in files a person writes. These files are left out:

- lockfiles
- generated code: API clients, ORM and SQL query output, contract ABIs and type bindings, files marked generated or vendored in `.gitattributes`
- build output, minified files, snapshots, migrations, deployment records
- images, fonts and other binary files
- data files (JSON, YAML, CSV, HTML and similar) with more than 500 changed lines
- lines that only moved with a renamed file, when GitHub detects the rename

**Size bands:** small is under 100 lines, medium 100 to 1,000, large 1,000 to 5,000, extra large 5,000 or more.

**Lines chart:** each PR counts at most 5,000 lines in the lines chart, so a few huge PRs can't carry the total. The "lines shipped" figure has no cap.

**Tests:** the share of lines in test files, such as files under `tests/`, `*.test.ts`, `*_test.go` and `*.t.sol`.

The rules are in [`collect.py`](collect.py).
