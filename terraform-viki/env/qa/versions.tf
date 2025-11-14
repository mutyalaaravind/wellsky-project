terraform {
  required_version = "1.9.0"


  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "6.8.0"
    }
    okta = {
      source  = "okta/okta"
      version = "3.46.0"
    }
    newrelic = {
      source = "newrelic/newrelic"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.1.0"
    }
    jwks = {
      source  = "iwarapter/jwks"
      version = "0.1.0"
    }
  }
}
