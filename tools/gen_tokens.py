#!/usr/bin/env python3
"""Generate assets/tokens.css (and the FIELD constants in assets/field.js) from tokens.json. Stdlib only.

    python3 tools/gen_tokens.py path/to/tokens.json assets/tokens.css [assets/field.js]

:root holds the light values of every token, [data-theme="dark"] overrides the colour tokens only,
and a prefers-color-scheme block gives dark colours without JavaScript. Aliases ("{step-0}") become
var() references. Each type style becomes custom properties (--t-<name>-size, -line, -weight,
-tracking) and a .t-<name> class built from them, so site.css can set Quarto's markup in the same
styles with var(--t-...). Fonts become @font-face rules that point at fonts/<basename>.woff2
(relative to tokens.css; convert the TTFs with tools/sync-ds.sh).

With a third argument, the line of assets/field.js that carries FIELD_MARK is rewritten from the
`field` tokens, so a field-token change reaches the live field without hand edits.
"""
import json, pathlib, re, sys

HEADER = "/* Natalie Gill — generated from tokens.json by tools/gen_tokens.py; do not edit */"
FIELD_MARK = "/* @generated from the field tokens by tools/gen_tokens.py */"


def field_js(t):
    """The FIELD object of bundle.js, with values taken from the field tokens."""
    f = {k["name"].removeprefix("field-"): k["value"] for k in t["field"]["tokens"]}
    m = re.fullmatch(r"B(\d+)/S(\d+)", f["rule"])
    assert m, f"unexpected field-rule {f['rule']}"
    num = lambda v: re.fullmatch(r"(-?[\d.]+)(px|ms)?", str(v)).group(1)
    return ("  var FIELD = { rule: { B: [%s], S: [%s] }, rainEvery: %s, rainSize: %s, speed: %s, easeMs: %s, cell: %s, density: %s }; %s"
            % (", ".join(m.group(1)), ", ".join(m.group(2)), num(f["rain-every"]), num(f["rain-size"]), num(f["speed"]),
               num(f["ease"]), num(f["cell"]), num(f["density"]), FIELD_MARK))


def write_field(t, path):
    p = pathlib.Path(path)
    lines = p.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if FIELD_MARK in l]
    if len(hits) != 1:
        sys.exit(f"{path}: expected exactly one line containing {FIELD_MARK!r}, found {len(hits)}")
    lines[hits[0]] = field_js(t)
    p.write_text("\n".join(lines), encoding="utf-8")


def val(v):
    m = re.fullmatch(r"\{([a-z0-9-]+)\}", v)
    return f"var(--{m.group(1)})" if m else v


def block(sel, decls, indent=""):
    body = "".join(f"{indent}  {d}\n" for d in decls)
    return f"{indent}{sel} {{\n{body}{indent}}}\n"


def main(src, out, field=None):
    t = json.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    colors = t["color"]["tokens"]
    names = {c["name"] for c in colors}
    light, dark = [], []
    for c in colors:
        v = c["value"]
        if isinstance(v, str):  # alias: repeated in the dark blocks so it re-resolves where data-theme is set
            assert v.strip("{}") in names, f"undefined alias {v} in {c['name']}"
            light.append(f"--{c['name']}: {val(v)};")
            dark.append(f"--{c['name']}: {val(v)};")
        else:
            light.append(f"--{c['name']}: {v['light']};")
            dark.append(f"--{c['name']}: {v['dark']};")
    other = [f"--{k['name']}: {k['value']};" for g in ("spacing", "radius", "field") for k in t[g]["tokens"]]
    fams = [f"--font-{k}: {v};" for k, v in t["type"]["families"].items()]
    styles = [(g, s) for g in t["type"]["groups"] for s in g["styles"]]
    typ = []
    for g, s in styles:
        n = s["name"]
        typ += [f"--t-{n}-size: {s['fontSize']};", f"--t-{n}-line: {s['lineHeight']};",
                f"--t-{n}-weight: {s['fontWeight']};", f"--t-{n}-tracking: {s.get('letterSpacing', 'normal')};"]

    css = [HEADER, ""]
    for f in t["type"]["fonts"]:
        file = pathlib.PurePosixPath(f["file"]).with_suffix(".woff2").name
        css.append(block("@font-face", [f'font-family: "{f["family"]}";', f"src: url(\"fonts/{file}\") format(\"woff2\");",
                                        f"font-weight: {f['weight']};", f"font-style: {f.get('style', 'normal')};",
                                        "font-display: swap;"]))
    css.append(block(":root", ["color-scheme: light;"] + light + other + fams + typ))
    css.append(block('[data-theme="dark"]', ["color-scheme: dark;"] + dark))
    css.append("@media (prefers-color-scheme: dark) {\n"
               + block(':root:not([data-theme="light"])', ["color-scheme: dark;"] + dark, "  ") + "}\n")
    for g, s in styles:
        n = s["name"]
        d = [f"font-family: var(--font-{g['family']});", f"font-size: var(--t-{n}-size);",
             f"line-height: var(--t-{n}-line);", f"font-weight: var(--t-{n}-weight);",
             f"letter-spacing: var(--t-{n}-tracking);"]
        if n == "label":
            d.append("text-transform: uppercase;")
        css.append(block(f".t-{n}", d))
    pathlib.Path(out).write_text("\n".join(css), encoding="utf-8")
    if field:
        write_field(t, field)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: gen_tokens.py tokens.json tokens.css [field.js]")
    main(*sys.argv[1:])
