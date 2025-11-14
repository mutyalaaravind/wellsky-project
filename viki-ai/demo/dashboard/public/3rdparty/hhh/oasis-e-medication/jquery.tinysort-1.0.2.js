/*
 * http://tinysort.sjeiti.com/
 * 
 */

/* Used in conjunction with the paginator.js 'pagination' function.  Will sort a page that is paginated. 
 * The 'paginate' function must be bound to the element being sorted (sortDiv1,sortDiv2, etc)
 * See /AM/Claims/ClaimBatches.cfm as an example 
 * */
function sortWithPaging(col,sortElem,colObj,pagingElem)
{
	if (pagingElem == undefined)
		pagingElem = sortElem
		
	$('#' + pagingElem).depagination();
	switch (sortElem) 
	{
		case "sortDiv1": sortDiv1(col,colObj); 
		break;
		case "sortDiv2": sortDiv2(col,colObj); 
		break;
		case "sortTable1": sortTable1(col,colObj); 
		break;
		case "sortTable2": sortTable2(col,colObj); 
		break;
		case "sortTable3": sortTable3(col,colObj); 
		break;
	}									
	$('#' + pagingElem).pagination()
}

/*
 * Usage Instructions:
 * Change the ID of the table or the parent Div to be the name of the function (sortDiv1, sortTable1, etc)
 * Add a link with '<a href="javascript:sortTable1(0)">' and increment the functions paramater for each column header
 *   If the column links are in a table, add a 'thead' around the column list  
 * For each column where the data lives, add a 'sortCol="0"' attribute and incrment it for each data column
 * Data will be sorted by what is in the column, to sort on something else add a 'customSort="SORT BY THIS"'
 * To have the rows renumber, add a 'showSortEnumeration="true"' attribute to the column where the numbering lives
 * 
 */

function showSortArrow(colObj,sortOrder,sortParent)
{	
	//preserve the class of the clicked item
	var thisClass = $(colObj).attr('class');
	//clear out all asc/desc classes
	$('#' + sortParent).find('.sortHeaderAsc').removeClass('sortHeaderAsc');
	$('#' + sortParent).find('.sortHeaderDesc').removeClass('sortHeaderDesc');

	//change the class of the selected column to the appropriate class 
	switch(sortOrder)
	{
		case 'desc':
		$(colObj).attr('class','sortHeaderDesc');
		break;

		default:
		$(colObj).attr('class','sortHeaderAsc');
		break;
	}	
}

 
var aAscDiv1 = [];
function sortDiv1(nr,colObj) {
	aAscDiv1[nr] = aAscDiv1[nr]=="asc"?"desc":"asc";
	$("#sortDiv1>ul").tsort("li:eq("+nr+")[sortCol]",{order:aAscDiv1[nr]});
	showSortArrow(colObj,aAscDiv1[nr],'sortDiv1Header')
}

var aAscDiv2 = [];
function sortDiv2(nr,colObj) {
	aAscDiv2[nr] = aAscDiv2[nr]=="asc"?"desc":"asc";
	$("#sortDiv2>ul").tsort("li:eq("+nr+")[sortCol]",{order:aAscDiv2[nr]});
	showSortArrow(colObj,aAscDiv2[nr],'sortDiv2Header')
}


var aAscTable1 = [];
function sortTable1(nr,colObj,altRow) {
	aAscTable1[nr] = aAscTable1[nr]=="asc"?"desc":"asc";
	$("#sortTable1>tbody>tr").tsort("td:eq("+nr+")[sortCol]",{order:aAscTable1[nr],altRow:altRow});
	showSortArrow(colObj,aAscTable1[nr],'sortTable1')
}

var aAscTable2 = [];
function sortTable2(nr,colObj) {
	aAscTable2[nr] = aAscTable2[nr]=="asc"?"desc":"asc";
	$("#sortTable2>tbody>tr").tsort("td:eq("+nr+")[sortCol]",{order:aAscTable2[nr]});
	showSortArrow(colObj,aAscTable2[nr],'sortTable2')
}

var aAscTable3 = [];
function sortTable3(nr,colObj) {
	aAscTable3[nr] = aAscTable3[nr]=="asc"?"desc":"asc";
	$("#sortTable3>tbody>tr").tsort("td:eq("+nr+")[sortCol]",{order:aAscTable3[nr]});
	showSortArrow(colObj,aAscTable3[nr],'sortTable3')
}

var aAscTableClass = [];
function sortTableClass(nr,colObj) {
	aAscTableClass[nr] = aAscTableClass[nr]=="desc"?"asc":"desc";
	//console.log(aAscTableClass[nr]);
	$('.sortTableClass').each(function()
		{
			$(this).find("tbody>tr").tsort("td:eq("+nr+")[sortCol]",{order:aAscTableClass[nr]});
		}
	)
	showSortArrow(colObj,aAscTableClass[nr],'sortTableClass')
}

