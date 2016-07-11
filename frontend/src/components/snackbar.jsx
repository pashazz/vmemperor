import React from 'react';
import Reflux from 'reflux';
import AlertsStore from '../flux/alert-store';

const Snackbar = React.createClass({
  mixins: [Reflux.ListenerMixin],

  onAlertsChange() {
    this.setState({
      alerts: AlertsStore.getData()
    });
  },

  componentDidMount() {
    this.listenTo(AlertsStore, this.onAlertsChange);
  },

  getInitialState() {
    return {
      alerts: AlertsStore.getData()
    };
  },

  render () {
    if(this.state.alerts.length === 0) {
      return null
    } else {
      const computeClass = function(type) {
        switch(type){
          case 'suc': return 'alert alert-success';
          case 'warn': return 'alert alert-warning';
          case 'err': return 'alert alert-danger';
        }
        return 'alert alert-info';
      }

      const inner = this.state.alerts.map((alert, id) => {
        return (<div key={id} className={computeClass(alert.type)} role="alert">{alert.message}</div>);
      });

      return (
        <div id="snackbar-container">
          <div className="snackbar snackbar-opened">
            <span className="snackbar-content">
              {inner}
            </span>
          </div>
        </div>
      );
    }
  }

});

export default Snackbar;
