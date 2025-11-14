resource "google_monitoring_dashboard" "pipeline_v4_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
    "displayName": "App VIKI Pipeline V4",
    "dashboardFilters": [],
    "labels": {},
    "mosaicLayout": {
        "columns": 48,
        "tiles": [
        {
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Pipeline Success/Failed",
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
                    "plotType": "STACKED_BAR",
                    "targetAxis": "Y1",
                    "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"priority\"",
                            "metric.label.\"status\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_success_metric\""
                    },
                    "unitOverride": ""
                    }
                },
                {
                    "breakdowns": [],
                    "dimensions": [],
                    "legendTemplate": "",
                    "measures": [],
                    "minAlignmentPeriod": "60s",
                    "plotType": "STACKED_BAR",
                    "targetAxis": "Y1",
                    "timeSeriesQuery": {
                    "outputFullDuration": false,
                    "timeSeriesFilter": {
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"priority\"",
                            "metric.label.\"status\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_failed_metric\""
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
            "title": "Queue depth for Cloud Tasks",
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
                            "resource.label.\"queue_id\""
                        ],
                        "perSeriesAligner": "ALIGN_MEAN"
                        },
                        "filter": "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=monitoring.regex.full_match(\"paperglass-classification-.*\")"
                    },
                    "unitOverride": ""
                    }
                },
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
                            "resource.label.\"queue_id\""
                        ],
                        "perSeriesAligner": "ALIGN_MEAN"
                        },
                        "filter": "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=monitoring.regex.full_match(\"paperglass-extraction-.*\")"
                    },
                    "unitOverride": ""
                    }
                },
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
                            "resource.label.\"queue_id\""
                        ],
                        "perSeriesAligner": "ALIGN_MEAN"
                        },
                        "filter": "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=monitoring.regex.full_match(\"v4-extraction-.*\")"
                    },
                    "unitOverride": ""
                    }
                },
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
                            "resource.label.\"queue_id\""
                        ],
                        "perSeriesAligner": "ALIGN_MEAN"
                        },
                        "filter": "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=monitoring.regex.full_match(\"v4-paperglass-.*\")"
                    },
                    "unitOverride": ""
                    }
                },
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
                            "resource.label.\"queue_id\""
                        ],
                        "perSeriesAligner": "ALIGN_MEAN"
                        },
                        "filter": "metric.type=\"cloudtasks.googleapis.com/queue/depth\" resource.type=\"cloud_tasks_queue\" resource.label.\"queue_id\"=monitoring.regex.full_match(\"v4-status-.*\")"
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
            "title": "Gemini 1.5 Flash prompt elapsed time [MEAN]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/prompt_gemini_1_5_flash_elapsedtime_metric\""
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
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Pipeline success elapsed time [MEAN]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_success_elapsedtime_metric\""
                    },
                    "unitOverride": ""
                    }
                },
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
                        "crossSeriesReducer": "REDUCE_PERCENTILE_99",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_success_elapsedtime_metric\""
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
            "title": "Orchestration recovery attempts",
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
                            "metric.label.\"retry_attempt\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_group_classify_metric\" metric.label.\"retry_attempt\"!=\"0\""
                    },
                    "unitOverride": ""
                    }
                },
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
                            "metric.label.\"retry_attempt\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_group_medications_metric\" metric.label.\"retry_attempt\"!=\"0\""
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
            "title": "SplitPages page count [MEAN], SplitPages page count [99TH PERCENTILE]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_splitpages_pagecount_metric\""
                    },
                    "unitOverride": ""
                    }
                },
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
                        "crossSeriesReducer": "REDUCE_PERCENTILE_99",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_splitpages_pagecount_metric\""
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
            "yPos": 48,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Pipeline Failed - By Step",
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
                            "metric.label.\"step\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_failed_metric\""
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
            "yPos": 48,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Pipeline Failed - By Step/Error",
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
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"error\"",
                            "metric.label.\"step\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_failed_metric\""
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
            "yPos": 64,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Vertex AI: Character Throughput PT Quota",
            "xyChart": {
                "chartOptions": {
                "displayHorizontal": false,
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
                            "metric.label.\"request_type\"",
                            "resource.label.\"model_user_id\""
                        ],
                        "perSeriesAligner": "ALIGN_RATE"
                        },
                        "filter": "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/consumed_throughput\" resource.type=\"aiplatform.googleapis.com/PublisherModel\""
                    }
                    }
                }
                ],
                "thresholds": [],
                "yAxis": {
                "scale": "LINEAR"
                }
            }
            }
        },
        {
            "yPos": 64,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Vertex AI Endpoint - Error count [SUM]",
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
                            "metric.label.\"deployed_model_id\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"aiplatform.googleapis.com/prediction/online/error_count\" resource.type=\"aiplatform.googleapis.com/Endpoint\""
                    },
                    "unitOverride": ""
                    }
                }
                ],
                "thresholds": [
                {
                    "color": "COLOR_UNSPECIFIED",
                    "direction": "DIRECTION_UNSPECIFIED",
                    "label": "",
                    "targetAxis": "Y1",
                    "value": 10
                }
                ],
                "yAxis": {
                "label": "",
                "scale": "LINEAR"
                }
            }
            }
        },
        {
            "yPos": 80,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Vertex AI: Token Throughput PT Quota",
            "xyChart": {
                "chartOptions": {
                "displayHorizontal": false,
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
                            "metric.label.\"request_type\"",
                            "resource.label.\"model_user_id\""
                        ],
                        "perSeriesAligner": "ALIGN_RATE"
                        },
                        "filter": "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/consumed_token_throughput\" resource.type=\"aiplatform.googleapis.com/PublisherModel\""
                    }
                    }
                }
                ],
                "thresholds": [],
                "yAxis": {
                "scale": "LINEAR"
                }
            }
            }
        },
        {
            "yPos": 80,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Pipeline Start [SUM]",
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
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_start_metric\""
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
            "yPos": 96,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "DocAI: Page_OCR Number of online process document requests (US) quota usage [SUM]",
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
                            "metric.label.\"processor_type\"",
                            "metric.label.\"method\"",
                            "resource.label.\"location\""
                        ],
                        "perSeriesAligner": "ALIGN_RATE"
                        },
                        "filter": "metric.type=\"documentai.googleapis.com/quota/processor_online_process_document_requests_us/usage\" resource.type=\"documentai.googleapis.com/Location\""
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
            "yPos": 96,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Orchestration Page Classification StepGroup elapsed time (Classification & OCR)",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_group_classify_elapsedtime_metric\""
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
            "yPos": 112,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Orchestration Page Classification StepGroup (Classify & OCR)",
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
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_group_classify_metric\""
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
            "yPos": 112,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Pipeline Group Medications Elapsed Time (Medications & Medispan)",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_group_medications_elapsedtime_metric\""
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
            "yPos": 128,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Orchestration Medication Extraction StepGroup (Medications & Medispan)",
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
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/pipeline_group_medications_metric\""
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
            "yPos": 128,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Gemini - Prediction Count",
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
                            "metric.label.\"request_type\"",
                            "resource.label.\"model_user_id\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/model_invocation_count\" resource.type=\"aiplatform.googleapis.com/PublisherModel\""
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
            "yPos": 144,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Gemini 1.5 Flash prompt",
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
                            "metric.label.\"priority\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/prompt_gemini_1_5_flash_metric\""
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
            "yPos": 144,
            "xPos": 24,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Model invocation latencies [99TH PERCENTILE]",
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
                        "crossSeriesReducer": "REDUCE_PERCENTILE_99",
                        "groupByFields": [
                            "resource.label.\"model_user_id\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"aiplatform.googleapis.com/publisher/online_serving/model_invocation_latencies\" resource.type=\"aiplatform.googleapis.com/PublisherModel\""
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
            "yPos": 160,
            "height": 16,
            "width": 24,
            "widget": {
            "title": "Document AI Usage (OCR)",
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
                        "groupByFields": [],
                        "perSeriesAligner": "ALIGN_MEAN"
                        },
                        "filter": "metric.type=\"documentai.googleapis.com/quota/processor_online_process_document_requests_us/limit\" resource.type=\"documentai.googleapis.com/Location\""
                    },
                    "unitOverride": ""
                    }
                },
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
                        "groupByFields": [],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"documentai.googleapis.com/quota/processor_online_process_document_requests_us/usage\" resource.type=\"documentai.googleapis.com/Location\""
                    },
                    "unitOverride": ""
                    }
                },
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
                        "groupByFields": [],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"documentai.googleapis.com/quota/processor_online_process_document_requests_us/exceeded\" resource.type=\"documentai.googleapis.com/Location\""
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