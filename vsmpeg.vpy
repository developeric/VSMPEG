#!/usr/bin/env python3

# vapoursynth
from vapoursynth import core
# std
import os
import math
import functools
import binascii
import subprocess
# pip packages
from pvsfunc.psourcer import PSourcer
from pvsfunc.pdeinterlacer import PDeinterlacer
from pvsfunc.pdebox import PDebox
from pvsfunc.pdecimate import PDecimate
from pvsfunc.helpers import anti_file_prefix
from pyd2v import D2V
import havsfunc
import yaml


"""
Documentation and information:
https://rlaphoenix.github.io/VSMPEG
"""

"""
# /!\ Do not edit beyond here unless you know what your doing /!\
"""

# get config from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# load file path with PSourcer
psourcer = PSourcer(config["Input"], debug=config["DEBUG"])
sourcer = psourcer.sourcer
clip = psourcer.clip

# >>> Scan

# Deinterlace
clip = PDeinterlacer(
    clip,
    kernel=eval(config["Deinterlacer"]),
    kernel_args=config["Deinterlacers"][config["Deinterlacer"]],
    debug=config["DEBUG"]
).clip

# >>> Frame-rate

# Decimation
if config["Decimation"]["Enabled"]:
    clip = PDecimate(
        clip=clip,
        per_vob_id=config["Decimation"]["ResetCyclePerVobCell"],
        mode={False: 0, True: 1}[len(config["Decimation"]["Offsets"]) == 0],
        cycle=config["Decimation"]["Cycle"],
        offsets=config["Decimation"]["Offsets"] or None,
        debug=config["DEBUG"]
    ).clip

# >>> Color

# Chroma location
if type(config["ChromaLocation"]) is int:
    if config["ChromaLocation"] < 0 or config["ChromaLocation"] > 5:
        raise ValueError("ChromaLocation value is invalid. Must be an integer between 0..5")
    clip = core.resize.Point(
        clip,
        chromaloc=config["ChromaLocation"],
        chromaloc_in=clip.get_frame(0).props["_ChromaLocation"]
    )

# >>> Resizing and Cropping

# Debox
if config["Debox"]["Enabled"]:
    for mode, aspect, offset in config["Debox"]["Operations"]:
        clip = PDebox(
            clip,
            aspect_ratio=aspect,
            mode={"w": 0, "h": 1}[mode],
            offset=offset
        ).clip

# Crop
if config["Crop"]["Enabled"]:
    clip = core.std.Crop(clip, **{k.lower(): v for k,v in config["Crop"] if k != "Enabled"})

# Aspect Ratio
if config["AspectRatio"]["Value"]:
    ar = config["AspectRatio"]["Value"]
    if ar == "DAR":
        if sourcer == "core.d2v.Source":
            d2v = D2V(clip.get_frame(0).props["PVSFilePath"])
            ar = d2v.settings["Aspect_Ratio"]
        else:
            # todo ; needs support for other codecs, perhaps via pymediainfo?
            ar = None
    if ar:
        ar = [int(x) for x in ar.split(":")]
        axis = config["AspectRatio"]["Axis"].lower()
        clip = eval("core.resize." + config["AspectRatio"]["Kernel"])(
            clip=clip,
            **{axis: {
                "w": math.ceil(clip.height * (ar[0] / ar[1])),
                "h": math.ceil(clip.width / (ar[0] / ar[1]))
            }[axis[0]]}
        )

# >>> Machine Learning and Networks

# VSGAN
if config["VSGAN"]["Enabled"]:
    import mvsfunc
    from vsgan import VSGAN
    if config["VSGAN"]["Comparer"]:
        og = clip
    for enabled, model, device, chunk, presample, resample in config["VSGAN"]["Operations"]:
        if not enabled:
            continue
        vsgan_device = VSGAN(model)
        vsgan_device.load_model(anti_file_prefix(model))
        if presample:
            clip = core.resize.Spline36(
                clip,
                width=presample * (clip.width / clip.height),
                height=presample
            )
        clip = vsgan_device.run(clip, chunk=chunk)
        if resample:
            clip = core.resize.Spline36(
                clip,
                width=resample * (clip.width / clip.height),
                height=resample
            )
    if config["VSGAN"]["ConvertToYUV"]:
        clip = mvsfunc.ToYUV(clip, css="4:2:0", depth=clip.format.bits_per_sample)
    if config["VSGAN"]["Comparer"]:
        # match the res and format between the before clip and current clip
        if og.height != clip.height or og.width != clip.width:
            og = core.resize.Spline64(og, width=clip.width, height=clip.height)
        if og.format.id != clip.format.id:
            # assuming RGB24 as VSGAN returns an RGB24 clip, maybe check if RGB or YUV
            og = mvsfunc.ToRGB(og, depth=clip.format.bits_per_sample)
        clip = eval("core.std." + config["VSGAN"]["Comparer"])([
            core.text.Text(og, "Original"),
            core.text.Text(clip, "Result")
        ])

clip.set_output()
