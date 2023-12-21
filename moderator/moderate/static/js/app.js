jQuery(document).ready(function ($) {
    $('.vote.btn').on("click", function () {
        var question_id = this.id;
        var icon = '#' + question_id + ' > .glyphicon';
        $.ajax({
            url: '/q/' + question_id + '/upvote',
            type: 'GET',
            dataType: 'json',
            success: function (json) {
                $('#' + question_id).prev().html(json.current_vote_count);
                $(icon).toggleClass('glyphicon-thumbs-down').toggleClass('glyphicon-thumbs-up');
            }
        });
    });

    $('#page-select').on('change', function () {
        window.location = $(this).val();
    });

    $('.reply-button').on("click", function () {
        var action_post = $('#question-form').attr('action')+'q/'+this.id + '/reply';
        $('#answer-form').attr('action', action_post);
    });

    $('.moderate-button').on("click", function () {
        var action_post = $('#moderate-form').attr('action')+this.id + '/rejected';
        $('#moderate-form').attr('action', action_post);
    });

    function toggleContactInfo() {
        if ( $("#id_is_anonymous").is(":checked")) {
            $(".contact-info-container").show();
        }
        else {
            $(".contact-info-container").hide();
        }
    }

    $('[data-toggle="tooltip"]').tooltip();
    toggleContactInfo()
    $("#id_is_anonymous").on("click", toggleContactInfo);

    $('#logout').on("click", function() {
        $('#logout_form').submit();
    });
});
