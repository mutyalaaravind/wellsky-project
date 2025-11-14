# This script will create an authentication client that can be used for the ColdFusion
# monolith to create access tokens that can be used to access JWT protected APIs.  The 
# idea is that we would have a single client (per environment) that all parts/features
# of the monolith would use.  Each area would just request the scopes that they need for 
# their specific calls.  This would allow the JWTs generated to have the least amount of
# privileges needed.
#
# If the client already exists, the script will do nothing.  
#
# The script will prompt the caller to log into the Atlas.Authentication service to 
# validate the caller's identity (and that they are allowed to create new clients).
#
param (
    [string] $clientId = "client.hhh.medication.genai.qa",
    [string] $clientSecret = $null,
    [string] $clientDescription = "Client used by the Medication Profile Gen AI",
    [int] $tokenLifetimeInSeconds = 3600,
    [string[]] $scopes = @(
        "api.wellsky.hhh.monolith.api.attachments.read"
    ),
    [string] $authServer = "https://auth.stable.wellsky.io",
    [string] $adminClientId = "client.AtlasPS"
)

Import-Module ./oidc-helpers -Force

Assert-AtlasPSInstalled

Import-Module -Name "AtlasPS" -Force

Connect-ToAuthentication $authServer $adminClientId

$clientSecret = New-ClientCredential $clientId $clientDescription $clientSecret $tokenLifetimeInSeconds $scopes

if ($clientSecret) 
{
    Write-Host "Client '$($clientId)' created with secret '$clientSecret'"
}

Set-ScopesForClient $clientId $scopes