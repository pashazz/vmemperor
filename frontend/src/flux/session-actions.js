var Reflux = require('reflux');

SessionActions = Reflux.createActions([
  'auth',
  'authSuccess',
  'authFail',

  'logout',
  'logoutSuccess',
  'logoutFail'
]);

module.exports = SessionActions;