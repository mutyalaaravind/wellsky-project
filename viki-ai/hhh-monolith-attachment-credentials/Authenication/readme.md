# Authentication Client Creation Scripts

The scripts here will create an Open Id Authentication Client that is registered with the Atlas Authentication Service.  This client can then be used to generate a JWT that can be used to authenticate the caller for HTTP calls.

The best practice for authentication clients is that they should map to a specific "binary".  That is, you don't want one process using a different client id for each feature that might need a JWT.  Instead, the process should use the same client id and just request the scopes that it needs for the feature that is running.  

Making this more practical and less theoritical, the ColdFusion monolith should have a single authentication client that is allowed to request scopes from multiple microservices.  This means the one client could request a scope for talking to the kmail service and/or a scope for talking to the storage service.  It would be up to the caller (the part of the monolith requesting a JWT) to specify what scopes it needs at that time.  If that code doesn't need to talk to the Storage Service, it shouldn't ask for those scopes in the JWT creation even thought it is _allowed_ to ask for them.

# Atlas Authentication Powershell Scipts
The scripts in this directory use the [Atlas Powershell Module](https://confluence.wellsky.com/display/~zeid.derhally/Atlas+PowerShell+Module) to talk to the Atlas Authentication Service APIs to create the client.

The "meat" of the scripts are in the underscore prefixed files (_createMonolithClient.ps1) but the idea is that you would only ever call the scripts based on which environment you want to update (createMonolithClient-dev.ps1,createMonolithClient-qa.ps1, etc.)

When run, the script will open a browser window for you to log into [WAP](https://wap.wellsky.io/) (the WellSky Admin Portal).  Once you have logged in, the script will continue.  It will check to see if the client id for the current environment already exists.  If it does not exist, the client would be created and the client secret would be output to the screen.  This is the only time the client secret is accessible.  The client secret is like a password.  It should be stored in a secure location.  For the HHH ColdFusion monolith, this is normally Azure Vault.  If the client already exists, the script does not attempt to recreate it since this would cause a new client secret to be generated (there by breaking anyone currently using the old secret).  

While there shouldn't be much of a need to recreate the client after it is created, there will be times when the list of allowed scopes needs to be updated.  When a new service is created, or just a new feature in an existing service, new scopes would be generated.  We need to tell the authentication service this client is allowed to use those new scopes.  Every time the script runs, it will compare the list of scopes currently on the client to the list of scoped defined in the script.  New scopes will be added. Old scopes will be removed.  Running the script multiple times will not harm anything.

## Running the scripts.

0. Ensure the [Atlas Powershell Module](https://confluence.wellsky.com/display/~zeid.derhally/Atlas+PowerShell+Module) is installed.  This is a one time thing.  The scripts here will complain if the module is not available.

1. Open a powershell prompt (I use Powershell Core 7.3.5 currently.  I don't know if Windows Powershell would work or not).

2. Change to the directory containing this scripts.

3. Run the script for the environment you are wanting to update.  For dev:
```
.\createMonolithClient-dev.ps1
```

4. When the script runs, it will open a browser and ask you to log into the Atlas Authentication Service.  This would be the same password you use to log into [WAP](https://wap.wellsky.io/).

5. Once you are logged in, go back to the powershell console.  The script should continue to run.