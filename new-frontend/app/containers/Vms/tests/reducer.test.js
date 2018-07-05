
import { fromJS } from 'immutable';
import vmsReducer from '../reducer';

describe('vmsReducer', () => {
  it('returns the initial state', () => {
    expect(vmsReducer(undefined, {})).toEqual(fromJS({}));
  });
});
