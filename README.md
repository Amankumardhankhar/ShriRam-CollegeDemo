# Shri Ram College of Medical Science & Research: WordPress site

WordPress website for the college at Digrota, Mahendragarh (Haryana). It has a custom block theme, and every page is generated from the researched facts in [Info/](Info/).

## Run locally

Requires Podman. The site runs in its own pod (`srcmsr`) on port 8092.

```bash
scripts/start.sh     # create/start the pod  -> http://localhost:8092
scripts/setup.sh     # install WordPress (first run) and load/refresh all pages
scripts/stop.sh      # stop (data is kept in Podman volumes)
```

Admin: http://localhost:8092/wp-admin, user `admin`, password `admin`. **Change this before going live.**

## Project layout

| Path | What it is |
|---|---|
| `wp-content/themes/shriram-college/` | Block theme: `theme.json` (colours, fonts, spacing), `style.css`, `templates/`, `parts/`, `patterns/` (header and footer) |
| `…/assets/images/hero-illustration.svg`, `…/assets/js/site.js` | Animated home illustration; scroll-reveal, count-up and header effects (motion is turned off for visitors who ask for reduced motion) |
| `tools/build_icons.py` | Line-icon set → `assets/css/icons.css`. Use `sr-icon ico-<name>` on a block (add `sr-icon--accent` / `--soft` for colour variants) |
| `tools/build_content.py` | Source of all page content (Python → block markup). Edit it, then run `scripts/setup.sh` |
| `tools/hindi.py` | Hindi text for every page (English → Hindi). The build stops and lists any English text that has no Hindi version |
| `…/inc/i18n.php` | Hindi header, footer, menu and page banner, the English/हिन्दी switcher, `lang="hi-IN"` and hreflang links |
| `content/pages/*.html`, `content/pages.json` | Generated page markup and the page list. Do not edit by hand |
| `content/cf7-*.{txt,json}` | Admission enquiry forms (Contact Form 7), English and Hindi (`-hi`), and their email templates |
| `scripts/` | start / setup / stop / export |
| `Info/` | Researched information about the college, with sources |

> Re-running `scripts/setup.sh` **overwrites** page content with the generated version. After the college starts editing pages in WP Admin, stop using it for content (or remove those pages from `pages.json`).

## Pages

Home · About · Courses (B.Sc Nursing, Post Basic B.Sc Nursing, B.Sc Paramedical Science, GNM, ANM) · Admissions · Fee Structure · Approvals & Affiliations · Hospital · Campus & Facilities · Faculty · Gallery · Notices (blog) · Contact · Mandatory Disclosure

## Hindi version

Every page has a Hindi version under `/hi/` with the same address: `/about/` ↔ `/hi/about/`, `/courses/gnm/` ↔ `/hi/courses/gnm/`. The **English | हिन्दी** switch in the top bar opens the same page in the other language. In WP Admin the Hindi pages are children of the page "होम" (slug `hi`).

- To change page text, edit the English text in `tools/build_content.py` **and** the matching entry in `tools/hindi.py`, then run `scripts/setup.sh`.
- Header, footer and menu text in Hindi is in `inc/i18n.php` (`shriram_t()`).
- Notices (posts) are shared by both languages; the Hindi Notices page lists the same posts.
- Please have someone at the college proofread the Hindi, especially place names (e.g. नानवां, नांगल माला) and the name of the managing society.

## Still needed from the college

Every missing item appears on the site as a **yellow dashed "✎" box**. The main ones:

- Confirm the official name ("Shri Ram College of Medical Science & Research" vs "Shri Ram College of Nursing"). Change it in *Settings → General → Site Title*.
- **Phone and email**: enter them in *Settings → General → College phone / College email*. The header, footer and Contact page update automatically.
- Official logo. The shield-and-lamp emblem at `assets/images/emblem.svg` is a placeholder.
- Leadership names and messages, vision and mission, faculty list, trust name, year of establishment.
- The college's own fee sheet, approval letters (PDFs), hospital details, and photos for the Gallery and facilities.
- Enquiry emails currently go to the WordPress admin email. On live hosting, set that email and install an SMTP plugin (e.g. WP Mail SMTP) so mail is delivered.

## Going live

1. `scripts/export.sh` creates `dist/`, containing the theme zip, `database.sql` and `uploads.tar.gz`.
2. **Simplest route:** on the host, install WordPress, upload `shriram-college-theme.zip` (*Appearance → Themes → Add New → Upload*), install Contact Form 7, then import the database with a migration plugin. Alternatively, import `database.sql` and run `wp search-replace 'http://localhost:8092' 'https://your-domain'`.
3. Set a strong admin password, and install security, backup and SEO plugins (e.g. Wordfence, UpdraftPlus, Yoast/Rank Math).
4. Domain: the old domain `srgroupofcolleges.com` has expired. Re-register it if possible, or pick a new one.
