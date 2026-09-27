/* Shri Ram College: small progressive enhancements. The site works fully without this file. */
( function () {
	var reduce = window.matchMedia && window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches;
	var root = document.documentElement;

	/* Header gets a stronger shadow once the page scrolls. */
	var onScroll = function () {
		root.classList.toggle( 'sr-scrolled', window.scrollY > 40 );
	};
	window.addEventListener( 'scroll', onScroll, { passive: true } );
	onScroll();

	/* Course filter: All / Degrees / Diplomas. */
	document.querySelectorAll( '.sr-filter' ).forEach( function ( bar ) {
		var section = bar.closest( '.sr-courses' ) || document;
		var grid = section.querySelector( '.sr-bento' );
		if ( ! grid ) {
			return;
		}
		bar.addEventListener( 'click', function ( e ) {
			var btn = e.target.closest( 'button[data-filter]' );
			if ( ! btn ) {
				return;
			}
			var f = btn.getAttribute( 'data-filter' );
			bar.querySelectorAll( 'button' ).forEach( function ( b ) {
				var on = b === btn;
				b.classList.toggle( 'is-active', on );
				b.setAttribute( 'aria-pressed', on ? 'true' : 'false' );
			} );
			grid.classList.toggle( 'is-filtered', f !== 'all' );
			grid.querySelectorAll( '.sr-course-card' ).forEach( function ( card ) {
				card.classList.toggle( 'is-hidden', f !== 'all' && ! card.classList.contains( 'sr-kind-' + f ) );
			} );
		} );
	} );

	if ( reduce || ! ( 'IntersectionObserver' in window ) ) {
		return;
	}

	/* Scroll reveal: fade/slide items in as they enter the viewport, staggered within a row. */
	var targets = document.querySelectorAll(
		'.sr-card, .sr-section-head, .sr-stats > .wp-block-column, .sr-approvals > .wp-block-column, .sr-pillar, .sr-reveal, .wp-block-table, .sr-photo-slot'
	);
	root.classList.add( 'sr-js' );
	var io = new IntersectionObserver( function ( entries ) {
		entries.forEach( function ( e ) {
			if ( e.isIntersecting ) {
				e.target.classList.add( 'is-visible' );
				io.unobserve( e.target );
			}
		} );
	}, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 } );
	targets.forEach( function ( el ) {
		var parent = el.parentElement;
		var siblings = parent ? Array.prototype.indexOf.call( parent.children, el ) : 0;
		/* Cards inside a column: stagger by the column's position in its row. */
		if ( parent && parent.classList.contains( 'wp-block-column' ) && parent.parentElement ) {
			siblings = Array.prototype.indexOf.call( parent.parentElement.children, parent );
		}
		el.style.setProperty( '--sr-delay', Math.min( siblings, 5 ) * 90 + 'ms' );
		el.classList.add( 'sr-will-reveal' );
		io.observe( el );
	} );

	/* Count-up for stat numbers such as "100" or "170+". */
	var counters = document.querySelectorAll( '.sr-stat__num' );
	var cio = new IntersectionObserver( function ( entries ) {
		entries.forEach( function ( e ) {
			if ( ! e.isIntersecting ) {
				return;
			}
			cio.unobserve( e.target );
			var m = e.target.textContent.match( /^(\d+)(.*)$/ );
			if ( ! m ) {
				return;
			}
			var end = parseInt( m[ 1 ], 10 );
			var suffix = m[ 2 ];
			var start = null;
			var dur = 1400;
			var step = function ( t ) {
				if ( ! start ) {
					start = t;
				}
				var p = Math.min( ( t - start ) / dur, 1 );
				var eased = 1 - Math.pow( 1 - p, 3 );
				e.target.textContent = Math.round( end * eased ) + suffix;
				if ( p < 1 ) {
					requestAnimationFrame( step );
				}
			};
			requestAnimationFrame( step );
		} );
	}, { threshold: 0.6 } );
	counters.forEach( function ( c ) {
		cio.observe( c );
	} );
} )();
