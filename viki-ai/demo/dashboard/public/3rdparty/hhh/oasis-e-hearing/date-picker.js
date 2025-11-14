(function ($moment) {
	'use strict';

	var datePicker = angular.module('directives.kinnser.ux.date-picker', []);
	datePicker.directive('kDatePicker', ['$parse', '$filter', '$timeout', function ($parse, $filter, $timeout) {
		return {
			link: function (scope, element, attrs, controller) {

				var ngModel = $parse(attrs.ngModel);

				//An array of date ranges for specific date picking
				var availableDates = scope.$eval(attrs.dateRanges);

				var handleChange = function(){
					$(".ui-datepicker a").removeAttr("href");
					var thisVal = $(this).val();

                    // only save a valid date
                    if( moment(thisVal, 'MM/DD/YYYY') === null || !(moment(thisVal, 'MM/DD/YYYY').isValid())){
                        thisVal = '';
                        $(this).val('');
                    }

					scope.$apply(function(scope){
						 //This prevents IE8 from doing a redirect
						ngModel.assign( scope, thisVal);
					});
                };

                //Moved ngModel assign out of the anonymous function so that the date will be converted before the timeout. This avoids the datepicker from breaking by having an invalid date initialized.
                ngModel.assign( scope, $filter('date')(scope.$eval(attrs.ngModel), 'MM/dd/yyyy'));

                /*Timeout was added so that the datepicker can be used in an ng-repeat. DO NOT REMOVE UNLESS IT'S DETRIMENTAL TO THE APP ELSEWHERE*/
				$timeout(function () {
					$(function(){

						ux.datepicker( element, {
							defaultDate: scope[attrs.ngModel]  || null,
							maxDate: attrs.maxDate || null,
							minDate: attrs.minDate || null,
							onClose: handleChange,
							onSelect: handleChange,
							beforeShowDay: attrs.dateRanges ? function (date) {
								var currentDate = new Date(date),
								exist = false,
								it = 0;
								if(availableDates) {
									while( it < availableDates.length && !exist) {
										if(currentDate >= availableDates[it].StartDate && currentDate <= availableDates[it].EndDate) {
											exist = true;
										} else {
											it++;
										}
									}
									return [exist];
								}
								return [false];
							} : null
						});

						element.bind('change', handleChange);
						element.bind('focusout', handleChange);
						element.bind('input', handleChange);
						element.bind("keydown keypress", function(event) {
			                if(event.which === 13) {
			                	var thisVal = $(this).val();
			                	ngModel.assign( scope, thisVal);
			                }
			            });

						attrs.minDate =  attrs.minDate || '';
						attrs.maxDate =  attrs.maxDate || '';

						//change min/max date on update
						if(attrs.minDate) {
							scope.$watch(attrs.minDate, function(){
								$(element).datepicker('option', 'minDate', scope.$eval(attrs.minDate));
								$(element).datepicker('setDate', scope.$eval(attrs.ngModel));
							});
						}
						if(attrs.maxDate) {
							scope.$watch(attrs.maxDate, function(){
								$(element).datepicker('option', 'maxDate', scope.$eval(attrs.maxDate));
								$(element).datepicker('setDate', scope.$eval(attrs.ngModel));
							});
						}
					});
				});
			}
		};
	}]);

})(moment);

