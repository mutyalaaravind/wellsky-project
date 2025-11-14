resource "google_monitoring_dashboard" "aiplatform_firestore_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
      "displayName" : "App VIKI Firestore",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/firestore_operation_create_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"collection\""
                          ]
                        }
                      },
                      "unitOverride" : "",
                      "outputFullDuration" : false
                    },
                    "plotType" : "LINE",
                    "legendTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "targetAxis" : "Y2",
                    "dimensions" : [],
                    "measures" : [],
                    "breakdowns" : []
                  }
                ],
                "thresholds" : [],
                "y2Axis" : {
                  "label" : "",
                  "scale" : "LINEAR"
                },
                "chartOptions" : {
                  "mode" : "COLOR",
                  "showLegend" : false,
                  "displayHorizontal" : false
                }
              },
              "title" : "Firestore Create Operations",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/firestore_operation_update_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"collection\""
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
              "title" : "Firestore Update Operations",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/firestore_operation_event_metric\"",
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
              "title" : "Firestore Event Operations",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/firestore_operation_rollback_metric\"",
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
              "title" : "Firestore Rollback",
              "id" : ""
            }
          },
          {
            "yPos" : 32,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "logsPanel" : {
                "filter" : "\"FirestoreUnitOfWork::__aexit__ error\"\nseverity=(EMERGENCY OR ALERT OR CRITICAL OR ERROR)\n",
                "resourceNames" : [
                  "projects/viki-stage-app-wsky/locations/global/logScopes/_Default"
                ]
              },
              "title" : "Firestore Error Logs",
              "id" : ""
            }
          },
          {
            "widget" : {
              "title" : "Firestore Error",
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
                            "metric.label.\"excType\""
                          ],
                          "perSeriesAligner" : "ALIGN_SUM"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/firestore_operation_error_metric\""
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
            "xPos" : 24,
            "yPos" : 32
          }
        ]
      },
      "dashboardFilters" : [],
      "labels" : {}
    }
  )
}