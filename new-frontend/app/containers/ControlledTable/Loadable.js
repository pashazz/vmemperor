/**
 *
 * Asynchronously loads the component for ControlledTable
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});
