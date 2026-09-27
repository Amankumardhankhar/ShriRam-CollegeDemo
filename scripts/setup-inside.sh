#!/usr/bin/env bash
# Runs inside the WP-CLI container (called by scripts/setup.sh).
set -euo pipefail
cd /var/www/html

SITE_URL="${SITE_URL:-http://localhost:8092}"
TITLE="Shri Ram College of Medical Science & Research"
TAGLINE="Nursing & Paramedical Education · Digrota, Mahendragarh"

if ! wp core is-installed 2>/dev/null; then
	wp core install --url="$SITE_URL" --title="$TITLE" --admin_user=admin --admin_password=admin \
		--admin_email=admin@example.com --skip-email
	# Remove sample content once, on first install.
	wp post delete $(wp post list --post_type=post,page --format=ids) --force >/dev/null 2>&1 || true
	wp plugin delete hello akismet >/dev/null 2>&1 || true
	echo "Installed WordPress. Login: $SITE_URL/wp-admin  (admin / admin — change this!)"
fi

wp option update blogname "$TITLE" >/dev/null
wp option update blogdescription "$TAGLINE" >/dev/null
wp option update timezone_string "Asia/Kolkata" >/dev/null
# College landline from its 2018-19 admission notice; staff can change it in Settings -> General.
[ -z "$(wp option get shriram_phone 2>/dev/null)" ] && wp option update shriram_phone "01285-222514" >/dev/null
wp option update date_format "d M Y" >/dev/null
wp rewrite structure '/%postname%/' --hard >/dev/null
wp theme activate shriram-college >/dev/null

# ---- Contact forms (Contact Form 7): English and Hindi. Falls back to a note if the plugin can't be installed.
FORM_BLOCK='<!-- wp:paragraph {"className":"sr-placeholder"} -->
<p class="sr-placeholder">Enquiry form will appear here once Contact Form 7 is installed.</p>
<!-- /wp:paragraph -->'
FORM_BLOCK_HI="$FORM_BLOCK"
# cf7_form <slug> <title> <form file> <mail file> <messages json>  -> prints the shortcode block
cf7_form() {
	local id
	id=$(wp post list --post_type=wpcf7_contact_form --name="$1" --field=ID --format=ids)
	if [ -z "$id" ]; then
		id=$(wp post create --post_type=wpcf7_contact_form --post_status=publish --post_title="$2" --post_name="$1" --porcelain)
	fi
	wp post meta update "$id" _form "$(cat "$3")" >/dev/null
	wp post meta update "$id" _mail --format=json "$(cat "$4")" >/dev/null
	wp post meta update "$id" _messages --format=json "$5" >/dev/null
	printf '<!-- wp:shortcode -->\n[contact-form-7 id="%s" title="%s"]\n<!-- /wp:shortcode -->' "$id" "$2"
}
if wp plugin is-installed contact-form-7 || wp plugin install contact-form-7 >/dev/null 2>&1; then
	wp plugin activate contact-form-7 >/dev/null 2>&1 || true
	FORM_BLOCK=$(cf7_form admission-enquiry "Admission Enquiry" /project/content/cf7-form.txt /project/content/cf7-mail.json \
		'{"mail_sent_ok":"Thank you! Our admissions office will contact you shortly.","mail_sent_ng":"Sorry, your message could not be sent. Please call the college office.","validation_error":"Please check the highlighted fields and try again."}')
	FORM_BLOCK_HI=$(cf7_form admission-enquiry-hi "Admission Enquiry (Hindi)" /project/content/cf7-form-hi.txt /project/content/cf7-mail-hi.json \
		'{"mail_sent_ok":"धन्यवाद! हमारा प्रवेश कार्यालय जल्द ही आपसे संपर्क करेगा।","mail_sent_ng":"क्षमा करें, आपका संदेश नहीं भेजा जा सका। कृपया कॉलेज कार्यालय को फ़ोन करें।","validation_error":"कृपया चिह्नित फ़ील्ड जाँचें और फिर से प्रयास करें।","invalid_required":"यह फ़ील्ड भरना आवश्यक है।","invalid_tel":"कृपया सही फ़ोन नंबर लिखें।","invalid_email":"कृपया सही ईमेल पता लिखें।"}')
fi

# ---- Fee structure PDF into the media library (once).
FEE_URL=$(wp post list --post_type=attachment --post_status=inherit --name=haryana-gazette-2024-nursing-fee-structure --field=guid 2>/dev/null | head -1)
if [ -z "$FEE_URL" ]; then
	FEE_ID=$(wp media import "/project/Info/04_Fees/Haryana_Gazette_2024_Nursing_Fee_Structure.pdf" \
		--title="Haryana Gazette 2024 - Nursing Fee Structure" --porcelain)
	wp post update "$FEE_ID" --post_name=haryana-gazette-2024-nursing-fee-structure >/dev/null
	FEE_URL=$(wp post get "$FEE_ID" --field=guid)
fi

# ---- Campus photos into the media library (once each).
wp eval-file /project/scripts/import-photos.php

# ---- Pages (create or update by slug, parents first).
export FORM_BLOCK FORM_BLOCK_HI FEE_URL
wp eval-file /project/scripts/load-pages.php

HOME_ID=$(wp post list --post_type=page --name=home --post_parent=0 --field=ID --format=ids)
NOTICES_ID=$(wp post list --post_type=page --name=notices --post_parent=0 --field=ID --format=ids)
wp option update show_on_front page >/dev/null
wp option update page_on_front "$HOME_ID" >/dev/null
wp option update page_for_posts "$NOTICES_ID" >/dev/null

# ---- A first notice so the notices area is not empty.
if [ -z "$(wp post list --post_type=post --name=welcome-to-our-new-website --field=ID --format=ids)" ]; then
	wp post create --post_type=post --post_status=publish --post_name=welcome-to-our-new-website \
		--post_title="Welcome to our new website" \
		--post_content='<!-- wp:paragraph -->
<p>Welcome to the official website of Shri Ram College of Medical Science &amp; Research, Digrota. Admission notices, examination schedules, results and campus news will be posted here.</p>
<!-- /wp:paragraph -->' >/dev/null
fi

wp rewrite flush --hard >/dev/null
wp cache flush >/dev/null 2>&1 || true
echo "Done: $SITE_URL"
