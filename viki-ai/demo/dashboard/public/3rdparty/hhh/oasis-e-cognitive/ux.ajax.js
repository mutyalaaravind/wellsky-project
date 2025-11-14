/**
 * Ajax functionality
 *
 */

(function(ux){

	$.extend( ux, {
		/** @lends ux */

		/**
		 * <p>Initializes Ajax on the current page.</p>
		 *
		 * @author Rodrigo Fuentes (rodrigo.fuentes@kinnser.com)
		 */

		'ajax': {

			'onError' : function(xhr, textStatus, errorThrown){
				// Do not display anything on ajax errors
				// Leave this as centralized place 
				// for ajax errors to be handled in a centralized way
	        }

		}
		 
	});

})(ux);
