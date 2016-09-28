import React, { PropTypes as T } from 'react';
import classNames from 'classnames';

export function validate(cpu) {
  if (cpu < 1 || cpu > 16) {
    return 'should be between 1 and 16';
  }
  return '';
}

function CPU({ cpu, onChange, className, touched }) {
  const validation = validate(cpu);
  const isValid = validation === '';

  const mainClassName = classNames(className, 'form-group', {
    'has-success': touched && isValid,
    'has-error': touched && !isValid,
  });

  const errorText = touched && !isValid ?
    <span className="help-block">{ validation }</span> : null;

  return (
    <div className={mainClassName}>
      <div className="input-group">
        <span className="input-group-addon"><i className="icon-processorthree"></i></span>
        <input
          type="number"
          className="form-control"
          id="cpu"
          name="cpu"
          min="1"
          value={cpu}
          onChange={onChange}
        />
        <span className="input-group-addon">cores</span>
      </div>
      { errorText }
    </div>
  );
}

CPU.propTypes = {
  cpu: T.any.isRequired,
  touched: T.bool.isRequired,
  onChange: T.func.isRequired,
  className: T.string,
};

export default CPU;
