#!/usr/bin/env python


import os


from cytoolz import partition_all
from render_pil import raw_interpolate_svg


#
# Constants
#


prefix = os.path.dirname(os.path.abspath(__file__))


#
# Business
#


def asteroid_from_record(record):
    interpolator = raw_interpolate_svg(f"{prefix}/svg_templates/asteroid.svg")
    abbreviations = {
        "Iron": "Fe",
        "Silicates": "Si",
        "Ice": "Ic",
        "Uranium": "U",
        "Gold": "Au",
    }
    triples = [k for (k, v) in record.items() if v == "3"]
    doubles = [k for (k, v) in record.items() if v == "2"]
    singles = [k for (k, v) in record.items() if v == "1"]
    resources_present = triples * 3 + doubles * 2 + singles * 1
    resources = dict(
        zip(
            ["r1", "r2", "r3"], [abbreviations[r] for r in resources_present],
        ),
    )
    return interpolator({"name": record["Name"], **resources})


def module_from_record(record):
    fields = [
        "Rules Text",
        "Adjacent",
        "Anywhere 1",
        "Anywhere 2",
        "Not Adjacent",
        "Iron",
        "Ice",
        "Silicate",
        "VP",
        "Gold",
        "Uranium",
    ]
    defaults = {k: "" for k in fields}
    data = {**defaults, **record}
    interpolator = raw_interpolate_svg(f"{prefix}/svg_templates/module.svg")
    return interpolator(data)


def upgrade_from_record(record):
    fields = [
        "Rules Text",
        "Iron",
        "Ice",
        "Silicate",
        "VP",
        "Gold",
        "Gold Out",
        "Uranium",
        "Uranium Out",
    ] + [f"Mod{i}" for i in range(1, 8+1)]
    modules_present = {
        k: v
        for (k, v) in record.items()
        if k not in fields and v.strip()
    }
    modules = {
        f"Mod{i}": f"{v} {k}"
        for (i, (k, v)) in enumerate(modules_present.items())
    }
    defaults = {k: "" for k in fields}
    data = {**defaults, **modules, **record}
    interpolator = raw_interpolate_svg(f"{prefix}/svg_templates/upgrade.svg")
    return interpolator(data)


def action_from_record(record):
    fields = [
        "Name",
        "Settlement",
        "Rules text",
    ]
    defaults = {k: "" for k in fields}
    data = {**defaults, **record}
    rules_text_split = split_to_multiple_fields(
        data["Rules text"],
        field_name="Rules text",
        chars_per=24,
        max_lines=7,
    )
    data.update(rules_text_split)
    interpolator = raw_interpolate_svg(f"{prefix}/svg_templates/action.svg")
    return interpolator(data)


def split_to_multiple_fields(text, field_name, chars_per, max_lines):
    segments = []
    current_segment = []
    for word in text.split():
        if sum(len(w) for w in current_segment) + len(word) < chars_per:
            current_segment.append(word)
        else:
            segments.append(" ".join(current_segment))
            current_segment = [word]
    segments.append(" ".join(current_segment))

    default = {f"{field_name}#{i}": "" for i in range(1, max_lines+1)}
    populated = {
        f"{field_name}#{i}": "".join(segment)
        for (i, segment) in enumerate(segments, start=1)
        if segment
    }
    if len(populated) > max_lines:
        raise ValueError(
            f"Need more lines; {max_lines} available, "
            f"{len(populated)} required."
        )
    else:
        return {**default, **populated}
