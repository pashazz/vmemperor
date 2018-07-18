import T from 'prop-types';
import React from 'react';
import { Input , InputGroup} from 'reactstrap';

const  Name = ({name,onChange}) =>
{
  return (
    <div>
      <InputGroup>
        <Input
          name="name_label"
          id="name_label"
          placeholder="Enter VM name..."
          lg
          onChange={onChange}
          value={name}
          />
      </InputGroup>
    </div>
  );
};

export default Name;
