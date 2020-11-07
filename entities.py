#!/usr/bin/env python


import os


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