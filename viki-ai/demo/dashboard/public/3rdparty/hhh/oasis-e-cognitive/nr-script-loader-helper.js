var NRScriptLoader = NRScriptLoader || (function(){
    var _environmentID = "ASIDE-APMID";
    var _cfSideFlag = {}; // private
    var _cfBSide = "B-SIDE";

    return {
        init : function(cfSideFLag) {
            _cfSideFlag = cfSideFLag;
        },
        buildNREUM : function() {
            //New Relic Account Link
            var linkValue="842e32b89c";
            var appID = this.getApplicationID(_cfSideFlag[0]);

            //These values append to generic New Relic browser snippet
            NREUM.info = { applicationID: appID,
            licenseKey:    linkValue };

        },
        getApplicationID : function(cfUpgradeFLag) {
            var host = window.location.host;

            //New Relic EnvironmentIDs
            var nonProdEnvironmentIDs =  {
                "integration.kinnser.net" : {"APMID":""},             // not logged
                "dev.kinnser.net" :         {"APMID":""},             // not logged
                "support.kinnser.net" :     {"APMID":""},             // not logged
                "qa.kinnser.net" :          {"APMID":"495461634"},    // Log to HHH.QA.Monolith
                "stg.kinnser.net" :         {"APMID":"297235464"}     // Log to HHH.STG.Monolith
                };

            var prodEnvironmentID =  {
                "kinnser.net" : {"ASIDE-APMID":"515168422",   // Log to HHH.Prod.Monolith.A
                                "BSIDE-APMID":"514975114" }  // Log to HHH.Prod.Monolith.B
            };

            for (var key in nonProdEnvironmentIDs){
                if (nonProdEnvironmentIDs.hasOwnProperty(key)) {
                    //we do an indexOf here because we need to account for different potential sub-domains
                    //in the target environment, e.g., financials.qa.kinnser.net
                    if (host.indexOf(key) >= 0) {
                        return nonProdEnvironmentIDs[key]["APMID"];
                    }
                }
            }
            if (host.indexOf(Object.keys(prodEnvironmentID)[0]) >= 0) {
                switch (_cfSideFlag[0]) {
                    case _cfBSide:
                        _environmentID = Object.values(prodEnvironmentID)[0]["BSIDE-APMID"];
                        break;
                    default:
                        _environmentID = Object.values(prodEnvironmentID)[0]["ASIDE-APMID"];
                }
                return _environmentID;
            }
            return "";
        }
    }
}());
