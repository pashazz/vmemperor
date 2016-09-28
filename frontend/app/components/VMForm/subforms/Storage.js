import React, { PropTypes as T } from 'react';

function Template({ storages = [], selected, onChange }) {
  if (storages.length === 0) {
    return null;
  }
  return (
    <div className="input-group" style={{ paddingBottom: '10px' }}>
      <span className="input-group-addon"><i className="icon-database"></i></span>
      <select
        required
        className="form-control"
        id="storage-select"
        name="storage-select"
        onChange={onChange}
        value={selected}
      >
        <option value="">Select storage backend for your virtual machine</option>
        {
          storages.map(storage =>
            <option key={storage.id} value={storage.id}>{storage.description}</option>)
        }
      </select>
    </div>
  );
}

Template.propTypes = {
  storages: T.any.isRequired,
  selected: T.string.isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Template;
