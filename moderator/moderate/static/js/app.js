jQuery(document).ready(function ($) {
    $('.vote.button').click(function () {
        var question_id = this.id;
        $.ajax({
            url: '/q/' + question_id + '/upvote',
            type: 'GET',
            dataType: 'json',
            success: function (json) {
                $('#' + question_id).prev().html(json.current_vote_count);
                $('#' + question_id).toggleClass('insensitive').text(json.status);
            }
        });
    });

    $(document).on("click", ".alert-box a.close", function (event) {
        event.preventDefault();
        $(this).closest(".alert-box").fadeOut(function (event) {
            $(this).remove();
        });
    });

    $("#page-select").on('change', function () {
        window.location = $(this).val();
    });

});

function login() {
    var settings_b64 = $('body').data('auth0-settings');
    var settings = JSON.parse(atob(settings_b64));

    $.getJSON('/set_oidc_state', function(response) {
        var lock = new Auth0LockPasswordless(settings.AUTH0_CLIENT_ID, settings.AUTH0_DOMAIN);
        var options = {
            callbackURL: settings.AUTH0_CALLBACK_URL,
            authParams: {
                state: response.oidc_state
            }
        };
        lock.magiclink(options);
    });
}

$('.login').click(function(){
    login();
});
