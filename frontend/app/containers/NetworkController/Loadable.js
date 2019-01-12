/**
 *
 * Asynchronously loads the component for NetworkController
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});
