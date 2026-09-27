<?php
/**
 * Hindi version of the site.
 *
 * Hindi pages live under the page with slug "hi" (/hi/, /hi/about/, /hi/courses/gnm/ …) and
 * mirror the English pages slug for slug, so every page can link to its twin. The header,
 * footer and page banner read shriram_lang() and switch their text and links to match.
 *
 * @package shriram-college
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const SHRIRAM_HI_ROOT = 'hi';

/** 'hi' on the Hindi page tree, 'en' everywhere else (posts, archives, search, 404, admin). */
function shriram_lang() {
	static $lang = null;
	if ( null !== $lang ) {
		return $lang;
	}
	// The queried page is only known once the main query has run; don't cache a guess before then.
	if ( is_admin() || ! did_action( 'wp' ) ) {
		return 'en';
	}
	$lang = 'en';
	$post = get_queried_object();
	if ( $post instanceof WP_Post && 'page' === $post->post_type ) {
		$ancestors = get_post_ancestors( $post );
		$root      = $ancestors ? get_post( end( $ancestors ) ) : $post;
		if ( $root && SHRIRAM_HI_ROOT === $root->post_name ) {
			$lang = 'hi';
		}
	}
	return $lang;
}

/** Hindi text for a header/footer/template string, or the English text on English pages. */
function shriram_t( $en ) {
	static $hi = null;
	if ( 'hi' !== shriram_lang() ) {
		return $en;
	}
	if ( null === $hi ) {
		$hi = array(
			'Home'                             => 'होम',
			'About'                            => 'परिचय',
			'About the College'                => 'कॉलेज के बारे में',
			'Approvals & Affiliations'         => 'मान्यता एवं संबद्धता',
			'Faculty'                          => 'संकाय',
			'Mandatory Disclosure'             => 'अनिवार्य प्रकटीकरण',
			'Courses'                          => 'पाठ्यक्रम',
			'B.Sc Nursing'                     => 'बी.एससी. नर्सिंग',
			'Post Basic B.Sc Nursing'          => 'पोस्ट बेसिक बी.एससी. नर्सिंग',
			'B.Sc Paramedical Science'         => 'बी.एससी. पैरामेडिकल साइंस',
			'GNM'                              => 'जीएनएम',
			'ANM'                              => 'एएनएम',
			'Admissions'                       => 'प्रवेश',
			'Admission Process'                => 'प्रवेश प्रक्रिया',
			'Fee Structure'                    => 'शुल्क संरचना',
			'Hospital'                         => 'अस्पताल',
			'Campus'                           => 'परिसर',
			'Facilities'                       => 'सुविधाएँ',
			'Gallery'                          => 'गैलरी',
			'Notices'                          => 'सूचनाएँ',
			'Contact'                          => 'संपर्क',
			'Apply Now'                        => 'आवेदन करें',
			'Enquire Now'                      => 'पूछताछ करें',
			'Quick Links'                      => 'महत्वपूर्ण लिंक',
			'Digrota, Satnali, Mahendragarh (Haryana)' => 'डिगरोता, सतनाली, महेंद्रगढ़ (हरियाणा)',
			'INC Approved'                     => 'INC द्वारा अनुमोदित',
			'HNRC Recognised'                  => 'HNRC से मान्यता प्राप्त',
			'Affiliated to UHSR Rohtak'        => 'UHSR रोहतक से संबद्ध',
			'Admissions Open →'                => 'प्रवेश जारी हैं →',
			'Shri Ram College'                 => 'श्री राम कॉलेज',
			'of Medical Science & Research'    => 'ऑफ़ मेडिकल साइंस एंड रिसर्च',
			'Shri Ram College of Medical Science & Research, home' => 'श्री राम कॉलेज ऑफ़ मेडिकल साइंस एंड रिसर्च, होम',
			'SRGI Haryana logo'                => 'एसआरजीआई हरियाणा का लोगो',
			'Digrota, Mahendragarh'            => 'डिगरोता, महेंद्रगढ़',
			'Nursing and paramedical education in rural Haryana, approved by the Indian Nursing Council and affiliated to Pt. B.D. Sharma University of Health Sciences, Rohtak, with clinical training at our own 100-bed hospital.' => 'ग्रामीण हरियाणा में नर्सिंग और पैरामेडिकल शिक्षा — भारतीय नर्सिंग परिषद से अनुमोदित, पं. बी.डी. शर्मा स्वास्थ्य विज्ञान विश्वविद्यालय, रोहतक से संबद्ध, और हमारे अपने 100 बिस्तरों वाले अस्पताल में क्लिनिकल प्रशिक्षण के साथ।',
			'VPO Digrota, Nangal Mala Road, Tehsil Satnali, Distt. Mahendragarh, Haryana – 123024' => 'गाँव व डाकघर डिगरोता, नांगल माला रोड, तहसील सतनाली, जिला महेंद्रगढ़, हरियाणा – 123024',
			'View on Google Maps ↗'            => 'गूगल मैप्स पर देखें ↗',
			'Send an enquiry →'                => 'पूछताछ भेजें →',
			'All rights reserved.'             => 'सर्वाधिकार सुरक्षित।',
			'Digrota · Satnali · Mahendragarh · Haryana 123024' => 'डिगरोता · सतनाली · महेंद्रगढ़ · हरियाणा 123024',
			'To be updated'                    => 'शीघ्र अपडेट किया जाएगा',
			'Language'                         => 'भाषा',
			'Shri Ram College of Medical Science & Research' => 'श्री राम कॉलेज ऑफ़ मेडिकल साइंस एंड रिसर्च',
			'Nursing & Paramedical Education · Digrota, Mahendragarh' => 'नर्सिंग एवं पैरामेडिकल शिक्षा · डिगरोता, महेंद्रगढ़',
		);
	}
	return isset( $hi[ $en ] ) ? $hi[ $en ] : $en;
}

