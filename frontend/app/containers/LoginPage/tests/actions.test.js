import expect from 'expect';
import {
  setPools,
} from '../actions';
import {
  SET_POOLS,
} from '../constants';

describe('LoginPage actions', () => {
  describe('Set Pools Action', () => {
    it('has a type of SET_POOLS', () => {
      const expected = {
        type: SET_POOLS,
        pools: [1, 2, 3],
      };
      expect(setPools([1, 2, 3])).toEqual(expected);
    });
  });
});
