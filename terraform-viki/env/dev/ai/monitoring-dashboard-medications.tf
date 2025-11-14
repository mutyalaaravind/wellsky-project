resource "google_monitoring_dashboard" "aiplatform_medications_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
      "displayName" : "App VIKI Medications",
      "mosaicLayout" : {
        "columns" : 48,
        "tiles" : [
          {
            "xPos" : 24,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "pieChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_evidencelinking_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"status\""
                          ]
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : true
                    },
                    "sliceNameTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "dimensions" : [],
                    "measures" : []
                  }
                ],
                "chartType" : "DONUT",
                "showTotal" : false,
                "showLabels" : false,
                "sliceAggregatedThreshold" : 0
              },
              "title" : "Evidence linked",
              "id" : ""
            }
          },
          {
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_evidencelinking_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"status\""
                          ]
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : false
                    },
                    "plotType" : "STACKED_BAR",
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
              "title" : "Evidence linked",
              "id" : ""
            }
          },
          {
            "yPos" : 16,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "title" : "Avg Medications per page",
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
                          "crossSeriesReducer" : "REDUCE_PERCENTILE_50",
                          "groupByFields" : [],
                          "perSeriesAligner" : "ALIGN_DELTA"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_medicationsperpage_metric\""
                      }
                    }
                  },
                  {
                    "minAlignmentPeriod" : "60s",
                    "plotType" : "LINE",
                    "targetAxis" : "Y1",
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "crossSeriesReducer" : "REDUCE_PERCENTILE_95",
                          "groupByFields" : [],
                          "perSeriesAligner" : "ALIGN_DELTA"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_medicationsperpage_metric\""
                      }
                    }
                  },
                  {
                    "minAlignmentPeriod" : "60s",
                    "plotType" : "LINE",
                    "targetAxis" : "Y1",
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "crossSeriesReducer" : "REDUCE_PERCENTILE_99",
                          "groupByFields" : [],
                          "perSeriesAligner" : "ALIGN_DELTA"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_medicationsperpage_metric\""
                      }
                    }
                  },
                  {
                    "minAlignmentPeriod" : "60s",
                    "plotType" : "LINE",
                    "targetAxis" : "Y1",
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "crossSeriesReducer" : "REDUCE_PERCENTILE_05",
                          "groupByFields" : [],
                          "perSeriesAligner" : "ALIGN_DELTA"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_medicationsperpage_metric\""
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
            }
          }
        ]
      },
      "dashboardFilters" : [],
      "labels" : {}
    }
  )
}