/** Site-relative link in the current language: '/about/' -> '/hi/about/' on Hindi pages. */
function shriram_url( $path ) {
	if ( 'hi' === shriram_lang() ) {
		$path = '/' . SHRIRAM_HI_ROOT . $path;
	}
	return home_url( $path );
}

/**
 * The same page in the other language: array( 'en' => url, 'hi' => url ). Falls back to the
 * other language's home page when the twin page does not exist (posts, archives, 404…).
 */
function shriram_alternates() {
	$urls = array(
		'en' => home_url( '/' ),
		'hi' => home_url( '/' . SHRIRAM_HI_ROOT . '/' ),
	);
	$post = get_queried_object();
	if ( ! ( $post instanceof WP_Post ) || 'page' !== $post->post_type ) {
		return $urls;
	}
	$path = get_page_uri( $post );
	if ( 'hi' === shriram_lang() ) {
		$en_path = preg_replace( '#^' . SHRIRAM_HI_ROOT . '(/|$)#', '', $path );
		$twin    = '' === $en_path ? (int) get_option( 'page_on_front' ) : get_page_by_path( $en_path );
		$urls['hi'] = get_permalink( $post );
	} else {
		$front      = (int) get_option( 'page_on_front' ) === $post->ID;
		$twin       = get_page_by_path( $front ? SHRIRAM_HI_ROOT : SHRIRAM_HI_ROOT . '/' . $path );
		$urls['en'] = get_permalink( $post );
	}
	if ( $twin && 'publish' === get_post_status( $twin ) ) {
		$urls[ 'hi' === shriram_lang() ? 'en' : 'hi' ] = get_permalink( $twin );
	}
	return $urls;
}

/** <html lang="hi-IN"> on Hindi pages. */
add_filter(
	'language_attributes',
	function ( $output ) {
		return 'hi' === shriram_lang() ? preg_replace( '/lang="[^"]*"/', 'lang="hi-IN"', $output ) : $output;
	}
);

