(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.layout-mapper-service', [])
        .factory('pvLayoutMapperService', pvLayoutMapperService);

    function pvLayoutMapperService() {

        var one_column_layouts = {},
            three_column_layouts = {},
            five_column_layouts = {},
            two_column_layouts = {},
            four_column_layouts = {},
            unit_height = 38, //in px
            //CellHeights in %
            cellHeight100Percent = 1,
            cellHeight65Percent = 0.65,
            cellHeight58Percent = 0.58,
            cellHeight50Percent = 0.5,
            cellHeight42Percent = 0.42,
            cellHeight35Percent = 0.35;
        // 5c
        five_column_layouts = {
            "fiveCell": {
                "t1": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5",
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5",
                                }
                            }]
                        },
                        {
                            index: 3,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5",
                                }
                            }]
                        },
                        {
                            index: 4,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                            }]
                        },
                        {
                            index: 5,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5",
                                }
                            }]
                        }
                    ]
                }
            }
        };
        // 4c
        four_column_layouts = {
            "fourCell": {
                "t1": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        },
                        {
                            index: 3,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 4,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5",
                                }
                            }]
                        }
                    ]
                },
                "t2": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            }]
                        },
                        {
                            index: 2,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        },
                        {
                            index: 3,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            }]
                        },
                        {
                            index: 4,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            }]
                        }
                    ]
                }
            }
        };
        // 3c
        three_column_layouts = {
            "sixCell": {
                "t1": {
                    rowHeight: unit_height * 2,
                    layout: [{
                            index: 1,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-top": "none"
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span6",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-top": "none",
                                        "border-left": "solid 1px #d5d5d5"
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span6",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-top": "none",
                                        "border-left": "solid 1px #d5d5d5"

                                    }
                                },
                                {
                                    index: 3,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                        "border-top": "solid 1px #d5d5d5"
                                    }
                                }
                            ]
                        },
                        {
                            index: 3,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                        "border-bottom": "solid 1px #d5d5d5"
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "t2": {
                    rowHeight: unit_height * 2,
                    layout: [{
                            index: 1,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span6",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-right": "solid 1px #d5d5d5"
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span6",
                                    cellHeight: cellHeight50Percent,

                                },
                                {
                                    index: 3,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-top": "solid 1px #d5d5d5"
                                    }

                                }
                            ]
                        },
                        {
                            index: 2,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }, {
                            index: 3,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                        "border-bottom": "solid 1px #d5d5d5",
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                    }
                                }
                            ]
                        }
                    ]
                },
                "t3": {
                    rowHeight: unit_height * 2,
                    layout: [{
                            index: 1,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-bottom": "solid 1px #d5d5d5"
                                    }

                                },
                                {
                                    index: 2,
                                    span: "span6",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-right": "solid 1px #d5d5d5"
                                    }

                                },
                                {
                                    index: 3,
                                    span: "span6",
                                    cellHeight: cellHeight50Percent,
                                }
                            ]
                        },
                        {
                            index: 2,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }, {
                            index: 3,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                        "border-bottom": "solid 1px #d5d5d5",
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                    }
                                }
                            ]
                        }
                    ]
                },
                "t4": {
                    rowHeight: unit_height * 2,
                    layout: [{
                            index: 1,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight42Percent,
                                    style: {
                                        "border-bottom": "solid 1px #d5d5d5"
                                    }

                                },
                                {
                                    index: 2,
                                    span: "span6",
                                    cellHeight: cellHeight58Percent,
                                    style: {
                                        "border-right": "solid 1px #d5d5d5"
                                    }

                                },
                                {
                                    index: 3,
                                    span: "span6",
                                    cellHeight: cellHeight42Percent
                                }
                            ]
                        },
                        {
                            index: 2,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }, {
                            index: 3,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight42Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                        "border-bottom": "solid 1px #d5d5d5",
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight58Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5",
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
            "fiveCell": {
                "t1": {
                    rowHeight: unit_height * 2,
                    layout: [{
                            index: 1,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-bottom": "solid 1px #d5d5d5",
                                        "border-right": "solid 1px #d5d5d5"
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-right": "solid 1px #d5d5d5"
                                    }
                                }
                            ]
                        },
                        {
                            index: 2,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,

                            }]
                        },
                        {
                            index: 3,
                            span: "span4",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-bottom": "solid 1px #d5d5d5",
                                        "border-left": "solid 1px #d5d5d5"
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5"
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
            "threeCell": {
                "t1": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span8",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 3,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        }
                    ]
                },
                "t2": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span7",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 3,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        }
                    ]
                },
                "t3": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 3,
                            span: "span8",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        }
                    ]
                },
                "t4": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 2,
                            span: "span5",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-right": "solid 1px #d5d5d5"
                                }
                            }]
                        },
                        {
                            index: 3,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        }
                    ]
                }
            }
        };
        // 2c
        two_column_layouts = {
            "twoCell": {
                "t1": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span9",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,

                            }]
                        },
                        {
                            index: 2,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                     "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }
                    ]
                },
                "t2": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span6",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,

                            }]
                        },
                        {
                            index: 2,
                            span: "span6",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"                                    
                                }
                            }]
                        }
                    ]
                },
                "t3": {
                    rowHeight: unit_height * 2,
                    layout: [{
                            index: 1,
                            span: "span6",
                            cells: [{
                                    index: 1,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-bottom": "solid 1px #d5d5d5"
                                    }
                                },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                }
                            ]
                        },
                        {
                            index: 2,
                            span: "span6",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }
                    ]
                },
                "t4": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span10",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,

                            }]
                        },
                        {
                            index: 2,
                            span: "span2",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }
                    ]
                },
                "t5": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span8",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: 1
                            }]
                        },
                        {
                            index: 2,
                            span: "span4",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                        }
                    ]
                },
                "t6": {
                    rowHeight: unit_height/2,
                    layout: [{
                            index: 1,
                            span: "span9",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent                             
                            }]
                        },
                        {
                            index: 2,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent                                
                            }]
                        }
                    ]
                },
                "t7": {
                    rowHeight: unit_height,
                    layout: [{
                            index: 1,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent                       
                            }]
                        },
                        {
                            index: 2,
                            span: "span9",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            }]
                        }
                    ]
                }
            },
            "fourCell": {
                "t1": {
                    rowHeight: unit_height * 2,
                    layout: [{
                        index: 1,
                        span: "span9",
                        cells: [{
                            index: 1,
                            span: "span6",
                            cellHeight: cellHeight100Percent
                        },
                            {
                                index: 2,
                                span: "span6",
                                cellHeight: cellHeight100Percent,
                                style: {
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            }]
                    },
                        {
                            index: 2,
                            span: "span3",
                            cells: [{
                                index: 1,
                                span: "span12",
                                cellHeight: cellHeight50Percent,
                                style: {
                                    "border-bottom": "solid 1px #d5d5d5",
                                    "border-left": "solid 1px #d5d5d5"
                                }
                            },
                                {
                                    index: 2,
                                    span: "span12",
                                    cellHeight: cellHeight50Percent,
                                    style: {
                                        "border-left": "solid 1px #d5d5d5"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }	            
        };
        // 1c
        one_column_layouts = {
            "oneCell": {
                "t1": {
                    rowHeight: unit_height,
                    layout: [{
                        index: 1,
                        span: "span12",

                        cells: [{
                            index: 1,
                            cellHeight: cellHeight100Percent,
                            span: "span12"
                        }]
                    }]
                },
                "t2": {
                    rowHeight: unit_height,
                    layout: [{
                        index: 1,
                        span: "span12",
                        cells: [{
                            index: 1,
                            cellHeight: cellHeight100Percent,
                            span: "span12"
                        }]
                    }]
                },
                "t3": {
                    rowHeight: unit_height,
                    layout: [{
                        index: 1,
                        span: "span12",
                        cells: [{
                            index: 1,
                            cellHeight: cellHeight100Percent,
                            style: {
                                "color":"#FFF",
                                "font-weight":"bold",
                                "vertical-align":"middle",
                                "background-color":"#ccc"
                            }
                        }]
                    }]
                },
                "t4": {
                    rowHeight: unit_height / 2,
                    layout: [{
                        index: 1,
                        span: "span12",
                        cells: [{
                            index: 1,
                            cellHeight: cellHeight100Percent,
                            span: "span12"
                        }]
                    }]
                },
                "t5": {
                    rowHeight: unit_height,
                    layout: [{
                        index: 1,
                        span: "span12",
                        cells: [{
                            index: 1,
                            cellHeight: cellHeight100Percent,
                            span: "span12"
                        }]
                    }]
                }
            },
            "twoCell": {
                "t1": {
                    rowHeight: unit_height / 2,
                    layout: [{
                        index: 1,
                        span: "span12",
                        cells: [{
                            index: 1,
                            span: "span12",
                            cellHeight: cellHeight100Percent
                        },
                        {
                            index: 2,
                            span: "span12",
                            cellHeight: cellHeight100Percent
                        }]
                    }]
                }
            },
            "fiveCell": {
                "t1": {
                    rowHeight: unit_height / 2,
                    layout: [{
                        index: 1,
                        span: "span12",
                        cells: [{
                            index: 1,
                            span: "span12",
                            cellHeight: cellHeight100Percent
                            },
                            {
                                index: 2,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            },
                            {
                                index: 3,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            },
                            {
                                index: 4,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            },
                            {
                                index: 5,
                                span: "span12",
                                cellHeight: cellHeight100Percent
                            }
                    ]}
                ]}
            }
        };

        function getRowLayout(layoutName) {
            var layoutKeys = [],
                layout_columns = {};
            angular.isDefined(layoutKeys) ? layoutKeys = layoutName.split('-') : layoutKeys = [];
            if (layoutKeys.length > 1) {
                layout_columns = this.column_layouts[layoutKeys[0]][layoutKeys[1]][layoutKeys[2]];
            }
            return layout_columns === undefined ? [] : layout_columns.layout;
        }
        // returns row height of given layout
        function getRowHeight(layoutName) {
            var layoutKeys = [],
                layout_columns = {};
            angular.isDefined(layoutKeys) && angular.isDefined(layoutName) ? layoutKeys = layoutName.split('-') : layoutKeys = [];
            if (layoutKeys.length > 0) {
                layout_columns = this.column_layouts[layoutKeys[0]][layoutKeys[1]][layoutKeys[2]];
            }
            return layout_columns === undefined ? 0 : layout_columns.rowHeight;
        }
        //returns cell height
        function getCellHeight(layoutName, columnIndex, cellIndex, rowHeight) {
            var layoutKeys = [],
                cellHeight = 0,
                layoutRef = {};
            angular.isDefined(layoutKeys) ? layoutKeys = layoutName.split('-') : layoutKeys = [];
            if (layoutKeys.length > 0) {
                layoutRef = this.column_layouts[layoutKeys[0]][layoutKeys[1]][layoutKeys[2]];
                cellHeight = (angular.isDefined(rowHeight) ? rowHeight : layoutRef.rowHeight) * layoutRef.layout[columnIndex].cells[cellIndex].cellHeight;
            }
            return cellHeight;
        }

        return {
            getRowLayout: getRowLayout,
            getRowHeight: getRowHeight,
            getCellHeight: getCellHeight,
            column_layouts: {
                "oneColumn": one_column_layouts,
                "twoColumn": two_column_layouts,
                "threeColumn": three_column_layouts,
                "fourColumn": four_column_layouts,
                "fiveColumn": five_column_layouts
            }
        };
    }
})();