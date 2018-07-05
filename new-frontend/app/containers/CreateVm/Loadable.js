/**
 *
 * Asynchronously loads the component for CreateVm
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});
