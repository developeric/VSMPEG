#!/usr/bin/env python3

import functools
import importlib
import math
import os

import pkg_resources
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

# Constants
VSGAN_MIN_VER = 121

# get config from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# load file path with PSourcer
Input = locals()["Input"].decode("utf-8") if "Input" in locals() else config["Input"]
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
    crop_values = {k.lower(): v for k, v in config["Crop"] if k != "Enabled"}
    if sum(*crop_values.values()) != 0:
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
    try:
        if int(pkg_resources.get_distribution("vsgan").version.replace(".", "")) < VSGAN_MIN_VER:
            raise EnvironmentError(
                f"VSMPEG: Your VSGAN installation is too old. Update with `pip install --upgrade vsgan`")
    except pkg_resources.DistributionNotFound:
        raise EnvironmentError("VSMPEG: VSGAN needs to be installed, https://rlaphoenix.github.io/VSMPEG")
    from vsgan import VSGAN

    before = clip if config["VSGAN"]["Comparer"] else None
    instances = {}
    for enabled, model, device, chunk, presample, resample in [x.values() for x in config["VSGAN"]["Operations"]]:
        if not enabled:
            continue
        if device not in instances:
            instances[device] = VSGAN(device)
        model = anti_file_prefix(model)
        if instances[device].model != model:
            instances[device].load_model(model)
        if presample:
            clip = core.resize.Spline36(
                clip,
                width=presample * (clip.width / clip.height),
                height=presample
            )
        clip = core.resize.Spline64(clip, format=vs.RGB24)
        if config["Deinterlacer"] == PDeinterlacer.VoidWeave:
            clip = core.std.FrameEval(
                clip,
                functools.partial(
                    lambda n, f, c: c if f.props["PVSFlagProgressiveFrame"] else instances[device].run(c, chunk=chunk),
                    c=clip
                ),
                prop_src=clip
            )
        else:
            clip = instances[device].run(clip, chunk=chunk)
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
        cs_format = getattr(vs, config["VSGAN"]["ConvertColorSpace"]["Format"])
        if clip.format.id != cs_format:
            clip = core.resize.Point(clip, matrix_s="709", format=cs_format)

clip.set_output()
