import expect from 'expect';
import createVmReducer from '../reducer';
import { fromJS } from 'immutable';

describe('createVmReducer', () => {
  it('returns the initial state', () => {
    expect(createVmReducer(undefined, {})).toEqual(fromJS({}));
  });
});
