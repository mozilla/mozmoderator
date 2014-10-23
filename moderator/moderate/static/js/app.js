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
