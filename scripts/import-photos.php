<?php
/**
 * Import Photos/web/*.jpg into the Media Library once (run via `wp eval-file`).
 * Each attachment gets slug "srphoto-<slug>", alt text, and, for photos by Google Maps
 * contributors, a credit caption. Re-running skips photos that already exist.
 */
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

$photos = json_decode( file_get_contents( '/project/Photos/web/photos.json' ), true );
$new    = 0;

foreach ( $photos as $ph ) {
	$name = 'srphoto-' . $ph['slug'];
	if ( get_page_by_path( $name, OBJECT, 'attachment' ) ) {
		continue;
	}
	$tmp = wp_tempnam( $ph['slug'] . '.jpg' );
	copy( '/project/' . $ph['file'], $tmp );
	$id = media_handle_sideload(
		array(
			'name'     => $ph['slug'] . '.jpg',
			'tmp_name' => $tmp,
		),
		0,
		$ph['alt'],
		array(
			'post_name'    => $name,
			'post_excerpt' => $ph['credit'] ? $ph['credit'] : '',
		)
	);
	if ( is_wp_error( $id ) ) {
		WP_CLI::warning( $ph['slug'] . ': ' . $id->get_error_message() );
		continue;
	}
	update_post_meta( $id, '_wp_attachment_image_alt', $ph['alt'] );
	update_post_meta( $id, '_sr_source', 'Google Maps: ' . $ph['uploader'] . ( $ph['date'] ? ', ' . $ph['date'] : '' ) );
	++$new;
}
WP_CLI::log( "Photos imported: $new new, " . ( count( $photos ) - $new ) . ' already present.' );
