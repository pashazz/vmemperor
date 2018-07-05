
import { fromJS } from 'immutable';
import vncviewReducer from '../reducer';

describe('vncviewReducer', () => {
  it('returns the initial state', () => {
    expect(vncviewReducer(undefined, {})).toEqual(fromJS({}));
  });
});
