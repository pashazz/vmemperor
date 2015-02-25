var React = require('react'),
    Reflux = require('reflux')
    AlertsStore = require('../flux/alert-store');

var Snackbar = React.createClass({

  mixins: [Reflux.ListenerMixin],

  onAlertsChange: function() {
    this.setState({
      alerts: AlertsStore.getData()
    });
  },

  componentDidMount: function() {
    this.listenTo(AlertsStore, this.onAlertsChange);
  },

  getInitialState: function() {
    return {
      alerts: AlertsStore.getData()
    };
  },
    
  render: function () {
    if(this.state.alerts.length === 0) {
      return null
    } else {
      var computeClass = function(type) {
        switch(type){
          case 'suc': return 'alert alert-success';
          case 'warn': return 'alert alert-warning';
          case 'err': return 'alert alert-danger';
        }
        return 'alert alert-info';
      }

      var inner = this.state.alerts.map(function(alert, id){
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

module.exports = Snackbar;