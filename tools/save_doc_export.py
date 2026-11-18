#!/usr/bin/env python3
"""Decode a Claude Docs `export` tool result (saved as a JSON text file) into a real .docx or .pdf.

    python tools/save_doc_export.py <saved_result.txt> <out_path>

The export result is one JSON object whose `data` holds the file as base64. For a .docx this also prints the
number of pictures in word/media/, which CLAUDE.md says must equal the number of charts and diagrams in the doc.
Stdlib only.
"""
import base64, json, pathlib, sys, zipfile


def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    obj = json.loads(src.read_text(encoding="utf-8"))
    data = obj.get("data", obj)
    key = max((k for k, v in data.items() if isinstance(v, str)), key=lambda k: len(data[k]))
    raw = base64.b64decode(data[key], validate=True)
    if data.get("bytes") and data["bytes"] != len(raw):
        sys.exit(f"size mismatch: result says {data['bytes']} bytes, decoded {len(raw)}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    line = f"wrote {out} ({len(raw)} bytes, format {data.get('format')}, notes {data.get('notes')})"
    if out.suffix.lower() == ".docx":
        with zipfile.ZipFile(out) as z:
            media = [n for n in z.namelist() if n.startswith("word/media/")]
            body = z.read("word/document.xml").decode("utf-8", "replace")
        line += f"; word/media pictures: {len(media)}"
        for needle in sys.argv[3:]:
            line += f"; '{needle}' in body: {needle in body}"
    elif raw[:4] != b"%PDF":
        sys.exit("decoded file is not a PDF")
    print(line)


if __name__ == "__main__":
    main()
