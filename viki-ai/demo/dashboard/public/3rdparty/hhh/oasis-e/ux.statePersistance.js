/**
 * StatePersistance functionality
 *
 */

(function(ux){


	// State Persistance class to create the elememt
	// and return the proper object
	/** @constructor */
	var StatePersistance = function( options ){

		var options = $.extend( 
			{
				'namespace' : window.location.pathname.toLowerCase(),
				'sessionCacheKeyDefault' : '-1'
			}
			, options );

		// Using toLowerCase() to fix TP26919 saving separate states when accessing 
		// a single page using diferent (not case sensitive) URL
		var prefix = 'sp_' + options.namespace,
			defaultPrefix = 'sp_def_' + options.namespace,

            setSessionId = function() {
                // Set SID both in local storage and session storage at the same time.
                if (typeof shouldFixHotboxFilters === 'function' && shouldFixHotboxFilters()) {
                    var sid = new Date().getTime();

                    if (window.localStorage) {
                        localStorage.setItem('sid', sid);
                    }

                    if (window.sessionStorage) {
                        sessionStorage.setItem('sid', sid);
                    }

                // Setting SID only on local storage has side effects on the Hotbox
                // or whatever landing page that tries to set a variable on storage for the first time.
                // SID on session storage eventually catches up after the second request.
                } else {
                    localStorage.setItem('sid', (new Date()).getTime());
                }
            },

			getVariable = function( field ){ 
				return prefix + "_" + field; 
			},

			getDefaultVariable = function( field ){ 
				return defaultPrefix + "_" + field; 
			};

			getNewSessionCacheKey = function(currentSessionCacheKey){
				//Stripping json prefix and adding token to header
				$.ajaxSetup({
					cache:false,
					dataFilter:function(data,type) {
						//remove "//"
						if( type == 'json' ) {
						data = data.substring(2,data.length);//remove "//"
						}
						return data;
					}
				});

				var result;
				$.ajax({
					type: 'GET',
					async: false,
					cache: false,
					dataType: 'json',
					url: '/SessionManagement/SessionManager.cfc?method=CreateNewSessionCacheKey&sessionCacheKey=' + currentSessionCacheKey,
					success: function (data) {
						result = data.SESSIONCACHEKEY;
					},
					error: function (textStatus, errorThrown){
						result = {};
					}
				});
				return result;
			};

            shouldFixHotboxFilters = function() {
				var result = false;
                var ddMethod = 'isApplicationLevelFeatureEnabled';
                var settingName = 'DARK_DEPLOY_HCL10222_FixHotboxFilters';
                var endpoint = '/API/services/DarkDeploy/DarkDeployService.cfc?method=' + ddMethod + '&settingName=' + settingName;

				$.ajax({
					type: 'GET',
					async: false,
					cache: false,
					dataType: 'text',
					url: endpoint,
					success: function(response) {
                        result = response === "true" ? true : false;
					},
					error: function(textStatus, errorThrown) {
                        console.error('uxsp - failed to verify DARK_DEPLOY_HCL10222_FixHotboxFilters');
                        return false;
					}
				});

				return result;
			};

            /*  This functions takes a URL like this:
                https://kinnser.net/am/Forms/index.cfm?PatientTaskKey=582852161&sessionCacheKey=C16F2791-FCB0-344C-41BDF28A15A057BD:D7DB0D7F#/index.cfm?sessionCacheKey=C16F2791-FCB0-344C-41BDF28A15A057BD:D7DB0D7F
                and returns it minus the selected query param key/value (e.g., sessionCacheKey):
                https://kinnser.net/am/Forms/index.cfm?PatientTaskKey=582852161#/index.cfm  */
                removeParam = function(key, sourceURL) {
                    // do a top level split the URL by hash (#, fragment identifier)
                    var initialSplit = sourceURL.split("#");
                    // initialize everything else
                    var mainURL = initialSplit[0];
                    var mainURLBase = mainURL.split("?")[0];
                    var mainURLQueryParams = (mainURL.indexOf("?") !== -1) ? mainURL.split("?") : [];
                    var hashStringFull = '';
    
                    // process the hash string of the URL separately if available. Remove the desired key/query param
                    if (typeof(initialSplit[1]) != "undefined"){
                        var hashString = '';
                        var hashBase = initialSplit[1];
                        hashStringQueryParams = (initialSplit[1].indexOf("?") !== -1) ? initialSplit[1].split("?") : [];
                        // if query params were found in the hash portion, find and remove the desired key (e.g., SessionCacheKey)
                        if (typeof(hashStringQueryParams[1]) != "undefined"){
                            hashBase = hashStringQueryParams[0]; //preserve the url part of the hash string
                            hashString = paramRemoval(key, hashStringQueryParams.slice(1));
                        }
                        hashStringFull = '#' + hashBase + hashString;
                    }
    
                    // process the query params portion of the URL, remove desired key/query param
                    var mainURLQueryParamsModified = paramRemoval(key, mainURLQueryParams.slice(1));
    
                    // rebuild URL and return
                    return mainURLBase + mainURLQueryParamsModified + hashStringFull;
                };

            // loops through all of the query params and removes the matching key/value pair
            paramRemoval = function(key, queryParamString) {
                var queryStrings = [],
                index = 0;

                queryParamString.forEach(function (queryString, i) {
                    var queryStringTemp = [];
                    queryStringTemp = queryString.split("&");
                    for (var i = queryStringTemp.length - 1; i >= 0; i -= 1) {
                        var param = queryStringTemp[i].split("=")[0];
                        if (param.toLowerCase() === key.toLowerCase()) {
                            queryStringTemp.splice(i, 1);
                        }
                    }
                    if (queryStringTemp.length) {
                        queryStrings[index] = '?' + queryStringTemp.join("&");
                    }
                    index++;
                });

                return queryStrings.join('');
            };

            /*  This functions takes a URL like this:
                https://kinnser.net/am/Forms/index.cfm?PatientTaskKey=582852161#/index.cfm
                and adds a sessionCacheKey key/value pair as a query param to the appropriate parts of the URL, e.g.:
                https://kinnser.net/am/Forms/index.cfm?sessionCacheKey=C16F2791-FCB0-344C-41BDF28A15A057BD:D7DB0D7F&PatientTaskKey=582852161#/index.cfm?sessionCacheKey=C16F2791-FCB0-344C-41BDF28A15A057BD:D7DB0D7F
                  */
                appendSessionCacheKey = function(url, sck = '') {
                    var sessionCacheKey = (sck.length > 0) ? sck : window.sessionStorage.sessionCacheKey;
    
                    if (statePersistance.isValidSessionCacheKey(sessionCacheKey)) {
                        var appendedURL = '';
                        var anchorString = '';
                        var sessionCacheKeyAppend = 'sessionCacheKey=' + sessionCacheKey;
                        var isAngularURL = url.indexOf('/EHR/#/') != -1;
                        var angularURLAppended = false;
    
                        // remove sessionCacheKey from URL and split the resultant URL by hash for angular URLs and fragment identifiers
                        // the first index of the array will contain the baseURL
                        var cleanURL = removeParam("sessionCacheKey", url);
                        var splitURLbyHash = cleanURL.split("#");
                        var baseURL = splitURLbyHash[0];
    
                        // if there is a hash (#) in the URL, separate that part and process it separately (this is not the common case)
                        if (typeof(splitURLbyHash[1]) != 'undefined'){
                            // check for '?' delimiter and replace it with the delimiter plus the sessionCacheKey
                            if (splitURLbyHash[1].indexOf('?') != -1) {
                                anchorString = splitURLbyHash[1].replace('?', '?' + sessionCacheKeyAppend + '&');
                                angularURLAppended = isAngularURL;
                            // if there is no '?' delimiter but the string ends with .cfc or .cfm append sessionCacheKey
                            } else if (splitURLbyHash[1].search(/\.cf(c|m)/) != -1) {
                                anchorString = splitURLbyHash[1] + '?' + sessionCacheKeyAppend;
                            // if no delimiter or .cf* in string do nothing
                            } else {
                                anchorString = splitURLbyHash[1];
                            }
                            //restore hash to hash portion
                            anchorString = '#' + anchorString;
                        }
    
                        // if this was an Angular URL we can return the appended URL here
                        if (splitURLbyHash[0].indexOf('/EHR/') != -1 && isAngularURL){
                            var angularSessionCacheKeyAppend = angularURLAppended ? '' : '?' + sessionCacheKeyAppend;
                            return splitURLbyHash[0] + anchorString + angularSessionCacheKeyAppend;
                        }
    
                        // here we process the main, non hash, part of the URL.
                        // we split by '?' so that we can append the sessionCacheKey to the appropriate segements of the URL
                        baseURL = splitURLbyHash[0].split("?");
                        // no '?' separator was found so we can just append the sessionCacheKey
                        if (baseURL.length == 1) {
                            appendedURL = baseURL[0] + '?' + sessionCacheKeyAppend;
                        } else if (baseURL.length > 1){
                            // loop over each segment and append
                            baseURL.slice(1).forEach(function(value) {
                                var newPortion = '?' + sessionCacheKeyAppend + '&' + value;
                                appendedURL = appendedURL + newPortion;
                            });
                            appendedURL = baseURL[0] + appendedURL + anchorString;
                        }
                    } else {
                        // a valid sessionCacheKey was not passed in so return it as-is
                        return url;
                    }
    
                    return appendedURL;
                };

			getSessionStorageSessionCacheKey = function () {
                var sessionCacheKey = options.sessionCacheKeyDefault;
                if (typeof window.sessionStorage.sessionCacheKey !== 'undefined'){
                    sessionCacheKey =  isValidSessionCacheKey(window.sessionStorage.sessionCacheKey) ? window.sessionStorage.sessionCacheKey : options.sessionCacheKeyDefault;
                }
                return sessionCacheKey;
			};

            isValidSessionCacheKey = function (sessionCacheKey) {
                var regex = /[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{16}:[a-zA-Z0-9]{8}/g;
                return typeof sessionCacheKey !== 'undefined' && sessionCacheKey.match(regex);
            };

			duplicateTabConditions = function () {
				return (typeof window.sessionStorage.sessionCacheKey == 'undefined'
				||
				window.sessionStorage.reloadSessionCacheKey == 'undefined'
				||
				typeof window.sessionStorage.reloadSessionCacheKey == 'undefined'
				||
				window.sessionStorage.reloadSessionCacheKey == 1)
			};
            // helps us track when a browser tab has been duplicated
            resetReloadSessionCacheKeyFlag = function () {
                window.sessionStorage.reloadSessionCacheKey = 1;

                // not all browsers support the beforeunload event so we need to check the
                // beforeunloadSupported flag that is set on the login page
                if (isBeforeunloadSupported()){
                    window.addEventListener('beforeunload', function (e) {
                        window.sessionStorage.reloadSessionCacheKey = 0;
                    });
                    window.addEventListener('unload', function (e) {
                        window.sessionStorage.reloadSessionCacheKey = 0;
                    });
                } else {
                    window.sessionStorage.reloadSessionCacheKey = 0;
                }
            };

            isBeforeunloadSupported = function (){
                return window.localStorage.beforeunloadSupported === '1';
            };
			getQueryParamByName = function (name, url) {
				url = url || window.location.href;
				name = name.replace(/[\[\]]/g, '\\$&');
				var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
				results = regex.exec(url);
				if (!results) return null;
				if (!results[2]) return '';
				return decodeURIComponent(results[2].replace(/\+/g, ' '));
			};
            externalLoginCheck = function (){
                //check if app was accessed from an 'external' source like CallTrack so
                //that we don't create a new sessionCacheKey
                var param = 'CallTrackLogin';
                if (typeof getQueryParamByName(param) === "string"){
                    window.sessionStorage.reloadSessionCacheKey = 0;
                }
            };
            removeExternalLoginReference = function (){
                //remove CallTack query param from URL, if it exists, so we're not longer
                //looking for it
                var param = 'CallTrackLogin';
                if (getQueryParamByName(param)){
                    var sansParam = removeURLParameter(window.location.href, param);
                    //update URL without page refresh
                    window.history.pushState(null, null, sansParam);
                }
            }
            removeURLParameter = function (url, parameter) {
                var urlparts= url.split('?');
                if (urlparts.length>=2) {

                    var prefix= encodeURIComponent(parameter)+'=';
                    var params= urlparts[1].split(/[&;]/g);

                    for (var i= params.length; i-- > 0;) {
                        if (params[i].lastIndexOf(prefix, 0) !== -1) {
                            params.splice(i, 1);
                        }
                    }

                    url= urlparts[0]+'?'+params.join('&');
                    return url;
                } else {
                    return url;
                }
            };

		// Verify that the sessionStorage data corresponds to the same
		// session that is active now
		var sid = localStorage.getItem('sid');
		if( window.sessionStorage && window.localStorage && sid != null ) {
			
			if( sid != sessionStorage.getItem('sid') ){
				// Clear session storage if sid's are different in
				// localStorage and sessionStorage
				var sessionCacheKey = getSessionStorageSessionCacheKey();
				var reloadSessionCacheKey = window.sessionStorage.reloadSessionCacheKey;
				sessionStorage.clear();
				window.sessionStorage.sessionCacheKey = sessionCacheKey;
				window.sessionStorage.reloadSessionCacheKey = reloadSessionCacheKey;
			}
			if ( sessionStorage.getItem('sid') == null ){
				// If the user opens a new tab then copy the sid
				sessionStorage.setItem('sid', sid);
			}
		}


		var pageFieldsGroup = {},

			statePersistance = {

				'getItem':  function( field ){
					var value = '';
					if( window.sessionStorage && window.localStorage) {
						value = sessionStorage.getItem( getVariable( field ) );
						if( value == null) {
							value = localStorage.getItem( getVariable( field ) );
						}
					} else {
						value = $.cookie( getVariable( field )  );
					}
					
					return JSON.parse( value );
				},

				'setItem':  function( field, value, forceUpdateDefault ){

					var value = JSON.stringify(value);
					if( window.sessionStorage && window.localStorage) {

						// Update localStorage only if the instance is still
						// the active session
						if( localStorage.getItem('sid') == sessionStorage.getItem('sid') ){
							// Store default state of this element only the first time
							// to use it later for reseting filters
							if( localStorage.getItem( getDefaultVariable( field ) ) == null ||
								forceUpdateDefault ) {
								localStorage.setItem( getDefaultVariable( field ) , value);
							}
							localStorage.setItem( getVariable( field ), value );
						}
						sessionStorage.setItem( getVariable( field ), value );
					} else {
						$.cookie( getVariable( field ), value );
					}

				},

				'removeItem' : function( field ){

					if( window.sessionStorage && window.localStorage) {
						sessionStorage.removeItem( getVariable( field ) );
						localStorage.removeItem( getVariable( field ) );
					} else {
						$.cookie( getVariable( field ) , null );
					}

				},
				'clearDatatableState' : function( sDatatableId ){

					this.removeItem( 'DT_' + sDatatableId );

				},
				'clear' : function(  ){				
					if( window.sessionStorage && window.localStorage) {
						// preserve sessionStorage.sessionCacheKey and sessionStorage.reloadSessionCacheKey which tracks the session
						var sessionCacheKey = getSessionStorageSessionCacheKey();
						var reloadSessionCacheKey = window.sessionStorage.reloadSessionCacheKey;
						window.sessionStorage.clear();
						window.sessionStorage.sessionCacheKey = sessionCacheKey;
						window.localStorage.sessionCacheKey = sessionCacheKey;
						window.sessionStorage.reloadSessionCacheKey = reloadSessionCacheKey;
						var beforeunloadSupported = window.localStorage.beforeunloadSupported;
						localStorage.clear();
						window.localStorage.beforeunloadSupported = beforeunloadSupported;
						setSessionId();
					} else {
						var cookies = document.cookie.split(";");
						for(var i=0; i < cookies.length; i++) {
							var equals = cookies[i].indexOf("="),
								field = equals > -1 ? cookies[i].substr(0, e) : cookies[i];

							$.cookie( field , null );
						}
						
					}
				},
				'getDefaultItem':  function( field ){
					var value = '';
					if( window.sessionStorage && window.localStorage) {
						value = localStorage.getItem( getDefaultVariable( field )  );
					} else {
						value = $.cookie( getDefaultVariable( field )   );
					}
					
					return JSON.parse( value );
				},
				'setSessionCacheStateLogin': function(){
					window.sessionStorage.removeItem('sessionCacheKey');
					window.localStorage.removeItem('sessionCacheKey');
					window.sessionStorage.reloadSessionCacheKey = 0;
				},
				'setSessionCacheKey': function(){
					//TODO: make sure session is still valid before we duplicate it
					externalLoginCheck();
					var currentSessionCacheKey = getQueryParamByName('sessionCacheKey', window.location.href);
					window.sessionStorage.setItem('sessionCacheKey', currentSessionCacheKey);
					window.localStorage.setItem('sessionCacheKey', currentSessionCacheKey);
					if (duplicateTabConditions()) {
						var newSessionCacheKey = getNewSessionCacheKey(currentSessionCacheKey);
						$.ajax({
							url: '/AM/RemoteProxy/SessionManagerProxy.cfc?method=copySessionCacheToNewKey&SourceSessionCacheKey=' + currentSessionCacheKey + '&DestinationSessionCacheKey=' + newSessionCacheKey,
							success: function (result) {
								reloadLocation = removeParam("sessionCacheKey", window.location.href);
								var separator = reloadLocation.match(/\?/) ? '&' : '?';
								window.location = reloadLocation + separator + 'sessionCacheKey=' + newSessionCacheKey;
							},
							async: false
						});
					}
					removeExternalLoginReference();
                    resetReloadSessionCacheKeyFlag();
                },
                'addSessionCacheKeyToAnchors': function () {
                    ux.statePersistance.addSessionCacheKeyToForms();
                    var sessionCacheKey = window.sessionStorage.sessionCacheKey;
                    var hrefAttr = $(this).attr("href");

                    // no need to append urls that start with a hash tag
                    if ((typeof hrefAttr !== 'undefined') && hrefAttr.charAt(0) === "#"){
                        return;
                    }

                    if (isValidSessionCacheKey(sessionCacheKey) && hrefAttr) {
                        if (hrefAttr.indexOf('mailto:') < 0 && hrefAttr.indexOf('tel:') < 0 && hrefAttr.length > 0) {
                            if ($(this).attr("href").indexOf('sessionCacheKey=' + sessionCacheKey) === -1) {
                                var originalLink = hrefAttr;
                                var location = originalLink;

                                if (originalLink.indexOf(';') >= 0) {
                                    var locationStart = originalLink.indexOf('window.location');

                                    if (locationStart === -1) {
                                        locationStart = originalLink.indexOf('location.href');
                                    }

                                    if (locationStart >= 0) {
                                        var startLocation = originalLink.indexOf('\'', locationStart) + 1;
                                        var endLocation = originalLink.indexOf('\'', startLocation);
                                        location = originalLink.substring(startLocation, endLocation);
                                    }
                                }

                                if (location.indexOf('javascript') === -1 && location.length > 0) {
                                    var newLocation = appendSessionCacheKey(location);
                                    $(this).attr("href", originalLink.replace(location, newLocation));
                                }
                            }
                        }
                    }
                },
                'addSessionCacheKeyToOnClick': function () {
                    ux.statePersistance.addSessionCacheKeyToForms();
                    var sessionCacheKey = window.sessionStorage.sessionCacheKey;

                    if (isValidSessionCacheKey(sessionCacheKey) && $(this).attr('onClick')) {
                        var originalLink = $(this).attr('onClick');
                        var reLocation = /(window\.location|location\.href) {0,2}= {0,2}('|")/g; // match window.location or location.href
                        var locationStart = originalLink.indexOf('window.location');

                        // if window.location/location.href is not assigned a value, don't append
                        if (!originalLink.match(reLocation)){
                            return;
                        }

                        if (locationStart === -1) {
                            locationStart = originalLink.indexOf('location.href');
                        }

                        if (locationStart >= 0) {
                            var startLocation = originalLink.indexOf('\'', locationStart) + 1;
                            var endLocation = originalLink.indexOf('\'', startLocation);
                            var location = originalLink.substring(startLocation, endLocation);
                            var newLocation = appendSessionCacheKey(location);
                            var newLink = originalLink.replace(location, newLocation);
                            $(this).attr('onClick', newLink);
                        }
                    }
                },
                'addSessionCacheKeyToForms': function () {
                    var sessionCacheKey = window.sessionStorage.sessionCacheKey;
                    if (isValidSessionCacheKey(sessionCacheKey)) {
                        $('form').each(function (i, f) {
                            var action = f.getAttribute("action") ? f.getAttribute("action") : f.action;

                            if (typeof action === 'string') {
                                action = appendSessionCacheKey(action);
                                f.getAttribute("action") ? f.setAttribute("action", action) : f.action = action;
                            }
                        });
                    }
                },

                'addSessionCacheKeyToLinks' : function( ){
                    // Not checking for if links are external, so sessionCacheKey is appending to those also
                    var sessionCacheKey = window.sessionStorage.sessionCacheKey;

                    if (isValidSessionCacheKey(sessionCacheKey)) {
                        var anchors = Array.prototype.slice.apply(
                            document.querySelectorAll('a')
                          );
                        for (var a = 0; a < anchors.length; a++) {
                            if (anchors[a].href.indexOf('mailto:') < 0 && anchors[a].href.indexOf('tel:') < 0 && anchors[a].href.length > 0) {
                                if (anchors[a].href.indexOf('sessionCacheKey=' + sessionCacheKey) === -1) {
                                    var originalLink = anchors[a].href;
                                    var location = originalLink;

                                    if (originalLink.indexOf(';') >= 0) {
                                        var locationStart = originalLink.indexOf('window.location');

                                        if (locationStart === -1) {
                                            locationStart = originalLink.indexOf('location.href');
                                        }

                                        if (locationStart >= 0) {
                                            var startLocation = originalLink.indexOf('\'', locationStart) + 1;
                                            var endLocation = originalLink.indexOf('\'', startLocation);
                                            location = originalLink.substring(startLocation, endLocation);
                                        }
                                    }

                                    if (location.indexOf('javascript') === -1 && location.length > 0) {
                                        var newLocation = appendSessionCacheKey(location);
                                        anchors[a].href = originalLink.replace(location, newLocation);
                                    }
                                }
                            }
                        }

                        $('table tr td[onClick]').each(function (i, v) {
                            var originalLink = v.getAttribute('onClick');
                            var locationStart = originalLink.indexOf('window.location');

                            if (locationStart === -1) {
                                locationStart = originalLink.indexOf('location.href');
                            }

                            if (locationStart >= 0) {
                                var startLocation = originalLink.indexOf('\'', locationStart) + 1;
                                var endLocation = originalLink.indexOf('\'', startLocation);
                                var location = originalLink.substring(startLocation, endLocation);
                                if (location.indexOf('sessionCacheKey') === -1) {
                                    var newLocation = appendSessionCacheKey(location);
                                    var newLink = originalLink.replace(location, newLocation);
                                    v.setAttribute('onClick', newLink);
                                }
                            }
                        });

                        $('form').each(function (i, f) {
                            var action = f.getAttribute("action") ? f.getAttribute("action") : f.action;

                            if (typeof action === 'string') {
                                action = appendSessionCacheKey(action);
                                f.getAttribute("action") ? f.setAttribute("action", action) : f.action = action;
                            }
                        });

                        $('select').each(function (i, s) {
                            var locationregex = /location {0,2}=/;
                            var onchange = s.getAttribute("onchange") ? s.getAttribute("onchange") : s.onchange;

                            if (typeof onchange === 'string' && onchange.indexOf('sessionCacheKey') === -1 && onchange.search(locationregex) !== -1) {
                                var urlPart = onchange.replace(locationregex,'');
                                var locationString = 'location=ux.statePersistance.addSessionCacheKeyToURL('+ urlPart + ')';
                                s.getAttribute("onchange") ? s.setAttribute("onchange", locationString) : s.onchange = locationString;
                            }
                        });
                    }
                },
                'addSessionCacheKeyToURL': function (url, sck = '') {
                    return appendSessionCacheKey(url, sck);
                },
                'isValidSessionCacheKey': function(sessionCacheKey){
                    return isValidSessionCacheKey(sessionCacheKey);
                },
                'applyAjaxPrefilter': function () {
                    $.ajaxPrefilter(function (options) {
                        if (typeof options.url !== 'undefined' && options.url.length > 0 && options.url.search(/.*.cf[cm]/i) != -1) {
                            options.url = appendSessionCacheKey(options.url);
                        }
                    });
                },
                'reloadPageWithSessionCacheKey': function () {
                    // get values from window.location minus the sessionCacheKey param if it exists
                    var fullQueryParams = removeParam('sessionCacheKey', window.location.search);
                    var host = window.location.host;
                    var protocol = window.location.protocol;

                    // separate path and query params
                    var splitQueryParams = fullQueryParams.replace('?','');
                    var urlPath = splitQueryParams.split('?')[0].split('=')[1];
                    var queryParams = (typeof splitQueryParams.split('?')[1] === 'undefined') ? "" : splitQueryParams.split('?')[1]; //get query params

                    // get sessionCacheKey from sessionStorage
                    var sessionCacheKey = window.sessionStorage.getItem('sessionCacheKey');
                    // if sessionCacheKey is not available in sessionStorage, check localStorage
                    // localStorage will reflect the sessionCacheKey of the last CF page loaded
                    if (sessionCacheKey === null || sessionCacheKey == options.sessionCacheKeyDefault ){
                        sessionCacheKey = window.localStorage.getItem('sessionCacheKey');
                    };

                    // build url with sessionCacheKey
                    var partialURL = protocol + '//' + host + urlPath + '?' + queryParams
                    var separator = partialURL.match(/\?/) ? '&' : '?';
                    var fullURL = partialURL + separator + 'sessionCacheKey=' + sessionCacheKey;

                    window.location.href = fullURL;
                },
                'removeParam': function(key, url) {
                    return  removeParam(key, url);
                },
                'checkEvent': function() {
                    var field = 'beforeunloadSupported';
                    if (window.localStorage && window.localStorage.getItem && window.localStorage.setItem) {
                        window.localStorage.setItem(field, '0');
                        $(window).on('beforeunload', function () {
                            window.localStorage.setItem(field, '1');
                        });
                    }
                }
            };

		return $.extend( statePersistance, { 

			/**
			 * Creates and retrieves the Fields object container to handle
			 * group of fields all together
			 *
			 * @namespace
			 * 
			 * @function
			 * @constructor
			 * @return	{object}
			 */
			'Fields' : function( field, options ){

					// If object is not defined then create it
					if( ! pageFieldsGroup[field] ) {
						var pageFields = {};
						var options = $.extend( { 
							'resetCompleted' : function(){}
							}, options );
						pageFieldsGroup[field] = {

							/**
							 * Add a field to persist its state
							 *
							 * @function add
							 * @param {string} field Key name to use for field state saving
							 * @param {node} elem Node that represents the element in the DOM for which the state will be persisted
							 * @return	{object} self 
							 */
							'add' : function( field, elem, options ){
								// Do not register the field if the node does not exists in the DOM
								if( elem.size() == 0 ) return this;
								options = $.extend( { 
										// Method to get the node value 
										// Using val() by default
										getFieldValue : function(){
											return $(elem).val();
										},

										// Default onLoadState callback 
										onLoadStateDefault: function( event, value ){
											if( value != null )
												$(this).val( value );
										},

										// Default onResetState callback 
										onResetStateDefault: function( event, value ){
											if( $(this).val( ) != value )
												$(this).val( value ).trigger( 'change' );
											}
									}, options);
								var tmp = {};
								tmp[field] = { 'elem' : elem, 'options' : options };
								
								// Attaching event callbacks to dom element
								$.each( 
									['onLoadStateDefault', 'onResetStateDefault', 'onLoadState', 'onResetState'] ,
									function ( key , callbackName ) {
										// Get the eventName to attach the callback to
										var eventName = callbackName.replace(/^on(.*)$/,'$1').replace(/(.*)Default$/,'$1');
										eventName = eventName.charAt(0).toLowerCase() + eventName.slice(1);
										if( typeof( options[callbackName] ) == 'function' )
											elem.on( eventName, options[callbackName]);
									});
								
								$.extend( pageFields, tmp );
								return this;
							},

							/**
							 * Load the current state for the fields group and trigger
							 * loadState event on every field node
							 *
							 * @function 
							 * @return	{object} self 
							 */
							'load' : function(){
								$.each( pageFields, function( field, obj ){
									var value = statePersistance.getItem( field );
									$(obj.elem).trigger('loadState', [ value ]);
									// Store the initial state for this browser
									if( obj.options.getFieldValue() !== false )
										statePersistance.setItem( field , obj.options.getFieldValue() );
									});
								return this;
							},

							/**
							 * Reset the state for the fields group to the defaults and trigger
							 * resetState event on every field node
							 *
							 * @function 
							 * @return	{object} self 
							 */
							'reset' : function(){
								var anyChange = false;
								$.each( pageFields, function( field, obj ){
									var defaultValue = statePersistance.getDefaultItem( field );
									var previousValue = obj.options.getFieldValue();
									if( previousValue !== false )
										statePersistance.setItem( field , defaultValue );
									$(obj.elem).trigger('resetState', [ defaultValue ]);
									var currentValue = obj.options.getFieldValue();
									anyChange = anyChange || ( previousValue != currentValue && previousValue !== false );
									});
								options.resetCompleted.call(this, anyChange);
								return this;
							}
						};
					}

					// retrieve the fields group object
					return pageFieldsGroup[field];
				} 


			} );
	};


	$.extend( ux, {
		/** @lends ux */

		/**
		 * <p>Initializes StatePersistance on the current page.</p>
		 *
		 * @author Rodrigo Fuentes (rodrigo.fuentes@kinnser.com)
		 */

		 'statePersistance': new StatePersistance(),
		 

		/**
		 * <p>Expose StatePersistance constructor to access other pages cached data.</p>
		 *
		 * @author Rodrigo Fuentes (rodrigo.fuentes@kinnser.com)
		 */
		 'StatePersistance': StatePersistance
		 
		});



})(ux);
