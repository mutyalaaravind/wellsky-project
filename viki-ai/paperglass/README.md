# Auth

...is a mess:

`gcloud auth application-default login --impersonate-service-account=viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com`

# some key decisions
## summarizer document AI processor brings in OCR + summary so no need to use hcc one

## Obtain API token

```sh
$ python3 -m api.paperglass.entrypoints.mktoken -a app -t tenant -p patient
```
