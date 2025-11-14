(function () {
    'use strict';

    var utilityService = angular.module('services.util.util', []);


    utilityService.factory('UtilService', [
        '$rootScope',
        '$http',
        function ($rootScope, $http) {
            var UtilService = {};

            //right now this is a port of the rdm_password custom tag with default settings from UserManager/newuser.cfm
            UtilService.generatePassword = function (pwLength, excludedValues) {
                var authorizedASCII = [],
                    _password = '';

                //setup defaults
                pwLength = pwLength || 8;
                excludedValues = excludedValues || ['i', 'l', 'o', 'z', '0', '1'];

                var charCode;
                //numerals
                for (charCode = 48; charCode <= 57; charCode++) {
                    authorizedASCII.push(charCode);
                }

                //lowercase a-z
                for (charCode = 97; charCode <= 122; charCode++) {
                    authorizedASCII.push(charCode);
                }

                //remove excluded characters
                for (var excludeIndex = 0; excludeIndex < excludedValues.length; excludeIndex++) {
                    for (var codeIndex = 0; codeIndex < authorizedASCII.length; codeIndex++) {
                        var thisChar = String.fromCharCode(authorizedASCII[codeIndex]);

                        if (thisChar === excludedValues[excludeIndex]) {
                            authorizedASCII.splice(codeIndex, 1);
                            continue;
                        }
                    }
                }

                //actually generates the password
                for (var i = 0; i < pwLength; i++) {
                    var position = Math.floor(Math.random() * authorizedASCII.length);

                    _password += String.fromCharCode(authorizedASCII[position]);
                }

                return _password;
            };

            /*
                This function is useful when performing operations with floating point numbers. It takes
                a number and returns the number with the specified amount of decimal places WITHOUT rounding
                the decimal nearest to our requested precision.
                @fpNumber: a floating point number, ie. 2.389
                @decimalPlaces (optional): the desired number of decimal places, defaults to 2 (think money)
            */
            UtilService.truncateFloat = function (fpNumber, decimalPlaces) {
                if (fpNumber == 0) {
                    return fpNumber;
                }

                var mantissaLength = decimalPlaces || 2;
                var significantDigitsMultiplier = Number('1' + new Array(mantissaLength + 1).join('0'));

                //Look at ONLY the digits we are considering significant by moving the decimal place to be inclusive of our significant numbers.
                //Then lop off the insignificant (remaining) decimals and move the decimal place back to it's original position.
                return Math.floor(parseFloat((fpNumber * significantDigitsMultiplier).toFixed(2))) / significantDigitsMultiplier;
            };

            return UtilService;
        }
    ]);
})();
