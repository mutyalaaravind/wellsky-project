/*
 * Provides 8 extra placements for popover
 * Initially taken from https://github.com/dkleehammer/bootstrap-popover-extra-placements
 * CSS - /AM/lib/less/AM/popover-extra-placements.less
 *
 * Made some alterations to the container
 * Added "popoverClass" as an option, it gets appended to the main containing "popover" div
 * Added hiding the title bar if there is no title
 *
 * */
(function($) {
    "use strict";  // jshint;_;

    // save the original plugin function object
    var _super = $.fn.popover;

    // create a new constructor
    var Popover = function(element, options) {
        _super.Constructor.apply(this, arguments);
    };

    // extend prototypes and create a super function
    Popover.prototype = $.extend({}, _super.Constructor.prototype, {
        constructor: Popover,
        _super: function() {
            var args = $.makeArray(arguments);
            _super.Constructor.prototype[args.shift()].apply(this, args);
        },
        show: function() {
            var $tip, inside, pos, actualWidth, actualHeight, placement, tp, container, popoverClass;

            if (this.hasContent && this.enabled) {
                $tip = this.tip();
                this.setContent();

                if (this.options.animation) {
                    $tip.addClass('fade');
                }

                placement = typeof this.options.placement == 'function' ?
                    this.options.placement.call(this, $tip[0], this.$element[0]) :
                    this.options.placement;

                inside = /in/.test(placement);

                container = this.options.container ? document.getElementById(this.options.container) : document.body;
                popoverClass = this.options.popoverClass ? this.options.popoverClass : '';

                $tip
                    .remove()
                    .css({ top: 0, left: 0, display: 'block' })
                    .addClass(popoverClass)
                    .appendTo(inside ? this.$element : container);

                pos = this.getPosition(inside);
                actualWidth = $tip[0].offsetWidth;
                actualHeight = $tip[0].offsetHeight;

                switch (inside ? placement.split(' ')[1] : placement) {
                    case 'bottom':
                        tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - actualWidth / 2};
                        break;
                    case 'top':
                        tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2};
                        break;
                    case 'left':
                        tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth};
                        break;
                    case 'right':
                        tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width};
                        break;

                    // extend placements (top)
                    case 'topLeft':
                        tp = {top: pos.top - actualHeight,  left: pos.left + pos.width / 2 - (actualWidth * .25)};
                        break;
                    case 'topRight':
                        tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - (actualWidth * .75)};
                        break;

                    // extend placements (right)
                    case 'rightTop':
                        tp = {top: pos.top + pos.height / 2 - (actualHeight *.10), left: pos.left + pos.width};
                        break;
                    case 'rightBottom':
                        tp = {top: pos.top + pos.height / 2 - (actualHeight * .75), left: pos.left + pos.width};
                        break;

                    // extend placements (bottom)
                    case 'bottomLeft':
                        tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - (actualWidth * .25)};
                        break;
                    case 'bottomRight':
                        tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - (actualWidth * .75)};
                        break;

                    // extend placements (left)
                    case 'leftTop':
                        tp = {top: pos.top + pos.height / 2 - (actualHeight *.25), left: pos.left - actualWidth};
                        break;
                    case 'leftBottom':
                        tp = {top: pos.top + pos.height / 2 - (actualHeight * .75), left: pos.left - actualWidth};
                        break;

                }

                $tip
                    .css(tp)
                    .addClass(placement)
                    .addClass('in');
            }
            /*if there's no title, hide the title bar*/
            if(!this.options.title){ //
                $tip.find('.popover-title').hide();
            }
        }
    });

    $.fn.popover = $.extend(function (option) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('popover')
                , options = typeof option == 'object' && option;
            if (!data) $this.data('popover', (data = new Popover(this, options)));
            if (typeof option == 'string') data[option]();
        });
    }, _super);

    // this plugin uses styles stored in a separate file.
    /*  $(document).find('script').each(function(index, script){
     if (script.src.indexOf('popover-extra-placements.js') != -1) {
     $('head').append('<link rel="stylesheet" href="'+script.src.split('popover-extra-placements.js')[0]+'/popover-extra-placements.css" type="text/css" />');
     } else if (script.src.indexOf('popover-extra-placements.min.js') != -1) {
     $('head').append('<link rel="stylesheet" href="'+script.src.split('popover-extra-placements.min.js')[0]+'/popover-extra-placements.min.css" type="text/css" />');
     }
     });*/
})(jQuery);

/*
 * Closes popover whenever user clicks outside popover
 *
 * */
$(':not(anything)').on('click', function (e) {
 $('.popover-link').each(function () {
 //the 'is' for buttons that trigger popups
 //the 'has' for icons and other elements within a button that triggers a popup
 if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover, .ks-popover').has(e.target).length === 0) {
 $(this).popover('hide');
 return;
 }
 });
 });
