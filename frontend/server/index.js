/* eslint consistent-return:0 */

const express = require('express');
const logger = require('./logger');

const argv = require('minimist')(process.argv.slice(2));
const setup = require('./middlewares/frontendMiddleware');
const resolve = require('path').resolve;
const app = express();
const proxy = require('express-http-proxy');
const requestProxy = require('express-request-proxy');


// If you need a backend, e.g. an API, add your custom backend-specific middleware here

/*
app.use('/api/*', requestProxy({
  url: 'http://localhost:5000/*',
  timeout: 99999,
  },
  intercept: (rsp, data, req, res, callback) => {
    // rsp - original response from the target
    console.log('set-cookie', rsp.headers['set-cookie']);
    callback(null, data);
  },
}));
*/

app.use('/api', proxy('localhost:5000',
  {
    proxyReqOptDecorator: (opts, proxyReq) => {
      console.log('request path:', opts.path);
      if (opts.headers.cookie) {
        console.log('Cookie', opts.headers.cookie);
      }
      else
        {
        console.log('no cookie');
      }
      return opts;
    },
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

// get the intended port number, use port 4000 if not provided
const port = argv.port || process.env.PORT || 4000;

// Start your app.
app.listen(port, (err) => {
  if (err) {
    return logger.error(err.message);
  }

  logger.appStarted(port);
});
