import axios from 'axios'
const poollist = async () =>
{
  return await axios.get('api/poollist');
};

export default poollist;
