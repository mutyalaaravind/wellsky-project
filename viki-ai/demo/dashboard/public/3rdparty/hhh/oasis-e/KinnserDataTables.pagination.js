jQuery.fn.dataTableExt.oPagination.two_button.fnInit = function ( oSettings, nPaging, fnCallbackDraw ){
	var oLang = oSettings.oLanguage.oPaginate;
	var oClasses = oSettings.oClasses;
	var fnClickHandler = function ( e ) {
		if ( oSettings.oApi._fnPageChange( oSettings, e.data.action ) )
		{
			fnCallbackDraw( oSettings );
		}
	};

	var sAppend = (!oSettings.bJUI) ?
		'<a class="'+oSettings.oClasses.sPagePrevDisabled+'" tabindex="'+oSettings.iTabIndex+'" role="button"></a>'+
		'<a class="'+oSettings.oClasses.sPageNextDisabled+'" tabindex="'+oSettings.iTabIndex+'" role="button"></a>'
		:
		'<a class="'+oSettings.oClasses.sPagePrevDisabled+'" tabindex="'+oSettings.iTabIndex+'" role="button"><span class="'+oSettings.oClasses.sPageJUIPrev+'"></span></a>'+
		'<a class="'+oSettings.oClasses.sPageNextDisabled+'" tabindex="'+oSettings.iTabIndex+'" role="button"><span class="'+oSettings.oClasses.sPageJUINext+'"></span></a>';
	$(nPaging).append( sAppend );

	var els = $('a', nPaging);
	var nPrevious = els[0],
		nNext = els[1];

	oSettings.oApi._fnBindAction( nPrevious, {action: "previous"}, fnClickHandler );
	oSettings.oApi._fnBindAction( nNext,     {action: "next"},     fnClickHandler );

	/* ID the first elements only */
	if ( !oSettings.aanFeatures.p )
	{
		nPaging.id = oSettings.sTableId+'_paginate';
		nPrevious.id = oSettings.sTableId+'_previous';
		nNext.id = oSettings.sTableId+'_next';

		nPrevious.setAttribute('aria-controls', oSettings.sTableId);
		nNext.setAttribute('aria-controls', oSettings.sTableId);
	}
}		
	