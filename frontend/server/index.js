/* eslint consistent-return:0 */

const express = require('express');
const logger = require('./logger');

const argv = require('minimist')(process.argv.slice(2));
const setup = require('./middlewares/frontendMiddleware');
const resolve = require('path').resolve;
const app = express();
const requestProxy = require('express-request-proxy');

// If you need a backend, e.g. an API, add your custom backend-specific middleware here
app.use('/api/*', requestProxy({
  url: 'http://localhost:5000/*',
  timeout: 99999,
}));

app.use('/static/*', requestProxy({
  url: 'http://localhost:5000/static/*',
  timeout: 99999,
}));


// In production we need to pass these values in instead of relying on webpack
setup(app, {
  outputPath: resolve(process.cwd(), 'build'),
  publicPath: '/',
});

// get the intended port number, use port 3000 if not provided
const port = argv.port || process.env.PORT || 3000;

// Start your app.
app.listen(port, (err) => {
  if (err) {
    return logger.error(err.message);
  }

  logger.appStarted(port);
});
