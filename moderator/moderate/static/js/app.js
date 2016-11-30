jQuery(document).ready(function ($) {
    $('.vote.btn').click(function () {
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

    $("#page-select").on('change', function () {
        window.location = $(this).val();
    });

    $('.reply-button').click(function () {
        var action_post = $('#question-form').attr('action')+'/q/'+this.id;
        $('#answer-form').attr('action', action_post);
    });
});
