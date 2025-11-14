resource "google_monitoring_dashboard" "hhh_api_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
    "displayName": "App VIKI HHH API",
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
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_attachment_get_metric\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
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
            "title": "HHH API Attachments Get [SUM]",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "width": 24,
            "height": 16,
            "widget": {
            "title": "HHH API Attachments Get Elapsed Time [MEAN]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_attachment_get_elapsedtime_metric\""
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
        },
        {
            "yPos": 16,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_attachment_metadata_get_metric\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
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
            "title": "HHH API Attachment Metadata Get [SUM]",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 16,
            "width": 24,
            "height": 16,
            "widget": {
            "title": "HHH API Attachments Metadata Get Elapsed Time [MEAN]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_attachment_metadata_get_elapsedtime_metric\""
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
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_medication_get_metric\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"error\"",
                            "metric.label.\"branch\""
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
            "title": "HHH API Medication Get [SUM]",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 32,
            "width": 24,
            "height": 16,
            "widget": {
            "title": "HHH API Medication Get Elapsed Time",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_medication_get_elapsedtime_metric\""
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
        },
        {
            "yPos": 64,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_auth_metric\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": []
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
            "title": "HHH API Auth [SUM]",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 64,
            "width": 24,
            "height": 16,
            "widget": {
            "title": "HHH Auth Elapsed Time [MEAN]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_auth_elapsedtime_metric\""
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
        },
        {
            "yPos": 48,
            "width": 24,
            "height": 16,
            "widget": {
            "title": "HHH API Medication Add [SUM]",
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
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_SUM"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_medication_add_metric\""
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
        },
        {
            "xPos": 24,
            "yPos": 48,
            "width": 24,
            "height": 16,
            "widget": {
            "title": "HHH API Medication Add Elapsed Time [MEAN]",
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
                        "crossSeriesReducer": "REDUCE_MEAN",
                        "groupByFields": [
                            "metric.label.\"branch\"",
                            "metric.label.\"error\""
                        ],
                        "perSeriesAligner": "ALIGN_DELTA"
                        },
                        "filter": "metric.type=\"logging.googleapis.com/user/external_hhh_medication_add_elapsedtime_metric\""
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