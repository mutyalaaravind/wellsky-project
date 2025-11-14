/**
 * UX Library
 *
 * @description Provides common UX facilities to implement consistency on the entire application
 * @author mbozza, rfuentes
 * @namespace
 */
ux = (function(  ){
	/* Private Variables and Methods */

	/**
	 * General configuration values for the UX library
	 * @private
	 */
	var config = {
		appBaseUrl: '',
		shortDateFormat: 'mm/dd/yyyy',
		skinBaseUrl: '/AM/css/ux/'  	// with trailing slash
	}
	
	
	/* Public Variables and Methods */
	return {
		/**
		 * Config object
		 *
		 * @namespace
		 */
		config: {

			/**
			 * Retrieves the application short date format
			 * @function
			 * @return	{string}
			 */
			getShortDateFormat: function(){ return config.shortDateFormat;},
			
			/**
			 * Retrieves the application short date format for JQueryUI datepicker functions
			 * @function
			 * @return	{string}
			 */
			getShortDateFormatJUI: function(){ return config.shortDateFormat.replace('yyyy','yy');},

			/**
			 * Retrieves the application short date format mask
			 * @function
			 * @return	{string}
			 */
			getShortDateFormatMask: function(){ return config.shortDateFormat.replace(/[mdy]/g, '9');},

			/**
			 * Retrieves the skin base url (with trailing slash)
			 * @function
			 * @return	{string}
			 */
			getSkinBaseUrl: function(){ return config.skinBaseUrl;},

			/**
			 * Retrieves the app base url (with trailing slash)
			 * @function
			 * @return	{string}
			 */
			getAppBaseUrl: function(){ return config.appBaseUrl;},

			/**
			 * Set the app base url (with trailing slash)
			 * @function
			 * @return	{string}
			 */
			setAppBaseUrl: function( appBaseUrl ){ 
				config.appBaseUrl = appBaseUrl;
				delete this.setAppBaseUrl; // this variable can be set only once
			}



		},
		
		/**
		 * Validate object
		 * 
		 * All validation functions should be placed here
		 * @namespace
		 */
		validate: {

			/**
			 * Check if the given date is valid
			 * @param {string} dateStr Date to be validated in 'mm/dd/yyyy' format
			 * @return {boolean}
			 */
			isDate: function (dateStr){
				var datePat=/^(\d{1,2})(\/|-)(\d{1,2})(\/|-)(\d{4})$/;
				var matchArray=dateStr.match(datePat);
				if(matchArray==null){return false;}
				month=matchArray[1];
				day=matchArray[3];
				year=matchArray[5];
				if(month<1||month>12){return false;}
				if(day<1||day>31){return false;}
				if((month==4||month==6||month==9||month==11)&&day==31){return false;}
				if(month==2){var isleap=(year%4==0&&(year%100!=0||year%400==0));
				if(day>29||(day==29&&!isleap)){return false;}}
				if(year<1800 || year>2050){return false;}
				return true;
				},
				
			/**
			 * Checks if the given time is valid
			 * @param {string} timeStr Time to be validated
			 * @return {boolean}
			 */	
			isTime: function(timeStr){
				var timePat=/^(\d{1,2}):(\d{2})(:(\d{2}))?(\s?(AM|am|PM|pm))?$/;
				var matchArray=timeStr.match(timePat);
				if(matchArray==null){alert("Time is not in a valid format.");return false;}
				hour=matchArray[1];
				minute=matchArray[2];
				second=matchArray[4];
				ampm=matchArray[6];
				if(second==""){second=null;}
				if(ampm==""){ampm=null}
				if(hour<0||hour>23){alert("Enter time-in in military format. ex 5:00 pm = 17:00");return false;}
				if(minute<0||minute>59){alert("Minute must be between 0 and 59.");return false;}
				if(second!=null&&(second<0||second>59)){alert("Second must be between 0 and 59.");return false;}
				return true;
				},
				
			/**
			 * Checks if the given number is a valid decimal
			 * @param {string} number
			 * @return {boolean}
			 */
			isDecimal: function (number){
				return /^[-+]?[0-9]+(\.[0-9]+)?$/.test(number);
				}
		}
	};	
})(  );

// Dialog
(function(ux){
	$.extend(ux, (function(  ){

		/* Private Variables and Methods */

		/* Public Variables and Methods */
		return {
			/** @lends ux */

			/**
			 * Common functionality to display alerts, confirms
			 * and popup dialogs with a custom and unique style
			 * across the whole app.
			 *
			 * @namespace
			 */
			dialog: {

				/**
				 * Display an alert modal popup
				 *
				 * @param {string} [message=""]
				 * @param {string} [title="Alert"]
				 * @param {json} [options={}] Options
				 * @param {function} [options.onOk] function to be called when Ok is clicked
				 */
				alert: function () {
					var message = arguments[0] || "",
						title = arguments[1] || "Alert",
						options = arguments[2] || {
							onOk: function () {}
						 };

					$('<div title="' + title + '">' +
						'<p>' + message + '</p>' +
						'</div')
						.dialog({
							modal: true,
							buttons: {
								Ok: function () {
									if ( typeof(options['onOk']) == 'function') options.onOk();
									$(this).dialog("close");
								}
							}
						});
				},

				/**
				 * Display a confirmation modal popup
				 *
				 * @param {string} [message=""]
				 * @param {string} [title="Confirm"]
				 * @param {json} [options={}] Options
				 * @param {function} [options.onOk] function to be called when Ok is clicked
				 * @param {function} [options.onCancel] function to be called when Cancel is clicked
				 * @param {string} [options.okText] alternate text for the Ok button
				 * @param {string} [options.cancelText] alternate text for the Cancel button
				 */
				confirm: function() {
					var message = arguments[0] || "",
						title = arguments[1] || "Confirm",
						options = arguments[2] || {
								onOk: function(){},
								onCancel: function(){}
							};


					$('<div title="' + title + '">' +
						'<p>' + message + '</p>'+
						'</div>')
						.dialog({
							modal: true,
							buttons: [
								{text: options['okText'] || 'Ok',
									click: function() {
										if ( typeof(options['onOk']) == 'function') options.onOk();
										$(this).dialog( "close" );
									}},
								{text: options['cancelText'] || 'Cancel',
									click: function() {
										if( typeof(options['onCancel']) == 'function') options.onCancel();
										$(this).dialog( "close" );
									}}]
						});
					},
				popup: function (element, options) {},
				coldFusion: function (message) {}
			}
		};
	})());
})(ux);

// Set Browser title according to headings
$(document).ready(function() {
	//this breaks when you get to a page that doesn't use the left class, CM Hotbox
	var title = [];
	if ( $('h1:first').length > 0 )
	{
		// Get only the contents of h1 excluding its descendants
		title.push($.trim($('h1:first').contents().filter(function(){ return(this.nodeType == 3); }).text()));
	}
	
	// Sanitize the string
	$(title).each(function(i,o){
		title[i] = o.replace(/[\n\t :]+/ig, ' ');
	});

	// Trailing string for title
	title.push('Kinnser Software');
	
	document.title = title.join(' | ');
	 
});