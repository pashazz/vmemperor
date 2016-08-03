import Reflux from 'reflux';
import SessionActions from './session-actions';
import AlertActions from './alert-actions';
import VMAPI from '../api/vmemp-api';

const SessionStore = Reflux.createStore({
  init() {
    this.listenToMany(SessionActions);

    this.session = VMAPI.user.session();
    this.trigger(this.session);
  },

  onLogoutCompleted(response) {
    this.session = null;
    this.trigger(null);
  },

  onLogoutFailed(response) {
    AlertActions.err('Coudn\'t logout');
  },

  onAuthCompleted(response) {
    this.session = VMAPI.user.session();
    this.trigger(this.session);
  },

  onAuthFailed(response) {
    AlertActions.err('Coudn\'t login');
  },

  getData() {
    return this.session;
  }
});

export default SessionStore;
