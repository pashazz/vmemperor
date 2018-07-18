import React from 'react';

import SelectList from './SelectList';

const Network = ({networks, onChange}) =>
{
  return (
    <SelectList data={networks}
                onChange={onChange}
                placeholder="Select Network..."
                isSearchable
                name='network'
                id='network' />
      );
};

export default Network;
