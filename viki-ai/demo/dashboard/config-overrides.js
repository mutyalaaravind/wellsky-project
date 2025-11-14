const { override, adjustStyleLoaders } = require('customize-cra');
const webpack = require('webpack');

const changeOutput = (config) => {
  config.output = {
    ...config.output,
    filename: 'static/js/bundle.js',
    chunkFilename: 'static/js/[name].chunk.js',
  };
  return config;
};

const addStyleLoader = adjustStyleLoaders(({ use }) => {
  use.forEach((loader) => {
    if (/mini-css-extract-plugin/.test(loader.loader)) {
      loader.loader = require.resolve('style-loader');
      // Default injectType is "styleTag" - https://webpack.js.org/loaders/style-loader/#injecttype
      // loader.options = {
      //   injectType: 'lazySingletonStyleTag',
      //   insert: function insertIntoTarget(element, options) {
      //     const parent = options.target || document.body;
      //     parent.appendChild(element);
      //   },
      // };
    }
  });
});

module.exports = override(changeOutput, addStyleLoader);

