#!/usr/bin/env python


import json
from hashlib import sha1
from io import BytesIO
import base64
import os

import requests
from PIL import Image
from svglib.svglib import SvgRenderer
from lxml import etree
from reportlab.graphics import renderPM
from cytoolz import partition_all
from gspread.client import Client

import sheets


#
# Constants
#


prefix = os.path.dirname(os.path.abspath(__file__))


#
# Business
#


def svg_string_to_pil(svg):
    root = etree.fromstring(svg.encode("utf-8"))
    doc = SvgRenderer("").render(root)
    return renderPM.drawToPIL(doc)


def base64_pil(pil, fmt="JPEG"):
    buffered = BytesIO()
    pil.save(buffered, format=fmt)
    return base64.b64encode(buffered.getvalue())


def upload_pil_to_imgur_get_url(pil):
    r = upload_pil_to_imgur(pil)
    r.raise_for_status()
    return r.json().get("data", {}).get("link")


def upload_pil_to_imgur(pil, fmt="JPEG"):
    client_id = "54bdf86b7b696fe"
    return requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {client_id}"},
        data={"type": "base64", "image": base64_pil(pil)},
    )


def layout_pils(
    pils, num_width=10, num_height=7, xpad=0, ypad=0,
):
    pils = iter(pils)
    first = next(pils)

    width = first.width
    height = first.height
    total_width = width * num_width + xpad * num_width
    total_height = height * num_height + ypad * num_width

    output = Image.new(mode="RGB", size=(total_width, total_height),)

    output.paste(first, box=(0, 0))

    for vert in range(num_height):
        for horiz in range(0, num_width):
            if (horiz, vert) == (0, 0):
                # Skip the top-left, because that was `first`
                continue
            try:
                pil = next(pils)
            except StopIteration:
                break
            pos = (
                int(width + xpad) * horiz,
                int(height + ypad) * vert,
            )
            output.paste(pil, box=pos)

    return output


def generic_back(name):
    generator = raw_interpolate_svg(f"{prefix}/svg_templates/generic-back.svg")
    return lambda _: generator({"name": name})


def raw_interpolate_svg(path):
    with open(path) as f:
        template = f.read()

    def _raw_interpolate_svg(record):
        svg = template.format(**record)
        return svg_string_to_pil(svg)

    return _raw_interpolate_svg


def constant_pil(path):
    pil = Image.open(path)
    return lambda _: pil


def constant_svg_from_path(path):
    with open(path) as f:
        svg_data = f.read()
    pil = svg_string_to_pil(svg_data)
    return lambda _: pil
