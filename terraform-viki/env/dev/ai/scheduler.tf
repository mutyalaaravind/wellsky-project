
# resource "google_cloud_scheduler_job" "paperglass_e2e_medicationextraction_test_job" {
#   name        = "paperglass-e2e-medicationextraction-test-job"
#   description = "Job to trigger Viki E2E "
#   schedule    = "0 * * * *" # Every 1 hour
#   time_zone   = "UTC"       # Adjust to your preferred time zone
#   project     = var.app_project_id
#   region      = var.region

#   http_target {
#     http_method = "POST"
#     uri         = "${module.paperglass_api.url}/api/orchestrate/medication_extraction/test?mode=sample"
#     headers = {
#       Authorization : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjAwNyIsInRlbmFudElkIjoiNTQzMjEiLCJwYXRpZW50SWQiOiIyOTQzN2RkMjRmZmU0NjVlYjYxMWE2MWIwYjYyZjYwOCIsImFtdXNlcmtleSI6IjEyMzQ1In0.nNHPgG08X_YqaBN1spIKq2j0xTRT3vQmXhv-rOZ8JAU"
#       Content-Type : "application/json"
#     }
#   }
#   depends_on = [module.paperglass_api.url]
# }