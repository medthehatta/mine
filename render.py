#!/usr/bin/env python


import json
from hashlib import sha1
from io import BytesIO
import base64

import requests
from PIL import Image
from svglib.svglib import SvgRenderer
from lxml import etree
from reportlab.graphics import renderPM


#
# Constants
#


prefix = "/mnt/c/Users/Med/Desktop/matt-asteroids/"


#
# Business
#


def make_deck(
    records, svg_author_front, svg_author_back, uploader,
):
    records = list(records)
    fronts = layout_pils(
        (svg_author_front(record) for record in records),
        num_width=10,
        num_height=7,
    )
    front_url = uploader(fronts)
    backs = layout_pils(
        (svg_author_back(record) for record in records),
        num_width=10,
        num_height=7,
    )
    back_url = uploader(backs)
    return deck(
        front_url,
        back_url,
        num_cards=len(records),
        num_width=10,
        num_height=7,
    )


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


def mkguid(func):
    def _wrapped(*args, **kwargs):
        val = func(*args, **kwargs)
        guid = sha1(str(val).encode("utf-8")).hexdigest()
        val["GUID"] = str(guid).upper()[:6]
        return val

    return _wrapped


@mkguid
def board(image_url):
    return {
      "Name": "Custom_Board",
      "Transform": {
        "posX": 4.29940462,
        "posY": 2.00714159,
        "posZ": 5.20972157,
        "rotX": 0.0116666686,
        "rotY": 179.910736,
        "rotZ": 359.941925,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "scaleZ": 1.0
      },
      "Nickname": "",
      "Description": "",
      "GMNotes": "",
      "ColorDiffuse": {
        "r": 0.7867647,
        "g": 0.7867647,
        "b": 0.7867647
      },
      "Locked": False,
      "Grid": True,
      "Snap": True,
      "IgnoreFoW": False,
      "MeasureMovement": False,
      "DragSelectable": True,
      "Autoraise": True,
      "Sticky": True,
      "Tooltip": True,
      "GridProjection": False,
      "HideWhenFaceDown": False,
      "Hands": False,
      "CustomImage": {
        "ImageURL": image_url,
        "ImageSecondaryURL": "",
        "ImageScalar": 1.0,
        "WidthScale": 0.9524941,
      },
      "LuaScript": "",
      "LuaScriptState": "",
      "XmlUI": "",
    }


@mkguid
def card(card_id):
    return {
        "Name": "Card",
        "Transform": {
            "posX": 0.0,
            "posY": 1.0,
            "posZ": -1.0,
            "rotX": 0.0,
            "rotY": 180.0,
            "rotZ": 180.0,
            "scaleX": 1.0,
            "scaleY": 1.0,
            "scaleZ": 1.0,
        },
        "Nickname": "",
        "Description": "",
        "GMNotes": "",
        "ColorDiffuse": {"r": 1.0, "g": 1.0, "b": 1.0,},
        "Locked": False,
        "Grid": True,
        "Snap": True,
        "IgnoreFoW": False,
        "MeasureMovement": False,
        "DragSelectable": True,
        "Autoraise": True,
        "Sticky": True,
        "Tooltip": True,
        "GridProjection": False,
        "Hands": True,
        "CardID": f"{card_id}",
        "SidewaysCard": False,
        "LuaScript": "",
        "LuaScriptState": "",
        "XmlUI": "",
        "ContainedObjects": [],
    }


@mkguid
def deck(face_url, back_url, num_cards, num_width=10, num_height=7):
    deckids = list(range(100, 100 + num_cards))
    objects = [card(i) for i in deckids]
    return {
        "Name": "DeckCustom",
        "Transform": {
            "posX": 0.5,
            "posY": 1.0,
            "posZ": -1.0,
            "rotX": 0.0,
            "rotY": 180.0,
            "rotZ": 180.0,
            "scaleX": 1.0,
            "scaleY": 1.0,
            "scaleZ": 1.0,
        },
        "Nickname": "",
        "Description": "",
        "GMNotes": "",
        "ColorDiffuse": {"r": 1.0, "g": 1.0, "b": 1.0,},
        "Locked": False,
        "Grid": True,
        "Snap": True,
        "IgnoreFoW": False,
        "MeasureMovement": False,
        "DragSelectable": True,
        "Autoraise": True,
        "Sticky": True,
        "Tooltip": True,
        "GridProjection": False,
        "HideWhenFaceDown": True,
        "Hands": False,
        "SidewaysCard": False,
        "DeckIDs": deckids,
        "CustomDeck": {
            "1": {
                "FaceURL": face_url,
                "BackURL": back_url,
                "NumWidth": num_width,
                "NumHeight": num_height,
                "BackIsHidden": True,
                "UniqueBack": True,
                "Type": 0,
            },
        },
        "LuaScript": "",
        "LuaScriptState": "",
        "XmlUI": "",
        "ContainedObjects": objects,
    }


