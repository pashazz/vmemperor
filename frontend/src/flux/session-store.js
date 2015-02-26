var Reflux = require('reflux'),
    SessionActions = require('./session-actions'),
    AlertActions = require('./alert-actions'),
    VMAPI = require('../api/vmemp-api');

var SessionStore = Reflux.createStore({
  init: function() {
    this.listenTo(SessionActions.auth, this.auth);
    this.listenTo(SessionActions.logout, this.logout);

    this.session = VMAPI.session();
    this.trigger(this.session);
  },

  logout: function() {
    VMAPI.logout()
      .then(this.onLogoutSuccess)
      .catch(function(response) {
        AlertActions.err("Coudn't logout");
      });
  },

  onLogoutSuccess: function(response) {
    this.session = null;
    this.trigger(null);
  },

  auth: function(data) {
    VMAPI.auth(data)
      .then(this.onAuthSuccess)
      .catch(function(response) {
        AlertActions.err("Coudn't login");
      });
  },

  onAuthSuccess: function(response) {
    this.session = VMAPI.session();
    this.trigger(this.session);
  },

  getData: function() {
    return this.session;
  }
});

module.exports = SessionStore;