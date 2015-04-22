import _ from 'lodash';
import Reflux from 'reflux';
import AlertActions from './alert-actions';

const AlertStore = Reflux.createStore({

    init() {
      this.listenToMany(AlertActions);

      this.alerts = []

      setInterval(this.checkAlerts, 1000);
    },

    checkAlerts() {
      let now = new Date();
      this.alerts = _.filter(this.alerts, function(alert) {
        return now - alert.added < 5000;
      });
      if(this.alerts.length > 5) {
        this.alerts.shift();
      };
      this.trigger();
    },

    onSuc(message) {
      this.alerts.push({
        message: message,
        type: 'suc',
        added: new Date()
      });
      this.trigger();
    },

    onLog(message) {
      this.alerts.push({
        message: message,
        type: 'log',
        added: new Date()
      });
      this.trigger();
    },

    onWarn(message) {
      this.alerts.push({
        message: message,
        type: 'warn',
        added: new Date()
      });
      this.trigger();
    },

    onErr(message) {
      this.alerts.push({
        message: message,
        type: 'err',
        added: new Date()
      });
      this.trigger();
    },

    getData() {
      return this.alerts;
    }
});

export default AlertStore;
