var Reflux = require('reflux');

AlertActions = Reflux.createActions([
  'suc',
  'log',
  'warn',
  'err'
]);

module.exports = AlertActions;