/** Hindi site name and tagline in the browser title, footer and anywhere else they show. */
foreach ( array( 'blogname', 'blogdescription' ) as $shriram_opt ) {
	add_filter(
		"option_$shriram_opt",
		function ( $value ) {
			if ( 'hi' !== shriram_lang() ) {
				return $value;
			}
			// Stored HTML-escaped ("&amp;"), so look up the plain text.
			$plain = wp_specialchars_decode( $value, ENT_QUOTES );
			$hi    = shriram_t( $plain );
			return $hi === $plain ? $value : esc_html( $hi );
		}
	);
}

/** Tell search engines about the other-language twin of each page. */
add_action(
	'wp_head',
	function () {
		if ( ! is_page() ) {
			return;
		}
		foreach ( shriram_alternates() as $lang => $url ) {
			printf( '<link rel="alternate" hreflang="%1$s" href="%2$s">' . "\n", esc_attr( $lang ), esc_url( $url ) );
		}
	}
);

/** "English | हिन्दी" switcher used in the header. */
function shriram_lang_switcher() {
	$alt  = shriram_alternates();
	$cur  = shriram_lang();
	$html = '<nav class="sr-lang" aria-label="' . esc_attr( 'hi' === $cur ? shriram_t( 'Language' ) . ' / Language' : 'Language / भाषा' ) . '">';
	foreach ( array(
		'en' => 'English',
		'hi' => 'हिन्दी',
	) as $lang => $label ) {
		$html .= $lang === $cur
			? '<span aria-current="true" lang="' . $lang . '">' . $label . '</span>'
			: '<a href="' . esc_url( $alt[ $lang ] ) . '" hreflang="' . $lang . '" lang="' . $lang . '">' . $label . '</a>';
	}
	return $html . '</nav>';
}

/** The footer's site-title block links to the home page of the current language. */
add_filter(
	'render_block_core/site-title',
	function ( $html ) {
		if ( 'hi' !== shriram_lang() ) {
			return $html;
		}
		return preg_replace( '#href="' . preg_quote( esc_url( home_url() ), '#' ) . '/?"#', 'href="' . esc_url( shriram_url( '/' ) ) . '"', $html );
	}
);

/** Hindi alt text on photos (page banners) when the college has one stored (see load-pages.php). */
add_filter(
	'wp_get_attachment_image_attributes',
	function ( $attr, $attachment ) {
		if ( 'hi' === shriram_lang() ) {
			$alt = get_post_meta( $attachment->ID, '_sr_alt_hi', true );
			if ( $alt ) {
				$attr['alt'] = $alt;
			}
		}
		return $attr;
	},
	10,
	2
);

/** WordPress and plugin text that appears on the page (menu buttons, skip link, form dropdown). */
add_filter(
	'gettext',
	function ( $translation, $text ) {
		static $hi = array(
			'Skip to content'                     => 'सामग्री पर जाएँ',
			'Open menu'                           => 'मेनू खोलें',
			'Close menu'                          => 'मेनू बंद करें',
			'%s submenu'                          => '%s उप-मेनू',
			'&#8212;Please choose an option&#8212;' => '&#8212;कृपया एक विकल्प चुनें&#8212;',
		);
		return ( isset( $hi[ $text ] ) && 'hi' === shriram_lang() ) ? $hi[ $text ] : $translation;
	},
	10,
	2
);

/** Hindi month names in dates (notices) on Hindi pages. */
add_filter(
	'wp_date',
	function ( $date ) {
		if ( 'hi' !== shriram_lang() ) {
			return $date;
		}
		$en = array( 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' );
		$hi = array( 'जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर', 'जन॰', 'फ़र॰', 'मार्च', 'अप्रैल', 'जून', 'जुलाई', 'अग॰', 'सित॰', 'अक्टू॰', 'नव॰', 'दिस॰' );
		return preg_replace_callback(
			'/\b(' . implode( '|', $en ) . ')\b/',
			fn( $m ) => $hi[ array_search( $m[1], $en, true ) ],
			$date
		);
	}
);
