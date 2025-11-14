# Formographer

This is a simple API that uses free text to fill in the provided form.

## Usage

```sh
gcloud auth login
gcloud auth application-default login
make run
```

Now go to <http://127.0.0.1:12001>.

## GraphQL API

GraphQL query UI is available at <http://127.0.0.1:12000/graphql/>.

```gql
mutation M1 {
  complete_form(
    text: "Patient's name is Andrew Johnson, 48 years old. They are taking Zoloft and Diazepam. He was admitted with anemia.",
    form_fields: [
      {
        name: "name",
        question: "Is patient male, female, or unknown? One word please"
      },
      {
        name: "name",
        question: "What is patient's age? One word please"
      },
      {
        name: "name",
        question: "What medications is patient taking? Please give comma-separated string"
     },
    ]
  ) {
    error
    form_values {
      name
      value
    }
  }
}
```

Here's a quick-and-dirty example on asking the model to generate proper JSON:

```gql
mutation M2 {
  complete_form(
    text: "Patient's name is Andrew Johnson, 48 years old. They are taking Zoloft & Diazepam. He was admitted with anemia.",
    form_fields: [
      {
        name: "test",
        question: """
Generate JSON for schema:
  
{
    "type": "object",
    "properties": {
        "patient_name": {
            "type": "string"
        },
        "patient_age": {
            "type": "integer"
        },
        "patient_medications": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}
""",
      }
    ]
  ) {
    error
    form_values {
      name
      value
    }
  }
}
```
