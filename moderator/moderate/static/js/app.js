jQuery(document).ready(function ($) {
    $('.vote, .button').click(function() {
        var question_id = this.id;
        $.ajax({
            url: '/q/' + question_id + '/upvote',
            type: 'GET',
            dataType: 'json',
            success: function(json) {
                $('#'+question_id).prev().html(json.current_vote_count);
                $('#'+question_id).addClass('insensitive').text('supported');
            }
         })
    })
    $('.insensitive').html('supported');


    $(document).on("click", ".alert-box a.close", function(event) {
        event.preventDefault();
        $(this).closest(".alert-box").fadeOut(function(event){
            $(this).remove();
        });
    });
})
