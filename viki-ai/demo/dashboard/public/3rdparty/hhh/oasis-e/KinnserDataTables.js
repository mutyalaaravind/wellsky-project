

/***
 * Includes a js file
 *
 * @param file	String path to the js file
 */
var includeJS = function(file)
{
	var js = document.createElement('script');
	
	js.language = 'javascript';
	js.type = 'text/javascript';
	js.src = file;
	document.getElementsByTagName('head')[0].appendChild(js);
}

/***
 * Includes a css file
 *
 * @param file	String path to css file
 */
var includeCSS = function(file) {
	var css = document.createElement('link');
	css.rel = 'stylesheet'
	css.type = 'text/css';
	css.href = file;
	css.media = 'screen';
	document.getElementsByTagName('head')[0].appendChild(css);
}

/**
 *	Formats a number as US currency.
 *
 *	@param num	The number to be formatted
 */
var formatCurrency = function(number)
{
	var sign = (number < 0) ? '-' : '';
	
	// extracting the absolute value of the integer part of the number and converting to string
	number = Math.abs(number).toFixed(2);
	// round number and convert to string
	var numberString = parseInt(number) + '';
	// check to see if the number requires thousands separators
	var mod = ((mod = numberString.length) > 3) ? mod % 3 : 0;
	var result = (mod ? numberString.substr(0, mod) + ',' : '') + numberString.substr(mod).replace(/(\d{3})(?=\d)/g, "$1" + ',') + '.' + Math.abs(number - numberString).toFixed(2).slice(2); 
	return sign + '$' + result;
}

/***
 * This is the interface for creating the Kinnser dataTables plugin.
 * Once a dataTable is created, you can access it using normal jQuery
 * methods, (ex. $('#table').dataTable()), and have access to any of
 * the available dataTables features.
 *
 * The following are requirements for various features:
 *		Default : Have a div to put the dataTable in.
 *		Excel/Help : Have a div whose id is tableID + 'Header' in the div that you wish these links to show up in.
 *		Select All checkbox : Have a div whose id is tableID + 'Header' in the div that you wish these links to show up in.
 */
