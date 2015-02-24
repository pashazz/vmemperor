var Reflux = require('reflux');

VMActions = Reflux.createActions([
  'sort',

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