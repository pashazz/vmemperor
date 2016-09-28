import expect from 'expect';
import {
  auth,
  setSession,
  logout,
} from '../actions';
import {
  AUTH,
  SET_SESSION,
  LOGOUT,
} from '../constants';

describe('LoginPage actions', () => {
  describe('Auth Action', () => {
    it('has a type of AUTH', () => {
      const expected = {
        type: AUTH,
        payload: 1,
      };
      expect(auth(1)).toEqual(expected);
    });
  });

  describe('Logout Action', () => {
    it('has a type of LOGOUT', () => {
      const expected = {
        type: LOGOUT,
      };
      expect(logout()).toEqual(expected);
    });
  });

  describe('Set Session Action', () => {
    it('has a type of SET_SESSION', () => {
      const expected = {
        type: SET_SESSION,
        session: 123,
      };
      expect(setSession(123)).toEqual(expected);
    });
  });
});
