$(document).ready(function(){
    // site nav

    $('.js-site-nav').hover(
      function() {
        $('.js-site-sub-nav-wrapper').doTimeout('hover',250,'addClass','is-hovered');
      }, function() {
        $('.js-site-sub-nav-wrapper').doTimeout('hover',250,'removeClass','is-hovered');
      }
    );
    
    $('.js-site-nav-item').hover(
      function() {
        var navSection = $(this).data('section');
        $('.js-site-sub-nav').find('[data-section='+navSection+']').addClass('is-hovered');
      }, function() {
        var navSection = $(this).data('section');
        $('.js-site-sub-nav').find('ul[data-section='+navSection+']').removeClass('is-hovered');
      }
    );

    $('.js-site-sub-nav').find('ul').hover(
      function() {
        var navSection = $(this).data('section');
        $('.js-site-nav-item[data-section='+navSection+']').addClass('is-hovered');
      }, function() {
        var navSection = $(this).data('section');
        $('.js-site-nav-item[data-section='+navSection+']').removeClass('is-hovered');
      }
    );

});
