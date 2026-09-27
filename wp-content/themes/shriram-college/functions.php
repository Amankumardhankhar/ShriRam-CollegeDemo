<?php
/**
 * Shri Ram College theme functions.
 *
 * @package shriram-college
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

require_once __DIR__ . '/inc/i18n.php';

add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'editor-styles' );
		add_editor_style( array( 'assets/css/icons.css', 'style.css' ) );
	}
);

add_action(
	'wp_enqueue_scripts',
	function () {
		$ver = wp_get_theme()->get( 'Version' );
		wp_enqueue_style( 'shriram-college-icons', get_theme_file_uri( 'assets/css/icons.css' ), array(), $ver );
		wp_enqueue_style( 'shriram-college', get_stylesheet_uri(), array( 'shriram-college-icons' ), $ver );
		wp_enqueue_script( 'shriram-college', get_theme_file_uri( 'assets/js/site.js' ), array(), $ver, array( 'strategy' => 'defer', 'in_footer' => true ) );
	}
);

add_action(
	'init',
	function () {
		register_block_pattern_category( 'shriram-college', array( 'label' => __( 'Shri Ram College', 'shriram-college' ) ) );

		register_block_style(
			'core/group',
			array(
				'name'  => 'card',
				'label' => __( 'Card', 'shriram-college' ),
			)
		);
	}
);

/**
 * Details shown in the header and footer. Edit here (or override via Settings) once the
 * college confirms its phone number and email.
 */
function shriram_contact() {
	return array(
		'address' => shriram_t( 'VPO Digrota, Nangal Mala Road, Tehsil Satnali, Distt. Mahendragarh, Haryana – 123024' ),
		'phone'   => get_option( 'shriram_phone', '' ),
		'email'   => get_option( 'shriram_email', '' ),
		'map'     => 'https://www.google.com/maps?q=28.365143,76.040255',
	);
}

/**
 * [sr_contact field="phone"] prints a contact detail, or a placeholder when the college
 * has not supplied it yet. Keeps the number in one place (Settings option) for header,
 * footer and Contact page.
 */
add_shortcode(
	'sr_contact',
	function ( $atts ) {
		$atts  = shortcode_atts( array( 'field' => 'phone' ), $atts );
		$c     = shriram_contact();
		$value = isset( $c[ $atts['field'] ] ) ? $c[ $atts['field'] ] : '';
		if ( '' === $value ) {
			return '<span class="sr-missing">' . esc_html( shriram_t( 'To be updated' ) ) . '</span>';
		}
		if ( 'phone' === $atts['field'] ) {
			return '<a href="tel:' . esc_attr( preg_replace( '/[^0-9+]/', '', $value ) ) . '">' . esc_html( $value ) . '</a>';
		}
		if ( 'email' === $atts['field'] ) {
			return '<a href="mailto:' . esc_attr( $value ) . '">' . esc_html( $value ) . '</a>';
		}
		return esc_html( $value );
	}
);

/** Phone / email fields on Settings → General so staff can update them without code. */
add_action(
	'admin_init',
	function () {
		foreach ( array(
			'shriram_phone' => __( 'College phone', 'shriram-college' ),
			'shriram_email' => __( 'College email', 'shriram-college' ),
		) as $key => $label ) {
			register_setting( 'general', $key, array( 'sanitize_callback' => 'sanitize_text_field' ) );
			add_settings_field(
				$key,
				$label,
				function () use ( $key ) {
					printf( '<input type="text" class="regular-text" name="%1$s" value="%2$s">', esc_attr( $key ), esc_attr( get_option( $key, '' ) ) );
				},
				'general'
			);
		}
	}
);

// Use the SRGI logo as the favicon unless a Site Icon has been set in the Customizer.
add_action(
	'wp_head',
	function () {
		if ( ! has_site_icon() ) {
			printf( '<link rel="icon" type="image/svg+xml" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/images/srgi-logo.svg' ) ) );
		}
	}
);
