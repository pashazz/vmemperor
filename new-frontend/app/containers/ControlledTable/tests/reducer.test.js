
import { fromJS } from 'immutable';
import controlledTableReducer from '../reducer';

describe('controlledTableReducer', () => {
  it('returns the initial state', () => {
    expect(controlledTableReducer(undefined, {})).toEqual(fromJS({}));
  });
});
