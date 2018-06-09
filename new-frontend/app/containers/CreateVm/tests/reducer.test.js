
import { fromJS } from 'immutable';
import createVmReducer from '../reducer';

describe('createVmReducer', () => {
  it('returns the initial state', () => {
    expect(createVmReducer(undefined, {})).toEqual(fromJS({}));
  });
});
