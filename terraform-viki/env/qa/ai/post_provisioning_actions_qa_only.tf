resource "null_resource" "post_provisioning_action_api_call" {
  triggers = {
    always_run     = "${timestamp()}" # This will make it run on every apply
    paperglass_url = module.paperglass_api.url
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${var.paperglass_api_token}" \
        -d '{}' \
        ${module.paperglass_api.url}/api/orchestrate/medication_extraction/test?runnow=true&mode=sample&sample_size=10
    EOT
  }

  # Make this run after other resources
  depends_on = [
    module.medication_extraction_api,
    module.medication_extraction_api_2,
    module.paperglass_api
  ]
}