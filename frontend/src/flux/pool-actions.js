var Reflux = require('reflux');

PoolActions = Reflux.createActions([
  'list',
  'listSuccess',
  'listFail'
]);

module.exports = PoolActions;