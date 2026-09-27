<?php
/**
 * Title: Site footer
 * Slug: shriram-college/footer
 * Categories: footer
 * Block Types: core/template-part/footer
 * Inserter: no
 */

$c = shriram_contact();
$t = 'shriram_t';
$u = 'shriram_url';
?>
<!-- wp:group {"tagName":"footer","align":"full","className":"sr-footer","backgroundColor":"dark","textColor":"white","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|30"}}},"layout":{"type":"constrained","contentSize":"1200px"}} -->
<footer class="wp-block-group alignfull sr-footer has-white-color has-dark-background-color has-text-color has-background" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--30)">
	<!-- wp:columns {"style":{"spacing":{"blockGap":{"left":"var:preset|spacing|50"}}}} -->
	<div class="wp-block-columns">
		<!-- wp:column {"width":"36%"} -->
		<div class="wp-block-column" style="flex-basis:36%">
			<!-- wp:group {"className":"sr-brand","layout":{"type":"flex","flexWrap":"nowrap"}} -->
			<div class="wp-block-group sr-brand">
				<!-- wp:image {"width":"52px","height":"52px","sizeSlug":"full"} -->
				<figure class="wp-block-image size-full is-resized"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/srgi-logo.svg' ) ); ?>" alt="" style="width:52px;height:52px"/></figure>
				<!-- /wp:image -->
				<!-- wp:site-title {"level":0,"style":{"typography":{"fontSize":"1.05rem","fontWeight":"700","lineHeight":"1.25"},"elements":{"link":{"color":{"text":"#ffffff"}}}}} /-->
			</div>
			<!-- /wp:group -->
			<!-- wp:paragraph {"style":{"color":{"text":"#c9d6de"}}} -->
			<p class="has-text-color" style="color:#c9d6de"><?php echo esc_html( $t( 'Nursing and paramedical education in rural Haryana, approved by the Indian Nursing Council and affiliated to Pt. B.D. Sharma University of Health Sciences, Rohtak, with clinical training at our own 100-bed hospital.' ) ); ?></p>
			<!-- /wp:paragraph -->
		</div>
		<!-- /wp:column -->

		<!-- wp:column -->
		<div class="wp-block-column">
			<!-- wp:heading {"level":2} -->
			<h2 class="wp-block-heading"><?php echo esc_html( $t( 'Courses' ) ); ?></h2>
			<!-- /wp:heading -->
			<!-- wp:html -->
			<ul>
				<li><a href="<?php echo esc_url( $u( '/courses/bsc-nursing/' ) ); ?>"><?php echo esc_html( $t( 'B.Sc Nursing' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/courses/post-basic-bsc-nursing/' ) ); ?>"><?php echo esc_html( $t( 'Post Basic B.Sc Nursing' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/courses/bsc-paramedical-science/' ) ); ?>"><?php echo esc_html( $t( 'B.Sc Paramedical Science' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/courses/gnm/' ) ); ?>"><?php echo esc_html( $t( 'GNM' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/courses/anm/' ) ); ?>"><?php echo esc_html( $t( 'ANM' ) ); ?></a></li>
			</ul>
			<!-- /wp:html -->
		</div>
		<!-- /wp:column -->

		<!-- wp:column -->
		<div class="wp-block-column">
			<!-- wp:heading {"level":2} -->
			<h2 class="wp-block-heading"><?php echo esc_html( $t( 'Quick Links' ) ); ?></h2>
			<!-- /wp:heading -->
			<!-- wp:html -->
			<ul>
				<li><a href="<?php echo esc_url( $u( '/admissions/' ) ); ?>"><?php echo esc_html( $t( 'Admissions' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/fee-structure/' ) ); ?>"><?php echo esc_html( $t( 'Fee Structure' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/approvals/' ) ); ?>"><?php echo esc_html( $t( 'Approvals & Affiliations' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/hospital/' ) ); ?>"><?php echo esc_html( $t( 'Hospital' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/faculty/' ) ); ?>"><?php echo esc_html( $t( 'Faculty' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/gallery/' ) ); ?>"><?php echo esc_html( $t( 'Gallery' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/mandatory-disclosure/' ) ); ?>"><?php echo esc_html( $t( 'Mandatory Disclosure' ) ); ?></a></li>
			</ul>
			<!-- /wp:html -->
		</div>
		<!-- /wp:column -->

		<!-- wp:column {"width":"28%"} -->
		<div class="wp-block-column" style="flex-basis:28%">
			<!-- wp:heading {"level":2} -->
			<h2 class="wp-block-heading"><?php echo esc_html( $t( 'Contact' ) ); ?></h2>
			<!-- /wp:heading -->
			<!-- wp:html -->
			<ul>
				<li><?php echo esc_html( $c['address'] ); ?></li>
				<?php if ( $c['phone'] ) : ?><li>☎ <a href="tel:<?php echo esc_attr( preg_replace( '/[^0-9+]/', '', $c['phone'] ) ); ?>"><?php echo esc_html( $c['phone'] ); ?></a></li><?php endif; ?>
				<?php if ( $c['email'] ) : ?><li>✉ <a href="mailto:<?php echo esc_attr( $c['email'] ); ?>"><?php echo esc_html( $c['email'] ); ?></a></li><?php endif; ?>
				<li><a href="<?php echo esc_url( $c['map'] ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $t( 'View on Google Maps ↗' ) ); ?></a></li>
				<li><a href="<?php echo esc_url( $u( '/contact/' ) ); ?>"><?php echo esc_html( $t( 'Send an enquiry →' ) ); ?></a></li>
			</ul>
			<!-- /wp:html -->
		</div>
		<!-- /wp:column -->
	</div>
	<!-- /wp:columns -->

	<!-- wp:group {"className":"sr-footer__bottom","style":{"spacing":{"padding":{"top":"var:preset|spacing|30"},"margin":{"top":"var:preset|spacing|50"}}},"layout":{"type":"flex","flexWrap":"wrap","justifyContent":"space-between"}} -->
	<div class="wp-block-group sr-footer__bottom" style="margin-top:var(--wp--preset--spacing--50);padding-top:var(--wp--preset--spacing--30)">
		<!-- wp:paragraph -->
		<p>© <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php echo esc_html( get_bloginfo( 'name' ) ); ?>. <?php echo esc_html( $t( 'All rights reserved.' ) ); ?></p>
		<!-- /wp:paragraph -->
		<!-- wp:paragraph -->
		<p><?php echo esc_html( $t( 'Digrota · Satnali · Mahendragarh · Haryana 123024' ) ); ?></p>
		<!-- /wp:paragraph -->
	</div>
	<!-- /wp:group -->
</footer>
<!-- /wp:group -->

<!-- wp:html -->
<a class="sr-fab" href="<?php echo esc_url( $u( '/contact/' ) ); ?>"><?php echo esc_html( $t( 'Enquire Now' ) ); ?></a>
<!-- /wp:html -->
