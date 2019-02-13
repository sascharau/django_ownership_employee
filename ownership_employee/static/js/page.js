
$(document).ready(function () {
    $(".app-main").css("min-height", $(window).height() - 60 + "px");
})

var Side = {

  _ps: $('.app-side'),
  _body: $('body'),
  _heading: $('.side-heading'),

  responsive: function responsive() {
    $(window).width() < 768 ?
        Side._body.removeClass('app-side-mini app-side-opened').addClass('app-side-closed') :
        Side._body.addClass('app-side-mini app-side-opened').removeClass('app-side-closed');
  },

  collapse: function collapse(element) {
    $(element).on('click', function (event) {
      event.preventDefault();
      Side._body.toggleClass('app-side-opened app-side-closed');
      Side._stopMetisMenu();

    });
  },

  mini: function mini(element) {
    $(element).on('click', function (event) {
      event.preventDefault();
      Side._body.toggleClass('app-side-mini');
      Side._stopMetisMenu();

      $('.side-heading').toggleClass('heading-mini');
      $('.username').toggleClass('hidden');
      $('.user').toggleClass('client-icon-mini');
      $('.side-nav').toggleClass('side-nav-mini');
      $('.nav-title').toggleClass('hidden');

    });
  },

  _stopMetisMenu: function _stopMetisMenu() {
    $('.side-nav').find('li').removeClass('active');
    $('.side-nav').find('a').attr('aria-expanded', false);
    $('.side-nav').find('ul.collapse').removeClass('in').attr('aria-expanded', false);
  }

};

$(document).on("chl.side", function () {
  Side.responsive();
  $("[data-side]").each(function () {
    Side[$(this).attr("data-side")](this);
  });
}).trigger("chl.side");

