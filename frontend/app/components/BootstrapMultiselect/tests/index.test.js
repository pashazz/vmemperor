import BootstrapMultiselect from '../index';

import expect from 'expect';
import { shallow } from 'enzyme';
import React from 'react';

describe('<BootstrapMultiselect />', () => {
  it('should render empty', () => {
    const rendered = shallow(<BootstrapMultiselect />);
    expect(rendered.find(BootstrapMultiselect)).toExist();
  });
});
