/* eslint consistent-return:0 */

const express = require('express');
const logger = require('./logger');

const argv = require('./argv');
const port = require('./port');
const setup = require('./middlewares/frontendMiddleware');
const isDev = process.env.NODE_ENV !== 'production';
const ngrok = (isDev && process.env.ENABLE_TUNNEL) || argv.tunnel ? require('ngrok') : false;
const resolve = require('path').resolve;
const app = express();
const path = require('path');
const morgan = require('morgan');
const fs = require('fs');


const requestProxy = require('http-proxy-middleware');

// If you need a backend, e.g. an API, add your custom backend-specific middleware here
// app.use('/api', myApi);

// create a write stream (in append mode)
const accessLogStream = fs.createWriteStream(path.join(__dirname, 'access.log'), {flags: 'a'});

app.use(express.static(path.join(__dirname, '..',  'static')));

// setup the logger
app.use(morgan('combined', {stream: accessLogStream}));



/*app.use('/api/*', requestProxy({
  url: 'http://localhost:8889/*',
  timeout: 99999,
}));
*/
const options = {
  target: 'http://localhost:8889',
  ws: true,
  pathRewrite : {
    '^/api': '/'
  }
};
const proxy = requestProxy(options);
app.use('/api',proxy);


// In production we need to pass these values in instead of relying on webpack
setup(app, {
  outputPath: resolve(process.cwd(), 'build'),
  publicPath: '/',
});

// get the intended host and port number, use localhost and port 3000 if not provided
const customHost = argv.host || process.env.HOST;
const host = customHost || null; // Let http.Server use its default IPv6/4 host
const prettyHost = customHost || 'localhost';




// Start your app.
app.listen(port, host, (err) => {
  if (err) {
    return logger.error(err.message);
  }

  // Connect to ngrok in dev mode
  if (ngrok) {
    ngrok.connect(port, (innerErr, url) => {
      if (innerErr) {
        return logger.error(innerErr);
      }

      logger.appStarted(port, prettyHost, url);
    });
  } else {
    logger.appStarted(port, prettyHost);
  }
});
