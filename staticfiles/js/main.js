(function ($) {
    "use strict";

    // Keep the same scroll position after page refresh
    var scrollStorageKey = "dpramp_scroll_position";
    var currentPath = window.location.pathname + window.location.search;

    try {
        if ("scrollRestoration" in window.history) {
            window.history.scrollRestoration = "manual";
        }

        var savedScroll = sessionStorage.getItem(scrollStorageKey);
        if (savedScroll) {
            var parsed = JSON.parse(savedScroll);
            if (parsed && parsed.path === currentPath) {
                window.requestAnimationFrame(function () {
                    window.scrollTo(0, parsed.y || 0);
                });
            }
        }

        var saveScrollPosition = function () {
            sessionStorage.setItem(
                scrollStorageKey,
                JSON.stringify({ path: currentPath, y: window.scrollY || window.pageYOffset || 0 })
            );
        };

        window.addEventListener("beforeunload", saveScrollPosition);
        window.addEventListener("pagehide", saveScrollPosition);
    } catch (e) {
        // Ignore storage/restore errors safely
    }

        
    
    // Initiate wowjs (disable on small screens / reduced-motion for smoother scrolling)
    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var isSmallScreen = window.innerWidth < 768;
    if (!reduceMotion && !isSmallScreen) {
        new WOW().init();
    }

    // Optimized scroll handling (single passive listener + rAF)
    var lastScrollY = window.scrollY || 0;
    var ticking = false;
    var backToTopVisible = false;
    var navbarScrolled = false;

    var updateOnScroll = function () {
        var scrollY = lastScrollY;

        // Navbar shadow toggle
        var shouldNavbarScroll = scrollY > 100;
        if (shouldNavbarScroll !== navbarScrolled) {
            navbarScrolled = shouldNavbarScroll;
            $('.navbar').toggleClass('navbar-scrolled shadow-sm', shouldNavbarScroll);
        }

        // Back-to-top visibility toggle (avoid repeated animations every scroll tick)
        var shouldShowBackToTop = scrollY > 300;
        if (shouldShowBackToTop !== backToTopVisible) {
            backToTopVisible = shouldShowBackToTop;
            if (shouldShowBackToTop) {
                $('.back-to-top').stop(true, true).fadeIn(180);
            } else {
                $('.back-to-top').stop(true, true).fadeOut(180);
            }
        }

        ticking = false;
    };

    window.addEventListener('scroll', function () {
        lastScrollY = window.scrollY || window.pageYOffset || 0;
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(updateOnScroll);
        }
    }, { passive: true });

    // Run once on load for correct initial UI state
    updateOnScroll();

    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Facts counter
    $('[data-toggle="counter-up"]').counterUp({
        delay: 10,
        time: 2000
    });


    // Project carousel
    $(".project-carousel").owlCarousel({
        autoplay: true,
        autoplayTimeout: 2000,
        autoplayHoverPause: true,
        smartSpeed: 500,
        margin: 25,
        loop: true,
        center: true,
        dots: false,
        nav: true,
        navText : [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ],
        responsive: {
			0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        margin: 24,
        dots: true,
        loop: true,
        nav : false,
        responsive: {
            0:{
                items:1
            },
			576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });

    // Contact Form - Redirect to Email
    $('#contactForm').on('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        var name = $('#name').val().trim();
        var email = $('#email').val().trim();
        var phone = $('#phone').val().trim();
        var serviceSelect = $('#service');
        var service = serviceSelect.find('option:selected').text();
        var message = $('#message').val().trim();
        
        // Email subject
        var subject = encodeURIComponent('New Contact Form Submission - ' + service);
        
        // Format email body with all details
        var emailBody = 'Dear DPRAMP-TECH Solutions,\n\n';
        emailBody += 'I would like to get in touch regarding your services.\n\n';
        emailBody += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
        emailBody += 'CONTACT DETAILS\n';
        emailBody += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
        emailBody += 'Full Name: ' + name + '\n';
        emailBody += 'Email Address: ' + email + '\n';
        emailBody += 'Mobile Number: ' + phone + '\n';
        emailBody += 'Service Type: ' + service + '\n\n';
        emailBody += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
        emailBody += 'MESSAGE\n';
        emailBody += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
        emailBody += message + '\n\n';
        emailBody += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
        emailBody += 'Thank you for your time and consideration.\n\n';
        emailBody += 'Best regards,\n' + name;
        
        // Encode the body for URL
        var body = encodeURIComponent(emailBody);
        
        // Create mailto link with recipient email
        var recipientEmail = 'info@dpramp.com,dpramptechsolution@gmail.com';
        var mailtoLink = 'mailto:' + recipientEmail + '?subject=' + subject + '&body=' + body;
        
        // Open email client
        window.location.href = mailtoLink;
    });

    var initHeroCoin = function () {
        var coin = $('#heroCoin');
        if (!coin.length) {
            return;
        }

        var imagesRaw = coin.attr('data-images');
        if (!imagesRaw) {
            return;
        }

        var images = [];
        try {
            images = JSON.parse(imagesRaw);
        } catch (e) {
            return;
        }

        if (!Array.isArray(images) || images.length < 2) {
            return;
        }

        var front = coin.find('.hero-coin-front')[0];
        var back = coin.find('.hero-coin-back')[0];
        if (!front || !back) {
            return;
        }

        var currentIndex = 0;
        front.src = images[currentIndex];
        back.src = images[(currentIndex + 1) % images.length];

        var isFlipping = false;

        var flip = function () {
            if (isFlipping) {
                return;
            }

            isFlipping = true;
            var nextIndex = (currentIndex + 1) % images.length;

            back.src = images[nextIndex];
            coin.addClass('is-flipping');

            setTimeout(function () {
                coin.removeClass('is-flipping');
                front.src = images[nextIndex];
                currentIndex = nextIndex;
                isFlipping = false;
            }, 950);
        };

        setInterval(flip, 3000);
    };

    initHeroCoin();
    
})(jQuery);
