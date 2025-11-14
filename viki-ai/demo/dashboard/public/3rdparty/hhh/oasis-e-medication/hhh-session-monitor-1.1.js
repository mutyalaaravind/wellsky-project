/**
 * v1.1:
 * @author leonardo.neumann
 * - Factory instantiation
 * - Configurable
 * - separate file template
 * - Autoinject to body
 * v1.0:
 * @author timothy.thompson
 */

var HHHSessionMonitorConfig = 	{
	templateUrl: "/AM/assets/js/HHHSessionMonitor/hhh-session-monitor-1.1.html",
	//session management settings
	sessionManagementServiceToken: 'SESSIONMANAGEMENTTOKEN',
	sessionManagementServiceUrl : '/SessionManagement/index.cfm',
	refreshSessionUrl: '/AM/refreshSession.cfm',
	logoutUrl: '/logout.cfm?logout=1',
	timeoutCountdown: ( 5 /* minutes */ * 60 /* seconds */ ),
	tokenRefreshInterval: (1800000), // 30 minutes in milliseconds
	tokenRefreshURL: '/AM/RemoteProxy/SSOProxy.cfc?method=refreshTokens',  //sessionCacheKey should be automatically appended to this request
	sessionCacheKeyDefault: '-1'
};

var HHHSessionMonitorFactory = function (config) {

	var openCountdownDialog = function() {
		$( '#timeout-dialog' ).countDownDialog( 'open' );
	}

	var logout = function(reason) {
        window.location = config.logoutUrl + (reason ? '&reason=' + reason : '') + '&' + appendSessionCacheKey();
	}

	var refreshSSOTokens = function(errorHandlerCallback){
		// The SSOTRF cookie value is set during authentication in Authentication.cfc
		if (getCookie('SSOTRF') === 'true' && getSessionStorageSessionCacheKey() !== config.sessionCacheKeyDefault){
			$.ajax({
				url      : config.tokenRefreshURL,
				cache    : false,
				dataType : 'json',
				success  : function( data ) {
					if (data == "NO TOKEN" ){
						logout('TOKEN_EXPIRED_OR_NOT_FOUND')
					}
					else{
						return;
					}
				},
				error: function(XMLHttpRequest, textStatus, errorThrown) { 
					if(errorHandlerCallback) errorHandlerCallback(XMLHttpRequest, textStatus, errorThrown);
				}
			});
		}
	}

	var pingServer = function(errorHandlerCallback){
		var timeoutToken = $.cookie(config.sessionManagementServiceToken);

		var timeSpan = config.timeoutCountdown  + 5 /* seconds */;

		if(timeoutToken) {
			$.ajax({
				url      : config.sessionManagementServiceUrl,
				data     : {
					id : timeoutToken
				},
				cache    : false,
				dataType : 'json',
				success  : function( data ) {
					if ( data.timeout.data > timeSpan ) {
						window.setTimeout( pingServer, data.timeout.data * 1000 - ( timeSpan * 1000 ) ); // milliseconds
						refreshSSOTokens();
						return;
					}

					if (data.timeout.data > 0) {
						openCountdownDialog();
					} else {
						logout('SESSION_TOKEN_EXPIRED_OR_NOT_FOUND');
					}
				},
				error: function(XMLHttpRequest, textStatus, errorThrown) { 
					if(errorHandlerCallback) errorHandlerCallback(XMLHttpRequest, textStatus, errorThrown);
				}
			});
		} else {
			logout('SESSION_TOKEN_NOT_FOUND');
		}

	};

	// This is called when the user clicks the button indicating they want to stay signed in - refreshes the session timeout
	var refreshSession = function(errorHandlerCallback){
        var timeoutToken = $.cookie(config.sessionManagementServiceToken);
        var separator = config.refreshSessionUrl.match(/\?/) ? '&' : '?';
		$.ajax({
			url      : config.refreshSessionUrl + separator + appendSessionCacheKey(),
			data     : {
					id : timeoutToken
				},
			cache    : false,
			dataType : 'json',
			success  : function( data ){
				pingServer();
			},
			error: function(XMLHttpRequest, textStatus, errorThrown) { 
				if(errorHandlerCallback) errorHandlerCallback(XMLHttpRequest, textStatus, errorThrown);
			}
		});
	};

    var appendSessionCacheKey = function(){
        var sessionCacheKey = window.sessionStorage.sessionCacheKey;
        var sessionCacheKeyAppend = isValidSessionCacheKey(sessionCacheKey) ? 'sessionCacheKey=' + sessionCacheKey : '';
        return sessionCacheKeyAppend;
    };

    isValidSessionCacheKey = function (sessionCacheKey) {
        var regex = /[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{16}:[a-zA-Z0-9]{8}/g;
        return typeof sessionCacheKey !== 'undefined' && sessionCacheKey.match(regex);
    };

	getCookie = function(cname) {
		var name = cname + "=";
		var decodedCookie = decodeURIComponent(document.cookie);
		var ca = decodedCookie.split(';');
		for(var i = 0; i <ca.length; i++) {
		  var c = ca[i];
		  while (c.charAt(0) == ' ') {
			c = c.substring(1);
		  }
		  if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		  }
		}
		return "";
	}

	getSessionStorageSessionCacheKey = function () {
		var sessionCacheKey = config.sessionCacheKeyDefault;
		if (typeof window.sessionStorage.sessionCacheKey !== 'undefined'){
			sessionCacheKey =  isValidSessionCacheKey(window.sessionStorage.sessionCacheKey) ? window.sessionStorage.sessionCacheKey : config.sessionCacheKeyDefault;
		}
		return sessionCacheKey;
	};

	isValidSessionCacheKey = function (sessionCacheKey) {
		var regex = /[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{16}:[a-zA-Z0-9]{8}/g;
		return typeof sessionCacheKey !== 'undefined' && sessionCacheKey.match(regex);
	};

	//for testing purposes
	var forceExpireSession = function(errorHandlerCallback){
		var timeoutToken = $.cookie(config.sessionManagementServiceToken);
		$.ajax({
			url      : config.sessionManagementServiceUrl,
			data     : {
				id : timeoutToken,
				expire: true,
			},
			cache    : false,
			dataType : 'json',
			success  : function( data ){
				pingServer();
			},
			error: function(XMLHttpRequest, textStatus, errorThrown) { 
				if(errorHandlerCallback) errorHandlerCallback(XMLHttpRequest, textStatus, errorThrown);
			}
		});
	};

	//constructor
	var initialize = function( ) {

		//
		$.widget( 'ux.countDownDialog', $.ui.dialog, {
			/*********************************************************************
				Additional functionality added to jquery ui.dialog to allow it to
				be used as a countdown timer to warn when the users session is 
				about to expire.
			*********************************************************************/
			timer        : '',  // holds the countdown time text for the dialog
			totalSeconds : 0,   // total seconds left on countdown
			timeout      : [ ], // contains list of setTimeout references so they can be cleared when needed
			clearTimer   : function( ){
				for( var i = 0; i < this.timeout.length; i++ ){
					window.clearTimeout( this.timeout.pop( ) );
				};
			},
			getTotalSeconds : function( ){
				return this.totalSeconds;
			},
			setTotalSeconds : function( seconds ){
				this.totalSeconds = seconds;
			},
			createTimer  : function( timerID, time ){
				this.timer        = $( timerID );
				this.totalSeconds = time;
				this.updateTimer( );
				
				// Maintain a reference to this "widget" instead of changing to window
				with( this ){ timeout.push( window.setTimeout( function( ){ tick( ) }, 1000 /* miliseconds */ ) ); };
			},
			updateTimer  : function( ){
				var seconds = this.totalSeconds;
				var minutes = Math.floor( seconds / 60 );
				seconds -= minutes * ( 60 );
				var timeStr = minutes + ':' + this.leadingZero( seconds );
				this.timer.html( timeStr );
			},
			tick         : function( ){
				this.timeout.pop( ); // remove the reference for this setTimeout from the array/stack
				
				if ( this.totalSeconds <= 0){
					// Clear previous state perstance before logging in
					if( ux.statePersistance )
						ux.statePersistance.clear();
					$('#message').html( 'You have been timed out due to inactivity.' );
					$('#staySignedIn').attr('disabled', 'disabled' ).addClass( 'ui-state-disabled' );
					logout('SESSION_EXPIRED_COUNTDOWN_REACHED_0');
					return;
				};
	
				this.totalSeconds -= 1;
				this.updateTimer( );
								
				// Maintain a reference to this "widget" instead of changing to window
				with( this ){ timeout.push( window.setTimeout( function( ){ tick( ) }, 1000 /* miliseconds */ ) ); };					
			},
			leadingZero  : function( time ){
				return (time < 10) ? '0' + time : + time;
			}				
		});
	
		//bootstrap
		$( document ).ready( function( ){
			
			//auto load timeout-dialog
			if($('#timeout-dialog').length === 0 ){
			    $.ajax({ type: "GET",   
			        url: config.templateUrl,
			        async: false,
			        success : function(htmlData) {
				    $( "body" ).append( htmlData );
			        }
			    });
			}
			$( '#timeout-dialog' ).countDownDialog({
				autoOpen      : false,
				height        : 300,
				width         : 450,
				modal         : true,
				position      : { my : 'center', at : 'center', of : window }, // places the center of the modal at the center of the window
				closeOnEscape : false,
				buttons : [{
					id    : 'staySignedIn',
					text  : 'Stay signed in',
					click : function( ){ 
				
						// Need to send a request back to server to refresh session, then reset timer
						$( '#timeout-dialog' ).countDownDialog( 'close' );
	
						// If there is still time left, refresh the session
						if ( $( '#timeout-dialog' ).countDownDialog( 'getTotalSeconds' ) > 0){
							refreshSession( );
							refreshSSOTokens();
						};
					}
				}, {
					id    : 'signOut',
					text  : 'Sign out now (don\'t save this page)',
					click : function( ){ 
						$( '#timeout-dialog' ).countDownDialog( 'setTotalSeconds', 0 );
						$( '#timeout-dialog' ).countDownDialog( 'close' ); 
					}
				}],
				open : function( event, ui ){
					/************************************************************
					 Hide the close button.
					
					"this" refers to the div the dialog is tied to, which gets 
					wrapped by the jquery ui with another div, its parentElement.
					
					Getting the firstChild of the parentElement will give you the
					title bar and the close button is the last child of the title 
					bar element.
					*************************************************************/
					$( this.parentElement.firstChild.lastChild ).hide( );
					
					$('#message').html( 'For security reasons, you are about to be logged out of Kinnser.  You have five minutes to renew credentials, or <span style="font-weight:bold;">you may lose data</span> and will have to log in again.' );
	
					// Start the countdown timer at 5 minutes
					$( '#timeout-dialog').countDownDialog( 'createTimer', '#timer', config.timeoutCountdown );
				},
				close : function( event, ui ){
					// Clear the timers
					$( '#timeout-dialog' ).countDownDialog( 'clearTimer' );
					
					// If the timer has reached zero, any call to close the dialog will send the user to the logout page.
					if ( $( '#timeout-dialog' ).countDownDialog( 'getTotalSeconds' ) <= 0){
						// Clear previous state perstance before logging in
						if( ux.statePersistance )
							ux.statePersistance.clear();
						
						logout('SESSION_EXPIRED_COUNTDOWN_REACHED_0');
					};
				}
			});
			
			pingServer( );
		});
	}

	initialize();

	return {
		openCountdownDialog: openCountdownDialog,
		pingServer: pingServer,
		refreshSession: refreshSession,
		forceExpireSession: forceExpireSession
	}

}

var HHHSessionMonitor = HHHSessionMonitorFactory(HHHSessionMonitorConfig);
