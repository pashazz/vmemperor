import axios from 'axios'
const netinfo = async (uuid) =>
{
  return await axios.post('api/netinfo', {uuid});
};

export default netinfo;
