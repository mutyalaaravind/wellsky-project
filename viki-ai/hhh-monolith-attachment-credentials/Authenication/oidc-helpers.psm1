function LogStatus {
    param ([string] $msg)
    Write-Host -ForegroundColor Green $msg
}


function Assert-AtlasPSInstalled {
    $atlasPs = Get-Module -ListAvailable -Name "AtlasPS"
    if (-Not $atlasPs) {
        throw "The AtlasPS module must be installed for this script to work."
    }
}

function Connect-ToAuthentication {
    param (
        [string] $authServer,
        [string] $adminClientId
    )

    LogStatus "Connecting to $authServer..."
    Set-WSClient -AuthEndpoint $authServer -ClientId $adminClientId
    Connect-WS | Out-Null
}

function Assert-AwsRole {
    $json = aws sts get-caller-identity
    $user = $json | Out-String | ConvertFrom-Json

    if (-Not $user) {
        throw "Unable to determine AWS user.  Have you called Assume-Role?"
    }  
}

function Assert-GcpAuthenticated {
    (gcloud secrets list --limit=1 | Out-Null) 2> $null
    if (-Not $?) {
        throw "GCP User doesn't seem to be logged in. Reauthenticate with: gcloud auth login"
    }
}

function New-ClientCredential {
    param (
        [string] $clientId,
        [string] $clientDescription,
        [string] $clientSecret,
        [int] $tokenLifetimeInSeconds,
        [string[]] $scopesForClient,
        [object[]] $additionalClaims
    )

    # check if Client already exists...
    $existing = Get-Client | Where-Object { $_.clientId -eq $clientId }
    
    if ($existing) {
        LogStatus "Client '$clientId' already exists.  Nothing to create."
        return
    }

    LogStatus "Creating client $clientId..."

    $ProductIdClaimType = "ws:prod.id";
    $HomeHealthProductId = "AM";
    $GenericTenantId = GetOrCreateTenantId "HHH Generic Tenant" $HomeHealthProductId; 

    $request = @{
        GrantType = "client_credentials";
        ClientName = $clientId;
        ClientId = $clientId;
        Description = $clientDescription;
        AllowedScopes = $scopesForClient;
        AccessTokenLifetime = $tokenLifetimeInSeconds;
        Enabled = $true;
        TenantId = $GenericTenantId
        ClientClaims = @( @{
            Type = $ProductIdClaimType;
            Value = $HomeHealthProductId
        })
    }

    if ($clientSecret) {
        $request.Secret = $clientSecret;
    }

    if ($additionalClaims) {
        $request.ClientClaims += $additionalClaims;
    }

    $templateFile = New-TemporaryFile
    try {
        $request | ConvertTo-Json | Set-Content $templateFile

        $clientDetails = New-Client -Template $templateFile

        LogStatus "Client $clientId created."

        return $clientDetails.secret
    }
    finally {
        Remove-Item $templateFile   
    }

    return $null
}

function Set-ScopesForClient {
    param (
        [string] $clientId,
        [string[]] $scopesForClient
    )

    
    $client = Get-Client | Where-Object { $_.clientId -eq $clientId }

    # Write-Host "Scopes for client $cliendId..."
    # $client | ConvertTo-Json | Write-Host

    $existingScopes = $client.allowedScopes

    Write-Host "Requested scopes:`r`n  $($scopesForClient -join "`r`n  ")"
    Write-Host "Existing scopes on client:`r`n  $($existingScopes -join "`r`n  ")"

    $scopesToAdd = $scopesForClient | Where-Object { $existingScopes -NotContains $_}
    $scopesToRemove = $existingScopes | Where-Object { $scopesForClient -NotContains $_}

    Write-Host "Scopes to add:`r`n  $($scopesToAdd -join "`r`n  ")"
    Write-Host "Scopes to remove:`r`n  $($scopesToRemove -join "`r`n  ")"

    if ($scopesToAdd) {
        Add-ScopeToClient -ClientId $clientId -Scopes $scopesToAdd
    }

    if ($scopesToRemove) {
        Remove-ScopeFromClient -ClientId $clientId -Scopes $scopesToRemove    
    }

    LogStatus "Scopes for client '$clientId' updated."
}

