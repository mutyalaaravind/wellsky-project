const functions = require('firebase-functions');
const promiseRetry = require('promise-retry');

// Make sure to restart firebase-tools container after changing this file - the auto-reload does not seem to work well

const triggers = {
    'extract_embeddings_trigger': {
        pattern: `extract_embeddings_metadata/{docId}`,
        event: 'onWrite', // onCreate, onUpdate, onDelete, onWrite
        target: 'http://extract-events:12002/eventarc/firestore/json',
        type: 'firestore',
    },
    // WARNING: use "onWrite" only and then check if the document was created or deleted in Python code.
    // For some reason, the onCreate event is messed up when used with local emulator
    'extract_schema_chunks': {
        pattern: `extract_schema_chunks/{docId}`,
        event: 'onWrite', // onCreate, onUpdate, onDelete, onWrite
        target: 'http://extract-events:12002/eventarc/firestore/json',
        type: 'firestore',
    },
    'autoscribe_transactions': {
        pattern: `autoscribe_transactions/{docId}`,
        event: 'onWrite', // onCreate, onUpdate, onDelete, onWrite
        target: 'http://extract-events:12002/eventarc/firestore/json',
        type: 'firestore',
    },
    'paperglass_events': {
        pattern: `paperglass_events/{docId}`,
        event: 'onCreate', // onCreate, onUpdate, onDelete, onWrite
        target: 'http://paperglass-events:15002/eventarc/firestore/json',
        type: 'firestore',
    },
    'paperglass_commands': {
        pattern: `paperglass_commands/{docId}`,
        event: 'onCreate', // onCreate, onUpdate, onDelete, onWrite
        target: 'http://paperglass-events:15002/eventarc/firestore/json',
        type: 'firestore',
    },
    'extract_commands': {
        pattern: `extract_commands/{docId}`,
        event: 'onCreate', // onCreate, onUpdate, onDelete, onWrite
        target: 'http://extract-events:12002/eventarc/firestore/json',
        type: 'firestore',
    },
    'extraction_ordered_events_topic': {
        target: 'http://paperglass-events:15002/eventarc/pubsub/json',
        type: 'pubsub',
    },
    'extract_v4_topic':{
        target: 'http://medication-extraction-api:17000/run_extraction_pubsub',
        type: 'pubsub',
    },
    'extract_v4_classify_internal_topic':{
        target: 'http://medication-extraction-api:17000/classify_pubsub',
        type: 'pubsub',
    },
    'extract_v4_medication_internal_topic':{
        target: 'http://medication-extraction-api:17000/medications_pubsub',
        type: 'pubsub',
    },
    'extract_v4_document_status_topic':{
        target: 'http://medication-extraction-api:17000/update_status_pubsub',
        type: 'pubsub',
    },
    'extract_v4_paperglass_medications_topic':{
        target: 'http://paperglass-events:15002/eventarc/medications',
        type: 'pubsub',
    },
    'audit_logger_topic':{
        target: 'http://prompt-logger-api:18000/process-task-pubsub',
        type: 'pubsub',
    },
    'page_ocr_topic':{
        target: 'http://paperglass-events:15002/eventarc/pubsub/json',
        type: 'pubsub',
    }
};

module.exports = Object.fromEntries(Object.entries(triggers).map(([triggerName, trigger]) => {
    if (trigger.type == 'firestore') {
        return [triggerName, functions.firestore.document(trigger.pattern)[trigger.event](async (change, context) => {
            const path = context.resource.name.match(/documents\/(.*)/)[1];
            const collectionName = path.split('/')[0];
            let payload;
            if (trigger.event == 'onCreate') {
                payload = {
                    before: null,
                    after: change.data(),
                    collection_name: collectionName,
                    document_id: context.params.docId,
                };
            }
            else {
                payload = {
                    before: change.before ? change.before.data() : null, // For some God-forsaken reason, this is undefined when the document is created
                    after: change.after ? change.after.data() : null, // For some God-forsaken reason, this is undefined when the document is deleted
                    collection_name: collectionName,
                    document_id: context.params.docId,
                };
            }
            promiseRetry(async (retry, number) => {
                try {
                    const response = await fetch(trigger.target, { method: 'POST', body: JSON.stringify(payload) });
                    if (response.status >= 400) {
                        throw new Error(`Got status ${response.status} from app`);
                    }
                } catch (err) {
                    if (number == 5) {
                        console.error('Failed to forward event to app after 5 retries, giving up:', err);
                        return;
                    }
                    retry(err);
                }
            });
        })];
    }

    if (trigger.type == 'pubsub') {
        const handler = async (message, context) => {
            const payload = JSON.parse(Buffer.from(message.data, 'base64').toString());
            console.log('Received pubsub event:', payload);
            await promiseRetry(async (retry, number) => {
                try {
                    const response = await fetch(trigger.target, { method: 'POST',  
                        body: JSON.stringify(payload), 
                        // headers: {
                        //     'Accept': 'application/json',
                        //     'Content-Type': 'application/json'
                        // }, 
                    });
                    console.log('Response:', response.status, await response.text());
                    if (response.status >= 400) {
                        throw new Error(`Got status ${response.status} from app. response: ${await response.text()}`);
                    }
                } catch (err) {
                    if (number == 5) {
                        console.error('Failed to forward event to app after 5 retries, giving up:', err);
                        return;
                    }
                    retry(err);
                }
            });
        }
        const func = functions.pubsub.topic(triggerName).onPublish(handler);
        return [triggerName, func];
    }
}));

