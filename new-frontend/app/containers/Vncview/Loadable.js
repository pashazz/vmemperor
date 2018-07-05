/**
 *
 * Asynchronously loads the component for Vncview
 *
 */

import Loadable from 'react-loadable';

export default Loadable({
  loader: () => import('./index'),
  loading: () => null,
});
