// ----------------------------------------------------------------------------
// Pagination Plugin - A jQuery Plugin to paginate content
// v 1.0 Beta
// Dual licensed under the MIT and GPL licenses.
// ----------------------------------------------------------------------------
// Copyright (C) 2010 Rohit Singh Sengar
// http://rohitsengar.cueblocks.net/
// ----------------------------------------------------------------------------
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
// ----------------------------------------------------------------------------
 


//------------ initializing all the values needed in paginator. -----------------



	//--- Variables for internal use ----

	var pageElement = Array();

	var paginatorId = '';
	
	var currentPage = 1; // current page, default 1

	var allItems = 0; // no. of repeating items in the container where paginator is applied

	var lastPage = 1; // last page, default 1

	

	//--- Attributes that can be changed according to use ---

	var startPage = 1; // start page

	var itemsPerPage = 25; // no. of items you want to show on one page

	var firstPageSymbol = '<< First'; // to indicate First Page

	var previousPageSymbol = '< Previous'; // to indicate Previous Page

	var nextPageSymbol = 'Next >'; // to indicate Next Page

	var lastPageSymbol = 'Last >>'; // to indicate Last Page

	var separator = ''; // To separate paginator's items

	var paginatorPosition = 'bottom'; // where you want the paginator to be. Accepted values are 'top','bottom','both'

	var paginatorStyle = 1; // To define which style of paginator you need.

	// 1 - for << | < | 1 | 2 | 3 | > | >>

	// 2 - for << | < | 1/8 | > | >>

	// 3 - for < | 1 | 2 | 3 | >

	// 4 - for < | >
	var enablePageOfOption = false; // it shows on which are you currently, i.e. Page 3 of 6 Page(s), if turned true
	var enableGoToPage = false; // shows a drop down of all pages for go/jump to any page user want to go, if turned true. Useful incase there are large no. of pages
    var textGoToPage = 'Jump to'; // text for above option. You can change it to 'Jump to Page' or anything you like. The above option needs to turned on for this.
	var enableSelectNoItems = true; // if you want to change items per page on the fly.
    var textSelectNoItems = 'Items Per Page'; // text for above option. You can change it to 'Change No. of tag/page' or anything you like. The above option needs to turned on for this.

	var paginatorValues = Array(25,50,100,250,500); // list of values for above option (enableSelectNoItems).

    var anchorLink = 'javascript:void(0);'; // if you want to change href of the paginator anchor text (links for page) to '#' or to something else. As # is append on the address bar upon clicking I used javascript:void(); which is clean.
    
    var showIfSinglePage = true; // set it to false if you don't want to show paginator incase there is only one page, true if show paginator even if there is just one page.

	//var pagingMenu = $('#PagingMenu')
