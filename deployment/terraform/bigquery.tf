resource "google_bigquery_dataset" "weather_dataset" {
  dataset_id = "weather"
  location   = "US"
  description   = "This is dataset for saving weather data"
}

resource "google_bigquery_table" "my_table" {
  dataset_id = google_bigquery_dataset.weather_dataset.dataset_id
  table_id   = "my_terraform_table"

  labels = {
    env = "dev"
  }

  schema = <<EOF
[
  {
    "name": "id",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "The unique identifier."
  },
  {
    "name": "name",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The name of the item."
  },
  {
    "name": "created_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE",
    "description": "The timestamp when the record was created."
  }
]
EOF
}