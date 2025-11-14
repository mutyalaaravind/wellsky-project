
resource "google_monitoring_dashboard" "aiplatform_summary_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
      "displayName" : "App VIKI Summary",
      "mosaicLayout" : {
        "columns" : 48,
        "tiles" : [
          {
            "yPos" : 64,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"documentai.googleapis.com/quota/processor_online_process_document_requests_us/usage\" resource.type=\"documentai.googleapis.com/Location\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_RATE",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"processor_type\"",
                            "metric.label.\"method\"",
                            "resource.label.\"location\""
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
              "title" : "DocAI: Page_OCR Number of online process document requests (US) quota usage [SUM]",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "title" : "Queue depth for Cloud Tasks",
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
                            "resource.label.\"queue_id\""
                          ],
                          "perSeriesAligner" : "ALIGN_MEAN"
                        },
                        "filter" : "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=\"paperglass-extraction-queue\""
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
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "resource.label.\"queue_id\""
                          ],
                          "perSeriesAligner" : "ALIGN_MEAN"
                        },
                        "filter" : "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=\"paperglass-classification-queue\""
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
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "resource.label.\"queue_id\""
                          ],
                          "perSeriesAligner" : "ALIGN_MEAN"
                        },
                        "filter" : "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=\"paperglass-extraction-priority-queue\""
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
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "resource.label.\"queue_id\""
                          ],
                          "perSeriesAligner" : "ALIGN_MEAN"
                        },
                        "filter" : "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=\"paperglass-classification-priority-queue\""
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
          },
          {
            "xPos" : 24,
            "yPos" : 16,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "title" : "Orchestration success elapsed time [MEAN]",
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
                          "groupByFields" : [
                            "metric.label.\"priority\""
                          ],
                          "perSeriesAligner" : "ALIGN_DELTA"
                        },
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_success_elapsedtime_metric\" resource.type=\"cloud_run_revision\""
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
          },
          {
            "xPos" : 24,
            "yPos" : 64,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_documentcreated_metric\"",
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
              "title" : "Document created [SUM]",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "yPos" : 32,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_splitpages_pagecount_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
              "title" : "SplitPages page count [MEAN]",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "yPos" : 96,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_extraction_elapsedtime_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
                  },
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_extraction_waittime_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
              "title" : "Orchestration Medication Extraction StepGroup elapsed time [MEAN], ...",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "yPos" : 80,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_classification_elapsedtime_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
                  },
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_classification_waittime_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
              "title" : "Orchestration Page Classification StepGroup elapsed time",
              "id" : ""
            }
          },
          {
            "yPos" : 112,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/prompt_gemini_1_5_flash_metric\"",
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
              "title" : "Gemini 1.5 Flash prompt",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/prompt_gemini_1_5_flash_elapsedtime_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
              "title" : "Gemini 1.5 Flash prompt elapsed time [MEAN]",
              "id" : ""
            }
          },
          {
            "yPos" : 80,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_classification_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_DELTA",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
              "title" : "Orchestration Page Classification StepGroup",
              "id" : ""
            }
          },
          {
            "yPos" : 96,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_extraction_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_MEAN",
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
              "title" : "Orchestration Medication Extraction StepGroup",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "yPos" : 48,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"aiplatform.googleapis.com/prediction/online/error_count\" resource.type=\"aiplatform.googleapis.com/Endpoint\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"deployed_model_id\""
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
              "title" : "Vertex AI Endpoint - Error count [SUM]",
              "id" : ""
            }
          },
          {
            "xPos" : 24,
            "yPos" : 112,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/model_invocation_count\" resource.type=\"aiplatform.googleapis.com/PublisherModel\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"request_type\"",
                            "resource.label.\"model_user_id\""
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
              "title" : "Gemini - Prediction Count",
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
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_failed_metric\"",
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
                    "plotType" : "STACKED_BAR",
                    "legendTemplate" : "",
                    "minAlignmentPeriod" : "60s",
                    "targetAxis" : "Y1",
                    "dimensions" : [],
                    "measures" : [],
                    "breakdowns" : []
                  },
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_success_metric\"",
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
              "title" : "Orchestration Success/Failed",
              "id" : ""
            }
          },
          {
            "yPos" : 32,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"logging.googleapis.com/user/orchestration_medicationextraction_recover_metric\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
                          "crossSeriesReducer" : "REDUCE_SUM",
                          "groupByFields" : [
                            "metric.label.\"step_group\"",
                            "metric.label.\"retry_count\""
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
              "title" : "Orchestration recovery attempts",
              "id" : ""
            }
          },
          {
            "yPos" : 48,
            "width" : 24,
            "height" : 16,
            "widget" : {
              "xyChart" : {
                "dataSets" : [
                  {
                    "timeSeriesQuery" : {
                      "timeSeriesFilter" : {
                        "filter" : "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/consumed_throughput\" resource.type=\"aiplatform.googleapis.com/PublisherModel\"",
                        "aggregation" : {
                          "alignmentPeriod" : "60s",
                          "perSeriesAligner" : "ALIGN_SUM",
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
              "title" : "Vertex AI: Character Throughput [SUM]",
              "id" : ""
            }
          }
        ]
      },
      "dashboardFilters" : [],
      "labels" : {}
    }
  )
}