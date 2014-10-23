jQuery(document).ready(function ($) {
  $('.reply-button').click(function () {
    var action_post = $('.billboard.question form').attr('action')+'/q/'+this.id;
    $('#question-reply form').attr('action',action_post);
  });
});