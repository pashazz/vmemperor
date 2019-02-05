
import { fromJS } from 'immutable';
import accessControllerReducer from '../reducer';

describe('accessControllerReducer', () => {
  it('returns the initial state', () => {
    expect(accessControllerReducer(undefined, {})).toEqual(fromJS({}));
  });
});
