import axios from 'axios'
const isolist = async () =>
{
  return await axios.get('api/isolist');
};

export default isolist;
