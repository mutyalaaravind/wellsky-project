$(window).on('load', function() {
	
  var notificationCountName = 'cc-notification-count';
  var messageCountElementName = 'cc-messageCount';
  
  function addMessageCountElement(count, previousCount){
	var messageCountElementId = `#${messageCountElementName}`;
	var formattedTotal = ` (${count})`;
		
	//add link if its not on the screen
	var messageCountElement = $(messageCountElementId);
	
	if (messageCountElement.length == 0 || count != previousCount){
		//Add count to link id="goto-carecoordination-item-link"
		
		$("#goto-CareCoordination,#goto-carecoordination-item-link").each(function(){
			var ccButton = $(this);
			
			if (ccButton.length == 0)
				return;
			
			if (messageCountElement.length > 0){
				messageCountElement.text( ` (${count})` )
			}else{
				var solidNotSpan = $("<span>", {id: messageCountElementName, "class": ""});
				solidNotSpan.text( formattedTotal );
				ccButton.append(solidNotSpan);
				messageCountElement = $(messageCountElementId);
			}
		
		});
				
	}
	
	return messageCountElement;
  }
  
  function addNotifcationDotToGoto(gotoObject){
	var gotoButton = gotoObject;
		
	if (gotoButton.length == 0)
		return;
	
	gotoButton.click(function(){ $("#cc-notcircle").remove(); });
	var notSpan = $("<span>", {id: "cc-notcircle", "class": "care-coordination-pulsating-circle"});
	
	if ($('#cc-notcircle').length == 0){
		gotoButton.prepend(notSpan);
	}
	
	return true;
  }
  
  function addNotifcationDotToCareCoordLink(){
	var dotName = 'cc-staticcircle';
	var ccDotElementId = `#${dotName}`;
	  
	$("#goto-CareCoordination,#goto-carecoordination-item-link").each(function(){
		var ccButton = $(this);
		
		ccButton.click(function(){ $(ccDotElementId).remove();  });
		var solidNotSpan = $("<span>", {id: dotName, "class": "care-coordination-pulsating-circle"});
		
		var staticCircle = $(ccDotElementId);
		
		if (staticCircle.length == 0){
			ccButton.append(solidNotSpan);
		}
	
	});  
	
	return true;
  }
  
  function showNotification(){
	var notifier = new Notifier({
            bell: {
                textColor: "#24292e",
                borderColor: "#c4c8cc",
                backgroundColor: "#fafbfc",
                progressColor: "#24292e",
                iconColor: "#24292e",
				borderRadius: "25px",
                icon: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\" class=\"bi bi-bell\" viewBox=\"0 0 16 16\"> <path d=\"M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2zM8 1.918l-.797.161A4.002 4.002 0 0 0 4 6c0 .628-.134 2.197-.459 3.742-.16.767-.376 1.566-.663 2.258h10.244c-.287-.692-.502-1.49-.663-2.258C12.134 8.197 12 6.628 12 6a4.002 4.002 0 0 0-3.203-3.92L8 1.917zM14.22 12c.223.447.481.801.78 1H1c.299-.199.557-.553.78-1C2.68 10.2 3 6.88 3 6c0-2.42 1.72-4.44 4.005-4.901a1 1 0 1 1 1.99 0A5.002 5.002 0 0 1 13 6c0 .88.32 4.2 1.22 6z\"/> </svg>"
            },
			position: 'top-right',
			direction: 'top'
        });
    
	notifier.notify("bell", " A new referral has been received!");
    
  }

    function processNotification(data){
		
		var messageCount = parseInt(localStorage.getItem(notificationCountName) || '0');
		var previousLastUpdate = getLastUpdated();
		
		var total = parseInt(data.notificationsCount);
		var curNotifications = data.notifications;
		var taskNotifications = curNotifications.find(x => x.hasOwnProperty('tasks'));
		var referralNotifications = curNotifications.find(x => x.hasOwnProperty('referrals'));
		
		if (isNaN(total)) 
			return;
		
		var formattedTotal = ` (${total})`;
				
		var messageCountElement = addMessageCountElement(total, previousTotal);
		
		var previousTotal = messageCount;
		window.localStorage.setItem(notificationCountName, total.toString());
		
		setLastUpdated( taskNotifications, referralNotifications );

		if (total <= 0)
			return;
		
		if (previousLastUpdate[taskUpdatedKey] >= taskNotifications.last_updated && previousLastUpdate[referralUpdatedKey] >= referralNotifications.last_updated)
			return;
		
		$(".menuBar > .menuButton:contains('Go To'),a#goto-dropdown.ng-binding").each(function(){
			
			addNotifcationDotToGoto($(this));
			addNotifcationDotToCareCoordLink();
			
		});
		showNotification();
	}
	
	var lastUpdatedKey = 'cc-last-updated';
	var taskUpdatedKey = 'task_last_updated';
	var referralUpdatedKey = 'referral_last_updated';
	
	function getEmptyLastUpdated(){
		var emptyObject = {};
		emptyObject[taskUpdatedKey] = 0;
		emptyObject[referralUpdatedKey] = 0;
		return emptyObject;
	}
	
	function getLastUpdated(){
		
		var retrievedObject = JSON.parse(window.localStorage.getItem(lastUpdatedKey) || JSON.stringify(getEmptyLastUpdated()));

		return retrievedObject;
		
	}

	function setLastUpdated(tasks, referrals){
		
		var lastUpdatedData = {};
		lastUpdatedData[taskUpdatedKey] = tasks.last_updated;
		lastUpdatedData[referralUpdatedKey] = referrals.last_updated;
		
		window.localStorage.setItem(lastUpdatedKey, JSON.stringify(lastUpdatedData));

		// Retrieve the object from storage
		var retrievedObject = window.localStorage.getItem(lastUpdatedKey);

	}
	
	const callNotificationApi = async () => {
      let url = `${window.location.origin}/rest/V1/CareCoordination/notifications`;
      let res = await fetch(url);
      let notData = await res.json();
      return notData;
    };
	
	const checkNotifications = async () => {
      let data = await callNotificationApi();
	  processNotification(data);
	  setTimeout( checkNotifications, 60000 );
	  return true;
    };
	
	checkNotifications();
  
});