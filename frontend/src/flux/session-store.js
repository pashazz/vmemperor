var Reflux = require('reflux'),
    SessionActions = require('./session-actions'),
    AlertActions = require('./alert-actions'),
    VMAPI = require('../api/vmemp-api');

var SessionStore = Reflux.createStore({
  init: function() {
    this.listenToMany(SessionActions);

    this.session = VMAPI.user.session();
    this.trigger(this.session);
  },

  onLogoutCompleted: function(response) {
    this.session = null;
    this.trigger(null);
  },

  onLogoutFailed: function(response) {
    AlertActions.err("Coudn't logout");
  },

  onAuthCompleted: function(response) {
    this.session = VMAPI.user.session();
    this.trigger(this.session);
  },

  onAuthFailed: function(response) {
    AlertActions.err("Coudn't login");
  },

  getData: function() {
    return this.session;
  }
});

module.exports = SessionStore;