import expect from 'expect';
import loginPageReducer from '../reducer';
import { fromJS } from 'immutable';

describe('loginPageReducer', () => {
  it('returns the initial state', () => {
    const initialState = fromJS({
      pools: [],
    });
    expect(loginPageReducer(undefined, {})).toEqual(initialState);
  });
});
