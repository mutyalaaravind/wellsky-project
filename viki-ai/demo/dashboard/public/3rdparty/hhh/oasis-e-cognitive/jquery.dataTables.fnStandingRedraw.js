$.fn.dataTableExt.oApi.fnStandingRedraw = function(oSettings) {
    if(oSettings.oFeatures.bServerSide === false){
        var before = oSettings._iDisplayStart;
 
        oSettings.oApi._fnReDraw(oSettings);
 
        // iDisplayStart has been reset to zero - so lets change it back
        // taking into account that should be smaller than the number of
        // records that will be displayed
        oSettings._iDisplayStart = before < oSettings.fnRecordsDisplay() ? before : 0;
        oSettings.oApi._fnCalculateEnd(oSettings);
    }
      
    // draw the 'current' page
    oSettings.oApi._fnDraw(oSettings);
};