resource "google_monitoring_dashboard" "aiplatform_prompt_summary_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
  {
    "displayName": "App VIKI Prompt Summary",
    "mosaicLayout": {
      "columns": 48,
      "tiles": [
        {
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_input_length_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_95",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                },
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_input_length_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_50",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt input length",
            "id": ""
          }
        },
        {
          "xPos": 24,
          "yPos": 48,
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_output_tokens_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_DELTA",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_95",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                },
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_output_tokens_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_DELTA",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_50",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt output token count",
            "id": ""
          }
        },
        {
          "xPos": 24,
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_output_length_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_95",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                },
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_output_length_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_50",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt output length",
            "id": ""
          }
        },
        {
          "yPos": 48,
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_input_tokens_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_95",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                },
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_input_tokens_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_PERCENTILE_50",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt input token count",
            "id": ""
          }
        },
        {
          "xPos": 24,
          "yPos": 16,
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_input_billable_length_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                          "metric.label.\"model\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt input billable length",
            "id": ""
          }
        },
        {
          "yPos": 32,
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_step_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                          "metric.label.\"step\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt by Step",
            "id": ""
          }
        },
        {
          "xPos": 24,
          "yPos": 32,
          "width": 24,
          "height": 16,
          "widget": {
            "xyChart": {
              "dataSets": [
                {
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "filter": "metric.type=\"logging.googleapis.com/user/prompt_step_elapsedtime_metric\"",
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                          "metric.label.\"step\""
                        ]
                      }
                    },
                    "unitOverride": "",
                    "outputFullDuration": false
                  },
                  "plotType": "LINE",
                  "legendTemplate": "",
                  "minAlignmentPeriod": "60s",
                  "targetAxis": "Y1",
                  "dimensions": [],
                  "measures": [],
                  "breakdowns": []
                }
              ],
              "thresholds": [],
              "yAxis": {
                "label": "",
                "scale": "LINEAR"
              },
              "chartOptions": {
                "mode": "COLOR",
                "showLegend": false,
                "displayHorizontal": false
              }
            },
            "title": "Prompt elapsed time by Step",
            "id": ""
          }
        },
        {
          "yPos": 16,
          "width": 24,
          "height": 16,
          "widget": {
            "title": "GCP Token count",
            "xyChart": {
              "chartOptions": {
                "mode": "COLOR"
              },
              "dataSets": [
                {
                  "minAlignmentPeriod": "60s",
                  "plotType": "LINE",
                  "targetAxis": "Y1",
                  "timeSeriesQuery": {
                    "timeSeriesFilter": {
                      "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                          "resource.label.\"model_user_id\"",
                          "metric.label.\"request_type\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                      },
                      "filter": "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/token_count\" resource.type=\"aiplatform.googleapis.com/PublisherModel\""
                    }
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
    },
    "dashboardFilters": [],
    "labels": {}
  }
  )
}