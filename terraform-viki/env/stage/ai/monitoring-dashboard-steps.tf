resource "google_monitoring_dashboard" "aiplatform_step_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
      "displayName" : "App VIKI Steps",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_step_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"step_id\""
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
              "title" : "Orchestration Step",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_step_elapsedtime_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
                          "groupByFields" : [
                            "metric.label.\"step_id\""
                          ]
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
              "title" : "Orchestration Step Elapsed Time",
              "id" : ""
            }
          },
          {
            "widget" : {
              "title" : "Orchestration StepGroup CloudTask submit",
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
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"priority\"",
                            "metric.label.\"category\""
                          ],
                          "perSeriesAligner" : "ALIGN_SUM"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_stepgroup_cloudtask_enqueue_metric\""
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
            "yPos" : 16
          }
        ]
      },
      "dashboardFilters" : [],
      "labels" : {}
    }
  )
}