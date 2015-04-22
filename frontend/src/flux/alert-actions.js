var Reflux = require('reflux');

var AlertActions = Reflux.createActions([
  'suc',
  'log',
  'warn',
  'err'
]);

module.exports = AlertActions;
