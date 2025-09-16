terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-01-a74217d980a3-terraform-state"
    prefix = "event-planner/prod"
  }
}
