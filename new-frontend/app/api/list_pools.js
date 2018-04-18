import axios from 'axios'
const list_pools = async () =>
{
  return await axios.get('api/list_pools');
};

export default list_pools;
