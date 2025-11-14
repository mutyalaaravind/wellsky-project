// This script customizes webpack loaders without needing to eject the CRA app.
// Main tweaks:
// - Add style-loader for CSS so that we can inject styles into the widget's shadow DOM
// - Write all output to non-chunked bundle.js

// WARNING:
// After editing this file, remove ./node_modules/.cache
// I don't know why.
// I don't want to know why.
// I couldn't care less why.
// Please don't ask me why.
// Working with modern JS has already shaved off too many years of my life.
// If you think modern JS is nice, I will hunt you down and destroy your life. /AD

// Set PUBLIC_URL to "./" so that built index.html can be served from any path
// (useful for making index.html work properly when served from a CDN subdirectory)
process.env.PUBLIC_URL = './';

const addStyleLoader = (webpackConfig) => {
  // Add style-loader for CSS
  const rule = webpackConfig.module.rules[1].oneOf.find((r) => r.test.toString().includes('css'));
  // Remove mini-css-extract-plugin
  rule.use.shift();
  // Add style-loader
  rule.use.unshift({
    loader: require.resolve('style-loader'),
    options: {
      injectType: 'lazyStyleTag',
      insert: function insertStyleElement(element, options) {
        if (typeof options === 'undefined' || typeof options.target === 'undefined' || options.target === null) {
          throw new Error('target option is required when calling styles.use()');
        }
        console.log('Injecting', element, 'into', options.target);
        options.target.appendChild(element);
      }
    },
  });
  return webpackConfig;
};

const disableChunking = ({ webpackConfig }) => {
  // Write all output to non-chunked bundle.js
  webpackConfig.output.filename = 'static/js/bundle.js';
  webpackConfig.output.chunkFilename = 'static/js/[name].chunk.js';
  return webpackConfig;
};

module.exports = {
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      webpackConfig = addStyleLoader(webpackConfig);
      return webpackConfig;
    },
  },
  plugins: [
    {
      plugin: {
        overrideWebpackConfig: disableChunking,
      },
    },
  ],
};
