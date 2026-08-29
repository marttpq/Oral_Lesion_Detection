"""
Bundle essential static assets (images, JS) into a base64-encoded zip
that git can reliably commit even on flaky drives.
Run: python bundle_assets.py
Output: assets_bundle.b64 (text file, safe for git)
"""
import base64, io, os, zipfile

ESSENTIAL_FILES = [
    "static/image/img2.png",
    "static/image/google.jpg",
    "static/image/production.png",
    "static/image/Logo.png",
    "static/image/doc.jpg",
    "static/image/docrmbg.png",
    "static/image/big-data.png",
    "static/image/simplicity.png",
    "static/image/camera.png",
    "static/image/upload.png",
    "static/image/picture.png",
    "static/image/DoctorWithApp.jpg",
    "static/image/line-qr.jpg",
    "static/image/img1.png",
    "static/image/pro.gif",
    "static/image/can1.png",
    "static/image/can2.png",
    "static/image/leu1.png",
    "static/image/leu2.png",
    "static/image/lia1.png",
    "static/image/lia2.png",
    "static/image/lic1.png",
    "static/image/lic2.png",
    "static/image/ulc1.png",
    "static/image/ulc2.png",
    "static/image/FB.jpg",
    "static/image/123.png",
    "static/js/index.js",
    "static/js/script.js",
]

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in ESSENTIAL_FILES:
        if os.path.exists(path):
            zf.write(path)
            print(f"  + {path}")
        else:
            print(f"  SKIP (not found): {path}")

b64 = base64.b64encode(buf.getvalue()).decode("ascii")

with open("assets_bundle.b64", "w") as f:
    f.write(b64)

print(f"\nDone! assets_bundle.b64 = {len(b64)} chars ({len(buf.getvalue())} bytes compressed)")
