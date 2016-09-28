// import SinglePoolLogin from '../index';

import expect from 'expect';
import { mount } from 'enzyme';
import React from 'react';
import { IntlProvider } from 'react-intl';
import SinglePoolLogin from '../';

describe('<SinglePoolLogin />', () => {
  it('should render proper description', () => {
    const description = Math.random().toString(36).substring(2);
    const renderedComponent = mount(
      <IntlProvider locale="en">
        <SinglePoolLogin description={description} index={0} />
      </IntlProvider>
    );
    expect(renderedComponent.find('div.input-group-addon').text()).toEqual(description);
  });
});
