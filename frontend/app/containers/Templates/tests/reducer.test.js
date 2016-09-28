import expect from 'expect';
import templatesReducer from '../reducer';
import { fromJS } from 'immutable';

describe('templatesReducer', () => {
  it('returns the initial state', () => {
    expect(templatesReducer(undefined, {})).toEqual(fromJS({}));
  });
});
