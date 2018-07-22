import axios from 'axios'
const vminfo = async (uuid) =>
{
  return await axios.post('api/vminfo', {uuid});
};

export default vminfo;
