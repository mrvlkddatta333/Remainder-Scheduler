// static/js/scripts.js

$(document).ready(function() {
    // Add smooth scrolling to anchor links
    $("a").on('click', function(event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800, function(){
                window.location.hash = hash;
            });
        }
    });

    // Password visibility toggle
    $('.password-toggle').click(function() {
        const passwordInput = $(this).siblings('.password-input');
        const icon = $(this).find('i');

        if (passwordInput.attr('type') === 'password') {
            passwordInput.attr('type', 'text');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        } else {
            passwordInput.attr('type', 'password');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        }
    });

    // Add fadeInUp animation to content sections
    $('.content').addClass('fadeInUp');
});
