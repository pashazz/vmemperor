import Reflux from 'reflux';
import VMAPI from '../api/vmemp-api';

const SessionActions = Reflux.createActions({
  'auth': { asyncResult: true },
  'logout': { asyncResult: true }
});

SessionActions.auth.listenAndPromise( VMAPI.user.auth );
SessionActions.logout.listenAndPromise( VMAPI.user.logout );

export default SessionActions;
