import axios from 'axios'
const tmpllist = async () =>
{
  return await axios.get('api/tmpllist');
};

export default tmpllist;
