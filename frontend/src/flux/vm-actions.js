var Reflux = require('reflux');

VMActions = Reflux.createActions([
  'list',
  'listSuccess',
  'listFail',

  'start',
  'startSuccess',
  'startFail',

  'shutdown',
  'shutdownSuccess',
  'shutdownFail'
]);

module.exports = VMActions;