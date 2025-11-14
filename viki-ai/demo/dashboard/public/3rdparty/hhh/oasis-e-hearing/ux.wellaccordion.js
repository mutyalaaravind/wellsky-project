(function(ux){
	$.extend(ux, {
		wellaccordion: function($elements){
			//verify an empty collection wasn't passed
			if( !$elements.length ){
				return $elements;
			}
			
			/*
				note: placement of ux-wellaccordion is important
				the "ux-wellaccordion" is replaced by an accordion (for kinnser-wells) specific class
			*/
			var resetClassesForDIV = function($DIV) {
				var sClassString = $DIV.attr('class').replace('ux-wellaccordion', 'kinnser-well-collapse');
				$DIV.attr('class', sClassString);
			}
			
			/*
				get the target ID of the element we want to expand/collapse via a specified class name
				in the form of accordionTarget[ {ELEMENT_ID} ]
			*/
			var getAccordionTarget = function(sElementClasses) {
				var sTarget = /accordionTarget\[[a-zA-Z]*\]/.exec(sElementClasses);
				sTarget = '#' + sTarget[0].slice(16, sTarget[0].length - 1);
				
				return sTarget;
			}
			
			
			return $elements.each(function() {
				var $currentElement = $(this);
				
				if( !$currentElement.data('_ux-wellaccordion-applied') ){
					//modify classes on DIV element as explained in comments above
					resetClassesForDIV($currentElement);
					
					//add trigger control (markup that makes the target DOM element collapse or expand
					$currentElement.prepend('<hgroup class="accordion-toggle" data-toggle="collapse" data-target="' +
						getAccordionTarget($currentElement.attr('class')) +
						'"><h4>Expand/Collapse</h4></hgroup>');
					
					//mark the current element as applied; requested changes made
					$currentElement.data('_ux-wellaccordion-applied', true);
					
					//attach an event to the HGROUP for iPad users so the collapse control is clickable
					if(navigator.userAgent.match(/iPad/i) != null){
						$('hgroup.accordion-toggle').on('click', function() {
							$('.collapse').collapse('toggle');
						});
					}
				}
			});
		}
	});
	
	ux.wellaccordion($("div.ux-wellaccordion"));
})(ux);