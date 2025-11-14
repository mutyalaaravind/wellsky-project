/**
 * UX Library
 *
 * @description Provides common UX facilities to implement consistency on the entire application
 * @author sammer salman
 * @namespace
 */
(function(ux){

	//Private Scope
	var private = {
		/**
		 * Takes a form object and adds v-required class to labels asociated with required inputs and adds v-required-field class those inputs
		 * @param {object} The form object where we want to check for inputs with validation class and add v-required class
		 * @return {void}
		 */	  
		 addRequiredToLabel: function(form){

		 	var $inputs = $('input[class*="required"],input[class*="condRequired"],' +
		 		'textarea[class*="required"], textarea[class*="condRequired"],' +
		 		'select[class*="required"], select[class*="condRequired"]', form)
		 	// Filter only the elements that contains required or condrequired 
		 	// inside the validate definition on the class
				.filter(function(index){ 
					var required = false;
					var className = $(this).attr('class');

					var requiredRE = (/validate\[\S*(?:required|condRequired)[\S]*\]/g);

					return className && className.match(requiredRE);
				});

			$inputs.each(function ()
			{

				var inputID = $(this).attr("id");
				var requiredRE = (/validate\[\S*(required|condRequired)[\S]*\]/g);
				var matches  = requiredRE.exec($(this).attr("class"));
				var labelClass = 'v-' + ( matches.length > 1 ? matches[1].toLowerCase() : 'required'); 
				var fieldClass = labelClass + '-field';

				//Add outline to each Required Input/select
				$(this).addClass(fieldClass);

				if(!$("label[for="+inputID+"]").hasClass(labelClass)){
					$("label[for="+inputID+"]").addClass(labelClass);
				}else if($(this).parents('label')){
					$(this).parents('label').addClass(labelClass);
				}
			});
		 }
	}


	$.extend(ux, {
		/**
		 * ValidationEngine object
		 * 
		 * All validationEngine functions should be placed here
		 * @namespace
		 */
		validationEngine: {
			//Placement of the prompt
			promptPosition:'bottomRight:10,-5',
			
			/**
			 * Instantiates the ValidationEngine
			 * @param {obj|string} The form object or the ID of the form to attach the engine to
			 * @param {obj} hash map of the custom error messages and what field/function they point to
			 * @param {function} SubmitHandler function to be attached to the form when validation is completed
			 * @return {void}
			 */	
			runValidationEngine: function(formId,customErrorMessages, onSubmit, options){
				var $form = $(formId).length > 0 ? $(formId) : $("#" + formId);
				
				if( typeof(onSubmit) != 'function' ){
					onSubmit = submitHandler;
				}

				if( !options ) {
					options = {};
				}

				if( options.promptPosition ) this.promptPosition = options.promptPosition;
				
				// Add user's custom options to the default validation options (overriding where appropriate)
				var opts = $.extend(
					{},
					{
					 	promptPosition : this.promptPosition,
	                	binded:false,
		                scroll:true,
	                    onValidationComplete:onSubmit,
	    	            'custom_error_messages': customErrorMessages
					},
					options);
                $form.validationEngine('attach', opts);

				//Add required Class to labels
				private.addRequiredToLabel($form);

				//Add ux-validationengine true to check if the current form has the validationengine attached 
				$form.data('ux-validationengine', true);
				
				// Fix submit buttons values not being posted
				$("input[type=submit]", $form).click(function() {
					var submitName = $(this).attr('name');
					if( ! submitName ) return;
					
					var $submitVar = $('input[type=hidden][name=' + submitName + ']', $form);
					if( $submitVar.length == 0 ) {
						$submitVar = $('<input type="hidden" name="' + submitName + '"/>');
						$(this).parents("form").append($submitVar);
					}
					$submitVar.val($(this).val());
				});
				
				// Change some options after an error is found (overridden by user's custom options)
				var errorFoundOptions = $.extend(opts, { binded: true, scroll: false }, options);
                var self = this;
                $form.unbind("jqv.form.result");
                $form.bind("jqv.form.result", function(event, errorFound) {
                    $form.validationEngine('resetOptions', errorFoundOptions);
                });
                
            },

			/**
			 * Takes a form object and checks if ux-validationengine is present
			 * @param {object} The form object where we want to know if validation is present
			 * @return {boolean}
			 */	                
            hasValidationEngine: function( form ){
                return $(form).data('ux-validationengine') === true;
            },	

			/**
			 * Takes a formID and converts it to a JSON string
			 * @param {string} The ID of the form to attach the engine to
			 * @return {string} A JSON formatted string representation of the form 
			 */	
			getFormAsJSON: function(formId){
     			var formStruct = getFormAsStruct(document.getElementById(formId));
				var formAsJSON = JSON.stringify(formStruct);
				return formAsJSON;
			},		
			
			/**
			 * Takes a formID and converts it to a JSON string
			 * @param {string} The ID of the form to attach the engine to
			 * @return {string} A JSON formatted string representation of the form 
			 */			
			showPrompt: function(fieldID,message,options){

				var opts = $.extend(
					{},
					{
					 	type : 'error',
	                	focusInvalidField : true,
	                	promptPosition : this.promptPosition
					},
					options);


				$('#' + fieldID).validationEngine('showPrompt', message, opts.type, opts.promptPosition,'true');
				if (!$('#' + fieldID).hasClass('ux-datepicker')){
					if(opts.type =='error' && opts.focusInvalidField )
						$('#' + fieldID).focus();
					if(opts.type =='pass')
						$('#' + fieldID).removeClass("error");
				}
				$('#' + fieldID).addClass('customPrompt');
			},
			
			hidePrompt: function(fieldID,options){

				var opts = $.extend(
					{},
					{
					 	type : 'error'
					},
					options);

					$('#' + fieldID).removeClass(opts.type);
					$('#' + fieldID).removeClass('customPrompt');
					$('#' + fieldID).validationEngine('hide');	
				
				},
			
			/**
			 * Displays a message in a modal window
			 * @param {string} A message to be displayed in the modal
			 * @return {void} 
			 */			
			showModal: function(message){
				$('#gTemplateErrorWindowText').text(message);
				$('#gTemplateErrorWindow').dialog('open');
			},			
			
			/**
			 * Takes a returnStruct and displays validation/error messages as appropriate
			 * @param {string} The ID of the form to attach the engine to
			 * @param {struct} A hash map of return status and messages 
			 * @return {boolean}  
			 */			
			processReturnData: function(formObj,returnStruct){
				switch (returnStruct.returnType) {
					case "validationError":
						if (returnStruct.errorArray.length > 0) {
							for (var i = 0; i < returnStruct.errorArray.length; i++) {
								this.showPrompt(returnStruct.errorArray[i].fieldID, returnStruct.errorArray[i].message);
							}
						}
						return false;
						break;
					case "fail":
						this.showModal(returnStruct.errorArray[0].message);
						return false;
						break;
					default:
						return true;		
				}				
				

			},

			/**
			 * Takes a value and determines if it is numeric
			 * @param {string} any stirng value
			 * @return {boolean}  
			 */				
			isNumeric: function(input){
				return (input - 0) == input && input.toString().length > 0;
			}
		
		}
		
	});	
})( ux );
	