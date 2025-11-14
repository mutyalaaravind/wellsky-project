/**
 * PatientDetail functionality
 *
 */

(function(ux){

    // To display errors 
    var pageError = function(errObject) {
            ux.dialog.alert( errObject.FRIENDLY + '<br>' + errObject.MESSAGE );
        };

	// Patient Detail class to create the elememt
	// and return the proper object
	var PatientDetail = function(){

		var $elem, patientKey, episodeKey;

		if( arguments.length == 1 ) {
			$elem = arguments[0];
			var tmp = $elem.attr('id').split('-');
			patientKey = tmp[1];
			episodeKey = tmp[2];
		} else if( arguments.length == 2 ) {
			patientKey = arguments[0];
			episodeKey = arguments[1];
			$elem = $('a#patientDetail-' + patientKey + '-' + episodeKey);
		} else {
			throw "Invalid number of arguments for PatientDetail";
		}


		var $modal = $(),
			patientData = {},


	        // Load the patient details information from server
			load = function(forceLoad){
				
				if( $modal.length > 0 && !forceLoad)
					return;

	            $.ajax({
	                type: 'GET',
	                url: ux.config.getAppBaseUrl() + 'Patient/PatientProxy.cfc',
	                dataType: 'json',
	                data: {
	                    method: 'getPatientDetails',
	                    patientKey: patientKey ,
	                    episodeKey: episodeKey
	                },
	                success: function(data){ //no ajax errors fall into here
	                    if (data.result === 'success') { //no errors returned from the proxy, manager, or gateway objects
	                    	patientData = data.patientData;
	                    	setPatientDetails();
	                    }
	                    else {
	                        ux.dialog.alert(data.errorStruct);
	                    }
	                },
	                error: function(xhr, textStatus, errorThrown){
	                    var ajaxErrorObject = {
	                        FRIENDLY: 'An error occurred.',
	                        MESSAGE: 'Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText
	                    }
	                    pageError(ajaxErrorObject);
	                }
	            });

			},

			// Populate popup template with data from patient
			// and creates/updates the modal popup
			setPatientDetails = function () {
				var patientModal = $.render.patientDetailTmpl(patientData);

				if( $modal.length > 0 ){	// If the modal exists let's update its content
					$modal.html( $(patientModal).html() );
				} else {					// If the modal doesn't exist let's add it to the DOM
					$modal = $(patientModal);
					$('body').append($modal);
				}
				// Set close button event handler 
				$('.modal-close', $modal).click(function(){
					$modal.modal('hide');
					});
			},

			// Show patient details popup
			show = function(){

				if( $modal.length > 0 )
					$modal.modal('show');
				else 
					setTimeout( show, 100);
			},

			// Hide the patient details popup
			hide = function(){
				$modal.modal('hide');
			},

			// Initializes the event handlers for anchors to display the patient details
			init = function(){
				$elem.click(function(){
					// Show modal with patient details
					load (patientKey, episodeKey);

					show();
					return false;
					});
			};



		init();

		return {
			/**
			 * Retrieves patientKey
			 **/
			patientKey: function(){ return patientKey;},

			/**
			 * Retrieves episodeKey
			 **/
			episodeKey: function(){ return episodeKey;},

			/**
			 * Shows the patient details popup
			 **/
			show: show,

			/**
			 * Hides the patient details popup
			 **/
			hide: hide,

			/**
			 * Refresh patient details information
			 **/
			refresh: function( forceReload ){ load(forceReload); }
		};
	}


	var extendUX = function(){
		$.extend( ux, {
			/** @lends ux */

			/**
			 * <p>Initializes Patient Detail on the given $elems.</p>
			 *
			 * <p>When loading this library the patientDetail
			 * will be applied to all the a fields with ux-patientdetail.
			 * So if you want to apply the patientDetail to an a field you
			 * only need to output something like this:</p>
			 * <pre>
			 * &lt;a id="patientDetail-[patientkey]-[episodeKey]" class="ux-patientdetail"&gt; &lt;a/&gt;
			 * </pre>
			 *
			 * <b>Remember:</b> The patientDetail will be looking for the patienttaskkey as the div id.
			 *
			 * @author Rodrigo Fuentes (rodrigo.fuentes@kinnser.com)
			 */
			 patientDetail: function($elems){
				/* Verify an empty collection wasn't passed */
				if ( !$elems.length ) {
					return $elems;
				}

				var init = function($elems){
					// wire up all $elems passed in
					$elems.each(function(){
						var $elem = $(this);

						// exit if the it was initizalized on the element
						if( $elem.data('ux-patientdetail') ) return;

						// init the element
						$elem.data('ux-patientdetail', new PatientDetail($elem));
					});
				}

				// 
				if( ! $.render.patientDetailTmpl ){
					// get modal markup
					$.ajax({
					    url : ux.config.getAppBaseUrl() + "assets/js/ux/view/patientDetail.html",
					    success : function(result){
							$.templates({ patientDetailTmpl: result });
					    }
					});	
				}

				init($elems);

				return $elems;
			 } 

		});

		// Initializes patientDetails automatically
		$(document).ready(function(){ ux.patientDetail($("a.ux-patientdetail")); });

	}
	
	extendUX();

})(ux);
