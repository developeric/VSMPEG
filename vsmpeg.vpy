#!/usr/bin/env python3

import functools
import importlib
import math
import os

import vapoursynth as vs
import yaml
from pvsfunc.helpers import anti_file_prefix
from pvsfunc.pdebox import PDebox
from pvsfunc.pdecimate import PDecimate
from pvsfunc.pdeinterlacer import PDeinterlacer
from pvsfunc.psourcer import PSourcer
from vapoursynth import core

"""
Documentation and information:
https://rlaphoenix.github.io/VSMPEG
"""

# get config from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# load file path with PSourcer
Input = locals()["Input"].decode("utf-8") if "Input" in locals() else config["Input"]
psourcer = PSourcer(Input, debug=config["Verbose"])
sourcer = psourcer.sourcer
clip = psourcer.clip

# >>> Scan

# Deinterlace
if config["Deinterlacer"]:
    deinterlacer = config["Deinterlacers"][config["Deinterlacer"]]
    # get the deinterlacer function (and import stuff as needed) without using
    # eval or exec. We want the user to be safe(r) I guess.
    kernel = None
    if "Environment" in deinterlacer:
        environment = deinterlacer["Environment"]
        if "From" in environment:
            kernel = getattr(importlib.import_module(environment["From"]), environment["Import"])
        elif "Import" in environment:
            kernel = importlib.import_module(environment["Import"])
    if kernel is None:
        raise ValueError("VSMPEG: The environment configuration for the deinterlacer is missing or invalid.")
    kernel = getattr(kernel, config["Deinterlacer"])
    clip = PDeinterlacer(
        clip,
        kernel=kernel,
        kernel_args=deinterlacer["Args"],
        debug=config["Verbose"]
    ).clip

# >>> Frame-rate

# Decimation
if config["Decimation"]["Enabled"]:
    clip = PDecimate(
        clip,
        per_vob_id=config["Decimation"]["ResetCyclePerVobCell"],
        mode={False: 0, True: 1}[len(config["Decimation"]["Offsets"]) == 0],
        cycle=config["Decimation"]["Cycle"],
        offsets=config["Decimation"]["Offsets"] or None,
        debug=config["Verbose"]
    ).clip

# >>> Color

# Chroma location
if type(config["ChromaLocation"]) is int:
    if config["ChromaLocation"] < 0 or config["ChromaLocation"] > 5:
        raise ValueError("ChromaLocation value is invalid. Must be an integer between 0..5")
    clip = core.resize.Point(
        clip=clip,
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
    clip = core.std.Crop(clip, **{k.lower(): v for k, v in config["Crop"] if k != "Enabled"})

# Aspect Ratio
if config["AspectRatio"]["Value"]:
    ar = config["AspectRatio"]["Value"]
    if ar == "DAR":
        ar = {
            "core.d2v.Source": psourcer.d2v.settings["Aspect_Ratio"],
            # todo ; needs support for other codecs, perhaps via pymediainfo?
        }.get(sourcer, None)
    if ar:
        ar = [int(x) for x in ar.split(":")]
        axis = config["AspectRatio"]["Axis"].lower()
        w = math.ceil(clip.height * (ar[0] / ar[1]))
        h = math.ceil(clip.width / (ar[0] / ar[1]))
        if clip.width != w or clip.height != clip.height:
            clip = eval("core.resize." + config["AspectRatio"]["Kernel"])(
                clip=clip,
                **{axis: {"w": w, "h": h}[axis[0]]}
            )

# >>> Machine Learning and Networks

# VSGAN
if config["VSGAN"]["Enabled"]:
    from vsgan import VSGAN

    before = None
    if config["VSGAN"]["Comparer"]:
        before = clip
    for enabled, model, device, chunk, presample, resample in [x.values() for x in config["VSGAN"]["Operations"]]:
        if not enabled:
            continue
        vsgan_device = VSGAN(device)
        vsgan_device.load_model(anti_file_prefix(model))
        if presample:
            clip = core.resize.Spline36(
                clip,
                width=presample * (clip.width / clip.height),
                height=presample
            )
        if config["Deinterlacer"] == "PDeinterlacer.VoidWeave":
            clip = core.std.FrameEval(
                clip,
                functools.partial(
                    lambda n, f, c: c if f.props["PVSFlagProgressiveFrame"] else vsgan_device.run(c, chunk=chunk),
                    c=clip
                ),
                prop_src=clip
            )
        else:
            clip = vsgan_device.run(clip, chunk=chunk)
        if resample:
            clip = core.resize.Spline36(
                clip,
                width=resample * (clip.width / clip.height),
                height=resample
            )
    if config["VSGAN"]["Comparer"]:
        # match the res and format between the before clip and current clip
        if before.height != clip.height or before.width != clip.width:
            before = core.resize.Spline64(before, width=clip.width, height=clip.height)
        if before.format.id != clip.format.id:
            before = core.resize.Point(before, format=clip.format.id)
        clip = getattr(core.std, config["VSGAN"]["Comparer"])([
            core.text.Text(before, "Original"),
            core.text.Text(clip, "Result")
        ])
    if config["VSGAN"]["ConvertColorSpace"]["Enabled"]:
        if clip.format.id != getattr(vs, config["VSGAN"]["ConvertColorSpace"]["Format"]):
            clip = core.resize.Point(clip, format=config["VSGAN"]["ConvertColorSpace"]["Format"])

clip.set_output()
