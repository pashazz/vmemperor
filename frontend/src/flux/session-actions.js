var Reflux = require('reflux'),
    VMAPI = require('../api/vmemp-api');

var SessionActions = Reflux.createActions({
  'auth': { asyncResult: true },
  'logout': { asyncResult: true }
});

SessionActions.auth.listenAndPromise( VMAPI.user.auth );
SessionActions.logout.listenAndPromise( VMAPI.user.logout );

module.exports = SessionActions;
