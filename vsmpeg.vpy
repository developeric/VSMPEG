#!/usr/bin/env python3

import functools
import importlib
import math
import os

import vapoursynth as vs
import yaml
from pvsfunc import PSourcer, PDeinterlacer, PDecimate, PDebox
from pvsfunc.helpers import anti_file_prefix
from vapoursynth import core

"""
Documentation and information:
https://rlaphoenix.github.io/VSMPEG
"""

# get config from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Cache Size
if config["MaxCacheSize"]:
    core.max_cache_size = config["MaxCacheSize"]

# load file path with PSourcer
if "video_in" in locals():  # MPV
    Input = locals()["video_in"]
elif "Input" in locals():   # VSPIPE
    Input = locals()["Input"].decode("utf-8")
else:
    Input = config["Input"]
psourcer = PSourcer(Input, debug=config["Verbose"])
sourcer = psourcer.sourcer
clip = psourcer.clip

# >>> Color

# Chroma location
if config["ChromaLocation"] is not None:
    clip = psourcer.change_chroma_loc(
        clip,
        new_loc=config["ChromaLocation"],
        verbose=config["Verbose"]
    )

# >>> Scan

# Deinterlace
if config["Deinterlacer"]:
    # get the deinterlacer function (and import stuff as needed) without using
    # eval or exec. We want the user to be safe(r) I guess.
    kernel = None
    deinterlacer = config["Deinterlacers"][config["Deinterlacer"]]
    if "Environment" in deinterlacer:
        environment = deinterlacer["Environment"]
        if "From" in environment:
            kernel = getattr(importlib.import_module(environment["From"]), environment["Import"])
        elif "Import" in environment:
            kernel = importlib.import_module(environment["Import"])
    if kernel is None:
        raise ValueError("VSMPEG: The environment configuration for the deinterlacer is missing or invalid.")
    config["Deinterlacer"] = getattr(kernel, config["Deinterlacer"])
    # send the deinterlacer function to PDeinterlacer
    clip = PDeinterlacer(
        clip,
        kernel=config["Deinterlacer"],
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

# >>> Resizing and Cropping

# Debox
if config["Debox"]["Enabled"] and config["Debox"]["Operations"]:
    for mode, aspect, offset in config["Debox"]["Operations"]:
        clip = PDebox(
            clip,
            aspect_ratio=aspect,
            mode={"w": 0, "h": 1}[mode],
            offset=offset
        ).clip

# Crop
if config["Crop"]["Enabled"]:
    crop_values = {k.lower(): v for k, v in config["Crop"].items() if k != "Enabled"}
    clip = core.std.Crop(clip, **crop_values)

# Aspect Ratio
if config["AspectRatio"]["Value"]:
    ar = config["AspectRatio"]["Value"]
    if ar == "DAR":
        # todo ; needs support for other codecs, perhaps via pymediainfo?
        if sourcer == "core.d2v.Source":
            ar = psourcer.d2v.settings["Aspect_Ratio"]
        else:
            ar = None
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

    before = clip if config["VSGAN"]["Comparer"] else None
    instances = {}
    for operation in config["VSGAN"]["Operations"]:
        if not operation["enabled"]:
            continue
        if operation["device"] not in instances:
            instances[operation["device"]] = VSGAN(operation["device"])
        model = anti_file_prefix(operation["model"])
        if instances[operation["device"]].model != model:
            instances[operation["device"]].load_model(model)
        kernel = getattr(core.resize, config["VSGAN"]["Kernel"])
        clip = kernel(
            clip,
            format=vs.RGB24,
            **(dict(
                width=operation["presample"] * (clip.width / clip.height),
                height=operation["presample"]
            ) if operation.get("presample") else {})
        )
        if operation.get("skip_progressive"):
            clip = core.std.FrameEval(
                clip,
                functools.partial(
                    lambda n, f, c: c if f.props["PVSFlagProgressiveFrame"] else instances[operation["device"]].run(c),
                    c=clip
                ),
                prop_src=clip
            )
        else:
            clip = instances[operation["device"]].run(clip)
        if operation.get("resample"):
            clip = kernel(
                clip,
                width=operation["resample"] * (clip.width / clip.height),
                height=operation["resample"]
            )
    if config["VSGAN"].get("Comparer"):
        # match the res and format between the before clip and current clip
        if before.height != clip.height or before.width != clip.width:
            before = core.resize.Spline64(before, width=clip.width, height=clip.height)
        if before.format.id != clip.format.id:
            before = core.resize.Point(before, format=clip.format.id)
        clip = getattr(core.std, config["VSGAN"]["Comparer"])([
            core.text.Text(before, "Original"),
            core.text.Text(clip, "Result")
        ])

clip.set_output()
