---
workflow: general-video
flow: automation
storyboard: no
message: "Two halves, better together"
aspect: 1080x1920
language: en
length: 30s
angle: two-halves
---

## Intent

"Make a very romantic video from this picture." Concept chosen (recommended, accepted by
no-preference): **Two Halves** — the selfie opens split in two, each person alone in soft
darkness; the halves drift together and close into the full photo as one. "Better together."

## Assets

- assets/photo.jpg — the couple's selfie (user upload); the only picture in the film.

## Customizations

- Warm, restrained portrait grade on the photo (Natural Portrait seed, slightly warmer).
- Soft synthesized piano + strings bed; the halves meet on a bar downbeat.

## Notes

- No names or personal facts; short universal lines describe only what the photo shows.
- Vertical for phones/Stories.
- The grade (skin-soft 0.6, temperature +0.08, shadows +0.1, highlights -0.1) is baked into
  assets/photo-graded.jpg by snapshotting it through HyperFrames' own grading renderer: the live
  shader stalls `check` in this GPU-less sandbox. assets/photo.jpg stays the untouched source.
