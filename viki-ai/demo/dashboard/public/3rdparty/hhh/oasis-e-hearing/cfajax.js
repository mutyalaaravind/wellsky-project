/*ADOBE SYSTEMS INCORPORATED
Copyright 2012 Adobe Systems Incorporated
All Rights Reserved.

NOTICE:  Adobe permits you to use, modify, and distribute this file in accordance with the
terms of the Adobe license agreement accompanying it.  If you have received this file from a
source other than Adobe, then your use, modification, or distribution of it requires the prior
written permission of Adobe.*/
if(!String.prototype.startsWith){
Object.defineProperty(String.prototype,"startsWith",{value:function(_767,pos){
pos=!pos||pos<0?0:+pos;
return this.substring(pos,pos+_767.length)===_767;
}});
}
function cfinit(){
if(!window.ColdFusion){
ColdFusion={};
var $C=ColdFusion;
if(!$C.Ajax){
$C.Ajax={};
}
var $A=$C.Ajax;
if(!$C.AjaxProxy){
$C.AjaxProxy={};
}
var $X=$C.AjaxProxy;
if(!$C.Bind){
$C.Bind={};
}
var $B=$C.Bind;
if(!$C.Event){
$C.Event={};
}
var $E=$C.Event;
if(!$C.Log){
$C.Log={};
}
var $L=$C.Log;
if(!$C.Util){
$C.Util={};
}
var $U=$C.Util;
if(!$C.DOM){
$C.DOM={};
}
var $D=$C.DOM;
if(!$C.Spry){
$C.Spry={};
}
var $S=$C.Spry;
if(!$C.Pod){
$C.Pod={};
}
var $P=$C.Pod;
if(!$C.objectCache){
$C.objectCache={};
}
if(!$C.required){
$C.required={};
}
if(!$C.importedTags){
$C.importedTags=[];
}
if(!$C.requestCounter){
$C.requestCounter=0;
}
if(!$C.bindHandlerCache){
$C.bindHandlerCache={};
}
window._cf_loadingtexthtml="<div style=\"text-align: center;\">"+window._cf_loadingtexthtml+"&nbsp;"+CFMessage["loading"]+"</div>";
$C.globalErrorHandler=function(_773,_774){
if($L.isAvailable){
$L.error(_773,_774);
}
if($C.userGlobalErrorHandler){
$C.userGlobalErrorHandler(_773);
}
if(!$L.isAvailable&&!$C.userGlobalErrorHandler){
alert(_773+CFMessage["globalErrorHandler.alert"]);
}
};
$C.handleError=function(_775,_776,_777,_778,_779,_77a,_77b,_77c){
var msg=$L.format(_776,_778);
if(_775){
$L.error(msg,"http");
if(!_779){
_779=-1;
}
if(!_77a){
_77a=msg;
}
_775(_779,_77a,_77c);
}else{
if(_77b){
$L.error(msg,"http");
throw msg;
}else{
$C.globalErrorHandler(msg,_777);
}
}
};
$C.setGlobalErrorHandler=function(_77e){
$C.userGlobalErrorHandler=_77e;
};
$A.createXMLHttpRequest=function(){
try{
return new XMLHttpRequest();
}
catch(e){
}
var _77f=["Microsoft.XMLHTTP","MSXML2.XMLHTTP.5.0","MSXML2.XMLHTTP.4.0","MSXML2.XMLHTTP.3.0","MSXML2.XMLHTTP"];
for(var i=0;i<_77f.length;i++){
try{
return new ActiveXObject(_77f[i]);
}
catch(e){
}
}
return false;
};
$A.isRequestError=function(req){
return ((req.status!=0&&req.status!=200)||req.getResponseHeader("server-error"));
};
$A.sendMessage=function(url,_783,_784,_785,_786,_787,_788){
var req=$A.createXMLHttpRequest();
if(!_783){
_783="GET";
}
if(_785&&_786){
req.onreadystatechange=function(){
$A.callback(req,_786,_787);
};
}
if(_784){
_784+="&_cf_nodebug=true&_cf_nocache=true";
}else{
_784="_cf_nodebug=true&_cf_nocache=true";
}
if(window._cf_clientid){
_784+="&_cf_clientid="+_cf_clientid;
}
if(_783=="GET"){
if(_784){
_784+="&_cf_rc="+($C.requestCounter++);
if(url.indexOf("?")==-1){
url+="?"+_784;
}else{
url+="&"+_784;
}
}
$L.info("ajax.sendmessage.get","http",[url]);
req.open(_783,url,_785);
req.send(null);
}else{
$L.info("ajax.sendmessage.post","http",[url,_784]);
req.open(_783,url,_785);
req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
if(_784){
req.send(_784);
}else{
req.send(null);
}
}
if(!_785){
while(req.readyState!=4){
}
if($A.isRequestError(req)){
$C.handleError(null,"ajax.sendmessage.error","http",[req.status,req.statusText],req.status,req.statusText,_788);
}else{
return req;
}
}
};
$A.callback=function(req,_78b,_78c){
if(req.readyState!=4){
return;
}
req.onreadystatechange=new Function;
_78b(req,_78c);
};
$A.submitForm=function(_78d,url,_78f,_790,_791,_792){
var _793=$C.getFormQueryString(_78d);
if(_793==-1){
$C.handleError(_790,"ajax.submitform.formnotfound","http",[_78d],-1,null,true);
return;
}
if(!_791){
_791="POST";
}
_792=!(_792===false);
var _794=function(req){
$A.submitForm.callback(req,_78d,_78f,_790);
};
$L.info("ajax.submitform.submitting","http",[_78d]);
var _796=$A.sendMessage(url,_791,_793,_792,_794);
if(!_792){
$L.info("ajax.submitform.success","http",[_78d]);
return _796.responseText;
}
};
$A.submitForm.callback=function(req,_798,_799,_79a){
if($A.isRequestError(req)){
$C.handleError(_79a,"ajax.submitform.error","http",[req.status,_798,req.statusText],req.status,req.statusText);
}else{
$L.info("ajax.submitform.success","http",[_798]);
if(_799){
_799(req.responseText);
}
}
};
$C.empty=function(){
};
$C.setSubmitClicked=function(_79b,_79c){
var el=$D.getElement(_79c,_79b);
el.cfinputbutton=true;
$C.setClickedProperty=function(){
el.clicked=true;
};
$E.addListener(el,"click",$C.setClickedProperty);
};
$C.getFormQueryString=function(_79e,_79f){
var _7a0;
if(typeof _79e=="string"){
_7a0=(document.getElementById(_79e)||document.forms[_79e]);
}else{
if(typeof _79e=="object"){
_7a0=_79e;
}
}
if(!_7a0||null==_7a0.elements){
return -1;
}
var _7a1,elementName,elementValue,elementDisabled;
var _7a2=false;
var _7a3=(_79f)?{}:"";
for(var i=0;i<_7a0.elements.length;i++){
_7a1=_7a0.elements[i];
elementDisabled=_7a1.disabled;
elementName=_7a1.name;
elementValue=_7a1.value;
if(_7a1.id&&_7a1.id.startsWith("cf_textarea")){
var _7a5=CKEDITOR.instances;
if(_7a5){
for(ta in _7a5){
if(_7a5[ta].getData){
elementValue=_7a5[ta].getData();
break;
}
}
}
}
if(!elementDisabled&&elementName){
switch(_7a1.type){
case "select-one":
case "select-multiple":
for(var j=0;j<_7a1.options.length;j++){
if(_7a1.options[j].selected){
if(window.ActiveXObject){
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,_7a1.options[j].attributes["value"].specified?_7a1.options[j].value:_7a1.options[j].text);
}else{
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,_7a1.options[j].hasAttribute("value")?_7a1.options[j].value:_7a1.options[j].text);
}
}
}
break;
case "radio":
case "checkbox":
if(_7a1.checked){
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,elementValue);
}
break;
case "file":
case undefined:
case "reset":
break;
case "button":
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,elementValue);
break;
case "submit":
if(_7a1.cfinputbutton){
if(_7a2==false&&_7a1.clicked){
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,elementValue);
_7a2=true;
}
}else{
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,elementValue);
}
break;
case "textarea":
var _7a7;
if(window.FCKeditorAPI&&(_7a7=$C.objectCache[elementName])&&_7a7.richtextid){
var _7a8=FCKeditorAPI.GetInstance(_7a7.richtextid);
if(_7a8){
elementValue=_7a8.GetXHTML();
}
}
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,elementValue);
break;
default:
_7a3=$C.getFormQueryString.processFormData(_7a3,_79f,elementName,elementValue);
break;
}
}
}
if(!_79f){
_7a3=_7a3.substr(0,_7a3.length-1);
}
return _7a3;
};
$C.getFormQueryString.processFormData=function(_7a9,_7aa,_7ab,_7ac){
if(_7aa){
if(_7a9[_7ab]){
_7a9[_7ab]+=","+_7ac;
}else{
_7a9[_7ab]=_7ac;
}
}else{
_7a9+=encodeURIComponent(_7ab)+"="+encodeURIComponent(_7ac)+"&";
}
return _7a9;
};
$A.importTag=function(_7ad){
$C.importedTags.push(_7ad);
};
$A.checkImportedTag=function(_7ae){
var _7af=false;
for(var i=0;i<$C.importedTags.length;i++){
if($C.importedTags[i]==_7ae){
_7af=true;
break;
}
}
if(!_7af){
$C.handleError(null,"ajax.checkimportedtag.error","widget",[_7ae]);
}
};
$C.getElementValue=function(_7b1,_7b2,_7b3){
if(!_7b1){
$C.handleError(null,"getelementvalue.noelementname","bind",null,null,null,true);
return;
}
if(!_7b3){
_7b3="value";
}
var _7b4=$B.getBindElementValue(_7b1,_7b2,_7b3);
if(typeof (_7b4)=="undefined"){
_7b4=null;
}
if(_7b4==null){
$C.handleError(null,"getelementvalue.elnotfound","bind",[_7b1,_7b3],null,null,true);
return;
}
return _7b4;
};
$B.getBindElementValue=function(_7b5,_7b6,_7b7,_7b8,_7b9){
var _7ba="";
if(window[_7b5]){
var _7bb=eval(_7b5);
if(_7bb&&_7bb._cf_getAttribute){
_7ba=_7bb._cf_getAttribute(_7b7);
return _7ba;
}
}
var _7bc=$C.objectCache[_7b5];
if(_7bc&&_7bc._cf_getAttribute){
_7ba=_7bc._cf_getAttribute(_7b7);
return _7ba;
}
var el=$D.getElement(_7b5,_7b6);
var _7be=(el&&((!el.length&&el.length!=0)||(el.length&&el.length>0)||el.tagName=="SELECT"));
if(!_7be&&!_7b9){
$C.handleError(null,"bind.getbindelementvalue.elnotfound","bind",[_7b5]);
return null;
}
if(el.tagName!="SELECT"){
if(el.length>1){
var _7bf=true;
for(var i=0;i<el.length;i++){
var _7c1=(el[i].getAttribute("type")=="radio"||el[i].getAttribute("type")=="checkbox");
if(!_7c1||(_7c1&&el[i].checked)){
if(!_7bf){
_7ba+=",";
}
_7ba+=$B.getBindElementValue.extract(el[i],_7b7);
_7bf=false;
}
}
}else{
_7ba=$B.getBindElementValue.extract(el,_7b7);
}
}else{
var _7bf=true;
for(var i=0;i<el.options.length;i++){
if(el.options[i].selected){
if(!_7bf){
_7ba+=",";
}
_7ba+=$B.getBindElementValue.extract(el.options[i],_7b7);
_7bf=false;
}
}
}
if(typeof (_7ba)=="object"){
$C.handleError(null,"bind.getbindelementvalue.simplevalrequired","bind",[_7b5,_7b7]);
return null;
}
if(_7b8&&$C.required[_7b5]&&_7ba.length==0){
return null;
}
return _7ba;
};
$B.getBindElementValue.extract=function(el,_7c3){
var _7c4=el[_7c3];
if((_7c4==null||typeof (_7c4)=="undefined")&&el.getAttribute){
_7c4=el.getAttribute(_7c3);
}
return _7c4;
};
$L.init=function(){
if(window.YAHOO&&YAHOO.widget&&YAHOO.widget.Logger){
YAHOO.widget.Logger.categories=[CFMessage["debug"],CFMessage["info"],CFMessage["error"],CFMessage["window"]];
YAHOO.widget.LogReader.prototype.formatMsg=function(_7c5){
var _7c6=_7c5.category;
return "<p>"+"<span class='"+_7c6+"'>"+_7c6+"</span>:<i>"+_7c5.source+"</i>: "+_7c5.msg+"</p>";
};
var _7c7=new YAHOO.widget.LogReader(null,{width:"30em",fontSize:"100%"});
_7c7.setTitle(CFMessage["log.title"]||"ColdFusion AJAX Logger");
_7c7._btnCollapse.value=CFMessage["log.collapse"]||"Collapse";
_7c7._btnPause.value=CFMessage["log.pause"]||"Pause";
_7c7._btnClear.value=CFMessage["log.clear"]||"Clear";
$L.isAvailable=true;
}
};
$L.log=function(_7c8,_7c9,_7ca,_7cb){
if(!$L.isAvailable){
return;
}
if(!_7ca){
_7ca="global";
}
_7ca=CFMessage[_7ca]||_7ca;
_7c9=CFMessage[_7c9]||_7c9;
_7c8=$L.format(_7c8,_7cb);
YAHOO.log(_7c8,_7c9,_7ca);
};
$L.format=function(code,_7cd){
var msg=CFMessage[code]||code;
if(_7cd){
for(i=0;i<_7cd.length;i++){
if(!_7cd[i].length){
_7cd[i]="";
}
var _7cf="{"+i+"}";
msg=msg.replace(_7cf,_7cd[i]);
}
}
return msg;
};
$L.debug=function(_7d0,_7d1,_7d2){
$L.log(_7d0,"debug",_7d1,_7d2);
};
$L.info=function(_7d3,_7d4,_7d5){
$L.log(_7d3,"info",_7d4,_7d5);
};
$L.error=function(_7d6,_7d7,_7d8){
$L.log(_7d6,"error",_7d7,_7d8);
};
$L.dump=function(_7d9,_7da){
if($L.isAvailable){
var dump=(/string|number|undefined|boolean/.test(typeof (_7d9))||_7d9==null)?_7d9:recurse(_7d9,typeof _7d9,true);
$L.debug(dump,_7da);
}
};
$X.invoke=function(_7dc,_7dd,_7de,_7df,_7e0){
return $X.invokeInternal(_7dc,_7dd,_7de,_7df,_7e0,false,null,null);
};
$X.invokeInternal=function(_7e1,_7e2,_7e3,_7e4,_7e5,_7e6,_7e7,_7e8){
var _7e9="method="+_7e2+"&_cf_ajaxproxytoken="+_7e3;
if(_7e6){
_7e9+="&_cfclient="+"true";
var _7ea=$X.JSON.encodeInternal(_7e1._variables,_7e6);
_7e9+="&_variables="+encodeURIComponent(_7ea);
var _7eb=$X.JSON.encodeInternal(_7e1._metadata,_7e6);
_7e9+="&_metadata="+encodeURIComponent(_7eb);
}
var _7ec=_7e1.returnFormat||"json";
_7e9+="&returnFormat="+_7ec;
if(_7e1.queryFormat){
_7e9+="&queryFormat="+_7e1.queryFormat;
}
if(_7e1.formId){
var _7ed=$C.getFormQueryString(_7e1.formId,true);
if(_7e4!=null){
for(prop in _7ed){
_7e4[prop]=_7ed[prop];
}
}else{
_7e4=_7ed;
}
_7e1.formId=null;
}
var _7ee="";
if(_7e4!=null){
_7ee=$X.JSON.encodeInternal(_7e4,_7e6);
_7e9+="&argumentCollection="+encodeURIComponent(_7ee);
}
$L.info("ajaxproxy.invoke.invoking","http",[_7e1.cfcPath,_7e2,_7ee]);
if(_7e1.callHandler){
_7e1.callHandler.call(null,_7e1.callHandlerParams,_7e1.cfcPath,_7e9);
return;
}
var _7ef;
var _7f0=_7e1.async;
if(_7e7!=null){
_7f0=true;
_7ef=function(req){
$X.callbackOp(req,_7e1,_7e5,_7e7,_7e8);
};
}else{
if(_7e1.async){
_7ef=function(req){
$X.callback(req,_7e1,_7e5);
};
}
}
var req=$A.sendMessage(_7e1.cfcPath,_7e1.httpMethod,_7e9,_7f0,_7ef,null,true);
if(!_7f0){
return $X.processResponse(req,_7e1);
}
};
$X.callback=function(req,_7f5,_7f6){
if($A.isRequestError(req)){
$C.handleError(_7f5.errorHandler,"ajaxproxy.invoke.error","http",[req.status,_7f5.cfcPath,req.statusText],req.status,req.statusText,false,_7f6);
}else{
if(_7f5.callbackHandler){
var _7f7=$X.processResponse(req,_7f5);
_7f5.callbackHandler(_7f7,_7f6);
}
}
};
$X.callbackOp=function(req,_7f9,_7fa,_7fb,_7fc){
if($A.isRequestError(req)){
var _7fd=_7f9.errorHandler;
if(_7fc!=null){
_7fd=_7fc;
}
$C.handleError(_7fd,"ajaxproxy.invoke.error","http",[req.status,_7f9.cfcPath,req.statusText],req.status,req.statusText,false,_7fa);
}else{
if(_7fb){
var _7fe=$X.processResponse(req,_7f9);
_7fb(_7fe,_7fa);
}
}
};
$X.processResponse=function(req,_800){
var _801=true;
for(var i=0;i<req.responseText.length;i++){
var c=req.responseText.charAt(i);
_801=(c==" "||c=="\n"||c=="\t"||c=="\r");
if(!_801){
break;
}
}
var _804=(req.responseXML&&req.responseXML.childNodes.length>0);
var _805=_804?"[XML Document]":req.responseText;
$L.info("ajaxproxy.invoke.response","http",[_805]);
var _806;
var _807=_800.returnFormat||"json";
if(_807=="json"){
try{
_806=_801?null:$X.JSON.decode(req.responseText);
}
catch(e){
if(typeof _800._metadata!=="undefined"&&_800._metadata.servercfc&&typeof req.responseText==="string"){
_806=req.responseText;
}else{
throw e;
}
}
}else{
_806=_804?req.responseXML:(_801?null:req.responseText);
}
return _806;
};
$X.init=function(_808,_809,_80a){
if(typeof _80a==="undefined"){
_80a=false;
}
var _80b=_809;
if(!_80a){
var _80c=_809.split(".");
var ns=self;
for(i=0;i<_80c.length-1;i++){
if(_80c[i].length){
ns[_80c[i]]=ns[_80c[i]]||{};
ns=ns[_80c[i]];
}
}
var _80e=_80c[_80c.length-1];
if(ns[_80e]){
return ns[_80e];
}
ns[_80e]=function(){
this.httpMethod="GET";
this.async=false;
this.callbackHandler=null;
this.errorHandler=null;
this.formId=null;
};
_80b=ns[_80e].prototype;
}else{
_80b.httpMethod="GET";
_80b.async=false;
_80b.callbackHandler=null;
_80b.errorHandler=null;
_80b.formId=null;
}
_80b.cfcPath=_808;
_80b.setHTTPMethod=function(_80f){
if(_80f){
_80f=_80f.toUpperCase();
}
if(_80f!="GET"&&_80f!="POST"){
$C.handleError(null,"ajaxproxy.sethttpmethod.invalidmethod","http",[_80f],null,null,true);
}
this.httpMethod=_80f;
};
_80b.setSyncMode=function(){
this.async=false;
};
_80b.setAsyncMode=function(){
this.async=true;
};
_80b.setCallbackHandler=function(fn){
this.callbackHandler=fn;
this.setAsyncMode();
};
_80b.setErrorHandler=function(fn){
this.errorHandler=fn;
this.setAsyncMode();
};
_80b.setForm=function(fn){
this.formId=fn;
};
_80b.setQueryFormat=function(_813){
if(_813){
_813=_813.toLowerCase();
}
if(!_813||(_813!="column"&&_813!="row"&&_813!="struct")){
$C.handleError(null,"ajaxproxy.setqueryformat.invalidformat","http",[_813],null,null,true);
}
this.queryFormat=_813;
};
_80b.setReturnFormat=function(_814){
if(_814){
_814=_814.toLowerCase();
}
if(!_814||(_814!="plain"&&_814!="json"&&_814!="wddx")){
$C.handleError(null,"ajaxproxy.setreturnformat.invalidformat","http",[_814],null,null,true);
}
this.returnFormat=_814;
};
$L.info("ajaxproxy.init.created","http",[_808]);
if(_80a){
return _80b;
}else{
return ns[_80e];
}
};
$U.isWhitespace=function(s){
var _816=true;
for(var i=0;i<s.length;i++){
var c=s.charAt(i);
_816=(c==" "||c=="\n"||c=="\t"||c=="\r");
if(!_816){
break;
}
}
return _816;
};
$U.getFirstNonWhitespaceIndex=function(s){
var _81a=true;
for(var i=0;i<s.length;i++){
var c=s.charAt(i);
_81a=(c==" "||c=="\n"||c=="\t"||c=="\r");
if(!_81a){
break;
}
}
return i;
};
$C.trim=function(_81d){
return _81d.replace(/^\s+|\s+$/g,"");
};
$U.isInteger=function(n){
var _81f=true;
if(typeof (n)=="number"){
_81f=(n>=0);
}else{
for(i=0;i<n.length;i++){
if($U.isInteger.numberChars.indexOf(n.charAt(i))==-1){
_81f=false;
break;
}
}
}
return _81f;
};
$U.isInteger.numberChars="0123456789";
$U.isArray=function(a){
return (typeof (a.length)=="number"&&!a.toUpperCase);
};
$U.isBoolean=function(b){
if(b===true||b===false){
return true;
}else{
if(b.toLowerCase){
b=b.toLowerCase();
return (b==$U.isBoolean.trueChars||b==$U.isBoolean.falseChars);
}else{
return false;
}
}
};
$U.isBoolean.trueChars="true";
$U.isBoolean.falseChars="false";
$U.castBoolean=function(b){
if(b===true){
return true;
}else{
if(b===false){
return false;
}else{
if(b.toLowerCase){
b=b.toLowerCase();
if(b==$U.isBoolean.trueChars){
return true;
}else{
if(b==$U.isBoolean.falseChars){
return false;
}else{
return false;
}
}
}else{
return false;
}
}
}
};
$U.checkQuery=function(o){
var _824=null;
if(o&&o.COLUMNS&&$U.isArray(o.COLUMNS)&&o.DATA&&$U.isArray(o.DATA)&&(o.DATA.length==0||(o.DATA.length>0&&$U.isArray(o.DATA[0])))){
_824="row";
}else{
if(o&&o.COLUMNS&&$U.isArray(o.COLUMNS)&&o.ROWCOUNT&&$U.isInteger(o.ROWCOUNT)&&o.DATA){
_824="col";
for(var i=0;i<o.COLUMNS.length;i++){
var _826=o.DATA[o.COLUMNS[i]];
if(!_826||!$U.isArray(_826)){
_824=null;
break;
}
}
}
}
return _824;
};
$X.JSON=new function(){
var _827={}.hasOwnProperty?true:false;
var _828=/^("(\\.|[^"\\\n\r])*?"|[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t])+?$/;
var pad=function(n){
return n<10?"0"+n:n;
};
var m={"\b":"\\b","\t":"\\t","\n":"\\n","\f":"\\f","\r":"\\r","\"":"\\\"","\\":"\\\\"};
var _82c=function(s){
if(/["\\\x00-\x1f]/.test(s)){
return "\""+s.replace(/([\x00-\x1f\\"])/g,function(a,b){
var c=m[b];
if(c){
return c;
}
c=b.charCodeAt();
return "\\u00"+Math.floor(c/16).toString(16)+(c%16).toString(16);
})+"\"";
}
return "\""+s+"\"";
};
var _831=function(o){
var a=["["],b,i,l=o.length,v;
for(i=0;i<l;i+=1){
v=o[i];
switch(typeof v){
case "undefined":
case "function":
case "unknown":
break;
default:
if(b){
a.push(",");
}
a.push(v===null?"null":$X.JSON.encode(v));
b=true;
}
}
a.push("]");
return a.join("");
};
var _834=function(o){
return "\""+o.getFullYear()+"-"+pad(o.getMonth()+1)+"-"+pad(o.getDate())+"T"+pad(o.getHours())+":"+pad(o.getMinutes())+":"+pad(o.getSeconds())+"\"";
};
this.encode=function(o){
return this.encodeInternal(o,false);
};
this.encodeInternal=function(o,cfc){
if(typeof o=="undefined"||o===null){
return "null";
}else{
if(o instanceof Array){
return _831(o);
}else{
if(o instanceof Date){
if(cfc){
return this.encodeInternal({_date_:o.getTime()},cfc);
}
return _834(o);
}else{
if(typeof o=="string"){
return _82c(o);
}else{
if(typeof o=="number"){
return isFinite(o)?String(o):"null";
}else{
if(typeof o=="boolean"){
return String(o);
}else{
if(cfc&&typeof o=="object"&&typeof o._metadata!=="undefined"){
return "{\"_metadata\":"+this.encodeInternal(o._metadata,false)+",\"_variables\":"+this.encodeInternal(o._variables,cfc)+"}";
}else{
var a=["{"],b,i,v;
for(var i in o){
if(!_827||o.hasOwnProperty(i)){
v=o[i];
switch(typeof v){
case "undefined":
case "function":
case "unknown":
break;
default:
if(b){
a.push(",");
}
a.push(this.encodeInternal(i,cfc),":",v===null?"null":this.encodeInternal(v,cfc));
b=true;
}
}
}
a.push("}");
return a.join("");
}
}
}
}
}
}
}
};
this.decode=function(json){
if(typeof json=="object"){
return json;
}
if($U.isWhitespace(json)){
return null;
}
var _83c=$U.getFirstNonWhitespaceIndex(json);
if(_83c>0){
json=json.slice(_83c);
}
if(window._cf_jsonprefix&&json.indexOf(_cf_jsonprefix)==0){
json=json.slice(_cf_jsonprefix.length);
}
try{
if(_828.test(json)){
return JSON.parse(json);
}
}
catch(e){
}
throw new SyntaxError("parseJSON");
};
}();
if(!$C.JSON){
$C.JSON={};
}
$C.JSON.encode=$X.JSON.encode;
$C.JSON.encodeInternal=$X.JSON.encodeInternal;
$C.JSON.decode=$X.JSON.decode;
$C.navigate=function(url,_83e,_83f,_840,_841,_842){
if(url==null){
$C.handleError(_840,"navigate.urlrequired","widget");
return;
}
if(_841){
_841=_841.toUpperCase();
if(_841!="GET"&&_841!="POST"){
$C.handleError(null,"navigate.invalidhttpmethod","http",[_841],null,null,true);
}
}else{
_841="GET";
}
var _843;
if(_842){
_843=$C.getFormQueryString(_842);
if(_843==-1){
$C.handleError(null,"navigate.formnotfound","http",[_842],null,null,true);
}
}
if(_83e==null){
if(_843){
if(url.indexOf("?")==-1){
url+="?"+_843;
}else{
url+="&"+_843;
}
}
$L.info("navigate.towindow","widget",[url]);
window.location.replace(url);
return;
}
$L.info("navigate.tocontainer","widget",[url,_83e]);
var obj=$C.objectCache[_83e];
if(obj!=null){
if(typeof (obj._cf_body)!="undefined"&&obj._cf_body!=null){
_83e=obj._cf_body;
}
}
$A.replaceHTML(_83e,url,_841,_843,_83f,_840);
};
$A.checkForm=function(_845,_846,_847,_848,_849){
var _84a=_846.call(null,_845);
if(_84a==false){
return false;
}
var _84b=$C.getFormQueryString(_845);
$L.info("ajax.submitform.submitting","http",[_845.name]);
$A.replaceHTML(_847,_845.action,_845.method,_84b,_848,_849);
return false;
};
$A.replaceHTML=function(_84c,url,_84e,_84f,_850,_851){
var _852=document.getElementById(_84c);
if(!_852){
$C.handleError(_851,"ajax.replacehtml.elnotfound","http",[_84c]);
return;
}
var _853="_cf_containerId="+encodeURIComponent(_84c);
_84f=(_84f)?_84f+"&"+_853:_853;
$L.info("ajax.replacehtml.replacing","http",[_84c,url,_84f]);
if(_cf_loadingtexthtml){
try{
_852.innerHTML=_cf_loadingtexthtml;
}
catch(e){
}
}
var _854=function(req,_856){
var _857=false;
if($A.isRequestError(req)){
$C.handleError(_851,"ajax.replacehtml.error","http",[req.status,_856.id,req.statusText],req.status,req.statusText);
_857=true;
}
var _858=new $E.CustomEvent("onReplaceHTML",_856);
var _859=new $E.CustomEvent("onReplaceHTMLUser",_856);
$E.loadEvents[_856.id]={system:_858,user:_859};
if(req.responseText.search(/<script/i)!=-1){
try{
_856.innerHTML="";
}
catch(e){
}
$A.replaceHTML.processResponseText(req.responseText,_856,_851);
}else{
try{
_856.innerHTML=req.responseText;
$A.updateLayouttab(_856);
if(_84f.indexOf("window-id")>-1){
var q=_84f.substring(_84f.indexOf("window-id")+10,_84f.indexOf("&"));
var cmp=Ext.getCmp(q);
if(cmp){
cmp.update(_856.innerHTML);
}
}
}
catch(e){
}
}
$E.loadEvents[_856.id]=null;
_858.fire();
_858.unsubscribe();
_859.fire();
_859.unsubscribe();
$L.info("ajax.replacehtml.success","http",[_856.id]);
if(_850&&!_857){
_850();
}
};
try{
$A.sendMessage(url,_84e,_84f,true,_854,_852);
}
catch(e){
try{
_852.innerHTML=$L.format(CFMessage["ajax.replacehtml.connectionerrordisplay"],[url,e]);
}
catch(e){
}
$C.handleError(_851,"ajax.replacehtml.connectionerror","http",[_84c,url,e]);
}
};
$A.replaceHTML.processResponseText=function(text,_85d,_85e){
var pos=0;
var _860=0;
var _861=0;
_85d._cf_innerHTML="";
while(pos<text.length){
var _862=text.indexOf("<s",pos);
if(_862==-1){
_862=text.indexOf("<S",pos);
}
if(_862==-1){
break;
}
pos=_862;
var _863=true;
var _864=$A.replaceHTML.processResponseText.scriptTagChars;
for(var i=1;i<_864.length;i++){
var _866=pos+i+1;
if(_866>text.length){
break;
}
var _867=text.charAt(_866);
if(_864[i][0]!=_867&&_864[i][1]!=_867){
pos+=i+1;
_863=false;
break;
}
}
if(!_863){
continue;
}
var _868=text.substring(_860,pos);
if(_868){
_85d._cf_innerHTML+=_868;
}
var _869=text.indexOf(">",pos)+1;
if(_869==0){
pos++;
continue;
}else{
pos+=7;
}
var _86a=_869;
while(_86a<text.length&&_86a!=-1){
_86a=text.indexOf("</s",_86a);
if(_86a==-1){
_86a=text.indexOf("</S",_86a);
}
if(_86a!=-1){
_863=true;
for(var i=1;i<_864.length;i++){
var _866=_86a+2+i;
if(_866>text.length){
break;
}
var _867=text.charAt(_866);
if(_864[i][0]!=_867&&_864[i][1]!=_867){
_86a=_866;
_863=false;
break;
}
}
if(_863){
break;
}
}
}
if(_86a!=-1){
var _86b=text.substring(_869,_86a);
var _86c=_86b.indexOf("<!--");
if(_86c!=-1){
_86b=_86b.substring(_86c+4);
}
var _86d=_86b.lastIndexOf("//-->");
if(_86d!=-1){
_86b=_86b.substring(0,_86d-1);
}
if(_86b.indexOf("document.write")!=-1||_86b.indexOf("CF_RunContent")!=-1){
if(_86b.indexOf("CF_RunContent")!=-1){
_86b=_86b.replace("CF_RunContent","document.write");
}
_86b="var _cfDomNode = document.getElementById('"+_85d.id+"'); var _cfBuffer='';"+"if (!document._cf_write)"+"{document._cf_write = document.write;"+"document.write = function(str){if (_cfBuffer!=null){_cfBuffer+=str;}else{document._cf_write(str);}};};"+_86b+";_cfDomNode._cf_innerHTML += _cfBuffer; _cfBuffer=null;";
}
try{
eval(_86b);
}
catch(ex){
$C.handleError(_85e,"ajax.replacehtml.jserror","http",[_85d.id,ex]);
}
}
_862=text.indexOf(">",_86a)+1;
if(_862==0){
_861=_86a+1;
break;
}
_861=_862;
pos=_862;
_860=_862;
}
if(_861<text.length-1){
var _868=text.substring(_861,text.length);
if(_868){
_85d._cf_innerHTML+=_868;
}
}
try{
_85d.innerHTML=_85d._cf_innerHTML;
$A.updateLayouttab(_85d);
}
catch(e){
}
_85d._cf_innerHTML="";
};
$A.updateLayouttab=function(_86e){
var _86f=_86e.id;
var s=_86f.substr(13,_86f.length);
var cmp=Ext.getCmp(s);
var _872=_86e.innerHTML;
var _873=document.getElementById(_86f);
var html=_873.innerHTML;
if(cmp){
cmp.update("<div id="+_86e.id+">"+html+"</div>");
}
var _873=document.getElementById(_86f);
if(_873){
}
};
$A.replaceHTML.processResponseText.scriptTagChars=[["s","S"],["c","C"],["r","R"],["i","I"],["p","P"],["t","T"]];
$D.getElement=function(_875,_876){
var _877=function(_878){
return (_878.name==_875||_878.id==_875);
};
var _879=$D.getElementsBy(_877,null,_876);
if(_879.length==1){
return _879[0];
}else{
return _879;
}
};
$D.getElementsBy=function(_87a,tag,root){
tag=tag||"*";
var _87d=[];
if(root){
root=$D.get(root);
if(!root){
return _87d;
}
}else{
root=document;
}
var _87e=root.getElementsByTagName(tag);
if(!_87e.length&&(tag=="*"&&root.all)){
_87e=root.all;
}
for(var i=0,len=_87e.length;i<len;++i){
if(_87a(_87e[i])){
_87d[_87d.length]=_87e[i];
}
}
return _87d;
};
$D.get=function(el){
if(!el){
return null;
}
if(typeof el!="string"&&!(el instanceof Array)){
return el;
}
if(typeof el=="string"){
return document.getElementById(el);
}else{
var _881=[];
for(var i=0,len=el.length;i<len;++i){
_881[_881.length]=$D.get(el[i]);
}
return _881;
}
return null;
};
$E.loadEvents={};
$E.CustomEvent=function(_883,_884){
return {name:_883,domNode:_884,subs:[],subscribe:function(func,_886){
var dup=false;
for(var i=0;i<this.subs.length;i++){
var sub=this.subs[i];
if(sub.f==func&&sub.p==_886){
dup=true;
break;
}
}
if(!dup){
this.subs.push({f:func,p:_886});
}
},fire:function(){
for(var i=0;i<this.subs.length;i++){
var sub=this.subs[i];
sub.f.call(null,this,sub.p);
}
},unsubscribe:function(){
this.subscribers=[];
}};
};
$E.windowLoadImpEvent=new $E.CustomEvent("cfWindowLoadImp");
$E.windowLoadEvent=new $E.CustomEvent("cfWindowLoad");
$E.windowLoadUserEvent=new $E.CustomEvent("cfWindowLoadUser");
$E.listeners=[];
$E.addListener=function(el,ev,fn,_88f){
var l={el:el,ev:ev,fn:fn,params:_88f};
$E.listeners.push(l);
var _891=function(e){
if(!e){
var e=window.event;
}
fn.call(null,e,_88f);
};
if(el.addEventListener){
window.addEventListener("load",function(){
el.addEventListener(ev,_891,false);
});
el.addEventListener(ev,_891,false);
return true;
}else{
if(el.attachEvent){
el.attachEvent("on"+ev,_891);
return true;
}else{
return false;
}
}
};
$E.isListener=function(el,ev,fn,_896){
var _897=false;
var ls=$E.listeners;
for(var i=0;i<ls.length;i++){
if(ls[i].el==el&&ls[i].ev==ev&&ls[i].fn==fn&&ls[i].params==_896){
_897=true;
break;
}
}
return _897;
};
$E.callBindHandlers=function(id,_89b,ev){
var el=document.getElementById(id);
if(!el){
return;
}
var ls=$E.listeners;
for(var i=0;i<ls.length;i++){
if(ls[i].el==el&&ls[i].ev==ev&&ls[i].fn._cf_bindhandler){
ls[i].fn.call(null,null,ls[i].params);
}
}
};
$E.registerOnLoad=function(func,_8a1,_8a2,user){
if($E.registerOnLoad.windowLoaded){
if(_8a1&&_8a1._cf_containerId&&$E.loadEvents[_8a1._cf_containerId]){
if(user){
$E.loadEvents[_8a1._cf_containerId].user.subscribe(func,_8a1);
}else{
$E.loadEvents[_8a1._cf_containerId].system.subscribe(func,_8a1);
}
}else{
func.call(null,null,_8a1);
}
}else{
if(user){
$E.windowLoadUserEvent.subscribe(func,_8a1);
}else{
if(_8a2){
$E.windowLoadImpEvent.subscribe(func,_8a1);
}else{
$E.windowLoadEvent.subscribe(func,_8a1);
}
}
}
};
$E.registerOnLoad.windowLoaded=false;
$E.onWindowLoad=function(fn){
if(window.addEventListener){
window.addEventListener("load",fn,false);
}else{
if(window.attachEvent){
window.attachEvent("onload",fn);
}else{
if(document.getElementById){
window.onload=fn;
}
}
}
};
$C.addSpanToDom=function(){
var _8a5=document.createElement("span");
document.body.insertBefore(_8a5,document.body.firstChild);
};
$E.windowLoadHandler=function(e){
if(window.Ext){
Ext.BLANK_IMAGE_URL=_cf_ajaxscriptsrc+"/resources/ext/images/default/s.gif";
}
$C.addSpanToDom();
$L.init();
$E.registerOnLoad.windowLoaded=true;
$E.windowLoadImpEvent.fire();
$E.windowLoadImpEvent.unsubscribe();
$E.windowLoadEvent.fire();
$E.windowLoadEvent.unsubscribe();
if(window.Ext){
Ext.onReady(function(){
$E.windowLoadUserEvent.fire();
});
}else{
$E.windowLoadUserEvent.fire();
}
$E.windowLoadUserEvent.unsubscribe();
};
$E.onWindowLoad($E.windowLoadHandler);
$B.register=function(_8a7,_8a8,_8a9,_8aa){
for(var i=0;i<_8a7.length;i++){
var _8ac=_8a7[i][0];
var _8ad=_8a7[i][1];
var _8ae=_8a7[i][2];
if(window[_8ac]){
var _8af=eval(_8ac);
if(_8af&&_8af._cf_register){
_8af._cf_register(_8ae,_8a9,_8a8);
continue;
}
}
var _8b0=$C.objectCache[_8ac];
if(_8b0&&_8b0._cf_register){
_8b0._cf_register(_8ae,_8a9,_8a8);
continue;
}
var _8b1=$D.getElement(_8ac,_8ad);
var _8b2=(_8b1&&((!_8b1.length&&_8b1.length!=0)||(_8b1.length&&_8b1.length>0)||_8b1.tagName=="SELECT"));
if(!_8b2){
$C.handleError(null,"bind.register.elnotfound","bind",[_8ac]);
}
if(_8b1.length>1&&!_8b1.options){
for(var j=0;j<_8b1.length;j++){
$B.register.addListener(_8b1[j],_8ae,_8a9,_8a8);
}
}else{
$B.register.addListener(_8b1,_8ae,_8a9,_8a8);
}
}
if(!$C.bindHandlerCache[_8a8.bindTo]&&typeof (_8a8.bindTo)=="string"){
$C.bindHandlerCache[_8a8.bindTo]=function(){
_8a9.call(null,null,_8a8);
};
}
if(_8aa){
_8a9.call(null,null,_8a8);
}
};
$B.register.addListener=function(_8b4,_8b5,_8b6,_8b7){
if(!$E.isListener(_8b4,_8b5,_8b6,_8b7)){
$E.addListener(_8b4,_8b5,_8b6,_8b7);
}
};
$B.assignValue=function(_8b8,_8b9,_8ba,_8bb){
if(!_8b8){
return;
}
if(_8b8.call){
_8b8.call(null,_8ba,_8bb);
return;
}
var _8bc=$C.objectCache[_8b8];
if(_8bc&&_8bc._cf_setValue){
_8bc._cf_setValue(_8ba);
return;
}
var _8bd=document.getElementById(_8b8);
if(!_8bd){
$C.handleError(null,"bind.assignvalue.elnotfound","bind",[_8b8]);
}
if(_8bd.tagName=="SELECT"){
var _8be=$U.checkQuery(_8ba);
var _8bf=$C.objectCache[_8b8];
if(_8be){
if(!_8bf||(_8bf&&(!_8bf.valueCol||!_8bf.displayCol))){
$C.handleError(null,"bind.assignvalue.selboxmissingvaldisplay","bind",[_8b8]);
return;
}
}else{
if(typeof (_8ba.length)=="number"&&!_8ba.toUpperCase){
if(_8ba.length>0&&(typeof (_8ba[0].length)!="number"||_8ba[0].toUpperCase)){
$C.handleError(null,"bind.assignvalue.selboxerror","bind",[_8b8]);
return;
}
}else{
$C.handleError(null,"bind.assignvalue.selboxerror","bind",[_8b8]);
return;
}
}
_8bd.options.length=0;
var _8c0;
var _8c1=false;
if(_8bf){
_8c0=_8bf.selected;
if(_8c0&&_8c0.length>0){
_8c1=true;
}
}
if(!_8be){
for(var i=0;i<_8ba.length;i++){
var opt=new Option(_8ba[i][1],_8ba[i][0]);
_8bd.options[i]=opt;
if(_8c1){
for(var j=0;j<_8c0.length;j++){
if(_8c0[j]==opt.value){
opt.selected=true;
}
}
}
}
}else{
if(_8be=="col"){
var _8c5=_8ba.DATA[_8bf.valueCol];
var _8c6=_8ba.DATA[_8bf.displayCol];
if(!_8c5||!_8c6){
$C.handleError(null,"bind.assignvalue.selboxinvalidvaldisplay","bind",[_8b8]);
return;
}
for(var i=0;i<_8c5.length;i++){
var opt=new Option(_8c6[i],_8c5[i]);
_8bd.options[i]=opt;
if(_8c1){
for(var j=0;j<_8c0.length;j++){
if(_8c0[j]==opt.value){
opt.selected=true;
}
}
}
}
}else{
if(_8be=="row"){
var _8c7=-1;
var _8c8=-1;
for(var i=0;i<_8ba.COLUMNS.length;i++){
var col=_8ba.COLUMNS[i];
if(col==_8bf.valueCol){
_8c7=i;
}
if(col==_8bf.displayCol){
_8c8=i;
}
if(_8c7!=-1&&_8c8!=-1){
break;
}
}
if(_8c7==-1||_8c8==-1){
$C.handleError(null,"bind.assignvalue.selboxinvalidvaldisplay","bind",[_8b8]);
return;
}
for(var i=0;i<_8ba.DATA.length;i++){
var opt=new Option(_8ba.DATA[i][_8c8],_8ba.DATA[i][_8c7]);
_8bd.options[i]=opt;
if(_8c1){
for(var j=0;j<_8c0.length;j++){
if(_8c0[j]==opt.value){
opt.selected=true;
}
}
}
}
}
}
}
}else{
_8bd[_8b9]=_8ba;
}
$E.callBindHandlers(_8b8,null,"change");
$L.info("bind.assignvalue.success","bind",[_8ba,_8b8,_8b9]);
};
$B.localBindHandler=function(e,_8cb){
var _8cc=document.getElementById(_8cb.bindTo);
var _8cd=$B.evaluateBindTemplate(_8cb,true);
$B.assignValue(_8cb.bindTo,_8cb.bindToAttr,_8cd);
};
$B.localBindHandler._cf_bindhandler=true;
$B.evaluateBindTemplate=function(_8ce,_8cf,_8d0,_8d1,_8d2){
var _8d3=_8ce.bindExpr;
var _8d4="";
if(typeof _8d2=="undefined"){
_8d2=false;
}
for(var i=0;i<_8d3.length;i++){
if(typeof (_8d3[i])=="object"){
var _8d6=null;
if(!_8d3[i].length||typeof _8d3[i][0]=="object"){
_8d6=$X.JSON.encode(_8d3[i]);
}else{
var _8d6=$B.getBindElementValue(_8d3[i][0],_8d3[i][1],_8d3[i][2],_8cf,_8d1);
if(_8d6==null){
if(_8cf){
_8d4="";
break;
}else{
_8d6="";
}
}
}
if(_8d0){
_8d6=encodeURIComponent(_8d6);
}
_8d4+=_8d6;
}else{
var _8d7=_8d3[i];
if(_8d2==true&&i>0){
if(typeof (_8d7)=="string"&&_8d7.indexOf("&")!=0){
_8d7=encodeURIComponent(_8d7);
}
}
_8d4+=_8d7;
}
}
return _8d4;
};
$B.jsBindHandler=function(e,_8d9){
var _8da=_8d9.bindExpr;
var _8db=new Array();
var _8dc=_8d9.callFunction+"(";
for(var i=0;i<_8da.length;i++){
var _8de;
if(typeof (_8da[i])=="object"){
if(_8da[i].length){
if(typeof _8da[i][0]=="object"){
_8de=_8da[i];
}else{
_8de=$B.getBindElementValue(_8da[i][0],_8da[i][1],_8da[i][2],false);
}
}else{
_8de=_8da[i];
}
}else{
_8de=_8da[i];
}
if(i!=0){
_8dc+=",";
}
_8db[i]=_8de;
_8dc+="'"+_8de+"'";
}
_8dc+=")";
var _8df=_8d9.callFunction.apply(null,_8db);
$B.assignValue(_8d9.bindTo,_8d9.bindToAttr,_8df,_8d9.bindToParams);
};
$B.jsBindHandler._cf_bindhandler=true;
$B.urlBindHandler=function(e,_8e1){
var _8e2=_8e1.bindTo;
if($C.objectCache[_8e2]&&$C.objectCache[_8e2]._cf_visible===false){
$C.objectCache[_8e2]._cf_dirtyview=true;
return;
}
var url=$B.evaluateBindTemplate(_8e1,false,true,false,true);
var _8e4=$U.extractReturnFormat(url);
if(_8e4==null||typeof _8e4=="undefined"){
_8e4="JSON";
}
if(_8e1.bindToAttr||typeof _8e1.bindTo=="undefined"||typeof _8e1.bindTo=="function"){
var _8e1={"bindTo":_8e1.bindTo,"bindToAttr":_8e1.bindToAttr,"bindToParams":_8e1.bindToParams,"errorHandler":_8e1.errorHandler,"url":url,returnFormat:_8e4};
try{
$A.sendMessage(url,"GET",null,true,$B.urlBindHandler.callback,_8e1);
}
catch(e){
$C.handleError(_8e1.errorHandler,"ajax.urlbindhandler.connectionerror","http",[url,e]);
}
}else{
$A.replaceHTML(_8e2,url,null,null,_8e1.callback,_8e1.errorHandler);
}
};
$B.urlBindHandler._cf_bindhandler=true;
$B.urlBindHandler.callback=function(req,_8e6){
if($A.isRequestError(req)){
$C.handleError(_8e6.errorHandler,"bind.urlbindhandler.httperror","http",[req.status,_8e6.url,req.statusText],req.status,req.statusText);
}else{
$L.info("bind.urlbindhandler.response","http",[req.responseText]);
var _8e7;
try{
if(_8e6.returnFormat==null||_8e6.returnFormat==="JSON"){
_8e7=$X.JSON.decode(req.responseText);
}else{
_8e7=req.responseText;
}
}
catch(e){
if(req.responseText!=null&&typeof req.responseText=="string"){
_8e7=req.responseText;
}else{
$C.handleError(_8e6.errorHandler,"bind.urlbindhandler.jsonerror","http",[req.responseText]);
}
}
$B.assignValue(_8e6.bindTo,_8e6.bindToAttr,_8e7,_8e6.bindToParams);
}
};
$A.initSelect=function(_8e8,_8e9,_8ea,_8eb){
$C.objectCache[_8e8]={"valueCol":_8e9,"displayCol":_8ea,selected:_8eb};
};
$S.setupSpry=function(){
if(typeof (Spry)!="undefined"&&Spry.Data){
Spry.Data.DataSet.prototype._cf_getAttribute=function(_8ec){
var val;
var row=this.getCurrentRow();
if(row){
val=row[_8ec];
}
return val;
};
Spry.Data.DataSet.prototype._cf_register=function(_8ef,_8f0,_8f1){
var obs={bindParams:_8f1};
obs.onCurrentRowChanged=function(){
_8f0.call(null,null,this.bindParams);
};
obs.onDataChanged=function(){
_8f0.call(null,null,this.bindParams);
};
this.addObserver(obs);
};
if(Spry.Debug.trace){
var _8f3=Spry.Debug.trace;
Spry.Debug.trace=function(str){
$L.info(str,"spry");
_8f3(str);
};
}
if(Spry.Debug.reportError){
var _8f5=Spry.Debug.reportError;
Spry.Debug.reportError=function(str){
$L.error(str,"spry");
_8f5(str);
};
}
$L.info("spry.setupcomplete","bind");
}
};
$E.registerOnLoad($S.setupSpry,null,true);
$S.bindHandler=function(_8f7,_8f8){
var url;
var _8fa="_cf_nodebug=true&_cf_nocache=true";
if(window._cf_clientid){
_8fa+="&_cf_clientid="+_cf_clientid;
}
var _8fb=window[_8f8.bindTo];
var _8fc=(typeof (_8fb)=="undefined");
if(_8f8.cfc){
var _8fd={};
var _8fe=_8f8.bindExpr;
for(var i=0;i<_8fe.length;i++){
var _900;
if(_8fe[i].length==2){
_900=_8fe[i][1];
}else{
_900=$B.getBindElementValue(_8fe[i][1],_8fe[i][2],_8fe[i][3],false,_8fc);
}
_8fd[_8fe[i][0]]=_900;
}
_8fd=$X.JSON.encode(_8fd);
_8fa+="&method="+_8f8.cfcFunction;
_8fa+="&argumentCollection="+encodeURIComponent(_8fd);
$L.info("spry.bindhandler.loadingcfc","http",[_8f8.bindTo,_8f8.cfc,_8f8.cfcFunction,_8fd]);
url=_8f8.cfc;
}else{
url=$B.evaluateBindTemplate(_8f8,false,true,_8fc);
$L.info("spry.bindhandler.loadingurl","http",[_8f8.bindTo,url]);
}
var _901=_8f8.options||{};
if((_8fb&&_8fb._cf_type=="json")||_8f8.dsType=="json"){
_8fa+="&returnformat=json";
}
if(_8fb){
if(_8fb.requestInfo.method=="GET"){
_901.method="GET";
if(url.indexOf("?")==-1){
url+="?"+_8fa;
}else{
url+="&"+_8fa;
}
}else{
_901.postData=_8fa;
_901.method="POST";
_8fb.setURL("");
}
_8fb.setURL(url,_901);
_8fb.loadData();
}else{
if(!_901.method||_901.method=="GET"){
if(url.indexOf("?")==-1){
url+="?"+_8fa;
}else{
url+="&"+_8fa;
}
}else{
_901.postData=_8fa;
_901.useCache=false;
}
var ds;
if(_8f8.dsType=="xml"){
ds=new Spry.Data.XMLDataSet(url,_8f8.xpath,_901);
}else{
ds=new Spry.Data.JSONDataSet(url,_901);
ds.preparseFunc=$S.preparseData;
}
ds._cf_type=_8f8.dsType;
var _903={onLoadError:function(req){
$C.handleError(_8f8.errorHandler,"spry.bindhandler.error","http",[_8f8.bindTo,req.url,req.requestInfo.postData]);
}};
ds.addObserver(_903);
window[_8f8.bindTo]=ds;
}
};
$S.bindHandler._cf_bindhandler=true;
$S.preparseData=function(ds,_906){
var _907=$U.getFirstNonWhitespaceIndex(_906);
if(_907>0){
_906=_906.slice(_907);
}
if(window._cf_jsonprefix&&_906.indexOf(_cf_jsonprefix)==0){
_906=_906.slice(_cf_jsonprefix.length);
}
return _906;
};
$P.init=function(_908){
$L.info("pod.init.creating","widget",[_908]);
var _909={};
_909._cf_body=_908+"_body";
$C.objectCache[_908]=_909;
};
$B.cfcBindHandler=function(e,_90b){
var _90c=(_90b.httpMethod)?_90b.httpMethod:"GET";
var _90d={};
var _90e=_90b.bindExpr;
for(var i=0;i<_90e.length;i++){
var _910;
if(_90e[i].length==2){
_910=_90e[i][1];
}else{
_910=$B.getBindElementValue(_90e[i][1],_90e[i][2],_90e[i][3],false);
}
_90d[_90e[i][0]]=_910;
}
var _911=function(_912,_913){
$B.assignValue(_913.bindTo,_913.bindToAttr,_912,_913.bindToParams);
};
var _914={"bindTo":_90b.bindTo,"bindToAttr":_90b.bindToAttr,"bindToParams":_90b.bindToParams};
var _915={"async":true,"cfcPath":_90b.cfc,"httpMethod":_90c,"callbackHandler":_911,"errorHandler":_90b.errorHandler};
if(_90b.proxyCallHandler){
_915.callHandler=_90b.proxyCallHandler;
_915.callHandlerParams=_90b;
}
$X.invoke(_915,_90b.cfcFunction,_90b._cf_ajaxproxytoken,_90d,_914);
};
$B.cfcBindHandler._cf_bindhandler=true;
$U.extractReturnFormat=function(url){
var _917;
var _918=url.toUpperCase();
var _919=_918.indexOf("RETURNFORMAT");
if(_919>0){
var _91a=_918.indexOf("&",_919+13);
if(_91a<0){
_91a=_918.length;
}
_917=_918.substring(_919+13,_91a);
}
return _917;
};
$U.replaceAll=function(_91b,_91c,_91d){
var _91e=_91b.indexOf(_91c);
while(_91e>-1){
_91b=_91b.replace(_91c,_91d);
_91e=_91b.indexOf(_91c);
}
return _91b;
};
$U.cloneObject=function(obj){
var _920={};
for(key in obj){
var _921=obj[key];
if(typeof _921=="object"){
_921=$U.cloneObject(_921);
}
_920.key=_921;
}
return _920;
};
$C.clone=function(obj,_923){
if(typeof (obj)!="object"){
return obj;
}
if(obj==null){
return obj;
}
var _924=new Object();
for(var i in obj){
if(_923===true){
_924[i]=$C.clone(obj[i]);
}else{
_924[i]=obj[i];
}
}
return _924;
};
$C.printObject=function(obj){
var str="";
for(key in obj){
str=str+"  "+key+"=";
value=obj[key];
if(typeof (value)=="object"){
value=$C.printObject(value);
}
str+=value;
}
return str;
};
}
}
cfinit();
