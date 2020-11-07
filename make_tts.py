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
import render_pil
import entities


#
# Constants
#


prefix = os.path.dirname(os.path.abspath(__file__))


#
# Business
#


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
            "scaleZ": 1.0,
        },
        "Nickname": "",
        "Description": "",
        "GMNotes": "",
        "ColorDiffuse": {"r": 0.7867647, "g": 0.7867647, "b": 0.7867647},
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


def make_deck(
    records, pil_author_front, pil_author_back, uploader,
):
    records = list(records)
    fronts = render_pil.layout_pils(
        (pil_author_front(record) for record in records),
        num_width=10,
        num_height=7,
    )
    front_url = uploader(fronts)
    backs = render_pil.layout_pils(
        (pil_author_back(record) for record in records),
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


def make_decks(
    records, pil_author_front, pil_author_back, uploader,
):
    record_batches = partition_all(70, records)
    return [
        make_deck(batch, pil_author_front, pil_author_back, uploader)
        for batch in record_batches
    ]


#
# Entry point
#


generators = {
    "asteroid": entities.asteroid_from_record,
    "module": entities.module_from_record,
    "upgrade": entities.upgrade_from_record,
    "action": entities.action_from_record,
}


def main():
    gsheet_client = Client(sheets.login("sheets-credentials.json"))

    with open(f"{prefix}/decks/decks.json") as f:
        manifest = json.load(f)

    all_decks = {}

    for (name, src) in manifest.items():
        print(f"Processing {name}...")
        generator = generators.get(name)
        # Just skip those types that we don't know how to generate
        # yet
        if not generator:
            print(
                f"(skipping {name} as we don't know how to generate these yet)"
            )
            continue
        records = sheets.entries(gsheet_client, **src)
        decks = make_decks(
            records,
            pil_author_front=generator,
            pil_author_back=render_pil.generic_back(name),
            uploader=render_pil.upload_pil_to_imgur_get_url,
        )

        with open(f"{prefix}/decks/out/{name}.json", "w") as f:
            json.dump(game(decks), f)
        print(json.dumps(decks))

        all_decks[name] = decks

    return all_decks


if __name__ == "__main__":
    main()
