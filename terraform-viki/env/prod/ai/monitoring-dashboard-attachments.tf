resource "google_monitoring_dashboard" "aiplatform_attachments_dashboard" {
  project = var.app_project_id
  dashboard_json = jsonencode(
    {
    "displayName": "App VIKI Attachments",
    "mosaicLayout": {
        "columns": 48,
        "tiles": [
        {
            "yPos": 15,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_metric\"",
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
            "title": "Attachment event",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 31,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_updatefilter_metric\"",
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
            "title": "Attachment event filter: Skip Updates",
            "id": ""
            }
        },
        {
            "yPos": 31,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_whitelistfilter_metric\"",
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
                },
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_missingmetadatafilter_metric\"",
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
            "title": "Attachment event filter: Skip (Whitelist & Missing Metadata)",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 47,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_retrievalerror_metric\"",
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
            "title": "Attachment event filter: Retrieval error",
            "id": ""
            }
        },
        {
            "yPos": 47,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_unsupportedtypefilter_metric\"",
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
            "title": "Attachment event filter: Unsupported type",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 15,
            "width": 24,
            "height": 16,
            "widget": {
            "xyChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_accept_metric\"",
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
            "title": "Attachment event: Accept",
            "id": ""
            }
        },
        {
            "yPos": 79,
            "width": 24,
            "height": 16,
            "widget": {
            "pieChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_unsupportedtypefilter_metric\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"file_type\""
                        ]
                        }
                    },
                    "unitOverride": "",
                    "outputFullDuration": true
                    },
                    "sliceNameTemplate": "",
                    "minAlignmentPeriod": "60s",
                    "dimensions": [],
                    "measures": [],
                    "breakdowns": []
                }
                ],
                "chartType": "DONUT",
                "showTotal": false,
                "showLabels": false,
                "sliceAggregatedThreshold": 0
            },
            "title": "Attachment event filter: Unsupported type by File Type",
            "id": ""
            }
        },
        {
            "xPos": 24,
            "yPos": 63,
            "width": 24,
            "height": 16,
            "widget": {
            "pieChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_accept_metric\" metric.label.\"branch\"=\"ImportHostAttachmentFromExternalStorageUri\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"file_type\""
                        ]
                        }
                    },
                    "unitOverride": "",
                    "outputFullDuration": true
                    },
                    "sliceNameTemplate": "",
                    "minAlignmentPeriod": "60s",
                    "dimensions": [],
                    "measures": [],
                    "breakdowns": []
                }
                ],
                "chartType": "DONUT",
                "showTotal": false,
                "showLabels": false,
                "sliceAggregatedThreshold": 0
            },
            "title": "Attachment event filter: Accepted by File Type (PubSub)",
            "id": ""
            }
        },
        {
            "yPos": 63,
            "width": 24,
            "height": 16,
            "widget": {
            "pieChart": {
                "dataSets": [
                {
                    "timeSeriesQuery": {
                    "timeSeriesFilter": {
                        "filter": "metric.type=\"logging.googleapis.com/user/orchestration_attachmentevent_accept_metric\" metric.label.\"branch\"=\"ImportHostAttachments\"",
                        "aggregation": {
                        "alignmentPeriod": "60s",
                        "perSeriesAligner": "ALIGN_SUM",
                        "crossSeriesReducer": "REDUCE_SUM",
                        "groupByFields": [
                            "metric.label.\"file_type\""
                        ]
                        }
                    },
                    "unitOverride": "",
                    "outputFullDuration": true
                    },
                    "sliceNameTemplate": "",
                    "minAlignmentPeriod": "60s",
                    "dimensions": [],
                    "measures": [],
                    "breakdowns": []
                }
                ],
                "chartType": "DONUT",
                "showTotal": false,
                "showLabels": false,
                "sliceAggregatedThreshold": 0
            },
            "title": "Attachment event filter: Accepted by File Type (API)",
            "id": ""
            }
        },
        {
            "width": 48,
            "height": 15,
            "widget": {
            "title": "Overview",
            "collapsibleGroup": {
                "collapsed": true
            },
            "id": ""
            }
        },
        {
            "xPos": 1,
            "width": 46,
            "height": 15,
            "widget": {
            "title": "Graph Summary",
            "text": {
                "content": "## Attachment event\r\nThe volume of attachment events sent from HHH to Viki\r\n\r\n## Attachment event: Accept\r\nThe volume of attachements which passed filters and are imported into Viki\r\n\r\n## Attachment event filter: Skip Not on Tenant Whitelist\r\nIf the attachment was for a tenant which is not on the whitelist, the attachment will be filtered.  This shows the volume of attachments filtered for this reason.\r\n\r\n## Attachment event filter: Skip Updates\r\nIf the attachment was an update to an older document, the attachment will be filtered.  This shows the volume of attachments filtered for this reason.\r\n\r\n## Attachment event filter: Unsupported type\r\nIf the attachment is not for a supported type, the attachment will be filtered.  This shows the volume of attachments filtered for this reason.\r\n\r\n## Attachment event filter: Retrieval error\r\nIf the attachment could not be retrieved from Google storage, the attachment will not be processed.  This shows the volume of attachments filtered for this reason.",
                "format": "MARKDOWN",
                "style": {
                "backgroundColor": "#FFFFFF",
                "textColor": "#212121",
                "horizontalAlignment": "H_LEFT",
                "verticalAlignment": "V_TOP",
                "padding": "P_EXTRA_SMALL",
                "fontSize": "FS_LARGE",
                "pointerLocation": "POINTER_LOCATION_UNSPECIFIED"
                }
            },
            "id": ""
            }
        }
        ]
    },
    "dashboardFilters": [],
    "labels": {}
    }
  )
}