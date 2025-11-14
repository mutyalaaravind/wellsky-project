
(function($, window, document) {
function updateFilterState ( oSettings, oData ){
	var nDTWrapper = oSettings.oInstance.parents('.dataTables_wrapper'),
		nFilter = nDTWrapper.find('#dataTableFilter'),
		nLength = nDTWrapper.find('.dataTables_length select'),
		nGroupBy = $("#" + oSettings.sInstance + '_groupBy_row');


	if( nGroupBy.size() > 0 && oData['groupBy'] && typeof( oData['groupBy']['currentValue'] ) != 'undefined' )
		nGroupBy.val( oData.groupBy.currentValue ).trigger( 'change' );

	if( nFilter )
		nFilter.val( oData.oSearch.sSearch ).trigger('change').trigger('keyup');

	if( nLength )
		nLength.val( oData.iLength );

	if( $.isArray(oData.aaSorting) || $.isNumeric(oData.aaSorting) )
	    oSettings.oInstance.fnSort( oData.aaSorting );

	if( $.isNumeric(oData.iStart) && oData.iStart >= 0){
		oSettings._iDisplayStart = oData.iStart;
	    oSettings.oInstance.fnPageChange( oSettings.oInstance.fnPagingInfo().iPage );
	}

}
 
$.fn.dataTableExt.oApi.fnStateReset = function ( oSettings )
{

	var sName = 'DT_' + oSettings.sInstance,
		sValue = ux.statePersistance.getDefaultItem(sName);


	if( sValue != null ) {
		ux.statePersistance.setItem(sName, sValue);

		oSettings.oApi._fnLoadState( oSettings, oSettings.oInit );
		updateFilterState(oSettings, JSON.parse(sValue));
		oSettings.oInstance.fnStandingRedraw();

	}
}

jQuery.fn.dataTable.defaults.fnStateLoad = function(oSettings) {
		var sName = 'DT_' + oSettings.sInstance ,
			sValue = ux.statePersistance.getItem(sName);
		
		return JSON.parse(sValue);
	};

jQuery.fn.dataTable.defaults.fnStateSave = function(oSettings, oData){
		var sName = 'DT_' + oSettings.sInstance ,
			sValue = JSON.stringify(oData),
			sDefaultValue = ux.statePersistance.getDefaultItem( sName ),
			oDefaultValue = JSON.parse( sDefaultValue );

		if ( sDefaultValue != null &&
			(
			! oDefaultValue['groupBy'] && 
				oData['groupBy'] 
			|| typeof(oDefaultValue['groupBy']['currentValue']) == 'undefined' && 
				typeof(oData['groupBy']['currentValue']) != 'undefined' 
			)
			){
			// If current group is not defined on the defaults then save it
			ux.statePersistance.setItem(sName, JSON.stringify( $.extend( oDefaultValue, { 'groupBy' : oData['groupBy']} ) ) , true);
		} else {
			ux.statePersistance.setItem( sName, sValue );
		}
	};

var DT_StatePersistanceControl = function ( oSettings )
{
	oSettings.oFeatures.bStateSave = true;

	var oStateSave = $.extend( { 'oFilters': {} }, oSettings.oInit['oStateSave'] )
		oTable = oSettings.oInstance;

	oTable.bind( 'stateSaveParams', function( e, oSettings, oData ){
			var that = this,
				oCustomFilters = {};

			$.each( oStateSave.oFilters, function( key, oFilter ){ 
				oCustomFilters[ key ] = oFilter.get();
				});

			$.extend( oData , { 'oCustomFilters' : oCustomFilters });

		});

	// This event is perform custom actions when state is loaded
	// eg: to se the current option selected on a custom dropdown
	oTable.bind('stateLoaded', function( e, oSettings, oData ){
			var that = this,
				oCustomFilters = oData.oCustomFilters || {};

			$.each( oStateSave.oFilters, function( key, oFilter ){ 
				if( typeof oCustomFilters[ key ] != 'undefined' )
					oFilter.set( oCustomFilters[ key ] );
			});

		});




	// If datatable has grouping
	if( $("#" + oSettings.sInstance + '_groupBy_row') ) {
		// Store groupby state if present
		oSettings.oInstance.bind('stateSaveParams', function(e,dtSettings,json){ 
			var $groupBy = $("#" + oSettings.sInstance + '_groupBy_row');
			if( ! $groupBy ) return;
			json['groupBy'] = {
				'currentValue': $groupBy.find(':selected').val()
				};

			});

		// Load groupby state if present
		oSettings.oInstance.bind('stateLoaded', function(e,dtSettings,json){
			var $groupBy = $("#" + oSettings.sInstance + '_groupBy_row');
			if( json['groupBy'] && typeof json['groupBy']['currentValue'] != 'undefined' ){
				$groupBy.val( json['groupBy']['currentValue'] );
			}

			});
		
	}

	oSettings.oApi._fnLoadState( oSettings, oSettings.oInit );
	oSettings.oApi._fnCallbackReg( oSettings, 'aoDrawCallback', oSettings.oApi._fnSaveState, 'state_save' );

}
 
if ( typeof $.fn.dataTable == "function" &&
     typeof $.fn.dataTableExt.fnVersionCheck == "function" &&
     $.fn.dataTableExt.fnVersionCheck('1.8.0') &&
     window.localStorage && 
     window.sessionStorage )
{
    $.fn.dataTableExt.aoFeatures.push( {
        "fnInit": function( oDTSettings ) {
          new DT_StatePersistanceControl( oDTSettings );
        },
        "cFeature": "P",
        "sFeature": "StatePersistance"
    } );
}
else
{
    alert( "Warning: StatePersistance requires DataTables 1.8.0 or greater - www.datatables.net/download and your browser must support localStorage and sessionStorage");
}
 
 
})(jQuery, window, document);
 
