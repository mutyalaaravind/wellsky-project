resource "google_monitoring_dashboard" "aiplatform_e2e_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
  {
    "displayName": "App VIKI E2E Tests",
    "dashboardFilters": [],
    "labels": {},
    "mosaicLayout": {
      "columns": 48,
      "tiles": [
        {
          "height": 16,
          "width": 24,
          "widget": {
            "title": "E2E Test Start [SUM]",
            "id": "",
            "xyChart": {
              "chartOptions": {
                "displayHorizontal": false,
                "mode": "COLOR",
                "showLegend": false
              },
              "dataSets": [
                {
                  "breakdowns": [],
                  "dimensions": [],
                  "legendTemplate": "",
                  "measures": [],
                  "minAlignmentPeriod": "60s",
                  "plotType": "LINE",
                  "targetAxis": "Y1",
                  "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                          "metric.label.\"mode\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                      },
                      "filter": "metric.type=\"logging.googleapis.com/user/paperglass_e2e_testharness_start_metric\""
                    },
                    "unitOverride": ""
                  }
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              }
            }
          }
        },
        {
          "xPos": 24,
          "height": 16,
          "width": 24,
          "widget": {
            "title": "E2E Test Complete Testcase Count [SUM]",
            "id": "",
            "xyChart": {
              "chartOptions": {
                "displayHorizontal": false,
                "mode": "COLOR",
                "showLegend": false
              },
              "dataSets": [
                {
                  "breakdowns": [],
                  "dimensions": [],
                  "legendTemplate": "",
                  "measures": [],
                  "minAlignmentPeriod": "60s",
                  "plotType": "LINE",
                  "targetAxis": "Y1",
                  "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                          "metric.label.\"mode\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                      },
                      "filter": "metric.type=\"logging.googleapis.com/user/paperglass_e2e_testharness_complete_testcase_count_metric\""
                    },
                    "unitOverride": ""
                  }
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              }
            }
          }
        },
        {
          "yPos": 16,
          "height": 16,
          "width": 24,
          "widget": {
            "title": "E2E Test Failed [SUM]",
            "id": "",
            "pieChart": {
              "chartType": "DONUT",
              "dataSets": [
                {
                  "breakdowns": [],
                  "dimensions": [],
                  "measures": [],
                  "minAlignmentPeriod": "60s",
                  "sliceNameTemplate": "",
                  "timeSeriesQuery": {
                    "outputFullDuration": true,
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                          "metric.label.\"mode\"",
                          "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                      },
                      "filter": "metric.type=\"logging.googleapis.com/user/paperglass_e2e_testharness_failed_metric\""
                    },
                    "unitOverride": ""
                  }
                }
              ],
              "showLabels": false,
              "showTotal": false,
              "sliceAggregatedThreshold": 0
            }
          }
        },
        {
          "yPos": 16,
          "xPos": 24,
          "height": 16,
          "width": 24,
          "widget": {
            "title": "E2E Test Failed [SUM]",
            "id": "",
            "xyChart": {
              "chartOptions": {
                "displayHorizontal": false,
                "mode": "COLOR",
                "showLegend": false
              },
              "dataSets": [
                {
                  "breakdowns": [],
                  "dimensions": [],
                  "legendTemplate": "",
                  "measures": [],
                  "minAlignmentPeriod": "60s",
                  "plotType": "LINE",
                  "targetAxis": "Y1",
                  "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                          "metric.label.\"mode\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                      },
                      "filter": "metric.type=\"logging.googleapis.com/user/paperglass_e2e_testharness_failed_metric\""
                    },
                    "unitOverride": ""
                  }
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              }
            }
          }
        },
        {
          "yPos": 32,
          "height": 16,
          "width": 24,
          "widget": {
            "title": "E2E Test Complete Testcase F1",
            "id": "",
            "xyChart": {
              "chartOptions": {
                "displayHorizontal": false,
                "mode": "COLOR",
                "showLegend": false
              },
              "dataSets": [
                {
                  "breakdowns": [],
                  "dimensions": [],
                  "legendTemplate": "",
                  "measures": [],
                  "minAlignmentPeriod": "3600s",
                  "plotType": "LINE",
                  "targetAxis": "Y1",
                  "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "3600s",
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                          "metric.label.\"mode\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                      },
                      "filter": "metric.type=\"logging.googleapis.com/user/paperglass_e2e_testharness_complete_testcase_f1_metric\""
                    },
                    "unitOverride": ""
                  }
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              }
            }
          }
        },
        {
          "yPos": 32,
          "xPos": 24,
          "height": 16,
          "width": 24,
          "widget": {
            "title": "E2E Test Complete Testcase Accuracy [MEAN]",
            "id": "",
            "xyChart": {
              "chartOptions": {
                "displayHorizontal": false,
                "mode": "COLOR",
                "showLegend": false
              },
              "dataSets": [
                {
                  "breakdowns": [],
                  "dimensions": [],
                  "legendTemplate": "",
                  "measures": [],
                  "minAlignmentPeriod": "3600s",
                  "plotType": "LINE",
                  "targetAxis": "Y1",
                  "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "3600s",
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                          "metric.label.\"mode\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                      },
                      "filter": "metric.type=\"logging.googleapis.com/user/paperglass_e2e_testharness_complete_testcase_accuracy_metric\""
                    },
                    "unitOverride": ""
                  }
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              }
            }
          }
        }
      ]
    }
  }
  )
}