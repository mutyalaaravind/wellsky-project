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

const addTxtLoader = config => {
  const newRule = {
    test: /\.txt$/i,
    loader: 'raw-loader',
    options: {
      esModule: false,
    },
  }
  config.module.rules.find((r) => r.oneOf).oneOf.unshift(newRule)
  return config
};

const addWASMLoader = config => {
  const newRule = {
    test: /\.wasm$/i,
    type: 'asset/inline',
    // loader: 'url-loader',
    // options: {
    //   esModule: false,
    // },
  }
  config.module.rules.find((r) => r.oneOf).oneOf.unshift(newRule)
  return config
};

const overrideUselessBrowserifyStuffForTerribleJavaScriptPolyfillsFML = (config) => {
  const fallback = config.resolve.fallback || {};
  Object.assign(fallback, {
    // "fs": require.resolve("fs"),
    "path": require.resolve("path-browserify"),
    // "fs": require.resolve("fs"),
    // "crypto": require.resolve("crypto-browserify"),
    // "stream": require.resolve("stream-browserify"),
    // "assert": require.resolve("assert"),
    // "http": require.resolve("stream-http"),
    // "https": require.resolve("https-browserify"),
    // "os": require.resolve("os-browserify"),
    // "url": require.resolve("url")
  })
  config.resolve.fallback = fallback;
  // config.plugins = (config.plugins || []).concat([
  //   new webpack.ProvidePlugin({
  //     process: 'process/browser',
  //     Buffer: ['buffer', 'Buffer']
  //   })
  // ])
  return config;
};

module.exports = override(changeOutput, addStyleLoader, addTxtLoader, addWASMLoader);
