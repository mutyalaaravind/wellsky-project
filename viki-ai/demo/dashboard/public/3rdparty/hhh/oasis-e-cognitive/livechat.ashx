window["comm100main"] = (function (bundleJsName) {
	window["Comm100API"] = window["Comm100API"] || {};
	var api = window["Comm100API"];
	api.call = function (name) {
		return (new Function('return ' + name)).call();
	};
	api.chat_buttons = api.chat_buttons || [];
	window["brandingNameLowerCase"] = "comm100";
	window["brandingName"] = "Comm100";
	window.chatWindowInit && window.chatWindowInit();
	return function (main, standby, vue, others) {
		api.main = main;
        api.standby = standby;
		api.vue = vue;
		api.others = others;

		var iframe = document.createElement('iframe');
		iframe.style.display = 'none';
		iframe.id = "comm100-iframe";
		iframe.title = "comm100-iframe";
		document.body.appendChild(iframe);
		var innerDoc = iframe.contentDocument;
		innerDoc.open();
		var prefix = vue + '/visitorside/js/';
		try {
			var names = JSON.parse(bundleJsName);
			if (Array.isArray(names)) {
				var src = '';
				if (names.length >= 1) {
					for(var i = 0; i < names.length; i += 1) {
						src = src + '<script src="' + prefix + names[i] + '" defer type="module"></script>';
					}
				}
				innerDoc.write('<!doctype html><head>' + src + '</head><body></body>');
			}
		} catch(e) {
			var src = prefix + bundleJsName;
			innerDoc.write('<!doctype html><head><script src="' + src + '" async type="text/javascript" charset="utf-8"></script></head><body></body>');
		}
		innerDoc.close();
	};
}('["common.2b7b1091.js","vendor.f04a5f8d.js","bundle.13094a23.js"]'));
window["comm100main"]('https://chatserver12.comm100.io','https://chatserver12.comm100.io','https://entchatserver7.comm100.com');
delete window["comm100main"];