def game(objects):
    objects = objects or []
    return {
        "SaveName": "",
        "GameMode": "",
        "Date": "",
        "Gravity": 0.5,
        "PlayArea": 0.5,
        "GameType": "",
        "GameComplexity": "",
        "Tags": [],
        "Table": "",
        "Sky": "",
        "Note": "",
        "Rules": "",
        "TabStates": {},
        "ObjectStates": objects,
        "LuaScript": "",
        "LuaScriptState": "",
        "XmlUI": "",
        "VersionNumber": "",
    }


def author_asteroid(record):
    with open("/mnt/c/Users/Med/Desktop/matt-asteroids/asteroid.svg") as f:
        template = f.read()
    svg = template.format(**record)
    return svg_string_to_pil(svg)


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


def asteroid_from_record(record):
    interpolator = raw_interpolate_svg(f"{prefix}/asteroid.svg")
    abbreviations = {
        "Iron": "Fe",
        "Silicates": "Si",
        "Ice": "Ic",
        "Uranium": "U",
        "Gold": "Au",
    }
    triples = [
        k
        for (k, v) in record.items()
        if isinstance(v, (int, float)) and v == 3
    ]
    doubles = [
        k
        for (k, v) in record.items()
        if isinstance(v, (int, float)) and v == 2
    ]
    singles = [
        k
        for (k, v) in record.items()
        if isinstance(v, (int, float)) and v == 1
    ]
    resources_present = triples * 3 + doubles * 2 + singles * 1
    resources = dict(
        zip(
            ["r1", "r2", "r3"], [abbreviations[r] for r in resources_present],
        ),
    )
    return interpolator({"name": record["Name"], **resources})


#
# Entry point
#


def main():
    asteroids = [
        {
            "Gold": 0,
            "Ice": 1.0,
            "Iron": 2.0,
            "Name": "Vesta",
            "Silicates": 0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 1.0,
            "Iron": 1.0,
            "Name": "Pallas",
            "Silicates": 1.0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 1.0,
            "Iron": 0,
            "Name": "Hygiea",
            "Silicates": 2.0,
            "Uranium": 0,
        },
        {
            "Gold": 2.0,
            "Ice": 0,
            "Iron": 1.0,
            "Name": "Psyche",
            "Silicates": 0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 2.0,
            "Iron": 1.0,
            "Name": "Eros",
            "Silicates": 0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 3.0,
            "Iron": 0,
            "Name": "Interamnia",
            "Silicates": 0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 2.0,
            "Iron": 0,
            "Name": "Davida",
            "Silicates": 1.0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 0,
            "Iron": 0,
            "Name": "Sylvia",
            "Silicates": 3.0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 0,
            "Iron": 1.0,
            "Name": "Eunomia",
            "Silicates": 2.0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 0,
            "Iron": 2.0,
            "Name": "Euphrosyne",
            "Silicates": 1.0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 0,
            "Iron": 3.0,
            "Name": "Hesperia",
            "Silicates": 0,
            "Uranium": 0,
        },
        {
            "Gold": 0,
            "Ice": 1.0,
            "Iron": 0,
            "Name": "Comet Fragment",
            "Silicates": 0,
            "Uranium": 2.0,
        },
        {
            "Gold": 1.0,
            "Ice": 0,
            "Iron": 0,
            "Name": "Derelict Satellite",
            "Silicates": 1.0,
            "Uranium": 1.0,
        },
    ]
    my_deck = make_deck(
        asteroids,
        svg_author_front=asteroid_from_record,
        svg_author_back=constant_svg_from_path(
            f"{prefix}/asteroid-backs.svg",
        ),
        uploader=upload_pil_to_imgur_get_url,
    )
    result = json.dumps(game([my_deck]))

    with open(f"{prefix}/saved-objects/Foo.json", "w") as f:
        f.write(result)
    print(result)
    return result


if __name__ == "__main__":
    main()
