import 'react-toggle-switch/dist/css/switch.min.css';
import React, { PropTypes as T } from 'react';
import Switch from 'react-toggle-switch';

class Hook extends React.Component {
  hookOptions(props) {
    return props.options.map((option, idx) =>
      <div key={idx}>
        <label className="control-label" htmlFor={option.field}>{option.legend}</label>
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-cog"></i></span>
          <input
            type="text"
            className="form-control"
            id={option.field}
            name={`hooks[${props.hookName}][${option.field}]`}
            value={props.selected[option.field]}
            onChange={props.onChange(props.hookName, option.field)}
          />
        </div>
      </div>
    );
  }

  render() {
    const { header, help, hookName, selected, onChange } = this.props;
    const enabled = selected ? selected.enabled : false;

    return (
      <div>
        <input type="hidden" name={`hooks[${hookName}][enabled]`} value={enabled} />
        <Switch on={enabled} onClick={onChange(hookName, !enabled)} />
        <h5>{header}</h5>
        {
          enabled ?
            this.hookOptions(this.props) : <h6>{help}</h6>
        }
      </div>
    );
  }
}

Hook.propTypes = {
  header: T.string.isRequired,
  hookName: T.string.isRequired,
  selected: T.any,
  help: T.string.isRequired,
  options: T.array.isRequired,
  onChange: T.func.isRequired,
};

export default Hook;
