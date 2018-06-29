import React from 'react';
import T from 'prop-types';


function Network({ networks = [], selected, onChange }) {
  if (networks.length === 0) {
    return null;
  }
  return (
    <div className="input-group" style={{ paddingBottom: '10px' }}>
      <span className="input-group-addon"><i className="icon-network"></i></span>
      <select
        required
        className="form-control"
        id="network-select"
        name="network-select"
        value={selected}
        onChange={onChange}
      >
        <option value="">Select physical network for your virtual machine</option>
        {
          networks.map(network =>
            <option key={network.id} value={network.id}>{network.description}</option>)
        }
      </select>
    </div>
  );
}

Network.propTypes = {
  networks: T.any.isRequired,
  selected: T.string.isRequired,
  isValid: T.bool,
  onChange: T.func.isRequired,
};

export default Network;
