var React = require('react'),
    _ = require('lodash');

var Modal = React.createClass({

  hide: function() {
    if(_.isFunction(this.props.close)) {
      this.props.close();
    } else {
      if(this.props.close) {
        this.setState({show: false});
      }
    }
  },

  getInitialState: function() {
    return {
      show: this.props.show
    };
  },

  renderCloseButton: function() {
    return this.props.close ?
      <button type="button" className="close" aria-label="Close" onClick={this.hide}><span aria-hidden="true">×</span></button> :
      null;
  },
    
  render: function () {
    if(!this.state.show) {
      return null;
    }
    var modalSizeClass = this.props.lg ? "modal-dialog modal-lg" : "modal-dialog";
    
    return (
      <div className='modal fade in' role="dialog" aria-hidden="false" style={{ display: 'block' }}>
        <div className="modal-backdrop fade in" style={{ height: '100%' }} onClick={this.hide}></div>
        <div className={modalSizeClass}>
          <div className="modal-content">
            <div className="modal-header">
              {this.renderCloseButton()}
              <h4 className="modal-title">{this.props.title}</h4>
            </div>
            <div className="modal-body">
              {this.props.children}
            </div>
          </div>
        </div>
      </div>
    );
  }
});

module.exports = Modal;