#!/usr/bin/env python3
"""Inspect a folder of raw podcast footage and report what's actually in it.

This runs before anything else in the edit pipeline. Everything downstream
(speaker detection especially) forks on what this finds, so it answers three
questions:

  1. What are the media files, and what's inside each one?
  2. Where does the speech live -- one mic per person, or baked into each
     camera? That decides which speaker-detection profile we use.
  3. Do the cameras actually line up? Multicam sync is the classic silent
     killer: everything "works" and the result is unwatchable because camera B
     is 400ms behind camera A.

It only reads. Nothing here modifies footage.

Usage:
    python3 tools/probe_footage.py /path/to/episode-folder
"""

import json
import subprocess
import sys
from pathlib import Path

# --- CONSTANTS ---------------------------------------------------------------
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".mts", ".mxf"}
AUDIO_EXTS = {".wav", ".aif", ".aiff", ".mp3", ".m4a", ".flac"}

# Duration spread across cameras above this many seconds is worth flagging.
# Cameras started by hand are never frame-identical; a second or two is normal
# and fixable, but a large gap usually means a stop/restart mid-take.
DURATION_SPREAD_WARN_S = 2.0

# A "camera" clip shorter than this is probably a stray clip, not an angle.
MIN_CAMERA_DURATION_S = 60.0
# -----------------------------------------------------------------------------


def ffprobe(path):
    """Return ffprobe's JSON for one file, or None if it isn't media."""
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(path),
            ],
            capture_output=True, text=True, check=True,
        ).stdout
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def summarize(path, probe):
    """Flatten ffprobe's output into the handful of fields we care about."""
    fmt = probe.get("format", {})
    streams = probe.get("streams", [])

    video, audio = [], []
    for s in streams:
        if s.get("codec_type") == "video":
            # avg_frame_rate is a rational string like "30000/1001".
            num, _, den = s.get("avg_frame_rate", "0/1").partition("/")
            fps = float(num) / float(den) if den and float(den) else 0.0
            video.append({
                "codec": s.get("codec_name"),
                "width": s.get("width"),
                "height": s.get("height"),
                "fps": round(fps, 3),
            })
        elif s.get("codec_type") == "audio":
            audio.append({
                "codec": s.get("codec_name"),
                "channels": s.get("channels"),
                "sample_rate": s.get("sample_rate"),
            })

    try:
        duration = float(fmt.get("duration", 0.0))
    except (TypeError, ValueError):
        duration = 0.0

    return {
        "name": path.name,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "duration_s": round(duration, 3),
        "video": video,
        "audio": audio,
    }


def hms(seconds):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}"


def classify(files):
    """Split probed files into camera angles vs standalone audio tracks."""
    cameras = [f for f in files if f["video"]]
    standalone_audio = [f for f in files if not f["video"] and f["audio"]]
    return cameras, standalone_audio


def detect_mode(cameras, standalone_audio):
    """Decide which speaker-detection profile applies.

    Standalone audio files mean someone recorded a mic per person, which makes
    speaker detection near-trivial: each track IS a speaker. Without them we
    fall back to comparing how loud each camera's onboard mic is, which works
    but needs calibration and a confidence pass.
    """
    if len(standalone_audio) >= 2:
        return "PER_MIC"
    if len(standalone_audio) == 1:
        # One shared room mic can't separate speakers on its own.
        return "SINGLE_MIX"
    if len([c for c in cameras if c["audio"]]) >= 2:
        return "BAKED_IN"
    return "UNKNOWN"


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    folder = Path(sys.argv[1]).expanduser().resolve()
    if not folder.is_dir():
        print(f"Not a directory: {folder}")
        return 1

    media_exts = VIDEO_EXTS | AUDIO_EXTS
    candidates = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in media_exts
    )

    if not candidates:
        print(f"No media files found in {folder}")
        print(f"Looked for: {', '.join(sorted(media_exts))}")
        return 1

    files = []
    for p in candidates:
        probe = ffprobe(p)
        if probe is None:
            print(f"  ! ffprobe could not read {p.name} -- skipping")
            continue
        files.append(summarize(p, probe))

    cameras, standalone_audio = classify(files)
    mode = detect_mode(cameras, standalone_audio)

    print(f"\nFolder: {folder}")
    print(f"Media files: {len(files)}   Total: "
          f"{sum(f['size_bytes'] for f in files) / 1e9:.1f} GB\n")

    print(f"CAMERAS ({len(cameras)})")
    for c in cameras:
        v = c["video"][0]
        has_audio = f"{c['audio'][0]['channels']}ch" if c["audio"] else "NO AUDIO"
        print(f"  {c['name']:<28} {hms(c['duration_s']):>8}  "
              f"{v['width']}x{v['height']} @{v['fps']}fps  {v['codec']}  {has_audio}")

    if standalone_audio:
        print(f"\nSEPARATE AUDIO ({len(standalone_audio)})")
        for a in standalone_audio:
            s = a["audio"][0]
            print(f"  {a['name']:<28} {hms(a['duration_s']):>8}  "
                  f"{s['channels']}ch @{s['sample_rate']}Hz  {s['codec']}")

    print(f"\nDETECTED MODE: {mode}")
    print({
        "PER_MIC": "  Per-person mics. Speaker detection is reliable.",
        "BAKED_IN": "  Camera onboard audio only. Needs calibration + confidence pass.",
        "SINGLE_MIX": "  One mixed track. Cannot separate speakers from audio alone.",
        "UNKNOWN": "  Could not determine. Needs a human look.",
    }[mode])

    # --- sanity checks -------------------------------------------------------
    warnings = []

    # The duration filter belongs to the sync check only: a 4-second stray clip
    # would blow up the spread and warn about nothing. Format mismatches, by
    # contrast, matter on every angle regardless of length.
    long_cams = [c for c in cameras if c["duration_s"] >= MIN_CAMERA_DURATION_S]
    if len(long_cams) >= 2:
        durs = [c["duration_s"] for c in long_cams]
        spread = max(durs) - min(durs)
        if spread > DURATION_SPREAD_WARN_S:
            warnings.append(
                f"Camera durations differ by {spread:.1f}s "
                f"({hms(min(durs))} to {hms(max(durs))}). They need syncing "
                f"before any multicam cut -- a shared clap or audio "
                f"cross-correlation."
            )

    fps_set = {c["video"][0]["fps"] for c in cameras}
    if len(fps_set) > 1:
        warnings.append(
            f"Mixed frame rates: {sorted(fps_set)}. Pick one for the timeline; "
            f"the rest get conformed on render."
        )

    res_set = {(c["video"][0]["width"], c["video"][0]["height"]) for c in cameras}
    if len(res_set) > 1:
        warnings.append(f"Mixed resolutions: {sorted(res_set)}. Will need scaling.")

    silent = [c["name"] for c in cameras if not c["audio"]]
    if silent and mode == "BAKED_IN":
        warnings.append(
            f"No audio on {', '.join(silent)} -- those angles can't vote on "
            f"who's speaking."
        )

    if warnings:
        print(f"\nWARNINGS ({len(warnings)})")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print("\nNo warnings.")

    out_dir = Path(__file__).resolve().parent.parent / ".tmp"
    out_dir.mkdir(exist_ok=True)
    dest = out_dir / "footage_probe.json"
    dest.write_text(json.dumps({
        "folder": str(folder),
        "mode": mode,
        "cameras": cameras,
        "standalone_audio": standalone_audio,
        "warnings": warnings,
    }, indent=2) + "\n")
    print(f"\nWrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
