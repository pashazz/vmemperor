import React from 'react';

import SelectList from './SelectList';

const Network = ({networks, onChange, required}) =>
{
  return (
    <SelectList data={networks}
                onChange={onChange}
                placeholder="Select Network..."
                isSearchable
                name='network'
                id='network'
                required={required}
    />
      );
};

export default Network;
