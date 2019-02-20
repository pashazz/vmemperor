import T from 'prop-types';

export const Access = T.arrayOf(
  T.shape({
    access: T.array.isRequired,
    userid: T.string.isRequired,
    }
  )
);