function KinnserDataTable()
{
	/* public methods */
	
	/***
	 * Creates a data table object based on a template.
	 *
	 * @param tableID					id of an html table
	 * @param templateID				id of the template to use
	 * @param templateDestinationID		DOM location to insert template data in, usually the body of the table.
	 * @param data						An array of objects in which each object holds a row from a query
	 * @param features					Specifications for additional features not covered by the DataTables plugin (such as checkboxes). Go to initFeatures for details.
	 * @param properties				The properties to give to the DataTables constructor. Refer to getDataTableProperties for details
	 */
	this.initByTemplate = function(containerID, tableID, tableBodyID, templateID, columnList, data, features, properties)
	{
		local.tableID = tableID;
		local.containerID = containerID;
		local.tableBodyID = tableBodyID;
		local.templateID = templateID;
		local.columnList = columnList;
		local.data = data;
		local.features = features;
		local.properties = properties;

		var htmlTableStr = '<table id="' + tableID + '" name="' + tableID + '" class="display"><thead><tr>'; //begin table structure
		
		for(i = 0; i < columnList.length; i++){
			htmlTableStr += '<th><strong>' + columnList[i] + '</strong></th>'; //include column headings
		}
		htmlTableStr += '</tr></thead><tbody id="' + tableBodyID + '"></tbody></table>'; //end header, begin table body
		
		$(htmlTableStr).appendTo('#' + containerID);
		
		// Add some style to the table for the previous look
		// @todo Remove this selective statement when UXTemplate is implemented on the entire app
		if($('.ux-datatables').length == 0) 
			$('#'+tableID).css({
				'width': '100%'
			});
		else
			$('#'+tableID).addClass('table');
		
		$.tmpl(templateID, data).appendTo('#' + tableBodyID);
		initFeatures(tableID, features, properties); // init data table
	}
		
	/***
	 * Generates a data table object based off of third function argument, "data". The data object
	 * is expected to be a "query" as an array of objects with the number of array items matching
	 * the number of items in the columnList array. 
	 * 
	 * @param tableID		id of the html table
	 * @param containerID	id of the div to contain the DataTable
	 * @param columnList	An array of column headings to display
	 * @param data			An array of objects in which each object holds a row from a query
	 * @param features		Specifications for additional features not covered by the DataTables plugin (such as checkboxes). Go to initFeatures for details.
	 * @param properties	The properties to give to the DataTables constructor. Refer to getDataTableProperties for details
	 * @param metadata		OPTIONAL. An array of objects that will be saved into each row for later use
	 */
	this.initByQuery = function(tableID, containerID, columnList, data, features, properties, metadata) 
	{
		local.tableID = tableID;
		local.containerID = containerID;
		local.columnList = columnList;
		local.data = data;
		local.features = features;
		local.properties = properties;
		local.metadata = metadata;
		
		var rowID = 1; //used to id each row (for automation testing among other things)
		var htmlTableStr = '<table id="' + tableID + '" name="' + tableID + '" class="">'; //begin table structure
		
		
		htmlTableStr += '<thead><tr>'; //begin table head
		for(i = 0; i < columnList.length; i++){
			htmlTableStr += '<th id="' + tableID + '_' + columnList[i].replace(' ', '_') + '_header" class="' + tableID + '_' + columnList[i].replace(' ', '_') + '" ><strong>' + columnList[i] + '</strong></th>'; //include column headings
		}
		htmlTableStr += '</tr></thead><tbody>'; //end header, begin table body
		
		//walk through data and output
		$.each(data, function(idx, queryRow) {
			//include the rowMetadata attribute
			if(metadata){
				htmlTableStr += '<tr id="' + rowID +'" rowMetadata="' + JSON.stringify(metadata[idx]).replace(/"/g,"'") + '">'; //begin data row, no stripping here as the metadata should be a key
			}
			else{ //no metadata column specified
				htmlTableStr += '<tr id="' + rowID +'">'; //begin data row
			}
			
			for(i = 0; i < columnList.length; i++){
				//write column data, make columnList items upper case to match Coldfusion's output of uppercase columns names
				htmlTableStr += '<td columnID="' + columnList[i] + '" id="' + columnList[i] + '" class="' + tableID + '_' + columnList[i] + '">' + stripJSONFormatting( queryRow[columnList[i].toUpperCase()] ) + '</td>';
			}
			rowID++;
			htmlTableStr += '</tr>'; //end data row
		});
		htmlTableStr += '</tbody></table>'; //end table structure
		
		$(htmlTableStr).appendTo('#' + containerID);
		
		// Add some style to the table for the previous look
		// @todo Remove this selective statement when UXTemplate is implemented on the entire app
		if($('.ux-datatables').length == 0) 
			$('#'+tableID).css({
				'width': '100%'
			});
		else
			$('#'+tableID).addClass('table');
		
		// init data table
		initFeatures(tableID, features, properties);
	}
		
	/***
	 * Generates a defer rendered data table object based off of third function argument, "data". 
	 * The data object is expected to be a "query" as an array of objects with the number of array
	 * items matching the number of items in the columnList array. 
	 * 
	 * @param tableID		id of the html table
	 * @param containerID	id of the div to contain the DataTable
	 * @param columnList	An array of column headings to display
	 * @param data			An array of objects in which each object holds a row from a query
	 * @param features		Specifications for additional features not covered by the DataTables plugin (such as checkboxes). Go to initFeatures for details.
	 * @param properties	The properties to give to the DataTables constructor. Refer to getDataTableProperties for details
	 * @param metadata		OPTIONAL. An array of objects that will be saved into each row for later use
	 */
	this.initByQueryDeferred = function(tableID, containerID, columnList, data, features, properties, metadata) 
	{
		local.tableID = tableID;
		local.containerID = containerID;
		local.columnList = columnList;
		local.data = data;
		local.features = features;
		local.metadata = metadata;

		properties = properties || {};
		tableData = data;
		
		var rowID = 1; //used to id each row (for automation testing among other things)
		var htmlTableStr = '<table id="' + tableID + '" name="' + tableID + '" class="table"></table>'; //begin table structure
	
		$(htmlTableStr).appendTo('#' + containerID);


		if( ! properties.aoColumns ){
			properties.aoColumns = [];
		}

		// Skip metadata column if present
		for(var i=columnList.length-1; i >=0 ; i--){
			columnList[i].toUpperCase() == 'METADATA' && columnList.splice(i,1);
		}

		$.each(columnList, function (i,item){
			var oCol = {
				'sName'           : item.toUpperCase(),
				'sTitle'          : item,
				'mData'           : item.toUpperCase(),
				'bSearchable'     : item ? true : false
				};

			if( properties.aoColumns[i] && properties.aoColumns[i] != null ){
				$.extend( properties.aoColumns[i], $.extend( oCol, properties.aoColumns[i], oCol));
			} else {
				properties.aoColumns.push(oCol);
			}

		});

		$.extend( properties, {
			// Overriding fnServerData to use the received data object
			'fnServerData'   : function ( sSource, aoData, fnCallback, oSettings ) {
				fnCallback.call(null, { 'DATA': local.data });
			}

		});


		local.properties = properties;

		// init data table
		initFeatures(tableID, features, properties);

		return;
	}
		
	/***
	 * Generates a data table object based off of third function argument, "data". The data object
	 * is expected to be a "query" as an array of objects with the number of array items matching
	 * the number of items in the columnList array. 
	 * 
	 * @param tableID		id of the html table
	 * @param containerID	id of the div to contain the DataTable
	 * @param columnList	An array of column headings to display
	 * @param data			An array of objects in which each object holds a row from a query
	 * @param features		Specifications for additional features not covered by the DataTables plugin (such as checkboxes). Go to initFeatures for details.
	 * @param properties	The properties to give to the DataTables constructor. Refer to getDataTableProperties for details
	 * @param metadata		OPTIONAL. An array of objects that will be saved into each row for later use
	 */
	this.initByDom = function(tableID, containerID, features, properties) 
	{
		local.tableID = tableID;
		local.containerID = containerID;
		//local.columnList = columnList;
		local.features = features;
		local.properties = properties;
		//local.metadata = metadata;
		
		$('#'+tableID).addClass('table');
		
		// init data table
		initFeatures(tableID, features, properties);
	}
	
	/***
	 * Returns a reference to an existing DataTable object, or creates
	 * a new one with the default properties if none exist. Please use
	 * initByTemplate or initByQuery if you wish to create a new DataTable.
	 * 
	 * @param tableID	id of an html table
	 */
	this.getDataTable = function(tableID)
	{
		$('#' + tableID).dataTable();
	}
	
	/***
	 * Gets a DataTable properties object.
	 * @param type					OPTIONAL. Type of DataTable template to use
	 * @param sortBy				OPTIONAL. What to initially sort by and how. Ex. [columnNumber,"asc"] or [columnNumber,"desc"] . 
											  [[columnNumber, "asc"], [columnNumber, "asc"]] for multiple columns.
	 * @param sortableColumns		OPTIONAL. An array of column numbers that will determine which columns will be sortable
	 * @param notSortableColumns	OPTIONAL. An array of column numbers that will determine which columns will not be sortable
	 * @param dataTypeList			OPTIONAL. An array of strings and/or nulls defining what type of data format to expect for each column.
	 * 								Ex. [ { "sSortDataType": "dom-checkbox" }, null, null, null, null, null, null, { "sType": "currency" }, null, null ]
	 * 								This will make checkboxes sortable, as well as currency. The rest will be strings, dates, numbers, etc.
	 */
	this.getDataTableProperties = function(type, sortBy, sortableColumns, notSortableColumns, dataTypeList)
	{
		local.type = type;

		var sortDefs = new Array();
		var properties;
		
		if(!type || type === 'default')
		{
			properties = { "bPaginate":true, 
						   "bInfo":true,
						   "bFilter":true,
						   "oLanguage": { 'sSearch': "Filter by search:" }, // Sets the label text for the search bar
						   "iDisplayLength": 25 // Initially show 25 entries
						 };
		}
		else if(type === 'minimalistic')
		{
			properties = { "bPaginate":false, 
						   "bInfo":false,
						   "bFilter":false };
		}
		else if(type === 'deferred')
		{
			properties = {	'bPaginate'      : true, 
							'bInfo'          : true,
							'bFilter'        : true,
							'oLanguage'      : { 'sSearch': "Filter by search:" }, // Sets the label text for the search bar
						    'iDisplayLength' : 25, // Initially show 25 entries
							'bDeferRender'   : true,
							'sAjaxSource'    : '',
							'sAjaxDataProp'  : 'DATA'
							};
		}
		
		if(sortBy)
		{
			if(sortBy[0] instanceof Array)
				properties.aaSorting = sortBy; // multi-column sorting
			else
				properties.aaSorting = [sortBy]; // single-column sorting
		}
		if(sortableColumns)
			sortDefs.push({"aTargets":sortableColumns,"bSortable":true});
		if(notSortableColumns)
			sortDefs.push({"aTargets":notSortableColumns,"bSortable":false});
		if(dataTypeList)
			properties.aoColumns = dataTypeList;
		if(sortDefs.length > 0)
			properties.aoColumnDefs = sortDefs;
		
		return properties;
	}
	
	/***
	 * Returns an array of objects for the selected records
	 * 
	 */
	this.getSelectedRecords = function()
	{

		var $dt = $('#' + local.tableID).dataTable(),
			rowData = new Array(), 
			recordData = {}, 
			metaDataJSON = "",
			filter = "",
			$tr = "";

		if( local.type != 'deferred' ) {

			filter = ($('#' + local.containerID + ' #dataTableFilter').val()=='' ? 'none' : 'applied');

			$.each( $dt.$('input:checked', {'filter': filter, 'page': 'all'}), function(i, o){
				$tr = $(o).parents('tr');
				recordData = $.extend({}, $dt.fnGetData($tr.get(0)));
				metaDataJSON = $($dt.fnGetNodes($tr)).attr('rowmetadata');
				metaDataJSON = (metaDataJSON ? metaDataJSON : $tr.attr('rowmetadata'));
				// Convert String to a valid JSON delimited with " instead of '
				metaDataJSON = metaDataJSON.replace(/({|,|:)'/g, "$1#!X!#")
											.replace(/'(:|,|})/g, "#!X!#$1")
											.replace(/\\'/g, "'")
											.replace(/"/g,'\\"')
											.replace(/#!X!#/g, "\"");
				if( metaDataJSON )
				{
					recordData = $.extend(recordData, { 'metadata': $.parseJSON(metaDataJSON)});
				}
				rowData.push(recordData);
			});

		} else {

			$.each(local.rowSelection.getSelected(), function(i, o){
				recordData = $.extend({}, $dt.fnGetData(o));
				recordData._aoDataIndex = o;
				
				// If metadata is part of the record data then use it
				if( typeof(recordData['METADATA']) != 'undefined' ) 
				{
					recordData = $.extend(recordData, { 'metadata': recordData['METADATA']});
				}
				else if( local.metadata && local.metadata[o] )
				{
					recordData = $.extend(recordData, { 'metadata': local.metadata[o]});
				}
				rowData.push(recordData);
			});

		}
		

		return rowData;

	}
	
	/***
	 * Update the status of the selection hint text
	 * 
	 */
	this.updateSelectAll = function()
	{
		if( $('#' + local.tableID).length > 0 && local.features.selectAllCheckboxID )
			updateSelectAllCheckbox(local.tableID, local.features.selectAllCheckboxID);	
	}

	/***
	 * Clear selected records
	 * 
	 */
	this.deselectAllRecords = function()
	{
		local.rowSelection.deselectAllRecords();
	}
	
	/* private methods */
	
	/***
	 * Creates a DataTable object, and includes all defined features.
	 * To see the requirements necessary for these features to work,
	 * please look for "function KinnserDataTable()".
	 *
	 * Valid values for features: checkboxID 			: string,
	 * 							  selectAllCheckboxID 	: string,
	 *							  exportExcel 			: String representation of an array of json objects of the form 
	 * 								[{ "columnName" : "<string>", "dataType" : "<string>", "columnNum" : <numeric> }]
	 *								Each object corresponds to a column in the Excel file.
	 *									- columnName is what the name of the column is going to be in the Excel file. 
	 *									- dataType is the format to be used for a column. Acceptable values are string, numeric, currency, and ignore.
	 *									  Ignore means that the column will not be included in the Excel file, generally used for checkboxes and buttons in rows.
	 *									- columnNum is the data table column to use. Cold Fusion requests that column numbers start with 1 instead of 0.
	 *							  groupBy 				: Array of booleans that determine which columns can be grouped.
	 *							  columnSum 			: Array of json objects of the form [{ "columnName" : "<string>", "dataType" : "<string>", "columnNum" : <numeric> }],
	 * 								that determine which columns will be summed up, and how the sums will be formatted. Accepted datatypes: numeric, currency
	 *
	 * For data tables with tabs, please refer to the implementation in the Approve Claims screen.
	 *
	 * @param tableID		id of an html table
	 * @param features		Specifications for additional features not covered by the DataTables plugin (such as checkboxes)
	 * @param properties	The properties to give to the DataTables constructor. Refer to getDataTableProperties for details
	 */
	var initFeatures = function(tableID, features, properties)
	{
		//Store original table features
		$('#'+tableID).data('kinnserDT', features);

		//Verify that the requested features are available for the KDT type
		var unsupported = {
			 'deferred': [   ]
			};
		if( unsupported[local.type]){
			var err = [];
			$.each(unsupported[local.type], function(i,o){
				!features[o] || err.push( o + ' feature is not implemented for the type of table you selected.');
			});
			if( err.length > 0 ) throw 'KinnserDataTables (type: ' + local.type + ') Error: \n' + err.join('\n');
		}
		
		// add all requested features
		if(features)
		{
			// add features that need to be initialized
			// before the data table is created
			if(features.checkboxID)
			{
				local.type != 'deferred' && addCheckboxes(tableID, features.checkboxID, features.selectAllCheckboxID) ||
				local.type == 'deferred' && function(){ 
					local.rowSelection = new RowSelection($('#' + tableID));
					properties = local.rowSelection.addCheckboxes(features.checkboxID, features.selectAllCheckboxID, features.initialCheckboxMData, properties);

				}();
			}
			if(features.stateSave)
			{
				if ($('.ux-datatables').length > 0) {
					$.extend(properties, {
							// State saving using the state plugin
							'sDom': 'P' + (properties['sDom'] || $.fn.dataTable.defaults.sDom),
							'oStateSave': features.stateSave,
							'bStateSave': true //necesary to persist current page
						});
				}
			}
			
			$('#' + tableID).dataTable(properties);
			//add an id of 'dataTableFilter' to the filter box
			$('#' + tableID).parent().find('input[aria-controls="' + tableID + '"]').attr('id', 'dataTableFilter');
			
			// add features that require the data table
			// in order to be created
			if(features.exportExcel)
			{
				if ($('.ux-datatables').length > 0) {
					// new implementation ux template 
					addExportExcelUXStyle(tableID, features.exportExcel);
				} else {
					// old implementation
					addExportExcel(tableID, features.exportExcel);
				}
			}
			if(features.selectAllCheckboxID)
			{
				if(local.rowSelection)
					local.rowSelection.addSelectAllFeature();
				else {
					addSelectAllFeature(tableID, features.selectAllCheckboxID);
					
					$( '#' + tableID + '_length' ).change( function( e ){
						updateSelectAllCheckbox(tableID, features.selectAllCheckboxID);	
					});
				}
			}
			if(features.groupBy)
			{
				if (features.selectAllCheckboxID) {
					var iGroupedColumn = addGroupByFeature(tableID, features.groupBy, features.selectAllCheckboxID, features.disableGroupByRemoval, features.groupByDefault);
				}
				else {
					var iGroupedColumn = addGroupByFeature(tableID, features.groupBy, false, features.disableGroupByRemoval, features.groupByDefault);

				};
			}
			if(features.columnSum)
			{
				if ($('.ux-datatables').length > 0) {
					// new implementation col sum table - ux template
					addColumnSumFeatureUXStyle(tableID, features.columnSum);
				} else {
					// old implementation col sum table
					addColumnSumFeature(tableID, features.columnSum);
				}
			}
			
			$('#' + tableID + '_groupBy_row').val(iGroupedColumn).change();

		}
		else
		{
			// no features requested
			$('#' + tableID).dataTable(properties);
		}
	}

	/**
	 * Reset the loaded state (persisted) to its defaults
	 **/
	var resetDatatableCoreState = function(dt){
		// @todo: Reset datatable core state to its default

		// - Number of results 
		// - Filter by text to empty
		// ...
	};
	
	/**
	 * Adds an export to excel link.
	 *
	 * @param tableID	 The ID of the table to add the feature to.
	 * @param columnData Array of json objects of the form [{ "columnName" : "<string>", "dataType" : "<string>", "columnNum" : <numeric> }]
	 *					 Each object corresponds to a column in the Excel file.
	 *					 	- columnName is what the name of the column is going to be in the Excel file. 
	 *					 	- dataType is the format to be used for a column. Acceptable values are string, numeric, currency, and ignore.
	 *						  Ignore means that the column will not be included in the Excel file, generally used for checkboxes and buttons in rows.
	 *						- columnNum is the data table column to use. Cold Fusion requests that column numbers start with 1 instead of 0.
	 */
	var addExportExcel = function(tableID, columnData)
	{
		$('<span id="DT-ExcelMetadata-' + tableID + '" style="display:none">' + columnData + '</span>').prependTo('#' + tableID + 'Header');
		$('<div class="dataTablesExportToExcelText"><a id="' + tableID + '_exportExcelTextLink" href="javascript:void(0)" class="dataTablesExportToExcelText"></a></div>').prependTo('#' + tableID + 'Header');
		$('<a id="' + tableID + '_exportExcelLink" href="javascript:void(0)" class="dataTablesExportExcel"></a>').prependTo('#' + tableID + 'Header');
		
		$("#loadingContainer").dialog({
			autoOpen: false
		});
		
		$('#' + tableID + '_exportExcelLink').click(function() { exportToExcel(tableID); });
		$('#' + tableID + '_exportExcelTextLink').click(function() { exportToExcel(tableID); });


		// Change text of export link when filter status changes
		var exportAllLabel = 'Export all data';
		var exportFilteredLabel = 'Export filtered data';
		var $dataTableFilter = $('#' + tableID).parent().find('#dataTableFilter');
		$dataTableFilter.keyup(function(e) {
			var currentLabel = $('#' + tableID + '_exportExcelTextLink').text();
			if ($(this).val().length > 0 && currentLabel != exportFilteredLabel) {
				$('#' + tableID + '_exportExcelTextLink').text(exportFilteredLabel);
			}
			else if ($(this).val().length == 0 && currentLabel != exportAllLabel) {
				$('#' + tableID + '_exportExcelTextLink').text(exportAllLabel);
			}
			})
			.keyup();
	}
	
	/**
	 * this method was created to add the new implementation of the javascript on the datatable without change the
	 * current implementation. 
	 * Adds an export to excel link.
	 *
	 * @param tableID	 The ID of the table to add the feature to.
	 * @param columnData Array of json objects of the form [{ "columnName" : "<string>", "dataType" : "<string>", "columnNum" : <numeric> }]
	 *					 Each object corresponds to a column in the Excel file.
	 *					 	- columnName is what the name of the column is going to be in the Excel file. 
	 *					 	- dataType is the format to be used for a column. Acceptable values are string, numeric, currency, and ignore.
	 *						  Ignore means that the column will not be included in the Excel file, generally used for checkboxes and buttons in rows.
	 *						- columnNum is the data table column to use. Cold Fusion requests that column numbers start with 1 instead of 0.
	 */
	var addExportExcelUXStyle = function(tableID, columnData)
	{
		
		
		var $spanExport = $('<span id="DT-ExcelMetadata-' + tableID + '" style="display:none">' + columnData + '</span>');
		var $linkExportText = $('<div class="dataTablesExportToExcelText"><a id="' + tableID + '_exportExcelTextLink" href="javascript:void(0)" class="dataTablesExportToExcelText exportToExcelTextIcon">Export all data</a></div>');
		var $linkExport = $('<a id="' + tableID + '_exportExcelLink" href="javascript:void(0)" class="dataTablesExportExcel exportToExcelTextIcon"></a>');
		
		$("#loadingContainer").dialog({
			autoOpen: false
		});
		
		$linkExportText.click(function() { exportToExcel(tableID); });
		$linkExport.click(function() { exportToExcel(tableID); });


		// Change text of export link when filter status changes
		var exportAllLabel = 'Export all data';
		var exportFilteredLabel = 'Export filtered data';
		// Fixed to support multiple KinnserDataTables with filter
		var $dataTableFilter = $('#' + tableID).parent().find('#dataTableFilter');
		$dataTableFilter.keyup(function(e) {
			var currentLabel = $('#' + tableID + '_exportExcelTextLink').text();
			if ($(this).val().length > 0 && currentLabel != exportFilteredLabel) {
				$linkExportText.find('.dataTablesExportToExcelText').text(exportFilteredLabel);
			}
			else if ($(this).val().length == 0 && currentLabel != exportAllLabel) {
				$linkExportText.find('.dataTablesExportToExcelText').text(exportAllLabel);
			}
		});
		$dataTableFilter.keyup();
		
		// render html
		$('#' + tableID + 'HeaderCol2').html($linkExportText).append($linkExport).append($spanExport);
	}

    // To display errors 
    // Use global if defined, if not then use ux dialog.
	var pageError = window.pageError ?  window.pageError : function(errObject) {
		if( ux ) { 
	    	ux.dialog.alert( errObject.FRIENDLY + '<br>' + errObject.MESSAGE );
	    } else {
			$("#errorWindowText").html(errObject.FRIENDLY + '<br>' + errObject.MESSAGE);
			$("#errorWindow").dialog('open');
		}
	};
	
	/**
	 * Exports all displayed data in the data table to Excel.
	 * 
	 * @param tableID	id of an html table
	 */
	var exportToExcel = function(tableID)
	{
		// display loading...
		$(".ui-dialog-titlebar").hide();
		$('#loadingContainer').dialog("open");
		
		// get current data displayed in data table, filtered and sorted
		var rowData = new Array();
		var dataTableObject = $('#' + tableID).dataTable();

		$.each(dataTableObject.fnSettings().aiDisplay, function(i, o){
			rowData.push(dataTableObject.fnGetData(o));
		});
		// type of the tabledata (array | object)
		var tableDataType = rowData.length > 0 ? 
			( $.isArray(rowData[0]) ? 'array' :
				($.isPlainObject(rowData[0]) ? 'object' : '')
				) :
			'';
			
		// get column header metadata; set up json object
		var jsonData = { 'ColumnData' : JSON.parse($('#DT-ExcelMetadata-' + tableID).text()), 'TableData' : rowData };
		
		// get column sum data if there is any
		var columnSumRowData = new Array();
		if($('#' + tableID + '_columnsum').length > 0)
		{

			if ($('.ux-datatables').length > 0) {
			
				$('#' + tableID + '_columnsum td').each(function(idx, element){
					columnSumRowData.push({
						'data': $(element).text(),
						'column': $(element).attr('associatedColumn') ? $(element).attr('associatedColumn') : ''  
					});
				});
			} else {
				$($('#' + tableID + '_columnsum').dataTable().$('td')).each(function(idx, element) {
 					columnSumRowData.push({'data': $(element).text(), 'column': $(element).attr('associatedColumn')});
 				});
			}
		}
		
		if(rowData.length > 0)
		{ 

			// export to excel
			$.ajax({
				type : 'POST',
				url : '/AM/RemoteProxy/DataTablesProxy.cfc',
				data : {
					method: 'exportToExcel',
					dataTableExport: JSON.stringify(jsonData),
					columnSums: JSON.stringify(columnSumRowData),
					tableDataType: tableDataType
				},
				dataType : 'json',
				success : function(data){
					$('#loadingContainer').dialog('close');
					$(".ui-dialog-titlebar").show();

                    if (data.result === 'success') { //no errors returned from the proxy
						// download the file
						window.open(data.EXCELLOC, '_parent');
                    }
                    else {
                        pageError({
							FRIENDLY: 'It was not possible to export the data to Excel, an error occurred.',
							MESSAGE: 'Description: ' + data.errorStruct.MESSAGE
							});
                    }
				},
				error: function(xhr, textStatus, errorThown) {
					$('#loadingContainer').dialog('close');
					$(".ui-dialog-titlebar").show();
					
					var ajaxErrorObject = {
						FRIENDLY: 'An error occurred.',
						MESSAGE: 'Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText
					}
					pageError(ajaxErrorObject, true);
				}
			});
		}
		else
		{
			// nothing to do, since there is no data to export
			$('#loadingContainer').dialog('close');
			$(".ui-dialog-titlebar").show();
		}
	}
	
	/**
	 * Adds an export to excel link.
	 *
	 * @param tableID			The ID of the table to add the feature to.
	 * @param groupableList		Array of booleans that determine which columns can be grouped.
	 *							Or Json object of the form { group: [bool,bool,...], show: [bool,bool,bool] }
	 * @param selectAllCheckBoxID		
	 * @param groupByDefault			OPTIONAL: An integer representing the column that the table should be initially grouped by.
	 * @param disableGroupByRemoval		OPTIONAL: Disable the ability for users to remove grouping from the table.
	 *
	 */
	var addGroupByFeature = function(tableID, groupableList, selectAllCheckBoxID, disableGroupByRemoval, groupByDefault)
	{
		var current = false,
			showWhenGrouped = false,
			loadedSettings = $('#' + tableID).dataTable().fnSettings().oLoadedState,
			loadState = false;

		if( $.isPlainObject(arguments[1]) ){
			current = arguments[1].current;
			showWhenGrouped = arguments[1].show;
			groupableList = arguments[1].group;
		}

		var groupByHTML = '<div id="' + tableID + '_groupBy" class="dataTables_groupBy"><label>Grouped by <select id="' + tableID + '_groupBy_row" aria-controls="' + tableID + '">';
		if(!disableGroupByRemoval)
		{
			groupByHTML += '<option value="-1">None (all columns show)</option>';
		}
		if(groupByDefault !== false && groupByDefault >= 0)
		{
			current = groupByDefault;
		}

		// replace with a search by class later
		// make it so that all headers with exportable data have a class
		$.each( $('#' + tableID ).dataTable().fnSettings().aoColumns, function(idx, element) {
			if(groupableList[idx])
			{
				var columnHeader = element.sTitle;
				groupByHTML += '<option value="' + idx + '">' + columnHeader + '</option>';
			}
		});
		
		groupByHTML += '</select></label></div>';
		
		
		// @todo Remove this selective statement when UXTemplate is implemented on the entire app
		if ($('.ux-datatables').length > 0) {
			$('#' + tableID + 'Display .groupby-wrapper').append(groupByHTML);
		} else {
			$('#' + tableID + '_filter').before(groupByHTML);
		}
		$('#' + tableID + '_groupBy_row').change(function() {
			var group_col = $('#' + tableID + '_groupBy_row').val();
			var hide_grouped = ! (showWhenGrouped && showWhenGrouped[group_col]);

			// reset sum columns to it's default
			adjustTableFooterColumns(tableID);

			// Reset to first page when groupby is changed
			if( ! loadState ) {
				$('#' + tableID).dataTable().fnSettings()._iDisplayStart = 0;
			} else {
				loadState = false;
			}

			// group the data together
			// A value of -1 will disable row grouping
			$('#' + tableID).dataTable().rowGrouping({ 
				'iGroupingColumnIndex' : group_col,
				'bHideGroupingColumn'  : hide_grouped,
				'fnOnGrouped': function(){
					// @todo Remove this condition when UXTemplate is implemented on the entire app
					if( $('.ux-datatables').length > 0 ) {
						// if totals are present we should hide the grouped column too
						if( group_col  >= 0) {
							adjustTableFooterColumns(tableID, group_col);
						}
					}
				}
			});
			
			if (selectAllCheckBoxID) {
				updateSelectAllCheckbox(tableID, selectAllCheckBoxID);
			};
		});
		
		//return value we want to preselect for the group-by dropdown
		if( current!== false && current >= 0){
			// Load saved state if present
			//what is this supposed to be doing? if loadedSettings is null, loadedState = true
			loadState = loadedSettings && loadedSettings['groupBy'] && typeof(loadedSettings.groupBy['currentValue']) != 'undefined';
			
			return loadState ? loadedSettings.groupBy['currentValue'] : current;
		}
		else
			return -1 //return default value (group by none)
	}
	
	/**
	 * Makes adjustments to TFOOT for the column sums feature. This function is only relevant for DataTables
	 * that are using the groupBy and columnSum features. When we select some choice from the groupBy SELECT
	 * changes to the colspan on a TFOOT.TD and a TFOOT.TH visibility need to occur.
	 * @param sTableID			ID of the table sans #
	 * @param iGroupByColumn	number of the column we are grouping by (zero-based)
	**/
	var adjustTableFooterColumns = function(sTableID, iGroupByColumn) {
		if( $('tfoot', $('#' + sTableID)).length == 0 ) //no footer exists for this table, exit
			return true;
		
		var $table = $('#' + sTableID),
			bHideFooterElements = arguments.length == 2,
			$colspanTD = $('tfoot td[colspan]', $table).first(), //only adjust a single colspan
			$untouchables = $();
			iNewColspanValue = 1;
		
		if(bHideFooterElements){ //hide
			iNewColspanValue = $colspanTD.prop('defaultColspan') - 1; //decrement colspan
			$('tfoot th:eq(' + iGroupByColumn + ')', $table).hide(); //hide TFOOT header element (TH) of the column we are grouping by
		} else{ //show (slightly more complicated)
			//we need to check TFOOT for TH elements that are already hidden, as we don't want to disturb them
			if( $('tfoot', $table).prop('doNotAlter') === undefined ){ //initial run
				//using the DataTables settings here as the table may not be visible just yet
				var aHiddenColumns = $.map($table.dataTable().fnSettings().aoColumns, function(oValue, iKey) {
					if(!oValue.bVisible)
						return $('tfoot th:eq(' + iKey + ')', $table)[0];
				});
				$untouchables = $(aHiddenColumns); //get TH elements that we have not set as hidden (as a jQuery object)
				
				$('tfoot', $table).prop('doNotAlter', $untouchables); //persist these elements in TFOOT's properties
			} else{ //subsequent function executions
				$untouchables = $('tfoot', $table).prop('doNotAlter'); //grab TH element that we are not to touch (irrelevant)
			}
			
			iNewColspanValue = $colspanTD.prop('defaultColspan'); //get colspan value to restore
			$('tfoot th', $table).not($untouchables).show(); //restore visibility to all relevant TFOOT header elements
		}
				
		$colspanTD.attr('colspan', iNewColspanValue); //set colspan
	}
	
	/**
	 * Adds a small data table totaling numbers.
	 * @param tableID			The ID of the table to add the feature to.
	 * @param columnList		Array of json objects of the form [{ "columnName" : "<string>", "dataType" : "<string>", "columnNum" : <numeric> }],
	 * 							that determine which columns will be summed up, and how the sums will be formatted.
	 *							Accepted datatypes: numeric, currency
	 */
	var addColumnSumFeature = function(tableID, columnList)
	{
		var dataTableObj = $('#' + tableID).dataTable();
		var htmlTableStr = '<table id="' + tableID + '_columnsum" width="100%"><thead><tr>'; //begin table structure
		htmlTableStr += '<th style="padding-left: 2px; cursor: pointer;"><strong>Totals, current table data</strong></th>';
		
		// set up data table properties
		var nonSortableColumns = new Array();
		var columnDataTypes = new Array();
		columnDataTypes.push(null);
		
		// set up headers
		for(var i = 0; i < columnList.length; i++){
			htmlTableStr += '<th class="' + tableID + '_' + columnList[i]["columnName"].replace(/[ \.]/g, '_') + '" style="padding-left: 2px; cursor: pointer; text-align:left"><strong>' + columnList[i]["columnName"] + '</strong></th>'; //include column headings
			nonSortableColumns.push(i);
			
			if(columnList[i]["dataType"] === 'currency')
				columnDataTypes.push({ "sType": "currency" });
			else
				columnDataTypes.push(null);
		}
		nonSortableColumns.push(columnList.length);
		htmlTableStr += '</tr></thead><tbody>'; //end header, begin table body
		htmlTableStr += '<tr id="dataTableSum">';
		htmlTableStr += '<td associatedColumn="" style="border-bottom:1px solid #999"></td>'; // empty table cell for totals header
		
		// sum columns
		$('#' + tableID + ' th').each(function(idx_th, element) {
			// if current header is one of the ones to be summed up
			var th = $(element).children('strong:first').text();
			var colIndex = -1;
			for(var i = 0; i < columnList.length; i++)
			{
				if(columnList[i]["columnName"] === th)
				{
					colIndex = i;
					break;
				}
			}
			
			if(colIndex != -1)
			{
				var currentColumn = columnList[colIndex];
				currentColumn.columnNum += local.features.selectAllCheckboxID ? 1 : 0;

				// sum values across all pages, filtered
				var sum = 0;
				var rows = dataTableObj.fnSettings().aiDisplay; // get filtered data
				for(var i = 0; i < rows.length; i++)
				{
					var data = dataTableObj.fnGetData(rows[i], currentColumn.columnNum - 1);
					// clean up dollar amount
					data = data.replace('$', '');
					data = data.replace(/,/g, '');
					sum += Number(data);
				}
				// format sum
				if(columnList[colIndex]["dataType"] === "currency")
				{
					sum = formatCurrency(sum);
				}
				else if(columnList[colIndex]["dataType"] === "numeric")
				{
					sum = sum.toFixed(2);
				}
				else if(columnList[colIndex]["dataType"] === "int")
				{
					sum = Math.round(sum);
				}
				
				var columnName = columnList[colIndex]["columnName"].replace(/[ \.]/g, '_');
				htmlTableStr += '<td id="' + columnName + '_sum" associatedColumn="' + (columnNum) + '" class="' + tableID + '_' + columnName + '" style="padding-left: 2px; border-bottom:1px solid #999">' + sum + '</td>';
			}
		});
		
		// finish creating table
		htmlTableStr += '</tr>'; //end data row
		htmlTableStr += '</tbody></table>'; //end table structure
		
		$('#' + tableID).after(htmlTableStr);
		
		var dataTable = new KinnserDataTable();
		var sumDTProperties = dataTable.getDataTableProperties('minimalistic', null, null, nonSortableColumns, columnDataTypes);
		sumDTProperties.bAutoWidth = false;
		var columnSumDTObj = $('#' + tableID + '_columnsum').dataTable(sumDTProperties);
		
		// reset sorting
		columnSumDTObj.$('td', { 'filter' : 'none', 'page' : 'all' }).each(function(idx, element) { $(element).attr('class', ''); });
		
		// format columns to match the widths of the parent columns
		$('#' + tableID + ' th').each(function(idx_th, element) {
			var tableColumn = $('#' + tableID + '_columnsum .' + tableID + '_' + $(element).children('strong:first').text().replace(/[ \.]/g, '_'));
			tableColumn.css('width', $(element).css('width'));
			tableColumn.css('padding-left', $(element).css('padding-left'));
			tableColumn.css('padding-right', $(element).css('padding-right'));
		});
		

		var $dataTableFilter = $('#' + tableID).parent().find('#dataTableFilter');
		// updates the sums whenever the filter changes
		$dataTableFilter.keyup(function(oSettings)
		{
			// match the headers to be summed up
			$('#' + tableID + ' th').each(function(idx_th, element) {
				var th = $(element).children('strong:first').text();
				var colIndex = -1;
				for(var i = 0; i < columnList.length; i++)
				{
					if(columnList[i]["columnName"] === th)
					{
						colIndex = i;
						break;
					}
				}
				
				if(colIndex != -1)
				{
					var currentColumn = columnList[colIndex];
					currentColumn.columnNum += local.features.selectAllCheckboxID ? 1 : 0;

					// sum values across all pages, filtered
					var sum = 0;
					var rows = dataTableObj.fnSettings().aiDisplay; // get filtered data
					for(var i = 0; i < rows.length; i++)
					{
						var data = dataTableObj.fnGetData(rows[i], currentColumn.columnNum - 1);
						data = data.replace('$', '');
						data = data.replace(/,/g, '');
						sum += Number(data);
					}
					// format sum
					if(columnList[colIndex]["dataType"] === "currency")
					{
						sum = formatCurrency(sum);
					}
					else if(columnList[colIndex]["dataType"] === "numeric")
					{
						sum = sum.toFixed(2);
					}
					else if(columnList[colIndex]["dataType"] === "int")
					{
						sum = Math.round(sum);
					}
					$('#' + columnList[colIndex]["columnName"].replace(/[ \.]/g, '_') + '_sum').text(sum);
				}
			});
		});
	}
	
	
	/**
	 * Adds a small data table totaling numbers with the change requested by alex 
	 * @param tableID			The ID of the table to add the feature to.
	 * @param columnList		Array of json objects of the form [{ "columnName" : "<string>", "dataType" : "<string>", "columnNum" : <numeric> }],
	 * 							that determine which columns will be summed up, and how the sums will be formatted.
	 *							Accepted datatypes: numeric, currency
	 */
	var addColumnSumFeatureUXStyle = function(tableID, columnList)
	{
		
		var dataTableObj = $('#' + tableID).dataTable(),
			htmlTableStr = '<tfoot id="' + tableID + '_columnsum" class="totals">',
			columns = {},
			allColumns = $('#' + tableID).dataTable().fnSettings().aoColumns,
			totalLabel = 'Totals, selected data',
			colNames = [];
		
		// Fill columns with a hash
		$(columnList).each(function(i,o){ 
			columns[columnList[i]["columnName"]] = columnList[i];
			columns[columnList[i]["columnNum"]] = columnList[i]["columnName"];
			minSumColumn = Math.min()
			});

		htmlTableStr += '<tr class="heading">'; //begin tfoot headings

		if ( local.features.selectAllCheckboxID ){
			htmlTableStr += '<th><!--Checkbox Column--></th>';
		};
		// set up headers
		for(var i = 1; i <= allColumns.length; i++){ //Starting from the first non-checkbox column
			var colName = colNames[i] ? colNames[i] : ( columns[i] ? columns[i] : '');
			if (allColumns[i]) {
				var style = '';
				if ( !allColumns[i].bVisible ){
					style = 'style="display: none;"';
				};
				
				htmlTableStr += '<th class="' + tableID + '_' + colName.replace(/[ ,]+/g, '_') + '" ' + style + ' >' +
					'<strong>' +
					colName +
					'</strong></th>'; //include column headings
			};			
		};

		if ( typeof local.features.selectAllCheckboxID === 'undefined' ){ 
			htmlTableStr += '<th class="' + tableID + '_' + colName.replace(/[ ,]+/g, '_') + '" >' +
				'<strong>' +
				colName +
				'</strong></th>'; //end header
		};
		
		htmlTableStr += '<tr id="dataTableSum">';
		
		// sum columns
		$('#' + tableID + ' th').each(function(idx_th, element) {
			
			// if current header is one of the ones to be summed up
			var th = $(element).text();
			var currentColumn = columns[th] ? columns[th] : false;
			
			if( currentColumn )
			{
				currentColumn.columnNum += local.features.selectAllCheckboxID ? 1 : 0;

				// sum values across all pages, filtered
				var sum = 0;
				var rows = dataTableObj.fnSettings().aiDisplay; // get filtered data
				for(var i = 0; i < rows.length; i++)
				{
					var data = dataTableObj.fnGetData(rows[i], currentColumn.columnNum-1);
					// clean up dollar amount if present
					if( data.replace ){
						data = data.replace('$', '').replace(/,/g, '');
					}
					sum += Number(data);
				}
				// format sum
				if(currentColumn["dataType"] === "currency")
				{
					sum = formatCurrency(sum);
				}
				else if(currentColumn["dataType"] === "numeric")
				{
					sum = sum.toFixed(2);
				}
				else if(currentColumn["dataType"] === "int")
				{
					sum = Math.round(sum);
				}
				// Remove potential conflictive chars
				var columnName = currentColumn["columnName"].replace(/[^a-z0-9_\-]+/gi, '_');
				htmlTableStr += '<td id="' + columnName + '_sum" associatedColumn="' + currentColumn["columnNum"] + '" class="' + tableID + '_' + columnName + 
					'  ' +  dataTableObj.fnSettings().aoColumns[currentColumn.columnNum-1].sClass + '" style="">' + sum + '</td>';
			} else {
				htmlTableStr += '<td ></td>';
			}
		});
		
		// finish creating table
		htmlTableStr += '</tr>'; //end data row
		htmlTableStr += '</tfoot>'; //end tfoot structure
		
		$('#' + tableID).append(htmlTableStr);
		
		// Adding total label		
		$('#' + tableID + ' #dataTableSum td:not(:empty):first').prev()
			.html(totalLabel)
			.addClass('totals-label');
		
		
		/*
			Create a single column that will span multiple columns for the column
			sum's label. Count all of the empty TDs (non-summed columns) in the
			TFOOT's row. Once we come across a TD containing a column sum, we'll
			know that we're finished and can define the default colspan.
		*/
		colSpan = 1;
		labelExpanded = false; //flag to let us know when we're finished "expanding" the label column
		//walk the columns on TFOOT's row
		$('#' + tableID + ' #dataTableSum td').each(function(iIndex, oElement){
			if(labelExpanded)
				return;
			
			if( $(oElement).is(':empty') ){ //column (TD) does not contain anything...
				colSpan += 1; //increment the colspan
				$(oElement).remove(); //remove the TD as we no longer have a use for it
			} else if( colSpan > 1 ){ //column (TD) contains something and our colspan value is greater than the HTML standard value of 1
				$(oElement).attr('colspan', colSpan); //set the colspan attribute on the TD (column sums label)
				$(oElement).prop('defaultColspan', colSpan); //set a property on the TD to persist the value (useful for the GroupBy feature)
				labelExpanded = true; //we're finished leave the loop
			}
		});
		
		// updates the sums whenever the filter changes
		var $dataTableFilter = $('#' + tableID).parent().find('#dataTableFilter');
		$dataTableFilter.keyup(function(oSettings)
		{
			// match the headers to be summed up
			$('#' + tableID + ' th').each(function(idx_th, element) {

				// if current header is one of the ones to be summed up
				var th = $(element).text();
				var currentColumn = columns[th] ? columns[th] : false;
				
				if( currentColumn )
				{
					// sum values across all pages, filtered
					var sum = 0;
					var rows = dataTableObj.fnSettings().aiDisplay; // get filtered data
					for(var i = 0; i < rows.length; i++)
					{
						var data = dataTableObj.fnGetData(rows[i], currentColumn.columnNum - 1);
						// clean up dollar amount if present
						if( data.replace ){
							// clean up dollar amount
							data = data.replace('$', '').replace(/,/g, '');
						}
						sum += Number(data);
					}
					// format sum
					if(currentColumn["dataType"] === "currency")
					{
						sum = formatCurrency(sum);
					}
					else if(currentColumn["dataType"] === "numeric")
					{
						sum = sum.toFixed(2);
					}
					else if(currentColumn["dataType"] === "int")
					{
						sum = Math.round(sum);
					}
					// Remove potential conflictive chars
					var columnName = currentColumn["columnName"].replace(/[^a-z0-9_\-]+/gi, '_');
					$('#' + columnName  + '_sum').text(sum);

				}

			});
		});
	}
	
	/**
	 * Puts checkboxes for each row.
	 *
	 * @param tableID				The id of the table to add these to.
	 * @param selectAllCheckboxID	The id of the select/unselect all checkbox
	 * @param checkboxID			The id of the table row checkboxes.
	 */
	var addCheckboxes = function(tableID, checkboxID, selectAllCheckboxID) 
	{
		var tooltipMessage = 'Select/deselect all in this filter.';
		
		if(selectAllCheckboxID)
		{
			//add "select all / unselect all" checkbox to table header
			$('<th class="col-checkbox"><input type="checkbox" id="' + selectAllCheckboxID + '" name="' + selectAllCheckboxID + '" title="' + tooltipMessage + '"></th>').prependTo('#' + tableID + ' thead tr'); 
		}
		
		$('<td class="col-checkbox"><input type="checkbox" id="' + checkboxID + '" name="' + checkboxID + '"></td>').prependTo('#' + tableID + ' tbody tr ');
	}
	
	/**
	 * Gives the functionality for the select all/unselect all checkbox
	 * to automatically update depending on the currently selected choices.
	 *
	 * @param tableID				id of an html table
	 * @param selectAllCheckboxID	The id for the select/unselect all checkbox
	 */
	var addSelectAllFeature = function(tableID, selectAllCheckboxID) 
	{
		var altDeselectAll = '#' + tableID + '_altDeselectAll';
		var altSelectAll = '#' + tableID + '_altSelectAll';
		var selectState = '#' + tableID + '_selectState';
		$('<a id="' + tableID + '_altDeselectAll" href="javascript:void(0)" class="dataTablesSelectAllLink">Deselect all items.</a>').prependTo('#' + tableID + 'Header');
		$('<a id="' + tableID + '_altSelectAll" href="javascript:void(0)" class="dataTablesSelectAllLink">Select all items across all pages.</a>').prependTo('#' + tableID + 'Header');
		$('<span id="' + tableID + '_selectState">No items selected.</span>').prependTo('#' + tableID + 'Header');
		$(altDeselectAll).css('display', 'none');
		
		var tooltipMessage = 'Select/deselect all in this filter.';
		var dataTableObject = $('#' + tableID).dataTable();
		var filterAttribute = '';
		var filtered = dataTableObject.fnSettings().aiDisplayMaster.length != dataTableObject.fnSettings().aiDisplay.length;
		
		var $dataTableFilter = $('#' + tableID).parent().find('#dataTableFilter');
		if( filtered )
			filterAttribute = 'applied';
		else
			filterAttribute = 'none';
		
		var totalPageRows = $(dataTableObject.$('tr', { 'filter' : filterAttribute, 'page' : 'all'})).length; //total table rows visible on dataTable page
		
		//apply "select all / unselect all" actions to table header checkboxes
		if( totalPageRows > 0 ){ 
			// listener for row checkboxes
			// update the select all checkbox based on the number of checkboxes currently selected
			// only select the select all checkbox if all checkboxes across all pages are selected
			$(dataTableObject.$(':checkbox:not([disabled])')).each(function(idx, element) {
				$(element).click(function() {
					var cboxCounter = 0; //checked checkbox counter
					var filtered = dataTableObject.fnSettings().aiDisplayMaster.length != dataTableObject.fnSettings().aiDisplay.length;
					if(filtered)
						filter = 'applied';
					else
						filter = 'none';
					
					$(dataTableObject.$('input:checked', { 'filter' : filter, 'page' : 'all' })).each(function(idx, element) { //count all checked checkboxes
						cboxCounter++;
					});
					
					// display a link for deselecting all items if
					// something has been selected
					if(cboxCounter == 0)
					{
						$(selectState).text('No items selected.');
						$(altDeselectAll).css('display', 'none');
						
						if(filter === 'applied')
							$(altSelectAll).text('Select all items in this search.');
						else
							$(altSelectAll).text('Select all items across all pages.');
					}
					else if(cboxCounter != totalPageRows)
					{
							$(altDeselectAll).css('display', 'inline');
							$(selectState).text('You have some items selected.');
							
							if(filter === 'applied')
								$(altSelectAll).text('Select all items in this search.');
							else
								$(altSelectAll).text('Select all items across all pages.');
					}
					else
					{
						$(altDeselectAll).css('display', 'none');
						$(altSelectAll).text('Deselect all items.');
						
						if(filter === 'applied')
							$(selectState).text('You have selected all items in this search.');
						else
							$(selectState).text('You have selected all items.');
					}
					
					//if all checkboxes on the dataTable page are checked, check the "select all" checkbox
					var state = '';
					if($(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : filter, 'page' : 'current' })).length === $(dataTableObject.$('input:checked', { 'filter' : filter, 'page' : 'current' })).length)
					{
						state = 'true';
						$(selectState).text('You have selected all items on this page.');
					}
					
					changeCheckboxValue($('#' + selectAllCheckboxID), state);
				});
			});
			
			// listener for select/unselect all checkbox
			$('#' + selectAllCheckboxID).click(function(e) {
				//what we are setting the checked attribute to...
				var state = getValueProperty((this), 'checked');
				// select everything on the current page, or deselect everything across all pages
				// maintain filter if selecting, ignore filter if deselecting
				var pagesAffected = '';
				var filtered = dataTableObject.fnSettings().aiDisplayMaster.length != dataTableObject.fnSettings().aiDisplay.length;;
				if(filtered)
					filterAttribute = 'applied';
				else
					filterAttribute = 'none';
				
				if(state || state === 'true')
				{
					$(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : filterAttribute, 'page' : 'current' })).each(function(idx, element) { //look in the td tags to find the checkboxes
						changeCheckboxValue($(element), state);//set checkbox attribute
					});	
					
					var numChecked = $(dataTableObject.$('input:checked', { 'filter' : filterAttribute, 'page' : 'all' })).length;
					var numTotal = $(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : filterAttribute, 'page' : 'all' })).length;
					
					// select all, filtered
					if(filtered)
					{
						if(numChecked == numTotal)
						{
							$(selectState).text('You have selected all items in this search.');
							$(altSelectAll).text('Deselect all items.');
							$(altDeselectAll).css('display', 'none');
						}
						else
						{
							$(selectState).text('You have selected this page of items in this search.');
							$(altSelectAll).text('Select all items in this search.');
							$(altDeselectAll).css('display', 'inline');
						}
					}
					// select all unfiltered
					else
					{
						if(numChecked == numTotal)
						{
							$(selectState).text('You have selected all items.');
							$(altSelectAll).text('Deselect all items.');
							$(altDeselectAll).css('display', 'none');
						}
						else
						{
							$(selectState).text('You have selected all items on this page.');
							$(altSelectAll).text('Select all items across all pages.');
							$(altDeselectAll).css('display', 'inline');
						}
					}
				}
				else
				{
					$(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : filterAttribute, 'page' : 'all' })).each(function(idx, element) { //look in the td tags to find the checkboxes
						changeCheckboxValue($(element), state);//set checkbox attribute
					});	
					
					// deselect all, filtered
					if(filtered)
					{
						$(selectState).text('You have deselected all items in this search.');
						$(altSelectAll).text('Select all items in this search.');
					}
					// deselect all, unfiltered
					else
					{
						$(selectState).text('No items selected.');
						$(altSelectAll).text('Select all items across all pages.');
					}
					
					$(altDeselectAll).css('display', 'none');
				}
			});
			
			// listener for the select all link text
			$(altSelectAll).click(function(e) {
				// select all, unfiltered
				if($(this).text() === 'Select all items across all pages.')
				{
					$(this).text('Deselect all items.');
					$(selectState).text('You have selected all items.');
					$(altDeselectAll).css('display', 'none');
					changeCheckboxValue($('#' + selectAllCheckboxID), true);
					$(dataTableObject.$(':checkbox:not([disabled]):not([disabled])', { 'filter' : 'none', 'page' : 'all' })).each(function(idx, element) { //look in the td tags to find the checkboxes
						changeCheckboxValue($(element), true); //set checkbox attribute
					});
				}
				// deselect all
				else if($(this).text() === 'Deselect all items.')
				{
					var filtered = dataTableObject.fnSettings().aiDisplayMaster.length != dataTableObject.fnSettings().aiDisplay.length;
					// filtered
					if(filtered)
					{
						$(this).text('Select all items in this search.');
						$(selectState).text('You have deselected all items in this search.');
						$(altDeselectAll).css('display', 'none');
					}
					// unfiltered
					else
					{
						$(this).text('Select all items across all pages.');
						$(selectState).text('No items selected.');
						$(altDeselectAll).css('display', 'none');
					}
					
					changeCheckboxValue($('#' + selectAllCheckboxID), false);
					$(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : 'none', 'page' : 'all' })).each(function(idx, element) { //look in the td tags to find the checkboxes
						changeCheckboxValue($(element), false);
					});
				}
				// select all, filtered
				else if($(this).text() === 'Select all items in this search.')
				{
					$(this).text('Deselect all items.');
					$(altDeselectAll).css('display', 'none');
					$(selectState).text('You have selected all items in this search.');
					changeCheckboxValue($('#' + selectAllCheckboxID), true);
					
					$(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : 'applied', 'page' : 'all' })).each(function(idx, element) { //look in the td tags to find the checkboxes
						changeCheckboxValue($(element), true); //set checkbox attribute
					});
				}
			});
			
			// listener for the deselect link
			$(altDeselectAll).click(function(e) {
				$(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : 'none', 'page' : 'all' })).each(function(idx, element) { //look in the td tags to find the checkboxes
					changeCheckboxValue($(element), false); //set checkbox attribute
				});
				
				$(this).css('display', 'none');
				$(selectState).text('No items selected.');
				$(altSelectAll).text('Select all items across all pages.');
			});
			
			// when changing pages, if not everything on this page is selected,
			// unselect the select all checkbox 
			
			// @todo Remove this selective statement when UXTemplate is implemented on the entire app
			if ($('.ux-datatables').length > 0) {
				$('#' + tableID).dataTable().fnSettings().onPageNumberClick = function(){
					updateSelectAllCheckbox(tableID, selectAllCheckboxID);
				}
			}
			$('a', $('#' + tableID).dataTable().fnSettings().aanFeatures.p).click(function(e){
				updateSelectAllCheckbox(tableID, selectAllCheckboxID);
			});
			
			// Always deselect everything when the filter changes
			$dataTableFilter.keyup(function(e) {
				$(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : 'none', 'page' : 'all' })).each(function(idx, element) { //look in the td tags to find the checkboxes
					changeCheckboxValue($(element), false); //set checkbox attribute
				});
				changeCheckboxValue($('#' + selectAllCheckboxID), false); 
				
				if($(this).val().length > 0)
				{
					$(selectState).text('You have deselected all items in this search.');
					$(altSelectAll).text('Select all items in this search.');
				}
				else
				{
					$(selectState).text('No items selected.');
					$(altSelectAll).text('Select all items across all pages.');
				}
				
				$(altDeselectAll).css('display', 'none');
			});
		}
	}
	
	/**
	 * This function checks the current page of the table to see
	 * whether the select all checkbox should be checked or unchecked.
	 *
	 * @param tableID				id of an html table
	 * @param selectAllCheckboxID	The id for the select/unselect all checkbox
	 */
	var updateSelectAllCheckbox = function(tableID, selectAllCheckboxID)
	{
		var altDeselectAll = '#' + tableID + '_altDeselectAll';
		var altSelectAll = '#' + tableID + '_altSelectAll';
		var selectState = '#' + tableID + '_selectState';
		var dataTableObject = $('#' + tableID).dataTable();
		var $dataTableFilter = $('#' + tableID).parent().find('#dataTableFilter');
		var filtered = dataTableObject.fnSettings().aiDisplayMaster.length != dataTableObject.fnSettings().aiDisplay.length;
		var selectAllCheckboxState = '';
		// check state of search
		var filterAttribute = '';
		if(filtered)
		{
			filterAttribute = 'applied';
		}
		else
			filterAttribute = 'none';
		
		var cboxCounter = 0; //checked checkbox counter
		
		$(dataTableObject.$('input:checked', { 'filter' : filterAttribute, 'page' : 'current' })).each(function(idx, element) { //count all checked checkboxes
			cboxCounter++;
		});
		
		// deselect select all checkbox if not all checkboxes are checked on the current page
		if(cboxCounter != $(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : filterAttribute, 'page' : 'current' })).length
			// or if there are no records
			||	cboxCounter == 0)
		{
			changeCheckboxValue($('#' + selectAllCheckboxID), false);
		}
		else
		{
			changeCheckboxValue($('#' + selectAllCheckboxID), true);
			selectAllCheckboxState = 'true';
			
			$(selectState).text('You have some items selected.');
		}
		
		// update select all text
		var numChecked = $(dataTableObject.$('input:checked', { 'filter' : filterAttribute, 'page' : 'all' })).length;
		var numTotal = $(dataTableObject.$(':checkbox:not([disabled])', { 'filter' : filterAttribute, 'page' : 'all' })).length;
		if(numChecked > 0)
		{
			if(filtered)
			{
				if(numChecked == numTotal)
				{
					$(selectState).text('You have selected all items in this search.');
					$(altSelectAll).text('Deselect all items.');
					$(altDeselectAll).css('display', 'none');
				}
				else
				{
					// some items have been selected but not everything on the current page
					if(selectAllCheckboxState === '')
						$(selectState).text('You have some items selected.');
					$(altSelectAll).text('Select all items in this search.');
					$(altDeselectAll).css('display', 'inline');
				}
			}
			else
			{
				if(numChecked == numTotal)
				{
					$(selectState).text('You have selected all items.');
					$(altSelectAll).text('Deselect all items.');
					$(altDeselectAll).css('display', 'none');
				}
				else
				{
					// some items have been selected but not everything on the current page
					if(selectAllCheckboxState === '')
						$(selectState).text('You have some items selected.');
					$(altSelectAll).text('Select all items across all pages.');
					$(altDeselectAll).css('display', 'inline');
				}
			}
		}
		else
		{
			$(selectState).text('No items selected.');
			$(altSelectAll).text('Select all items across all pages.');
			$(altDeselectAll).css('display', 'none');
		}
	}

	
	/***
	 *	Returns string without a JSON packaging character ("<*>")
	 *
	 *	@param inputString	Trim the special character from this string
	 */
	var stripJSONFormatting = function(inputString)
	{
		if (inputString) {
			var specialCharacter = '<*>'; //character we want to strip
			if (inputString.length > 0 && inputString.slice(0, specialCharacter.length) === specialCharacter) { //test for special "formatting" character
				inputString = inputString.slice(specialCharacter.length, inputString.length); //strip character
			}
			return inputString;
		};
		
		return '';
	}
	
	/**
	 * This method is used to reuse this library on jquery 1.4 &  jquery1.7
	 * The problem is the change from attr to prop
	 * 
	 * @param $_element html element
	 * 	      value to set  
	 */
	var changeCheckboxValue;
	if ($.versioncompare('1.6', $.fn.jquery) < 1 ) {
		changeCheckboxValue = function (_element, value) { $(_element).prop('checked', value); }
	} else {
		changeCheckboxValue = function (_element, value) { $(_element).attr('checked', value); }
	}
	
	/**
	 * This method is used to reuse this library on jquery 1.4 &  jquery1.7
	 * The problem is the change from attr to prop
	 * 
	 * return the element value true/false
	 * 
	 * @param $_element html element
	 * 	        
	 */
	var getValueProperty;
	if ($.versioncompare('1.6', $.fn.jquery) < 1 ) {
		getValueProperty = function (_element, property) { return $(_element).prop(property); }
	} else {
		getValueProperty = function (_element, property) { return $(_element).attr(property); }
	}



	var local = {};


	/**
	 * Implements Rows selection for kinnser datatables with defer rendering
	 *
	 * If you need to combine this feature with validation engine, you can use the 
	 * input hidden that is appended to the dom that shows the number of records selected
	 * It can be found using this: $('#' + tableID + '_selectedRecordsCounter')
	 *
	 **/
	var RowSelection = function(dataTable){

		var that = this,
			_dt = dataTable,
			aSelected = [],
			$selectAll = $(),
			$deselectAll = $(),
			$selectState = $(),
			$checkAll = $(),
			$selectedRecordsCounter = $('<input type="hidden" value="0"/>').attr('id', $(dataTable).attr('id') + '_selectedRecordsCounter' );

		

		// Initialize selected records counter
		$(dataTable).parent().prepend($selectedRecordsCounter);

		// Initialize checkbox click event handler for all rows
		$(dataTable).on('click', '.row-selection', function(event){
			checkRowOnClick($(this).parents('tr').get(0));
			});


		/**
		 * Updates checkboxes state depending on the record selection
		 *
		 * @param type      string     Accepts 'checkall' or 'uncheckall'
		 *                  int        Record Id to update checkbox status
		 *                  null 	   Will update all checkboxes status.
		 **/
		var updateCheckboxState = function(type){
				if ( type == 'checkall' ){
					changeCheckboxValue( dt().$('.row-selection'), true );
				} else if( type == 'uncheckall' ){
					changeCheckboxValue( dt().$('.row-selection'), false );
				} else if( $.isNumeric(type) ){
					changeCheckboxValue( $(dt().fnGetNodes(type)).find('.row-selection'), $.inArray(type, aSelected) >= 0 ? true : false );
				} else {
					changeCheckboxValue( dt().$('.row-selection'), false );
					$.each(aSelected, function(i,o){
						dt().fnGetNodes(o) && changeCheckboxValue( $(dt().fnGetNodes(o)).find('.row-selection'), true );
					});
				}

				// Update checkall status
				changeCheckboxValue( $checkAll, 
					type != 'uncheckall' && (
						// If checkall was clicked
						type == 'checkall' ||
						// All checkboxes on the page are checked
						(function (){
							$checkboxes = dt().$('input.row-selection', { 'page' : 'current' });
							return $checkboxes.length > 0 &&
								$checkboxes.length == $checkboxes.filter(':checked').length;
							})()  
						)
					);

				// Update selectedRecordsCounter with the selected records quantity
				$selectedRecordsCounter.val(aSelected.length);
				
				// Event Hook that can be used to detect when the checkbox state(s) have changed
				$( $.fn.dataTable.fnTables( ) ).trigger( 'checkboxstatechange' );
			},

			/**
			 * Updates the select all text and links depending on the table status
			 * filter and current selection.
			 */
			updateSelectAllFeature = function( ) {
				var numSelected = aSelected.length,
					numRecordsDisplay = dt().fnSettings().fnRecordsDisplay(),
					numRecordsTotal = dt().fnSettings().fnRecordsTotal(),
					checkedAllVal = getValueProperty( $checkAll, 'checked' ),

					isFiltered = numRecordsDisplay < numRecordsTotal,
					isCheckedAll = checkedAllVal || checkedAllVal === 'true',
					isSelectedAll = numSelected == numRecordsTotal,

					selectionStatus = numSelected + "." +
						( isFiltered ? '1' : '0' ) + "." + 
						( isCheckedAll ? '1' : '0' ) + "." + 
						( isSelectedAll ? '1' : '0' ),

					/* st: 'status', sa: 'Select All', cla: 'Select all class', da: 'deselect all' */
					statusList = {
						"[1-9][0-9]*\.1\.1\.0": {
							st: 'You have selected all items on this search.',
							sa: false,
							cla: 'dt-des-all',
							da: true
						},
						"[1-9][0-9]*\.1\.0\.0": {
							st: 'You have some items selected.',
							sa: 'Select all items in this search.',
							cla: 'dt-sel-search',
							da: true
						},
						"[1-9][0-9]*\.[01]\.[01]\.1": {
							st: 'You have selected all items.',
							sa: false,
							cla: 'dt-des-all',
							da: true
						},
						"[1-9][0-9]*\.0\.1\.0": {
							st: 'You have selected all items on this page.',
							sa: 'Select all items across all pages.',
							cla: 'dt-sel-all',
							da: true
						},
						"[1-9][0-9]*\.0\.0\.0": {
							st: 'You have some items selected.',
							sa: 'Select all items across all pages.',
							cla: 'dt-sel-all',
							da: true
						},
						"0\.1.*": {
							st: 'No items selected.',
							sa: 'Select all items in this search.',
							cla: 'dt-sel-search',
							da: false
						},
						"0\.0.*": {
							st: 'No items selected.',
							sa: 'Select all items across all pages.',
							cla: 'dt-sel-all',
							da: false
						}			
					},

					action = {};


				$.each(statusList, function(statusCode, obj){
					re = new RegExp("^" + statusCode + "$","g");
					if( re.test( selectionStatus ) )
					{
						action = obj;
					}
				});

				if( action != {} )
				{
					$selectState.text(action['st']);

					$selectAll.toggle(action['sa'] ? true : false)
						.text(action['sa'])
						.attr('class', 'dataTablesSelectAllLink ' + action['cla']);

					$deselectAll.toggle(action['da'] ? true : false)
				}

			},

			/** 
			 * Select all records on the table
			 **/
			selectAll = function(){
				aSelected = dt().fnSettings().aiDisplayMaster; 
				updateCheckboxState('checkall');
				updateSelectAllFeature();
			},
			
			/** 
			 * Deselect all records on the table
			 **/
			deselectAll = function(){
				aSelected = [];
				updateCheckboxState('uncheckall');
				updateSelectAllFeature();
			},

			/** 
			 * Select all records matching the filter
			 **/
			selectAllSearch = function(){
				aSelected = dt().fnSettings().aiDisplay; 
				updateCheckboxState('checkall');
				updateSelectAllFeature();
			},

			/** 
			 * Select all records on the current page
			 **/
			selectAllPage = function(){
				pageRecords = [];
				$.each(dt().$('tr', {page: 'current'}), function(i,o){
					var index = dt().fnGetPosition(o);
					$.inArray(index, aSelected) >= 0 || aSelected.push(index);
				});
				updateCheckboxState();
				updateSelectAllFeature();
			},

			/** 
			 * Toggle current selection
			 **/
			selectToggle = function(index){
				if( $.inArray(index, dt().fnSettings().aiDisplayMaster) == -1 ){
					throw "Record " + index + " does not exist on the current dataset, thus can not be selected.";
				} 
				var pos = $.inArray(index, aSelected);
				if( pos == -1 )
					aSelected.push(index);
				else
					aSelected.splice(pos,1);

				updateCheckboxState(index);
				updateSelectAllFeature();
			},

			/**
			 * Update selection when checkall is clicked
			 **/
			checkAllOnClick = function(){
				$(this).is(':checked') ? selectAllPage() : deselectAll();
			},

			/**
			 * Update selection when check row is clicked
			 **/
			checkRowOnClick = function(nRow){
				selectToggle(dt().fnGetPosition(nRow));
			};



		/**
		 * Retrieves the dataTable object for the current table
		 **/
		var dt = function(){ 
			_dt.$ || (_dt = $(_dt).dataTable());
			return _dt; 
		}


		return $.extend( this, {

			/**
			 * Get all selected records index on the datatable 
			 *
			 * @return array
			 */
			getSelected: function(){ 
				return aSelected; 
			},

			/**
			 * Select all records on the datatable 
			 *
			 * @return RowSelection Object
			 */
			selectAllRecords: function(){ 
				selectAll();
				return that;
			},
			/**
			 * Deselect all records on the datatable 
			 *
			 * @return RowSelection Object
			 */
			deselectAllRecords: function(){ 
				deselectAll();
				return that;
			},


			/**
			 * Deselect all records on the datatable 
			 *
			 * @return RowSelection Object
			 */
			addCheckboxes: function(checkboxID, selectAllCheckboxID, initialCheckboxMData, properties){
				var tooltipMessage = 'Select/deselect all in this filter.';
				var sTitle = '';

				if( ! properties.aoColumns ){
					properties.aoColumns = [];
				}

				if( selectAllCheckboxID ){
					sTitle = '<input type="checkbox" id="' + selectAllCheckboxID + '" name="' + selectAllCheckboxID + '" title="' + tooltipMessage + '" class="page-rows-selection">';
				}
				
				// pre set checkboxes based on given checkbox data
				var checkboxData = null;				
				if(initialCheckboxMData)
				{
					checkboxData = initialCheckboxMData;
					for( var i = 0; i < local.data.length; i++)
					{
						// checkbox data must be a boolean; add to selected array if not already there
						if(local.data[i][initialCheckboxMData] && ($.inArray(i, aSelected) < 0))
							aSelected.push(i);
					}
				}
				
				var temp = 0;
				var oCol = {
					'mData'           : checkboxData,
					'sTitle'          : sTitle,
					'bSearchable'     : false,
					'bSortable'       : false,
					'sClass'          : 'col-checkbox',
					'mRender'         : function ( data, type, full ) {
						return '<input type="checkbox" id="' + checkboxID + '" name="' + checkboxID + '" class="row-selection">';
					}
				};
				if( properties.aoColumns[0] && properties.aoColumns[0] != null ){
					properties.aoColumns.splice(0,0, oCol);
				} else {
					properties.aoColumns.push(oCol);
				}

				var headerCallback = properties['fnHeaderCallback'] ? properties['fnHeaderCallback'] : function(){},
				    rowCallback = properties['fnRowCallback'] ? properties['fnRowCallback'] : function(){};

				// Overriding callbacks to customize
				$.extend( properties, {
					// Overriding fnHeaderCallback to remove tabstop on checkbox header cell
					"fnHeaderCallback": function( nHead, aData, iStart, iEnd, aiDisplay ) {
						$('th', $(nHead)).removeAttr('tabindex');
						if( $checkAll.length == 0 ){
							$checkAll = $('th', $(nHead))
								.find('.page-rows-selection')
								.on('click', checkAllOnClick);
						}

						headerCallback.call(this, nHead, aData, iStart, iEnd, aiDisplay );
					},

					// Overriding fnRowCallback to update checkbox state after the row is rendered
					"fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
						// update checkbox value checked status when rendered
						changeCheckboxValue( $('.row-selection', nRow), $.inArray(this.fnGetPosition(nRow), aSelected) >= 0 ? true : false );
						
						rowCallback.call(this, nRow, aData, iDisplayIndex, iDisplayIndexFull )
					}
				});
				return properties;
			},

			
			/**
			 * Initialize table dom to add select all feature
			 **/
			addSelectAllFeature: function(){
				var tableID = dt().attr('id');

				if ( $selectAll.length || $deselectAll.length || $selectState.length )
					throw "Select all feature was already initialized, it can only be called once.";

				$selectAll = $('<a href="javascript:void(0)"></a>')
					.addClass('dataTablesSelectAllLink')
					.attr('id', tableID + '_altSelectAll' )
					.text('Select all items across all pages.')
					.on( 'click', function(){
						$this = $(this);
						if( $this.hasClass( 'dt-sel-all' ) )
						{
							selectAll();
						}
						else if( $this.hasClass( 'dt-sel-search' ) )
						{
							selectAllSearch();
						}
					});
					
				$deselectAll = $('<a href="javascript:void(0)"></a>')
					.addClass('dataTablesSelectAllLink')
					.attr('id', tableID + '_altDeselectAll' )
					.text('Deselect all items.')
					.on( 'click', function(){
						deselectAll();
					})
					.hide();

				$selectState = $('<span>No items selected.</span>')
					.attr('id', tableID + '_selectState' );

				$('#' + tableID + 'Header')
					.append($selectState)
					.append($deselectAll)
					.append($selectAll);

				updateSelectAllFeature();

				// @todo Remove this selective statement when UXTemplate is implemented on the entire app
				if ($('.ux-datatables').length > 0) {
					dt().fnSettings().onPageNumberClick = function(){
						updateCheckboxState();
						updateSelectAllFeature();
					}
				}
				$('a', dt().fnSettings().aanFeatures.p).click(function(e){
					updateCheckboxState();
					updateSelectAllFeature();
				});
				
				$( '#' + tableID + '_length' ).change( function( e ){
					updateCheckboxState();
					updateSelectAllFeature();
				});

				// Always deselect everything when the filter changes
				$('input[aria-controls="' + $(dataTable).attr('id') + '"]').keyup(function(e) {
					deselectAll();
					$(this).val().length > 0 && $selectState.text( 'You have deselected all items in this search.');
				});

				return;
			}

		});

	}

	/**
	 * Static methods for RowSelection
	 **/
	$.extend( RowSelection, { });
}