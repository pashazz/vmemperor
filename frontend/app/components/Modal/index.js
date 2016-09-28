import React, { PropTypes as T } from 'react';

function getScrollbarWidth() {
  const outer = document.createElement('div');
  outer.style.visibility = 'hidden';
  outer.style.width = '100px';
  outer.style.msOverflowStyle = 'scrollbar';
  document.body.appendChild(outer);
  const widthNoScroll = outer.offsetWidth;
  outer.style.overflow = 'scroll';
  const inner = document.createElement('div');
  inner.style.width = '100%';
  outer.appendChild(inner);
  const widthWithScroll = inner.offsetWidth;
  outer.parentNode.removeChild(outer);
  return widthNoScroll - widthWithScroll;
}

export const scrollbarWidth = `${getScrollbarWidth()}px`;

class Modal extends React.Component {
  static propTypes = {
    lg: T.bool,
    closable: T.bool,
    close: T.func,
    show: T.bool,
    title: T.string.isRequired,
    children: T.any,
  }

  static defaultProps = {
    lg: false,
    closable: false,
    show: true,
  }

  constructor(props) {
    super();
    this.hide = this.hide.bind(this);
    this.renderCloseButton = this.renderCloseButton.bind(this);

    this.state = { show: props.show };
  }

  componentWillReceiveProps(newProps) {
    this.setState({ show: newProps.show });
  }

  componentWillUnmount() {
    document.body.style.overflow = 'auto';
    document.body.style.marginRight = 0;
  }

  hide() {
    if (this.props.close) {
      this.props.close();
    }
    if (this.props.closable) {
      this.setState({ show: false });
    }
  }

  renderCloseButton() {
    return this.props.closable || this.props.close ?
      <button type="button" className="close" aria-label="Close" onClick={this.hide}><span aria-hidden="true">×</span></button> :
      null;
  }

  render() {
    document.body.style.overflow = this.props.show ? 'hidden' : 'auto';
    if (document.body.clientHeight > window.innerHeight) {
      document.body.style.marginRight = this.props.show ? scrollbarWidth : 0;
    }
    if (!this.state.show) {
      return null;
    }
    const modalSizeClass = this.props.lg ? 'modal-dialog modal-lg' : 'modal-dialog';

    return (
      <div className="modal fade in" role="dialog" aria-hidden="false" style={{ display: 'block' }}>
        <div className="modal-backdrop fade in" style={{ height: '100%' }} onClick={this.hide}></div>
        <div className={modalSizeClass} style={{ zIndex: 9000 }}>
          <div className="modal-content">
            <div className="modal-header">
              {this.renderCloseButton()}
              <h4 className="modal-title">{this.props.title}</h4>
            </div>
            <div className="modal-body" style={{ maxHeight: '90vh', overflow: 'auto' }}>
              {this.props.children}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Modal;
