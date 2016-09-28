import expect from 'expect';
import history2Reducer from '../reducer';
import { fromJS } from 'immutable';

describe('history2Reducer', () => {
  it('returns the initial state', () => {
    expect(history2Reducer(undefined, {})).toEqual(fromJS({}));
  });
});
