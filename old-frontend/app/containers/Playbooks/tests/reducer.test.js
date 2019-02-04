
import { fromJS } from 'immutable';
import playbooksReducer from '../reducer';

describe('playbooksReducer', () => {
  it('returns the initial state', () => {
    expect(playbooksReducer(undefined, {})).toEqual(fromJS({}));
  });
});