//-----------functions starts----------------------------------------------------


    // function for extending function to dom object. Read more about it in jQuery docs.

	jQuery.fn.extend({

		pagination: function() {

			paginatorId=this;

			switch(paginatorPosition) // create paginator div (container for paginator) according to the position mentioned by user.

			{
				
				case 'top': { $('#PagingMenu').before('<div class="paginator"></div>'); break; }

				case 'bottom': { $('#PagingMenu').append('<div class="paginator"></div>'); break; }

				case 'both': {  $('#PagingMenu').before('<div class="paginator"></div>');

								$('#PagingMenu').after('<div class="paginator"></div>'); break; }
                                
                default: { $('#PagingMenu').after('<div class="paginator"></div>'); }

			} 

			initPaginator(); // calling function to start pagination.

		},
        
        depagination: function() {

			$('.paginator').remove(); // removing paginator class.

			paginatorId.children().show(); // show all content of the div where pagination was applied.

		}

	});

	

	function initPaginator(itemsPerPageLocal)  // for initializing the paginator

	{
		if (typeof(itemsPerPageLocal) != 'undefined'){
			itemsPerPage = itemsPerPageLocal;
		}

		if(itemsPerPage < 1)

			itemsPerPage = 5;

		allItems = paginatorId.children().length; // finding number of total items in content
		if(allItems%itemsPerPage == 0) // calculating last page of the paginator

			lastPage = parseInt(allItems/itemsPerPage);

		else

			lastPage = parseInt(allItems/itemsPerPage)+1;

		if((startPage < 1)||(startPage > lastPage))	// start page for pagination

			startPage = 1;
            
        if(!showIfSinglePage) // check if option is set to false
        {
            if(lastPage > 1)  // show pagination only if there is more than 1 page.
                appendContent(startPage, 1);
        }
        else
            appendContent(startPage, 1); // call function to show start page for first time. Fading effect is not required initially.

	}

	
    // function for appending the content of selected page. called everytime whenever user clicks on any active link of paginator. set effect true/1 for fading effects, false/0 for changing contents for 

	function appendContent(page, effect) 

	{

		if(page < 0)

		{

			if(page == -1)

				page = currentPage - 1;

			else

				page = currentPage + 1;

		}

		currentPage = page; // get current page or page selected.

		

		till = (currentPage-1)*itemsPerPage;

		

		if(!effect)  // Page change without fading effect

		{
			paginatorId.customFadeOut("medium", function () { // fade out the current content 
				createPaginator();  // create new paginator
				paginatorId.children().hide();  // hide all child element of content
				paginatorId.children().slice(till, itemsPerPage+till).show(); // show only those items according to page selected. 
				paginatorId.customFadeIn("medium"); // use nice fade in effect to show the items of that selected page.
			});

		}

		else //with fading effect

		{
            createPaginator();   // create new paginator
			paginatorId.children().hide();  // hide all child element of content
			paginatorId.children().slice(till, itemsPerPage+till).show();  // show only those items according to page selected.

		}

	}
    
    
	function createPaginator()  // for creating the paginator

	{

		$(".paginator").html("");

		

		var style1 = ''; // for << | < | 1 | 2 | 3 | > | >>

		var style2 = ''; // for << | < | 1/8 | > | >>

		var style3 = ''; // for < | 1 | 2 | 3 | >

		var style4 = ''; // for < | >

		var pageOfOption = ' <br> Page '+currentPage+' of '+lastPage+' Page(s) ';  // for showing page info option

		var goToPage = ' '+textGoToPage+' <select onchange="appendContent(this.value);" >'; // for go to page option 

		var selectNoItems = ' '+textSelectNoItems+' <select id="itemsPerPage" name="itemsPerPage" onchange="itemsPerPage=Number(this.value);initPaginator(Number(this.value));" >';  // for changing items per page option
		

		for(var i=0;i<paginatorValues.length;i++) // preparing drop down for selectNoItems option

		{

			if(itemsPerPage == paginatorValues[i])

				selectNoItems += '<option value="'+paginatorValues[i]+'" selected="selected">'+paginatorValues[i]+'</option>';

			else

				selectNoItems += '<option value="'+paginatorValues[i]+'">'+paginatorValues[i]+'</option>';

		}

		

		selectNoItems += '</select>';

		

		if(currentPage == 1) // for setting paginator style if current page is first page

		{

			style = '<a href="'+anchorLink+'" class="inactive" title="First Page">'+firstPageSymbol+'</a>' + separator;

			style1 = style2 = style;

			style = '<a href="'+anchorLink+'" class="inactive" title="Previous Page">'+previousPageSymbol+'</a>' + separator;

			style1 += style; 

			style2 += style;

			style3 += style;

			style4 += style;

		}	

		else // for setting paginator style for first page links

		{

			style = '<a href="'+anchorLink+'" class="active" onclick="appendContent(1);" title="First Page">'+firstPageSymbol+'</a>' + separator;

			style1 = style2 = style;

			style = '<a href="'+anchorLink+'" class="active" onclick="appendContent(-1);" title="Previous Page">'+previousPageSymbol+'</a>' + separator;

			style1 += style;

			style2 += style;

			style3 += style;

			style4 += style;

		}

		

		

		for(var i=1;i<=lastPage;i++) // prepareing links for pages 

		{

			if(i == currentPage) // if page is current page then set anchor class to inactive and no onclick function.

				{

					style1 += '<a href="'+anchorLink+'" class="inactiveSelected paginationLink" title="Page '+i+'">'+i+'</a>' + separator;

					style2 += '<a href="'+anchorLink+'" class="inactiveSelected paginationLink" title="Page '+i+'">'+i+'/'+lastPage+'</a>' + separator;

					style3 += '<a href="'+anchorLink+'" class="inactiveSelected paginationLink" title="Page '+i+'">'+i+'</a>' + separator;

					goToPage += '<option value="'+i+'" selected="selected">'+i+'</option>'; // preparing go to option drop down

				}

			else // if page is not current page then set anchor class to active and put onclick appendContent function.

				{

					style = '<a href="'+anchorLink+'" class="active paginationLink" onclick="appendContent('+i+');" title="Page '+i+'">'+i+'</a>' + separator;

					style1 += style;

					style3 += style;

					goToPage += '<option value="'+i+'">'+i+'</option>';  // preparing go to option drop down

				}

		}

		

		goToPage += '</select>';  // preparing go to option drop down

		

		if(currentPage == lastPage) // for setting paginator style if current page is last page

		{

			style = '<a href="'+anchorLink+'" class="inactive" title="Next Page">'+nextPageSymbol+'</a>';

			style1 += style;

			style2 += style;

			style3 += style;

			style4 += style;

			style = separator + '<a href="'+anchorLink+'" class="inactive" title="Last Page">'+lastPageSymbol+'</a>';

			style1 += style;

			style2 += style;

		}

		else // for setting paginator style for last page links

		{

			style = '<a href="'+anchorLink+'" class="active" onclick="appendContent(-2);" title="Next Page">'+nextPageSymbol+'</a>';

			style1 += style;

			style2 += style;

			style3 += style;

			style4 += style;

			style = separator + '<a href="'+anchorLink+'" class="active" onclick="appendContent('+lastPage+');" title="Last Page">'+lastPageSymbol+'</a>';

			style1 += style;

			style2 += style;

		}

			

		switch (paginatorStyle) // getting which style of pagination is mentioned.

		{

			case 1 : style = style1; break;

			case 2 : style = style2; break;

			case 3 : style = style3; break;

			case 4 : style = style4; break;

			default : style = style1;

		}

		
        
        // appending various other options if they are enabled or set to true.

		if(enablePageOfOption)

			style += '<span class="informational" title="Page Information">' + pageOfOption + '</span>';

		if(enableGoToPage)

			style += '<span class="informational" title="Select Page">' + goToPage + '</span>';

		if(enableSelectNoItems)

			style += '<span class="informational" title="Select no. of items per page">' + selectNoItems + '</span>';

		

		$(".paginator").html(style);	

	}
    
// --------------------- Plugin Ends ----------------------------

	