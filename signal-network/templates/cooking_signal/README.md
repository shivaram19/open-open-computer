# Signal Network: Cooking + Data Overlay Template

A 9:16 Revideo template for vertical short-form content with an embedded "signal" overlay.

## Variables

| Variable | Type | Description |
|----------|------|-------------|
| `backgroundVideo` | string (optional) | Path to background cooking/raw footage |
| `captionTrack` | `{start, end, text}[]` | Timed captions in target language |
| `priceOverlay` | string | The signal data, e.g. "ఉప్పు ధర: ₹45/kg (+12%)" |
| `regionTag` | string | Region label, e.g. "తెలంగాణ" |
| `language` | string | Language code, e.g. "te" |

## Render

```bash
cd templates/cooking_signal
npm install
npm run render -- --variables '{"captionTrack":[{"start":0,"end":2,"text":"ఉప్పు ధర పెరిగింది"}],"priceOverlay":"ఉప్పు ధర: ₹45/kg (+12%)","regionTag":"తెలంగాణ","language":"te"}' --outFile ../../outputs/te_salt_hook.mp4
```

## Fonts

Install Noto Sans Telugu / Noto Sans Devanagari on the render machine, or replace `fontFamily` with a system font that supports your target script.
