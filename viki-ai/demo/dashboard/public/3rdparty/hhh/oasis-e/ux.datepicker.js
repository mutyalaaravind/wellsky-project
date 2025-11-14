/**
 * Datepicker functionality
 *
 * @require jquery-ui, jquery.maskedinput
 */

(function(ux){
	$.extend(ux, {
		/** @lends ux */

		/**
		 * <p>Initializes datepicker on the given $elems applying the options if received.</p>
		 *
		 * <p>When loading this library the datepicker with default options
		 * will be applied to all the input fields with ux-datepicker.
		 * So if you want to apply the datepicker to an input field you
		 * only need to output something like this:</p>
		 * <pre>
		 * &lt;input type="text" id="BirthDate" name="BirthDate" class="ux-datepicker" /&gt;
		 * </pre>
		 *
		 * <b>Remember:</b> If your date fields are generated on execution time by javascript
		 * once the DOM was loaded then you'll have to initialize the datepickers using the
		 * javascript method ux.datepicker as shown in the examples below.
         *
         * @Dependencies
         *      jquery-1.7.1.min.js
         *      jquery-ui-1.8.21.min.js
         *      ux.js
         *      jquery.kinnser.utils.js
         *      jquery.maskedinput-1.3.min.js
		 *
		 * @class
		 *
		 * @param {jQuery} $elems
		 * @param {json} [options={}] See <a href="http://jqueryui.com/demos/datepicker/#options">JQueryUI Datepicker Options</a> for an extensive list of options
		 *
		 * @example
		 * // Apply datepicker with its defaults
		 * ux.datepicker($("#StartDate"));
		 * @example
		 * // Turn day link to move to the currently selected date instead of today
		 * ux.datepicker($("#EndDate"), {gotoCurrent: true});
		 *
		 * @return $elems  jQuery
		 * @author Rodrigo Fuentes (rodrigo.fuentes@kinnser.com)
		 */
		datepicker: function($elems, options){
			
			/* Verify an empty collection wasn't passed */
			if ( !$elems.length ) {
				return $elems;
			}

			/* Verify that the value coming (if there is a value) is a date. If it's not don't use a datepicker. */
			var i;
			for (i = $elems.length - 1; i >= 0; i--) {
				if ($($elems[i]).val() != '') {
					if(!ux.validate.isDate($($elems[i]).val()))
					{
						$elems.splice(i,1);
					}
				}
			}
			
			// Find the highest zIndex to place the datepicker over it
			var getMaxZIndex = function(){
					var index_highest = 500;
					$("*").each(function(){
						// always use a radix when using parseInt
						var index_current = parseInt($(this).css("zIndex"), 10);
						if (index_current > index_highest) {
							index_highest = index_current;
						}
					});
					return index_highest;
				};
			

			return $elems.each(function(){
				var $elem = $(this);
				//adding date validation to each date element
				$elem.addClass('validate[isDate[]] ux-datepicker')
				//adding ux-datepicker class for datepicker initialize via JS
					 .toggleClass('ux-datepicker', true);
				
				
				var opts = $.extend(
					{},
					{
						changeMonth: true,
						changeYear: true,
						yearRange: "-120:+10",
						dateFormat: ux.config.getShortDateFormatJUI(),
						showOn: "button",
						buttonImage: ux.config.getSkinBaseUrl() + "img/calendar-13x14trans.png",
						buttonImageOnly: true,
						buttonText: "Open Calendar View",
						inputmask: '  /  /    ',
						beforeShow: function(input, datepicker) {
							//Check if datepicker is inside a Coldfusion Popup
							var coldfusionContainer = $(this).parents('.x-window').find('.x-window-header').attr('id');
								if(coldfusionContainer){
									coldfusionContainer = coldfusionContainer.replace(/_title/g,'');
									ColdFusion.Window.onHide(coldfusionContainer,function(){
										$(input).datepicker("hide");
									});
								}
							// Do not show datepicker if date field is disabled
							if($elem.is(':disabled')){
								return false;
							}
							setTimeout(function() {
								$(datepicker.dpDiv).css('zIndex', getMaxZIndex() + 10);
							}, 200);
						},
						onSelect: function() {
							// Trigger blur on the input field to update placeholder status
							$elem.blur();
							// Move to next field in the form when date is selected
							if(typeof $(this).data("skipnextelementfocus") === 'undefined'){
								$elem.focusNextInputField();
							}
							//put the value into the linked field
							$elem.valueOfLinkedField();
						},
						maxDate: typeof options !== 'undefined' && 'maxDate' in options ? options.maxDate : null,
						minDate: typeof options !== 'undefined' && 'minDate' in options ? options.minDate : null
					},
					options);


				if( ! $elem.data('_ux-datepicker') ) {
					// add placeholder to the field with the date format
					$elem.attr('placeholder', ux.config.getShortDateFormat())
					//Placeholder fix for IE
						.placeholder({inputmask: '  /  /    '});
				}

				// implement the jQueryUI datepicker on the date field
				// only if it was not applied before or
				// or if we are receiving any options as parameter
				if( ! $elem.data('_ux-datepicker') || typeof(options) == typeof({}) ) {
					$elem.datepicker(opts);
				}

				if( ! $elem.data('_ux-datepicker') ) {

					$elem
						// apply mask using maskedinput plugin
						.mask(ux.config.getShortDateFormatMask(),{
							placeholder:" ",
							// Move to next field in the form when date is completed
							completed: function(){
								$(this).focusNextInputField();
								// add the value if the field is linked with other datepicker
								$(this).valueOfLinkedField();
								
							}
						})
						// apply our custom class to the trigger icon
						.next().toggleClass('datepicker-trigger', true);

					$elem
						// mark element as datepicker applied
						.data('_ux-datepicker', true)
						.parent()
							.toggleClass('control-group', true)
							.toggleClass('ux-datepicker-container', true);
				}
			});
		}
		

	});

	// Initializes datepickers automatically 
	ux.datepicker($("input.ux-datepicker"));
	// Also once the dom is fully loaded
	$(function(){ ux.datepicker($("input.ux-datepicker")); });
})(ux);
