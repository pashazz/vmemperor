var Reflux = require('reflux'),
    AlertActions = require('./alert-actions'),
    _ = require('lodash');

var AlertStore = Reflux.createStore({

    init: function() {
      this.listenTo(AlertActions.suc, this.onSuc);
      this.listenTo(AlertActions.log, this.onLog);
      this.listenTo(AlertActions.warn, this.onWarn);
      this.listenTo(AlertActions.err, this.onErr);

      this.alerts = []

      setInterval(this.checkAlerts, 1000);
    },

    checkAlerts: function() {
      var now = new Date();
      this.alerts = _.filter(this.alerts, function(alert) {
        return now - alert.added < 5000;
      });
      if(this.alerts.length > 5) {
        this.alerts.shift();
      };
      this.trigger();
    },

    onSuc: function(message) {
      this.alerts.push({
        message: message,
        type: 'suc',
        added: new Date()
      });
      this.trigger();
    },

    onLog: function(message) {
      this.alerts.push({
        message: message,
        type: 'log',
        added: new Date()
      });
      this.trigger();
    },

    onWarn: function(message) {
      this.alerts.push({
        message: message,
        type: 'warn',
        added: new Date()
      });
      this.trigger();
    },

    onErr: function(message) {
      this.alerts.push({
        message: message,
        type: 'err',
        added: new Date()
      });
      this.trigger();
    },

    getData: function() { 
      return this.alerts; 
    }
});

module.exports = AlertStore;