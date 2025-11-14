resource "google_monitoring_dashboard" "aiplatform_grader_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
      "displayName" : "App VIKI Grader",
      "mosaicLayout" : {
        "columns" : 48,
        "tiles" : [
          {
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/medication_medispan_matched_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : []
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : false
                    },
                    "plotType" : "LINE",
                    "legendTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "targetAxis" : "Y1",
                    "dimensions" : [],
                    "measures" : [],
                    "breakdowns" : []
                  }
                ],
                "thresholds" : [],
                "yAxis" : {
                  "label" : "",
                  "scale" : "LINEAR"
                },
                "chartOptions" : {
                  "mode" : "COLOR",
                  "showLegend" : false,
                  "displayHorizontal" : false
                }
              },
              "title" : "Medication matched to Medispan",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/medication_medispan_unmatched_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : []
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : false
                    },
                    "plotType" : "LINE",
                    "legendTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "targetAxis" : "Y1",
                    "dimensions" : [],
                    "measures" : [],
                    "breakdowns" : []
                  }
                ],
                "thresholds" : [],
                "yAxis" : {
                  "label" : "",
                  "scale" : "LINEAR"
                },
                "chartOptions" : {
                  "mode" : "COLOR",
                  "showLegend" : false,
                  "displayHorizontal" : false
                }
              },
              "title" : "Medication not matched to Medispan",
              "id" : ""
            }
          },
          {
            "yPos" : 16,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_grader_start_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : []
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : false
                    },
                    "plotType" : "LINE",
                    "legendTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "targetAxis" : "Y1",
                    "dimensions" : [],
                    "measures" : [],
                    "breakdowns" : []
                  }
                ],
                "thresholds" : [],
                "yAxis" : {
                  "label" : "",
                  "scale" : "LINEAR"
                },
                "chartOptions" : {
                  "mode" : "COLOR",
                  "showLegend" : false,
                  "displayHorizontal" : false
                }
              },
              "title" : "Orchestration grader start",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "yPos" : 16,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_grader_failed_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : []
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : false
                    },
                    "plotType" : "LINE",
                    "legendTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "targetAxis" : "Y1",
                    "dimensions" : [],
                    "measures" : [],
                    "breakdowns" : []
                  }
                ],
                "thresholds" : [],
                "yAxis" : {
                  "label" : "",
                  "scale" : "LINEAR"
                },
                "chartOptions" : {
                  "mode" : "COLOR",
                  "showLegend" : false,
                  "displayHorizontal" : false
                }
              },
              "title" : "Orchestration grader failed",
              "id" : ""
            }
          },
          {
            "widget" : {
              "title" : "Medication grader score",
              "xyChart" : {
                "chartOptions" : {
                  "mode" : "COLOR"
                },
                "dataSets" : [
                  {
                    "minAlignmentPeriod" : "60s",
                    "plotType" : "LINE",
                    "targetAxis" : "Y1",
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "crossSeriesReducer" : "REDUCE_MEAN",
                          "groupByFields" : [],
                          "perSeriesAligner" : "ALIGN_DELTA"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medication_grader_score_metric\""
                      }
                    }
                  }
                ],
                "thresholds" : [],
                "yAxis" : {
                  "label" : "",
                  "scale" : "LINEAR"
                }
              }
            },
            "height" : 16,
            "width" : 24,
            "yPos" : 32
          }
        ]
      },
      "dashboardFilters" : [],
      "labels" : {}
    }
  )
}