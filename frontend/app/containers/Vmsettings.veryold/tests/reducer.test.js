
import { fromJS } from 'immutable';
import vmsettingsReducer from '../reducer';

describe('vmsettingsReducer', () => {
  it('returns the initial state', () => {
    expect(vmsettingsReducer(undefined, {})).toEqual(fromJS({}));
  });
});
