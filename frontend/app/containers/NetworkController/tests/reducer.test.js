
import { fromJS } from 'immutable';
import networkControllerReducer from '../reducer';

describe('networkControllerReducer', () => {
  it('returns the initial state', () => {
    expect(networkControllerReducer(undefined, {})).toEqual(fromJS({}));
  });
});
