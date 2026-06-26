"""
debug_seg.py
------------
Run this locally:   python debug_seg.py
It will save step-by-step images so you can SEE exactly what the
pipeline finds at each stage.  Check the saved PNGs to diagnose
why only 'a' is predicted.
"""

import cv2
import numpy as np
import os

# ── CHANGE THIS to your actual test image path ──────────────────
IMAGE_PATH = r"Screenshot_2026-03-16_105325.png"
OUT_DIR    = "debug_output"
# ────────────────────────────────────────────────────────────────

os.makedirs(OUT_DIR, exist_ok=True)


def save(name, img):
    path = os.path.join(OUT_DIR, name)
    cv2.imwrite(path, img)
    print(f"  Saved: {path}")


def debug_pipeline(image_path, gap_threshold=30, scale=3, min_area=100):

    print("\n══════════════════════════════════════════")
    print(" BRAHMI SEGMENTATION DEBUG")
    print("══════════════════════════════════════════\n")

    # ── Step 1: Load ────────────────────────────────────────────
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"[ERROR] Cannot load image at: {image_path}")
        return
    print(f"[1] Loaded image  size: {img_bgr.shape[1]}×{img_bgr.shape[0]}")
    save("1_original.png", img_bgr)

    # ── Step 2: Grayscale ────────────────────────────────────────
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    save("2_gray.png", gray)
    print(f"[2] Grayscale  pixel range: {gray.min()}–{gray.max()}")

    # ── Step 3: Scale up ─────────────────────────────────────────
    gray = cv2.resize(gray, (scale * gray.shape[1], scale * gray.shape[0]),
                      interpolation=cv2.INTER_CUBIC)
    save("3_scaled.png", gray)
    print(f"[3] Scaled ×{scale}  new size: {gray.shape[1]}×{gray.shape[0]}")

    # ── Step 4: Blur ─────────────────────────────────────────────
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    save("4_blurred.png", blurred)

    # ── Step 5: Threshold ────────────────────────────────────────
    otsu_val, thresh = cv2.threshold(blurred, 0, 255,
                                     cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    save("5_thresh.png", thresh)
    ink_pixels = cv2.countNonZero(thresh)
    print(f"[5] OTSU threshold value: {otsu_val:.0f}  |  ink pixels: {ink_pixels}")

    if ink_pixels == 0:
        print("\n  !! PROBLEM: Threshold found ZERO ink pixels.")
        print("     The image background and ink are too similar,")
        print("     or the image is already inverted.")
        print("     → Try: change THRESH_BINARY_INV to THRESH_BINARY")
        # Try without invert
        _, thresh2 = cv2.threshold(blurred, 0, 255,
                                   cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        save("5b_thresh_noinvert.png", thresh2)
        ink2 = cv2.countNonZero(thresh2)
        print(f"     Without invert: {ink2} ink pixels  (saved 5b_thresh_noinvert.png)")
        thresh = thresh2

    # ── Step 6: Find contours ────────────────────────────────────
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    print(f"\n[6] Total contours found: {len(contours)}")

    # Show ALL contours on a colour image
    vis_all = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        cv2.rectangle(vis_all, (x, y), (x+w, y+h), (0, 0, 255), 1)
    save("6_all_contours.png", vis_all)

    # ── Step 7: Filter by area ───────────────────────────────────
    raw_bboxes = []
    for c in contours:
        area = cv2.contourArea(c)
        if area >= min_area:
            raw_bboxes.append(cv2.boundingRect(c))
        else:
            print(f"   skipped noise blob  area={area:.0f}")

    print(f"[7] After area filter (>={min_area}): {len(raw_bboxes)} blobs")

    vis_filtered = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for (x, y, w, h) in raw_bboxes:
        cv2.rectangle(vis_filtered, (x, y), (x+w, y+h), (255, 0, 0), 2)
    save("7_filtered_blobs.png", vis_filtered)

    if not raw_bboxes:
        print("\n  !! PROBLEM: No blobs survived area filter.")
        print(f"     Largest contour area = "
              f"{max(cv2.contourArea(c) for c in contours) if contours else 0:.0f}")
        print(f"     Try lowering min_area (currently {min_area})")
        return

    # ── Step 8: Merge nearby bboxes ──────────────────────────────
    effective_gap = gap_threshold * scale
    raw_sorted    = sorted(raw_bboxes, key=lambda b: b[0])

    merged = []
    cx, cy, cw, ch = raw_sorted[0]
    for (x, y, w, h) in raw_sorted[1:]:
        gap = x - (cx + cw)
        if gap <= effective_gap:
            nx = min(cx, x); ny = min(cy, y)
            nr = max(cx+cw, x+w); nb = max(cy+ch, y+h)
            cx, cy, cw, ch = nx, ny, nr-nx, nb-ny
        else:
            merged.append((cx, cy, cw, ch))
            cx, cy, cw, ch = x, y, w, h
    merged.append((cx, cy, cw, ch))

    print(f"[8] After merge (gap≤{effective_gap}px): {len(merged)} characters")

    vis_merged = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for i, (x, y, w, h) in enumerate(merged):
        cv2.rectangle(vis_merged, (x, y), (x+w, y+h), (0, 200, 0), 3)
        cv2.putText(vis_merged, str(i+1), (x, y-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
    save("8_merged_chars.png", vis_merged)

    # ── Step 9: Crop each character ──────────────────────────────
    pad   = 4
    H, W  = gray.shape
    print(f"\n[9] Individual character crops:")
    for i, (x, y, w, h) in enumerate(merged):
        x1 = max(0, x-pad); y1 = max(0, y-pad)
        x2 = min(W, x+w+pad); y2 = min(H, y+h+pad)
        crop = gray[y1:y2, x1:x2]
        fname = f"9_char_{i+1}.png"
        save(fname, crop)
        print(f"   Char {i+1}: bbox=({x},{y},{w},{h})  crop size={crop.shape[1]}×{crop.shape[0]}")

    # ── Summary ──────────────────────────────────────────────────
    print("\n══════════════════════════════════════════")
    print(f" RESULT: {len(merged)} character(s) found")
    print(f" Expected for 'प्रणय': 3 characters")
    print("══════════════════════════════════════════")
    print("\n Check the debug_output/ folder and look at:")
    print("  5_thresh.png       ← is the ink visible as white?")
    print("  7_filtered_blobs.png ← how many blobs after noise filter?")
    print("  8_merged_chars.png ← are characters correctly grouped?")
    print("  9_char_1.png etc   ← what does each character crop look like?\n")

    # ── Suggest fixes ────────────────────────────────────────────
    if len(merged) == 1:
        print("  ⚠  Only 1 character found.")
        print("     Possible causes:")
        print("     A) gap_threshold is too HIGH → all chars merged into 1")
        print(f"        Try: debug_pipeline(image_path, gap_threshold=10)")
        print("     B) Threshold is grabbing background as one big blob")
        print("        Check 5_thresh.png")

    elif len(merged) > 6:
        print("  ⚠  Too many characters found (strokes not merging).")
        print("     Try: debug_pipeline(image_path, gap_threshold=60)")

    elif len(merged) == 3:
        print("  ✓  3 characters found — segmentation looks correct!")
        print("     If model still gives wrong labels, the issue is in")
        print("     skeletonize/prune or model confidence.")


if __name__ == "__main__":
    # Run with default settings first
    debug_pipeline(IMAGE_PATH, gap_threshold=30)

    # Uncomment below to try different gap values:
    # debug_pipeline(IMAGE_PATH, gap_threshold=10)
    # debug_pipeline(IMAGE_PATH, gap_threshold=60)
