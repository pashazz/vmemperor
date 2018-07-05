import axios from 'axios'
const poollist = async (form) =>
{
  return await axios.post('api/createvm', form);
};

export default poollist;
