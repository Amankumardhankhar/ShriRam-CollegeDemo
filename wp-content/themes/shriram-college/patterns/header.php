<?php
/**
 * Title: Site header
 * Slug: shriram-college/header
 * Categories: header
 * Block Types: core/template-part/header
 * Inserter: no
 */

$c = shriram_contact();
$t = 'shriram_t';
$u = 'shriram_url';

// Main menu: label => link, or label => array( link, submenu items ).
$menu = array(
	'Home'       => '/',
	'About'      => array(
		'/about/',
		array(
			'About the College'        => '/about/',
			'Approvals & Affiliations' => '/approvals/',
			'Faculty'                  => '/faculty/',
			'Mandatory Disclosure'     => '/mandatory-disclosure/',
		),
	),
	'Courses'    => array(
		'/courses/',
		array(
			'B.Sc Nursing'             => '/courses/bsc-nursing/',
			'Post Basic B.Sc Nursing'  => '/courses/post-basic-bsc-nursing/',
			'B.Sc Paramedical Science' => '/courses/bsc-paramedical-science/',
			'GNM'                      => '/courses/gnm/',
			'ANM'                      => '/courses/anm/',
		),
	),
	'Admissions' => array(
		'/admissions/',
		array(
			'Admission Process' => '/admissions/',
			'Fee Structure'     => '/fee-structure/',
		),
	),
	'Hospital'   => '/hospital/',
	'Campus'     => array(
		'/campus-facilities/',
		array(
			'Facilities' => '/campus-facilities/',
			'Gallery'    => '/gallery/',
		),
	),
	'Notices'    => '/notices/',
	'Contact'    => '/contact/',
);

$nav_attrs = function ( $label, $link ) use ( $t, $u ) {
	return wp_json_encode(
		array(
			'label' => $t( $label ),
			'url'   => $u( $link ),
			'kind'  => 'custom',
		),
		JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG | JSON_HEX_AMP
	);
};
?>
<!-- wp:group {"tagName":"div","align":"full","className":"sr-topbar","backgroundColor":"dark","textColor":"white","style":{"spacing":{"padding":{"top":"0.45rem","bottom":"0.45rem"}}},"layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull sr-topbar has-white-color has-dark-background-color has-text-color has-background" style="padding-top:0.45rem;padding-bottom:0.45rem">
	<!-- wp:group {"layout":{"type":"flex","flexWrap":"wrap","justifyContent":"space-between"}} -->
	<div class="wp-block-group">
		<!-- wp:paragraph -->
		<p>📍 <?php echo esc_html( $t( 'Digrota, Satnali, Mahendragarh (Haryana)' ) ); ?><?php if ( $c['phone'] ) : ?> &nbsp;·&nbsp; ☎ <a href="tel:<?php echo esc_attr( preg_replace( '/[^0-9+]/', '', $c['phone'] ) ); ?>"><?php echo esc_html( $c['phone'] ); ?></a><?php endif; ?><?php if ( $c['email'] ) : ?> &nbsp;·&nbsp; ✉ <a href="mailto:<?php echo esc_attr( $c['email'] ); ?>"><?php echo esc_html( $c['email'] ); ?></a><?php endif; ?></p>
		<!-- /wp:paragraph -->
		<!-- wp:paragraph -->
		<p><?php echo esc_html( $t( 'INC Approved' ) ); ?> &nbsp;·&nbsp; <?php echo esc_html( $t( 'HNRC Recognised' ) ); ?> &nbsp;·&nbsp; <?php echo esc_html( $t( 'Affiliated to UHSR Rohtak' ) ); ?> &nbsp;·&nbsp; <a href="<?php echo esc_url( $u( '/admissions/' ) ); ?>"><strong><?php echo esc_html( $t( 'Admissions Open →' ) ); ?></strong></a></p>
		<!-- /wp:paragraph -->
		<!-- wp:html -->
		<?php echo shriram_lang_switcher(); // phpcs:ignore WordPress.Security.EscapeOutput -- built from escaped parts. ?>
		<!-- /wp:html -->
	</div>
	<!-- /wp:group -->
</div>
<!-- /wp:group -->

<!-- wp:group {"tagName":"header","align":"full","className":"sr-header","backgroundColor":"white","style":{"spacing":{"padding":{"top":"0.8rem","bottom":"0.8rem"}}},"layout":{"type":"default"}} -->
<header class="wp-block-group alignfull sr-header has-white-background-color has-background" style="padding-top:0.8rem;padding-bottom:0.8rem">
	<!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}} -->
	<div class="wp-block-group">
		<!-- wp:group {"className":"sr-brand","layout":{"type":"flex","flexWrap":"nowrap"}} -->
		<div class="wp-block-group sr-brand">
			<!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"sr-brand__logo"} -->
			<figure class="wp-block-image size-full sr-brand__logo"><a href="<?php echo esc_url( $u( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/srgi-logo.svg' ) ); ?>" alt="<?php echo esc_attr( $t( 'SRGI Haryana logo' ) ); ?>"/></a></figure>
			<!-- /wp:image -->
			<!-- wp:html -->
			<a class="sr-wordmark" href="<?php echo esc_url( $u( '/' ) ); ?>" aria-label="<?php echo esc_attr( $t( 'Shri Ram College of Medical Science & Research, home' ) ); ?>">
				<span class="sr-wordmark__main"><?php echo esc_html( $t( 'Shri Ram College' ) ); ?></span>
				<span class="sr-wordmark__sub"><?php echo esc_html( $t( 'of Medical Science & Research' ) ); ?></span>
			</a>
			<!-- /wp:html -->
		</div>
		<!-- /wp:group -->

		<!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap"},"style":{"spacing":{"blockGap":"1.4rem"}}} -->
		<div class="wp-block-group">
		<!-- wp:navigation {"overlayMenu":"mobile","layout":{"type":"flex","justifyContent":"right"},"style":{"spacing":{"blockGap":"1.4rem"}}} -->
<?php foreach ( $menu as $label => $item ) : ?>
<?php if ( is_array( $item ) ) : ?>
			<!-- wp:navigation-submenu <?php echo $nav_attrs( $label, $item[0] ); // phpcs:ignore ?> -->
<?php foreach ( $item[1] as $sub_label => $sub_link ) : ?>
				<!-- wp:navigation-link <?php echo $nav_attrs( $sub_label, $sub_link ); // phpcs:ignore ?> /-->
<?php endforeach; ?>
			<!-- /wp:navigation-submenu -->
<?php else : ?>
			<!-- wp:navigation-link <?php echo $nav_attrs( $label, $item ); // phpcs:ignore ?> /-->
<?php endif; ?>
<?php endforeach; ?>
		<!-- /wp:navigation -->
		<!-- wp:buttons {"className":"sr-nav-cta"} -->
		<div class="wp-block-buttons sr-nav-cta"><!-- wp:button -->
		<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="<?php echo esc_url( $u( '/admissions/' ) ); ?>"><?php echo esc_html( $t( 'Apply Now' ) ); ?></a></div>
		<!-- /wp:button --></div>
		<!-- /wp:buttons -->
		</div>
		<!-- /wp:group -->
	</div>
	<!-- /wp:group -->
</header>
<!-- /wp:group -->
