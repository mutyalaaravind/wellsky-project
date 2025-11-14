resource "google_document_ai_processor" "document_ocr_processor" {
  location     = "us"
  project      = var.app_project_id
  display_name = "viki-ocr-processor"
  type         = "OCR_PROCESSOR"
}