/*
* jQuery TinySort - A plugin to sort child nodes by (sub) contents or attributes.
*
* Version: 1.0.2
*
* Copyright (c) 2008 Ron Valstar
*
* Dual licensed under the MIT and GPL licenses:
*   http://www.opensource.org/licenses/mit-license.php
*   http://www.gnu.org/licenses/gpl.html
*
* description
*   - A plugin to sort child nodes by (sub) contents or attributes.
*     http://www.sjeiti.com/?page_id=321
*
* Usage:
*   $("ul#people>li").tsort();
*   $("ul#people>li").tsort("span.surname");
*   $("ul#people>li").tsort("span.surname",{order:"desc"});
*   $("ul#people>li").tsort({place:"end"});
*
* Change default like so:
*   $.tinysort.defaults.order = "desc";
*
* Changes in 1.0.2
*   - matching numerics did not work for trailing zero's, replaced with regexp (which should now work for + and - signs as well)
*
* Todos
*   - fix mixed literal/numeral values
*   - determine if I have to use setArray or pushStack
*
*/
;(function($) {
	// default settings
	$.tinysort = {
		 id: "TinySort"
		,version: "1.0.2"
		,defaults: {
			order: "asc"	// order: asc, desc or rand
			,attr: ""		// order by attribute value
			,place: "start"	// place ordered elements at position: start, end, org (original position), first
			,returns: false	// return all elements or only the sorted ones (true/false)
			, altRow: 'tr0'
		}
	};
	$.fn.extend({
		tinysort: function(_find,_settings) {
			if (_find&&typeof(_find)!="string") {
				_settings = _find;
				_find = null;
			}

			var oSettings = $.extend({}, $.tinysort.defaults, _settings);

			var oElements = {}; // contains sortable- and non-sortable list per parent
			this.each(function(i) {
				// element or sub selection
				var mElm = (!_find||_find=="")?$(this):$(this).find(_find);
								// text or attribute value
				var customSort = '';
				if (mElm.attr('customSort')!= undefined){customSort = mElm.attr('customSort')}	
				var sSort = (customSort==""?mElm.text():customSort);


				// to sort or not to sort
				var mParent = $(this).parent();
				if (!oElements[mParent]) oElements[mParent] = {s:[],n:[]};	// s: sort, n: not sort
				if (mElm.length>0)	oElements[mParent].s.push({s:sSort,e:$(this),n:i}); // s:string, e:element, n:number
				else				oElements[mParent].n.push({e:$(this),n:i});
			});
			
			
			// sort
			for (var sParent in oElements) {
				var oParent = oElements[sParent];
				oParent.s.sort(
					function zeSort(a,b) {
						var x = a.s.toLowerCase?a.s.toLowerCase():a.s;
						var y = b.s.toLowerCase?b.s.toLowerCase():b.s;
						if (isNum(a.s)&&isNum(b.s)) {
							x = parseFloat(a.s);
							y = parseFloat(b.s);
						}
						return (oSettings.order=="asc"?1:-1)*(x<y?-1:(x>y?1:0));
					}
				);
			}
			//
			// order elements and fill new order
			var aNewOrder = [];
			for (var sParent in oElements) {
				var oParent = oElements[sParent];
				var aOrg = []; // list for original position
				var iLow = $(this).length;
				switch (oSettings.place) {
					case "first": $.each(oParent.s,function(i,obj) { iLow = Math.min(iLow,obj.n) }); break;
					case "org": $.each(oParent.s,function(i,obj) { aOrg.push(obj.n) }); break;
					case "end": iLow = oParent.n.length; break;
					default: iLow = 0;
				}
				var aCnt = [0,0]; // count how much we've sorted for retreival from either the sort list or the non-sort list (oParent.s/oParent.n)
				
				for (var i=0;i<$(this).length;i++) 
				{
					var bSList = i>=iLow&&i<iLow+oParent.s.length;
					if (contains(aOrg,i)) bSList = true;
					var mEl = (bSList?oParent.s:oParent.n)[aCnt[bSList?0:1]].e;
					mEl.removeClass(oSettings.altRow).removeClass('tr1');
					if (i%2 == 0)
						mEl.addClass(oSettings.altRow)
					else
						mEl.addClass('tr1')
				
					mEl.children().each(function(){
						if ($(this).attr('showSortEnumeration')!=undefined)
						$(this).text(i+1 + '.')
					})
						
					mEl.parent().append(mEl);
					if (bSList||!oSettings.returns) aNewOrder.push(mEl.get(0));
					aCnt[bSList?0:1]++;
				}
			}
			//
			return this.pushStack(aNewOrder); // setArray or pushStack?
		}
	});
	// is numeric
	function isNum(n) {
		return /^[\+-]?\d*\.?\d*$/.exec(n);
	};
	// array contains
	function contains(a,n) {
		var bInside = false;
		$.each(a,function(i,m) {
			if (!bInside) bInside = m==n;
		});
		return bInside;
	};
	// set functions
	$.fn.TinySort = $.fn.Tinysort = $.fn.tsort = $.fn.tinysort;
})(jQuery);



