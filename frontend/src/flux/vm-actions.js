var Reflux = require('reflux');

VMActions = Reflux.createActions([
  'sort',

  'list',
  'listSuccess',
  'listFail',

  'start',
  'startSuccess',
  'startFail'
]);

module.exports = VMActions;