function Set-CredentialsInParameterStoreAws {
    param (
        $parameterPathPrefix,
        $clientId,
        $clientSecret,
        $scope = $null
    )

    if (-Not $clientSecret) {
        Write-Host "No client secret provided for client $clientId.  Nothing to save to Parameter Store."
        return;
    }

    aws ssm put-parameter --name "$parameterPathPrefix/AuthenticationClientId" --value $clientId  --type "String" --overwrite --region us-east-1
    aws ssm put-parameter --name "$parameterPathPrefix/AuthenticationClientSecret" --value $clientSecret  --type "SecureString" --overwrite --region us-east-1

    if ($scope)
    {
        aws ssm put-parameter --name "$parameterPathPrefix/AuthenticationClientScope" --value $scope  --type "String" --overwrite --region us-east-1

    }
    LogStatus "Client credentials saved to $parameterPathPrefix."

}

function Set-CredentialsInGcp {
    param (
        $bucket,
        $gcpProject,
        $gcpSecretName,
        $parameterPathPrefix,
        $clientId,
        $clientSecret,
        $scope = $null
    )

    if (-Not $clientSecret) {
        Write-Host "No client secret provided for client $clientId.  Nothing to save to GCP Parameter Store."
        return;
    }

    # Create a new secret version
    LogStatus "Adding new secret version to '${gcpSecretPath}'..."
    Set-Secret $gcpProject $gcpSecretName $clientSecret

    # Set the client id
    LogStatus "Saving client id to GCP parameter store '${bucket}'..."
    Set-ContentsInBucket "$bucket/$parameterPathPrefix/AuthenticationClientId" $clientId
    #aws ssm put-parameter --name "$parameterPathPrefix/AuthenticationClientId" --value $clientId  --type "String" --overwrite --region us-east-1
    #aws ssm put-parameter --name "$parameterPathPrefix/AuthenticationClientSecret" --value $clientSecret  --type "SecureString" --overwrite --region us-east-1

    if ($scope)
    {
        LogStatus "Saving scope to GCP parameter store '${bucket}'..."
        Set-ContentsInBucket "$bucket/$parameterPathPrefix/AuthenticationClientScope" $scope
    }
    LogStatus "Client credentials saved to GCP $parameterPathPrefix."
}

function Set-ContentsInBucket {
    param (
        $bucketAndPath,
        $contents
    )

    $tempFile = New-TemporaryFile
    try {
        $contents | Set-Content -NoNewline $tempFile
        gsutil cp $tempFile "gs://$bucketAndPath"
    }
    finally {
        Remove-Item $tempFile   
    }
}

function Set-Secret {
    param (
        $gcpProject,
        $gcpSecretName,
        $clientSecret
    )

    $tempFile = New-TemporaryFile
    try {
        $clientSecret | Set-Content -NoNewline $tempFile
        $gcpSecretPath = "projects/${gcpProject}/secrets/${gcpSecretName}"
        gcloud --project $gcpProject secrets versions add $gcpSecretPath --data-file=$tempFile    
    }
    finally {
        Remove-Item $tempFile   
    }    
}

function GetOrCreateTenantId {
    param (
        [string] $tenantName,
        [string] $productId
    )

    # check if a tenant already exists...
    $tenant = Get-Tenant | Where-Object { $_.Name -eq $tenantName}

    if ($tenant) {
        $tenantId = $tenant | Select-Object -ExpandProperty "id"
        Write-Host "Found existing tenant '$tenantName' with id $tenantId"
        return $tenantId
    } 

    $tenantId = New-Tenant -TenantName $tenantName -ProductId $productId | Select-Object -ExpandProperty "result"  | Select-Object -ExpandProperty "identifier"

    Write-Host "Created new tenant '$tenantName' with id $tenantId"
    return $tenantId
}

function New-ResourceApi {
    param (
        [string] $resourceToCreate,
        [string[]] $scopesForResource
    )

    # check if API Resource already exists...
    $existing = Get-ApiResource | Where-Object { $_.Name -eq $resourceToCreate}

    if ($existing) {
        LogStatus "API Resource '$resourceToCreate' already exists.  Nothing to create."
        return
    }

    LogStatus "Creating resource API $resourceToCreate..."
    New-ApiResource -Name $resourceToCreate -Scopes $scopesForResource
}