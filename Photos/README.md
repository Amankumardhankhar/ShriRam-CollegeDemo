# Photos

- `google-maps/owner/`: 43 photos posted by the college's own Google Maps account (Shri Ram college of Medical Science & Research).
- `google-maps/contributors/`: 22 photos posted by visitors. **Copyright belongs to the uploaders**; get permission or replace them before launch.
- `google-maps/manifest.json`: uploader and date for every downloaded photo.
- `web/`: 31 resized picks used on the website (≤1920px, EXIF/GPS stripped). `photos.json` holds slug, alt text, source and credit.

`scripts/setup.sh` imports `web/` into the Media Library. Pages reference photos as `{{IMG:slug}}` in `tools/build_content.py`.
To swap in better photos from the college, replace the file in `web/` under the same name and re-run setup (or edit the image in WP Admin → Media).
