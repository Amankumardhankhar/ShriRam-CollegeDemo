<?php
/**
 * Create or update every page listed in content/pages.json (run via `wp eval-file`).
 * Pages are matched by slug + parent so re-running updates content instead of duplicating.
 * Each page has a unique "key" (its slug, or "hi/<slug>" for Hindi pages under /hi/).
 */

$dir   = '/project/content';
$pages = json_decode( file_get_contents( "$dir/pages.json" ), true );
$form  = getenv( 'FORM_BLOCK' );
$form_hi = getenv( 'FORM_BLOCK_HI' );
$fee   = getenv( 'FEE_URL' );
$ids   = array();

// Parents first: sort by depth in the page tree.
$by_key = array_column( $pages, null, 'key' );
$depth  = function ( $p ) use ( &$depth, $by_key ) {
	return $p['parent'] ? 1 + $depth( $by_key[ $p['parent'] ] ) : 0;
};
usort( $pages, fn( $a, $b ) => $depth( $a ) <=> $depth( $b ) );

foreach ( $pages as $p ) {
	$content = file_get_contents( "$dir/pages/" . ( 'hi' === $p['lang'] ? $p['key'] : $p['slug'] ) . '.html' );
	$content = str_replace( array( '{{CONTACT_FORM}}', '{{CONTACT_FORM_HI}}', '{{FEE_PDF}}', '{{THEME}}' ), array( $form, $form_hi, esc_url( $fee ), get_theme_file_uri() ), $content );
	// {{IMG:slug}} -> photo URL, {{IMGID:slug}} -> attachment ID (see scripts/import-photos.php).
	$content = preg_replace_callback(
		'/\{\{IMG(ID)?:([a-z0-9-]+)\}\}/',
		function ( $m ) {
			$att = get_page_by_path( 'srphoto-' . $m[2], OBJECT, 'attachment' );
			if ( ! $att ) {
				WP_CLI::warning( "Missing photo: {$m[2]}" );
				return $m[1] ? '0' : '';
			}
			return $m[1] ? (string) $att->ID : esc_url( wp_get_attachment_image_url( $att->ID, 'full' ) );
		},
		$content
	);
	$parent  = $p['parent'] ? ( $ids[ $p['parent'] ] ?? 0 ) : 0;

	$existing = get_posts(
		array(
			'post_type'   => 'page',
			'name'        => $p['slug'],
			'post_parent' => $parent,
			'post_status' => 'any',
			'numberposts' => 1,
		)
	);

	$data = array(
		'post_type'    => 'page',
		'post_status'  => 'publish',
		'post_title'   => $p['title'],
		'post_name'    => $p['slug'],
		'post_parent'  => $parent,
		'menu_order'   => $p['order'],
		'post_content' => $content,
	);
	if ( $existing ) {
		$data['ID'] = $existing[0]->ID;
	}
	// wp_insert_post runs kses unless the user can post unfiltered HTML (iframe, form markup).
	kses_remove_filters();
	$id = wp_insert_post( wp_slash( $data ), true );
	if ( is_wp_error( $id ) ) {
		WP_CLI::warning( "{$p['slug']}: " . $id->get_error_message() );
		continue;
	}
	update_post_meta( $id, '_wp_page_template', $p['template'] ?: 'default' );
	if ( ! empty( $p['featured'] ) ) {
		$att = get_page_by_path( 'srphoto-' . $p['featured'], OBJECT, 'attachment' );
		if ( $att ) {
			set_post_thumbnail( $id, $att->ID );
		}
	}
	$ids[ $p['key'] ] = $id;
	WP_CLI::log( ( $existing ? 'Updated' : 'Created' ) . " page: {$p['title']} (#$id)" );
}

// Hindi alt text for each photo, shown when it is a featured image on a Hindi page.
foreach ( json_decode( file_get_contents( "$dir/photo-alt-hi.json" ), true ) as $slug => $alt ) {
	$att = get_page_by_path( 'srphoto-' . $slug, OBJECT, 'attachment' );
	if ( $att ) {
		update_post_meta( $att->ID, '_sr_alt_hi', $alt );
	}
}
