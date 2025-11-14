(function($){
    $.fn.validationEngineLanguage = function(){
    };
    $.validationEngineLanguage = {
        newLang: function(){
            $.validationEngineLanguage.allRules = {
                "required": { // Add your regex rules here, you can take telephone as an example
                    "regex": "none",
                    "alertText": "* This field is required",
                    "alertTextCheckboxMultiple": "* Please select an option",
                    "alertTextCheckboxe": "* This checkbox is required",
                    "alertTextDateRange": "* Both date range fields are required"
                },
                "requiredInFunction": {
                    "func": function(field, rules, i, options){
                        return (field.val() == "test") ? true : false;
                    },
                    "alertText": "* Field must equal test"
                },
				"dateRange": {
                    "regex": "none",
                    "alertText": "* Date range cannot be greater than ",
                    "alertText2": " days"
                },
                "minSize": {
                    "regex": "none",
                    "alertText": "* This field requires a minimum of ",
                    "alertText2": " characters"
                },
                "maxSize": {
                    "regex": "none",
                    "alertText": "* Maximum ",
                    "alertText2": " characters allowed"
                },
				"groupRequired": {
                    "regex": "none",
                    "alertText": "* You must fill one of the following fields"
                },
                "min": {
                    "regex": "none",
                    "alertText": "* Minimum value is "
                },
                "max": {
                    "regex": "none",
                    "alertText": "* Maximum value is "
                },
                "dateIsBefore": {
                    "regex": "none",
                    "alertText": "* Date cannot be greater than today ",
					"alertText2": "* Date must be before "

                },
                "dateIsAfter": {
                    "regex": "none",
                    "alertText": "* Date cannot be less than today ",
					"alertText2": "* Date must be on or after "
                },
                "maxCheckbox": {
                    "regex": "none",
                    "alertText": "* Maximum ",
                    "alertText2": " options allowed"
                },
                "minCheckbox": {
                    "regex": "none",
                    "alertText": "* Please select ",
                    "alertText2": " options"
                },
                "minDTCheckboxRequired": {
                    "regex": "none",
                    "alertText": "* Please select ",
                    "alertText2": " options"
                },
                "equals": {
                    "regex": "none",
                    "alertText": "* Fields do not match"
                },
                "creditCard": {
                    "regex": "none",
                    "alertText": "* Invalid credit card number"
                },
                "phone": {
                    // credit: jquery.h5validate.js / orefalo
                    "regex": /^([\+][0-9]{1,3}[\ \.\-])?([\(]{1}[0-9]{2,6}[\)])?([0-9\ \.\-\/]{3,20})((x|ext|extension)[\ ]?[0-9]{1,4})?$/,
                    "alertText": "* Invalid phone number"
                },
                "email": {
                    // HTML5 compatible email regex ( http://www.whatwg.org/specs/web-apps/current-work/multipage/states-of-the-type-attribute.html#    e-mail-state-%28type=email%29 )
                    "regex": /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/,
                    "alertText": "* Invalid email address"
                },
                "integer": {
                    "regex": /^[\-\+]?\d+$/,
                    "alertText": "* Not a valid number"
                },
                "number": {
                    // Number, including positive, negative, and floating decimal. credit: orefalo
                    "regex": /^[\-\+]?((([0-9]{1,3})([,][0-9]{3})*)|([0-9]+))?([\.]([0-9]+))?$/,
                    "alertText": "* Invalid floating decimal number"
                },
                "date": {
                    "regex": /^\d{4}[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12][0-9]|3[01])$/,
                    "alertText": "* Invalid date, must be in YYYY-MM-DD format"
                },
                "ipv4": {
                    "regex": /^((([01]?[0-9]{1,2})|(2[0-4][0-9])|(25[0-5]))[.]){3}(([0-1]?[0-9]{1,2})|(2[0-4][0-9])|(25[0-5]))$/,
                    "alertText": "* Invalid IP address"
                },
                "url": {
                    "regex": /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i,
                    "alertText": "* Invalid URL"
                },
                "onlyNumberSp": {
                    "regex": /^[0-9\ ]+$/,
                    "alertText": "* Numbers only"
                },
                "onlyLetterSp": {
                    "regex": /^[a-zA-Z\ \']+$/,
                    "alertText": "* Letters only"
                },
                "onlyLetterNumber": {
                    "regex": /^[0-9a-zA-Z]+$/,
                    "alertText": "* No special characters allowed"
                },
				
				"prv03": {
					"regex": /^[\da-zA-Z]{9}[a-zA-Z]$/,
					"alertText": "* Must be 10 digits with an alpha character in the 10th position"
				},
				
				// can be blank
				"alphaNumeric": {
					"regex": /^[0-9a-zA-Z]*$/,
					"alertText": "* No special characters allowed"
				},

				//****Kinnser Global Custom Rules/Alerts
				"isDate": {
					"regex": "none",
                    "alertText": "* Please enter a valid date in mm/dd/yyyy format"
                },

				"isTime": {
					"regex": "none",
                    "alertText": "* Please enter a valid time in hh:mm format, military time"
                },

               "timeIsAfter": {
                    "regex": "none",
					"alertText": "* Time Out must be after Time In"
                },

                "exactLength": {
                    "regex": "none",
                    "alertText": "* This field requires exactly ",
                    "alertText2": " characters"
                },

		        // US zip codes | Accepts 12345 and 12345-1234 format zipcodes
				"zipCode": {
                	"regex": /^\d{5}(-\d{4})?$/,
                	"alertText": "* Invalid zipcode"
				},

                // digits only (no spaces, commas, decimals, etc.)
                "onlyDigits": {
                    "regex": /^[0-9]+$/,
                    "alertText": "* Numbers only"
                },
                //
                "compareDates":{
                    "alertTextGreater":"To date must be greater than from date",
                    "alertText365":"Date range selected can not be more than 365 days",
                    "alertTextMinDate":"Date can not be less than 01/01/2010"
                },
                "notEqual": {
                    "regex": "none",
                    "alertText": "* Each ",
                    "alertText2": " must be unique"
                },

                "hcpcsCode": {
                    "regex": /^[A-Z][0-9]{4,5}$/,
                    "alertText": "* Invalid HCPCS code. "
                },
                "zipCodeValid": {
                    "alertText": "* This field requires a valid Zip Code"
                },

                "HISPatientNamesCharacters" : {
                    "regex": /^[\w\-\@\'\/\+\,\.\s]*$/,
                    "alertText": '* Invalid character(s) in field. Only alphanumeric characters, special characters "@", " \' ", "-", "/", "+", ",", ".", and "_" are allowed.'
                },

                "HISPatientNamesSpaces" : {
                    "regex": /^[^\s]+(([\s]*[^\s]+)*|[^\s]*)$/,
                    "alertText": '* Erroneous space(s) in field. Only embedded spaces are allowed (ex: "O Connor").'
                },

                "HISNumbers" : {
                    "regex": /^$|^[^\D]+$/,
                    "alertText": "* Not a valid number."
                },

                "HISSSNNoZeroString" : {
                    "regex": /^(?!000)/,
                    "alertText": "* This field cannot have the value '000'"
                },

                "Medicare" : {
                    "regex": /(^$)|(^[\d]{9}[\dA-Za-z]*$)|(^[a-zA-Z]{1,3}([\d]{6}|[\d]{9})[a-zA-Z\d]*$)/,
                    "alertText": "* This field is invalid. Enter a valid Medicare number."
                },

                "MedicareMBI" : {
                    "regex": /(^[0-9A-Z]{1,11}$)/,
                    "alertText": "* Numbers and uppercase letters only, no special characters allowed."
                },

                "Medicaid" : {
                    "regex": /(^[a-zA-Z\d]*$)|(^\+$)/,
                    "alertText": "* This field is invalid. Enter a valid Medicaid number, \"+\", or \"N\" in the field."
                },

                "balance": {
                    "regex": /(^[0-9]+$)|(^[0-9]+\.[0-9]{1,2}$)/,
                    "alertText": "* Invalid balance "
                },

                /*Optional Validation Rules: These validate as true on empty inputs as well as correct rule procedure*/
                "optionalEmail": {
                    // HTML5 compatible email regex ( http://www.whatwg.org/specs/web-apps/current-work/multipage/states-of-the-type-attribute.html#    e-mail-state-%28type=email%29 )
                    "regex": /(^$)|^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/,
                    "alertText": "* Invalid email address"
                },

                "optionalOnlyLetterSp": {
                    "regex": /^$|^[a-zA-Z\ \']+$/,
                    "alertText": "* Letters only"
                },

                "optionalZipCode": {
                    "regex": /^$|^[0-9]{5}$/,
                    "alertText": "* Not a valid zip-code"
                },

                "optionalZipCodePlusFour": {
                    "regex": /^$|^[0-9]{4}$/,
                    "alertText": "* Not a valid zip-code"
                },

                "triageRiskCode": {
                    "regex": /^[a-zA-Z0-9]{0,2}$/,
                    "alertText": "* Triage code must be numbers and letters only"
                },

                "timecardMileage": {
                    "regex": /^[-+]?[0-9]+(\.[0-9]+){0,5}?$/,
                    "alertText": "* Numeric Value Only"
                },

                "suffixValid": {
                    "regex": /^^[0-9a-zA-Z@\@\'\/\+\,\.\_\- ]+$/,
                    "alertText": "* Invalid Suffix"
                }
            };
        }
    };

    $.validationEngineLanguage.newLang();

})(jQuery);
