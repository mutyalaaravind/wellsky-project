ENV=$1
PROJECT="viki-${ENV}-app-wsky"

cp firebase-${ENV}.json firebase.json

cp -r extensions_template/ extensions/

gsutil cp gs://viki-ai-provisional-dev/bq-extensions/firebase-anydb-bigquery-export-0.1.57.tgz .
tar -xzf firebase-anydb-bigquery-export-0.1.57.tgz

for file in extensions/*; do
    if [ -f "$file" ]; then
        sed -i '' "s/viki-project-app-wsky/${PROJECT}/g" "$file"
        sed -i '' "s/viki-env/viki-${ENV}/g" "$file"
    fi
done

firebase use viki-${ENV}-app-wsky

#firebase ext:install ./firebase-anydb-bigquery-export-0.1.57.tgz --project=viki-${ENV}-app-wsky

firebase deploy --only extensions --project=viki-${ENV}-app-wsky --force
