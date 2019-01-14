import T from 'prop-types';

export const VMRecord = T.shape(
  {
    uuid : T.string.isRequired,
    name_label: T.string.isRequired,
    power_state: T.oneOf(['Halted', 'Running']).isRequired
  });

