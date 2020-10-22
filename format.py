#!/usr/bin/env python


import spectra
import random


def svg(txt):
    return """<?xml version="1.0" encoding="UTF-8"?>\n""" + txt


def vp_with_num(num):
    return f"""
<svg width="26.624mm" height="26.624mm" version="1.1" viewBox="0 0 26.624 26.624" xmlns="http://www.w3.org/2000/svg" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<g transform="translate(-79.965 -77.018)">
<path d="m93.387 78.115a13.265 13.265 0 0 1-13.162 11.696 13.265 13.265 0 0 1-0.10702-0.0057v0.01079a13.265 13.265 0 0 1 13.14 12.729h0.04537a13.265 13.265 0 0 1 13.133-12.731v-0.0092a13.265 13.265 0 0 1-13.05-11.69z" fill="#f55"/>
<text x="93.218376" y="93.151337" fill="#000000" font-family="sans-serif" font-size="10.583px" letter-spacing="0px" stroke-width=".26458" text-align="center" text-anchor="middle" word-spacing="0px" style="line-height:1.25" xml:space="preserve"><tspan x="93.218376" y="93.151337" font-weight="bold" font-size="7.7611px" stroke-width=".26458" text-align="center" text-anchor="middle">{num}</tspan></text>
</g>
</svg>
"""


def resource_with_num(resource, num, color=None, txt_color=None):
    color = color or spectra.html("white")
    txt_color = txt_color or spectra.html("black")

    return f"""
<svg width="26.624mm" height="26.624mm" version="1.1" viewBox="0 0 26.624 26.624" xmlns="http://www.w3.org/2000/svg" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<g transform="translate(-.29497 -1.7176)">
<g transform="translate(-198.31 -337.13)">
<circle cx="211.92" cy="352.16" r="13.142" fill="{color.hexcode}" stroke="#000" stroke-width=".34134"/>
<text x="211.89249" y="350.57233" fill="{txt_color.hexcode}" font-family="sans-serif" font-size="10.583px" letter-spacing="0px" stroke-width=".26458" text-align="center" text-anchor="middle" word-spacing="0px" style="line-height:1.25" xml:space="preserve"><tspan x="211.89249" y="350.57233" stroke-width=".26458" text-align="center" text-anchor="middle">{num}</tspan></text>
<text x="211.92349" y="363.1947" fill="{txt_color.hexcode}" font-family="sans-serif" font-size="10.583px" letter-spacing="0px" stroke-width=".26458" text-align="center" text-anchor="middle" word-spacing="0px" style="line-height:1.25" xml:space="preserve"><tspan x="211.92349" y="363.1947" font-weight="bold" stroke-width=".26458" text-align="center" text-anchor="middle">{resource}</tspan></text>
</g>
</g>
</svg>
"""


def uranium_num(num):
    return resource_with_num("U", num, spectra.html("#00FF00"))


def gold_num(num):
    return resource_with_num("Au", num, spectra.html("#FFFF00"))


def ice_num(num):
    return resource_with_num("Ic", num, spectra.html("#00FFFF"))


def silicate_num(num):
    return resource_with_num("Si", num, spectra.html("#D9D9D9"))


def iron_num(num):
    return resource_with_num("Fe", num, spectra.html("#000"), spectra.html("#FFF"))


def vp_num(num):
    return vp_with_num(num)



funcs = [
    uranium_num,
    gold_num,
    ice_num,
    silicate_num,
    iron_num,
    vp_with_num,
]
content = "\n".join(func(random.randint(1,99)) for func in funcs)
print(svg(f"<svg><g>{content}</g></svg>"))
